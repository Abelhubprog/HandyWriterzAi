from typing import Dict, Any, List
from typing import Optional, cast

try:
    import chromadb
    from sentence_transformers import SentenceTransformer
except Exception:
    chromadb = None  # type: ignore
    SentenceTransformer = None  # type: ignore

from ..base import BaseNode, NodeError
from ..handywriterz_state import HandyWriterzState

class RAGSummarizerNode(BaseNode):
    """A node that uses RAG to summarize documents."""

    def __init__(self):
        super().__init__("rag_summarizer")
        self.embedding_model = None
        self.chroma_client = None
        self.collection = None
        self._initialize_vector_stack()

    def _initialize_vector_stack(self) -> None:
        """Best-effort initialization of embedding model and Chroma collection."""
        try:
            if SentenceTransformer:
                self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
            if chromadb:
                self.chroma_client = chromadb.Client()
                self.collection = self.chroma_client.get_or_create_collection(name="documents")
            self.logger.info("RAG vector stack initialized")
        except Exception as e:
            self.logger.warning(f"RAG vector stack initialization failed: {e}")
            self.embedding_model = None
            self.collection = None

    async def execute(self, state: Dict[str, Any], config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Executes the RAG summarizer node.

        Args:
            state: The current workflow state (dict-like).
            config: Optional per-run config.

        Returns:
            A dictionary containing the summaries and experiment suggestions.
        """
        aggregated_data: List[Dict[str, Any]] = cast(List[Dict[str, Any]], state.get("aggregated_data", []))
        summaries: List[str] = []
        experiment_suggestions: List[str] = []

        if not aggregated_data:
            self.logger.info("RAG Summarizer: No aggregated_data found, returning empty results")
            return {"summaries": [], "experiment_suggestions": []}

        for item in aggregated_data:
            try:
                full_name = item.get("full_name") or item.get("title") or "unknown"
                abstract = item.get("abstract", "") or ""
                readme = item.get("readme", "") or ""
                content_to_embed = (abstract + "\n" + readme).strip()

                # Best-effort vector add
                if self.embedding_model and self.collection and content_to_embed:
                    try:
                        embedding = self.embedding_model.encode(content_to_embed).tolist()
                        self.collection.add(
                            embeddings=[embedding],
                            documents=[content_to_embed],
                            metadatas=[{"source": full_name}],
                            ids=[full_name],
                        )
                    except Exception as ve:
                        self.logger.debug(f"Vector add failed for {full_name}: {ve}")

                # Placeholder summary/suggestion generation (LLM integration to be added)
                summaries.append(f"Summary: {full_name} — evidence-aware placeholder.")
                experiment_suggestions.append(f"Suggestion: Consider follow-up experiments for {full_name}.")

            except Exception as e:
                self.logger.warning(f"RAG summarization skipped for an item due to error: {e}")
                continue

        return {
            "summaries": summaries,
            "experiment_suggestions": experiment_suggestions,
        }
