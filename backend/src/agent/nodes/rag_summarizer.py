from typing import Dict, Any
import chromadb
from sentence_transformers import SentenceTransformer
from src.agent.base import BaseNode
from ...agent.handywriterz_state import HandyWriterzState

class RAGSummarizerNode(BaseNode):
    """A node that uses RAG to summarize documents."""

    def __init__(self):
        super().__init__("rag_summarizer")
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        self.chroma_client = chromadb.Client()
        self.collection = self.chroma_client.create_collection(name="documents")

    async def execute(self, state: HandyWriterzState, config: dict) -> Dict[str, Any]:
        """
        Executes the RAG summarizer node.

        Args:
            state: The current state of the HandyWriterz workflow.
            config: The configuration for the agent.

        Returns:
            A dictionary containing the summaries and experiment suggestions.
        """
        aggregated_data = state.get("aggregated_data", [])
        
        summaries = []
        experiment_suggestions = []

        for item in aggregated_data:
            # Embed the document content
            content_to_embed = item.get("abstract", "") + "\n" + item.get("readme", "")
            embedding = self.embedding_model.encode(content_to_embed).tolist()
            
            # Add the document to the collection
            self.collection.add(
                embeddings=[embedding],
                documents=[content_to_embed],
                metadatas=[{"source": item.get("full_name")}],
                ids=[item.get("full_name")]
            )

            # Generate a summary
            # This is a simplified example. A more robust implementation would
            # use an LLM to generate the summary based on the document content.
            summary = f"This is a 3-line summary for {item.get('full_name')}."
            summaries.append(summary)

            # Generate experiment suggestions
            # This is a simplified example. A more robust implementation would
            # use an LLM to generate the suggestions based on the document content.
            suggestion = f"This is a suggested experiment pipeline for {item.get('full_name')}."
            experiment_suggestions.append(suggestion)

        return {
            "summaries": summaries,
            "experiment_suggestions": experiment_suggestions,
        }
