"""
Revolutionary Embedding Service for HandyWriterz.
Production-ready text embeddings for semantic search and vector operations.
"""

import os
import logging
import asyncio
from typing import List, Dict, Any, Optional
import numpy as np
from openai import AsyncOpenAI
import tiktoken

logger = logging.getLogger(__name__)


class RevolutionaryEmbeddingService:
    """Production-ready embedding service with advanced text processing."""

    def __init__(self):
        self.client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.model = "text-embedding-3-small"  # Efficient and cost-effective
        self.max_tokens = 8191  # Model limit
        self.dimension = 1536

        # Initialize tokenizer
        try:
            self.tokenizer = tiktoken.encoding_for_model("text-embedding-3-small")
        except:
            self.tokenizer = tiktoken.get_encoding("cl100k_base")

        # Rate limiting
        self.rate_limit_delay = 0.1  # 100ms between requests
        self.max_batch_size = 100

        logger.info("Revolutionary Embedding Service initialized")

    async def embed_text(self, text: str, prefix: str = "") -> List[float]:
        """Generate embedding for a single text."""
        try:
            # Prepare text
            processed_text = self._prepare_text(text, prefix)

            # Generate embedding
            response = await self.client.embeddings.create(
                model=self.model,
                input=processed_text,
                encoding_format="float"
            )

            embedding = response.data[0].embedding

            # Apply rate limiting
            await asyncio.sleep(self.rate_limit_delay)

            return embedding

        except Exception as e:
            logger.error(f"Failed to generate embedding: {e}")
            raise

    async def embed_batch(
        self,
        texts: List[str],
        prefixes: Optional[List[str]] = None
    ) -> List[List[float]]:
        """Generate embeddings for multiple texts efficiently."""
        try:
            if not texts:
                return []

            # Prepare texts
            if prefixes:
                processed_texts = [
                    self._prepare_text(text, prefix)
                    for text, prefix in zip(texts, prefixes)
                ]
            else:
                processed_texts = [self._prepare_text(text) for text in texts]

            # Process in batches to respect rate limits
            all_embeddings = []

            for i in range(0, len(processed_texts), self.max_batch_size):
                batch = processed_texts[i:i + self.max_batch_size]

                response = await self.client.embeddings.create(
                    model=self.model,
                    input=batch,
                    encoding_format="float"
                )

                batch_embeddings = [data.embedding for data in response.data]
                all_embeddings.extend(batch_embeddings)

                # Rate limiting
                if i + self.max_batch_size < len(processed_texts):
                    await asyncio.sleep(self.rate_limit_delay * len(batch))

            logger.info(f"Generated {len(all_embeddings)} embeddings successfully")
            return all_embeddings

        except Exception as e:
            logger.error(f"Failed to generate batch embeddings: {e}")
            raise

    async def embed_document_components(self, source_data: Dict[str, Any]) -> Dict[str, List[float]]:
        """Generate embeddings for different components of a document."""
        try:
            embeddings = {}

            # Title embedding
            title = source_data.get("title", "")
            if title:
                embeddings["title_embedding"] = await self.embed_text(
                    title,
                    prefix="Academic title: "
                )

            # Abstract embedding
            abstract = source_data.get("abstract", "") or source_data.get("snippet", "")
            if abstract:
                embeddings["abstract_embedding"] = await self.embed_text(
                    abstract,
                    prefix="Academic abstract: "
                )

            # Content embedding (if available)
            content = source_data.get("content", "")
            if content:
                # Use first 2000 characters for content embedding
                content_preview = content[:2000]
                embeddings["content_embedding"] = await self.embed_text(
                    content_preview,
                    prefix="Academic content: "
                )

            logger.info(f"Generated {len(embeddings)} component embeddings for document")
            return embeddings

        except Exception as e:
            logger.error(f"Failed to generate document embeddings: {e}")
            raise

    async def embed_evidence_batch(self, evidence_data: List[Dict[str, Any]]) -> List[List[float]]:
        """Generate embeddings for evidence paragraphs."""
        try:
            # Prepare evidence texts with academic context
            evidence_texts = []

            for evidence in evidence_data:
                text = evidence.get("text", "")
                evidence_type = evidence.get("evidence_type", "general_evidence")

                # Add context prefix based on evidence type
                prefix_map = {
                    "systematic_review": "Systematic review evidence: ",
                    "experimental": "Experimental research evidence: ",
                    "survey_research": "Survey research evidence: ",
                    "case_study": "Case study evidence: ",
                    "longitudinal": "Longitudinal study evidence: ",
                    "cross_sectional": "Cross-sectional study evidence: ",
                    "qualitative": "Qualitative research evidence: ",
                    "statistical_analysis": "Statistical analysis evidence: ",
                    "general_evidence": "Academic evidence: "
                }

                prefix = prefix_map.get(evidence_type, "Academic evidence: ")
                evidence_texts.append(self._prepare_text(text, prefix))

            # Generate embeddings in batch
            embeddings = await self.embed_batch(evidence_texts)

            logger.info(f"Generated embeddings for {len(embeddings)} evidence pieces")
            return embeddings

        except Exception as e:
            logger.error(f"Failed to generate evidence embeddings: {e}")
            raise

    async def embed_image(self, image_path: str) -> List[float]:
        """Generate embedding for an image by first getting a caption."""
        try:
            # In a real implementation, this would call a vision model to get a caption.
            # For now, we'll use a placeholder.
            caption = "A placeholder caption for the image"
            return await self.embed_text(caption, prefix="Image caption: ")
        except Exception as e:
            logger.error(f"Failed to generate image embedding: {e}")
            raise

    async def embed_audio(self, audio_path: str) -> List[float]:
        """Generate embedding for an audio file by first getting a transcript."""
        try:
            # In a real implementation, this would call a speech-to-text model.
            # For now, we'll use a placeholder.
            transcript = "A placeholder transcript for the audio"
            return await self.embed_text(transcript, prefix="Audio transcript: ")
        except Exception as e:
            logger.error(f"Failed to generate audio embedding: {e}")
            raise

    async def embed_query(self, query: str, query_type: str = "search") -> List[float]:
        """Generate embedding for search queries with appropriate context."""
        try:
            # Add context prefix based on query type
            prefix_map = {
                "search": "Search query: ",
                "academic_search": "Academic research query: ",
                "evidence_search": "Evidence search query: ",
                "similarity": "Find similar content: ",
                "classification": "Classify content: "
            }

            prefix = prefix_map.get(query_type, "Search query: ")

            embedding = await self.embed_text(query, prefix)

            logger.info(f"Generated query embedding for: {query[:50]}...")
            return embedding

        except Exception as e:
            logger.error(f"Failed to generate query embedding: {e}")
            raise

    def _prepare_text(self, text: str, prefix: str = "") -> str:
        """Prepare text for embedding generation."""
        if not text:
            return ""

        # Clean text
        cleaned_text = self._clean_text(text)

        # Add prefix if provided
        if prefix:
            full_text = prefix + cleaned_text
        else:
            full_text = cleaned_text

        # Truncate to model limits
        tokens = self.tokenizer.encode(full_text)
        if len(tokens) > self.max_tokens:
            # Truncate tokens and decode back to text
            truncated_tokens = tokens[:self.max_tokens]
            full_text = self.tokenizer.decode(truncated_tokens)

        return full_text

    def _clean_text(self, text: str) -> str:
        """Clean and normalize text for better embeddings."""
        import re

        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text)

        # Remove HTML tags if present
        text = re.sub(r'<[^>]+>', '', text)

        # Remove URLs
        text = re.sub(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', '', text)

        # Normalize quotes
        text = re.sub(r'["""]', '"', text)
        text = re.sub(r'['']', "'", text)

        # Remove excessive punctuation
        text = re.sub(r'[.]{3,}', '...', text)
        text = re.sub(r'[!]{2,}', '!', text)
        text = re.sub(r'[?]{2,}', '?', text)

        return text.strip()

    def calculate_similarity(self, embedding1: List[float], embedding2: List[float]) -> float:
        """Calculate cosine similarity between two embeddings."""
        try:
            # Convert to numpy arrays
            vec1 = np.array(embedding1)
            vec2 = np.array(embedding2)

            # Calculate cosine similarity
            dot_product = np.dot(vec1, vec2)
            norm1 = np.linalg.norm(vec1)
            norm2 = np.linalg.norm(vec2)

            if norm1 == 0 or norm2 == 0:
                return 0.0

            similarity = dot_product / (norm1 * norm2)
            return float(similarity)

        except Exception as e:
            logger.error(f"Failed to calculate similarity: {e}")
            return 0.0

    def find_most_similar(
        self,
        query_embedding: List[float],
        embeddings: List[List[float]],
        top_k: int = 5
    ) -> List[Tuple[int, float]]:
        """Find most similar embeddings to a query."""
        try:
            similarities = []

            for i, embedding in enumerate(embeddings):
                similarity = self.calculate_similarity(query_embedding, embedding)
                similarities.append((i, similarity))

            # Sort by similarity (descending)
            similarities.sort(key=lambda x: x[1], reverse=True)

            return similarities[:top_k]

        except Exception as e:
            logger.error(f"Failed to find similar embeddings: {e}")
            return []


# Global embedding service instance
embedding_service = RevolutionaryEmbeddingService()


# Dependency injection for FastAPI
def get_embedding_service() -> RevolutionaryEmbeddingService:
    """Get embedding service instance."""
    return embedding_service
