from typing import Dict, Any, List, Optional, cast
from langchain_core.messages import HumanMessage
from ...base import BaseNode, NodeError
from ...handywriterz_state import HandyWriterzState

try:
    import chromadb
    from sentence_transformers import SentenceTransformer
    from src.services.model_service import get_model_service
except ImportError as e:
    chromadb = None
    SentenceTransformer = None
    get_model_service = None

class SummarizerNode(BaseNode):
    """A node that uses RAG to summarize documents with LLM integration."""

    def __init__(self):
        super().__init__("summarizer", max_retries=2)
        self.embedding_model = None
        self.chroma_client = None
        self.collection = None
        self.model_service = None
        self.llm_client = None
        self.agent_name = "summarizer_gemini"
        self._initialize_services()

    def _initialize_services(self) -> None:
        """Initializes embedding model, ChromaDB, and the LLM service."""
        try:
            if SentenceTransformer:
                self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
            if chromadb:
                self.chroma_client = chromadb.Client()
                self.collection = self.chroma_client.get_or_create_collection(name="summarization_docs")
            if get_model_service:
                self.model_service = get_model_service()
            self.logger.info("RAG services initialized successfully.")
        except Exception as e:
            self.logger.warning(f"RAG service initialization failed: {e}")
            # Reset all components on failure
            self.embedding_model = self.collection = self.model_service = None

    async def execute(self, state: HandyWriterzState, config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Executes the RAG summarizer node with full LLM integration.
        """
        if not self.model_service or not self.collection or not self.embedding_model:
            raise NodeError("RAG services not available. Cannot execute.", self.name)

        # Dynamically get the LLM client for this execution
        self.llm_client = await self.model_service.get_model_client(self.agent_name)
        if not self.llm_client:
            raise NodeError(f"LLM client '{self.agent_name}' not available.", self.name)

        # The node can now process either 'aggregated_data' or a direct 'text_to_summarize'
        input_text = state.get("text_to_summarize")
        aggregated_data = cast(List[Dict[str, Any]], state.get("aggregated_data", []))

        if input_text:
            docs_to_process = [{"full_name": "direct_input", "content": input_text}]
        elif aggregated_data:
            docs_to_process = [
                {"full_name": item.get("full_name") or item.get("title") or f"doc_{i}",
                 "content": (item.get("abstract", "") + "\n" + item.get("readme", "")).strip()}
                for i, item in enumerate(aggregated_data)
            ]
        else:
            self.logger.info("RAG Summarizer: No content found, returning empty results.")
            return {"summaries": [], "experiment_suggestions": []}

        summaries: List[str] = []
        for doc in docs_to_process:
            try:
                doc_id = doc["full_name"]
                content_to_summarize = doc["content"]

                if not content_to_summarize:
                    continue

                # 1. Embed the content for retrieval and storage
                embedding = self.embedding_model.encode(content_to_summarize).tolist()

                # 2. Retrieve relevant context from ChromaDB
                retrieved = self.collection.query(query_embeddings=[embedding], n_results=3)
                context = "\n---\n".join(retrieved['documents'][0]) if retrieved['documents'] else "No relevant context found."

                # 3. Construct a sophisticated prompt for the LLM
                prompt = f"""
                **Task:** Summarize the following document concisely.

                **Instructions:**
                1.  Read the "Retrieved Context" for background information.
                2.  Read the "Document to Summarize".
                3.  Produce a high-quality, neutral summary of the main document.
                4.  The summary should be clear, accurate, and capture the key points.

                **Retrieved Context:**
                ```
                {context}
                ```

                **Document to Summarize:**
                ```
                {content_to_summarize}
                ```

                **Summary:**
                """

                # 4. Invoke the LLM to generate the summary
                messages = [HumanMessage(content=prompt)]
                llm_response = await self.llm_client.ainvoke(messages)
                summary = llm_response.content.strip()
                summaries.append(summary)

                # 5. Add the processed document to the vector store for future lookups
                self.collection.add(embeddings=[embedding], documents=[content_to_summarize], metadatas=[{"source": doc_id}], ids=[doc_id])

            except Exception as e:
                self.logger.error(f"RAG summarization failed for '{doc.get('full_name')}': {e}")
                summaries.append(f"Error summarizing document: {doc.get('full_name')}")
                continue

        # Update state
        state["summaries"] = summaries
        return {"summaries": summaries}
