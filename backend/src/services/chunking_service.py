import tiktoken

class ChunkingService:
    def __init__(self, chunk_size=6000, overlap=500):
        self.chunk_size = chunk_size
        self.overlap = overlap
        self.tokenizer = tiktoken.get_encoding("cl100k_base")

    def chunk_text(self, text: str) -> list[str]:
        tokens = self.tokenizer.encode(text)
        chunks = []
        start = 0
        while start < len(tokens):
            end = start + self.chunk_size
            chunk_tokens = tokens[start:end]
            chunks.append(self.tokenizer.decode(chunk_tokens))
            if end >= len(tokens):
                break
            start += self.chunk_size - self.overlap
        return chunks

def get_chunking_service():
    return ChunkingService()
