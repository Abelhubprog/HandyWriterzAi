import os
import json
import mimetypes
import logging
from dataclasses import dataclass
from typing import List, Optional, Tuple

from src.api.files import UPLOAD_DIR
from src.services.object_storage import get_r2_storage

logger = logging.getLogger(__name__)


@dataclass
class LoadedFile:
    file_id: str
    filename: str
    content: Optional[str]  # Text content or None if binary or error
    mime_type: str
    size: int
    error: Optional[str] = None


class FileContentService:
    """
    Loads uploaded files saved by src.api.files into memory for prompt ingestion.
    - Resolves file_id to an actual saved file in UPLOAD_DIR (prefix match on filename).
    - Decodes text files to UTF-8 with errors='ignore'.
    - Caps per-file content length and total prompt context length.
    - Provides a compact formatter for inclusion into LLM prompts.
    """

    # Reasonable caps to protect prompt and memory
    MAX_TEXT_BYTES_PER_FILE = 512 * 1024       # 512 KB per file for decoding
    MAX_TEXT_CHARS_PER_FILE = 200_000          # ~200k chars cap per file after decode
    MAX_TOTAL_PROMPT_CHARS = 350_000           # total across all files in prompt header
    SNIPPET_HEAD_TAIL = 2000                   # chars kept from start and end when truncating

    def __init__(self, upload_dir: Optional[str] = None):
        self.upload_dir = upload_dir or UPLOAD_DIR
        os.makedirs(self.upload_dir, exist_ok=True)

    def _resolve_file_path(self, file_id: str) -> Tuple[Optional[str], Optional[str]]:
        """
        Finds the first file whose name starts with file_id in UPLOAD_DIR.
        Returns (absolute_path, filename) or (None, None) if not found.
        """
        # First try R2/object storage
        try:
            storage = get_r2_storage()
            prefix = f"uploads/{file_id}/"
            keys = storage.list_with_prefix(prefix)
            if keys:
                # Return a pseudo-path marker with special scheme 'r2://' to indicate remote
                return f"r2://{keys[0]}", keys[0].split("/")[-1]
        except Exception:
            # Object storage not configured; fall back to local
            pass

        try:
            for fname in os.listdir(self.upload_dir):
                if fname.startswith(file_id):
                    path = os.path.join(self.upload_dir, fname)
                    if os.path.isfile(path):
                        return path, fname
        except Exception as e:
            logger.warning(f"Failed to list upload dir for {file_id}: {e}")
        return None, None

    async def load_file_contents(self, file_ids: List[str]) -> List[LoadedFile]:
        """
        Asynchronously load files by IDs saved through /api/files endpoints.
        Returns a list of LoadedFile with error populated on failures.
        """
        results: List[LoadedFile] = []

        for fid in file_ids or []:
            path, fname = self._resolve_file_path(fid)
            if not path or not os.path.exists(path):
                # Special case: r2:// indicates remote object; fetch bytes
                if path and path.startswith("r2://"):
                    try:
                        key = path[len("r2://"):]
                        storage = get_r2_storage()
                        data = storage.get_bytes(key)
                        size = len(data)
                        mime, _ = mimetypes.guess_type(fname or key)
                        mime = mime or "application/octet-stream"
                        text_content: Optional[str] = None
                        if mime.startswith("text") or mime in (
                            "application/json",
                            "application/xml",
                            "application/xhtml+xml",
                        ):
                            try:
                                text_content = data.decode("utf-8", errors="ignore")
                            except Exception:
                                try:
                                    text_content = data.decode("latin-1", errors="ignore")
                                except Exception:
                                    text_content = None
                            if text_content and len(text_content) > self.MAX_TEXT_CHARS_PER_FILE:
                                text_content = self._truncate_text(text_content, self.MAX_TEXT_CHARS_PER_FILE)
                        results.append(
                            LoadedFile(
                                file_id=fid,
                                filename=fname or key.split("/")[-1],
                                content=text_content,
                                mime_type=mime,
                                size=size,
                                error=None,
                            )
                        )
                        continue
                    except Exception as e:
                        logger.error(f"Failed to fetch from object storage for {fid}: {e}")
                        results.append(
                            LoadedFile(
                                file_id=fid,
                                filename=fname or f"{fid}",
                                content=None,
                                mime_type="application/octet-stream",
                                size=0,
                                error=str(e),
                            )
                        )
                        continue
                else:
                    results.append(
                        LoadedFile(
                            file_id=fid,
                            filename=fname or f"{fid}",
                            content=None,
                            mime_type="application/octet-stream",
                            size=0,
                            error="not_found",
                        )
                    )
                    continue

            try:
                size = os.path.getsize(path)
                mime, _ = mimetypes.guess_type(path)
                mime = mime or "application/octet-stream"

                # Load only up to MAX_TEXT_BYTES_PER_FILE to avoid huge memory
                read_bytes = min(self.MAX_TEXT_BYTES_PER_FILE, size)
                with open(path, "rb") as f:
                    data = f.read(read_bytes)

                text_content: Optional[str] = None
                if mime.startswith("text") or mime in (
                    "application/json",
                    "application/xml",
                    "application/xhtml+xml",
                ):
                    try:
                        text_content = data.decode("utf-8", errors="ignore")
                    except Exception:
                        # Fallback: best-effort latin-1
                        try:
                            text_content = data.decode("latin-1", errors="ignore")
                        except Exception:
                            text_content = None

                    # Enforce per-file char cap
                    if text_content and len(text_content) > self.MAX_TEXT_CHARS_PER_FILE:
                        text_content = self._truncate_text(text_content, self.MAX_TEXT_CHARS_PER_FILE)

                results.append(
                    LoadedFile(
                        file_id=fid,
                        filename=fname or os.path.basename(path),
                        content=text_content,
                        mime_type=mime,
                        size=size,
                        error=None,
                    )
                )
            except Exception as e:
                logger.error(f"Failed to read file {fid} at {path}: {e}")
                results.append(
                    LoadedFile(
                        file_id=fid,
                        filename=fname or f"{fid}",
                        content=None,
                        mime_type="application/octet-stream",
                        size=0,
                        error=str(e),
                    )
                )

        return results

    def _truncate_text(self, text: str, limit: int) -> str:
        """
        Truncate text preserving head and tail with a marker in the middle.
        """
        if len(text) <= limit:
            return text
        head = text[: self.SNIPPET_HEAD_TAIL]
        tail = text[-self.SNIPPET_HEAD_TAIL :]
        return f"{head}\n\n... [TRUNCATED {len(text) - (len(head) + len(tail))} CHARS] ...\n\n{tail}"

    def format_files_for_prompt(self, files: List[LoadedFile]) -> str:
        """
        Produce a compact prompt header that enumerates files and includes text previews.
        Non-text files (content=None) are listed with metadata only.
        Caps total characters to MAX_TOTAL_PROMPT_CHARS.
        """
        sections: List[str] = []
        header_lines = [
            "=== UPLOADED FILES CONTEXT START ===",
            f"Total files: {len(files)}",
        ]
        sections.append("\n".join(header_lines))

        total_chars = 0

        for f in files:
            meta = f"- file_id: {f.file_id}\n  filename: {f.filename}\n  mime_type: {f.mime_type}\n  size_bytes: {f.size}"
            if f.error:
                sections.append(f"{meta}\n  status: error\n  error: {f.error}")
                continue

            if f.content is None:
                sections.append(f"{meta}\n  status: binary_or_unsupported\n  note: content omitted from prompt")
                continue

            content = f.content
            # Ensure each file's contribution doesn't blow up the overall cap
            remaining = max(0, self.MAX_TOTAL_PROMPT_CHARS - total_chars)
            if remaining <= 0:
                sections.append(f"{meta}\n  status: skipped_due_to_prompt_limit")
                continue

            if len(content) > remaining:
                content = self._truncate_text(content, min(self.MAX_TEXT_CHARS_PER_FILE, remaining))

            snippet = (
                "  content_preview:\n"
                + "\n".join([f"    {line}" for line in content.splitlines()[:400]])
            )
            block = f"{meta}\n  status: ok\n{snippet}"
            sections.append(block)
            total_chars += len(content)

        sections.append("=== UPLOADED FILES CONTEXT END ===")
        formatted = "\n\n".join(sections)

        if len(formatted) > self.MAX_TOTAL_PROMPT_CHARS:
            # Final safeguard
            formatted = self._truncate_text(formatted, self.MAX_TOTAL_PROMPT_CHARS)

        return formatted


# Singleton-style accessor
_service_instance: Optional[FileContentService] = None


def get_file_content_service() -> FileContentService:
    global _service_instance
    if _service_instance is None:
        _service_instance = FileContentService()
    return _service_instance
