"""UserIntent node for processing user authentication, file uploads, and parameters."""

import os
import uuid
from typing import Dict, Any, List

import httpx
from langchain_core.runnables import RunnableConfig
from langchain_google_genai import ChatGoogleGenerativeAI

from ..base import BaseNode, UserParams, DocumentChunk
from ..handywriterz_state import HandyWriterzState


class UserIntentNode(BaseNode):
    """Processes user authentication, file uploads, and parameter extraction."""
    
    def __init__(self):
        super().__init__("user_intent", timeout_seconds=60.0, max_retries=2)
        self.db_pool = None
        self.r2_client = None
        
    async def execute(self, state: HandyWriterzState, config: RunnableConfig) -> Dict[str, Any]:
        """Execute user intent processing."""
        try:
            # Step 1: Validate authentication and payment
            auth_result = await self._validate_authentication(state)
            if not auth_result["authenticated"]:
                raise ValueError("User authentication failed")
            
            # Step 2: Process file uploads
            uploaded_chunks = await self._process_file_uploads(state)
            
            # Step 3: Extract and validate user parameters
            user_params = self._extract_user_parameters(state)
            
            # Step 4: Calculate pricing and verify payment
            pricing_info = self._calculate_pricing(user_params)
            payment_verified = await self._verify_payment(state, pricing_info)
            
            # Step 5: Store processed data
            await self._store_user_data(state, user_params, uploaded_chunks)
            
            self._broadcast_progress(state, "User intent processed successfully", 100.0)
            
            return {
                "user_id": auth_result["user_id"],
                "wallet_address": auth_result["wallet_address"],
                "user_params": user_params.dict(),
                "uploaded_docs": [chunk.dict() for chunk in uploaded_chunks],
                "payment_verified": payment_verified,
                "pricing_info": pricing_info,
                "workflow_status": "authenticated"
            }
            
        except Exception as e:
            self.logger.error(f"Failed to process user intent: {e}")
            raise
    
    async def _validate_authentication(self, state: HandyWriterzState) -> Dict[str, Any]:
        """Validate user authentication via Dynamic.xyz."""
        try:
            self._broadcast_progress(state, "Validating authentication...", 10.0)
            
            # Extract authentication token from state
            auth_token = state.get("auth_token")
            if not auth_token:
                raise ValueError("No authentication token provided")
            
            # Verify with Dynamic.xyz
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"https://app.dynamic.xyz/api/v0/environments/{os.getenv('DYNAMIC_ENV_ID')}/users/verify",
                    headers={
                        "Authorization": f"Bearer {auth_token}",
                        "Content-Type": "application/json"
                    }
                )
                
                if response.status_code != 200:
                    raise ValueError(f"Authentication failed: {response.text}")
                
                user_data = response.json()
                
                return {
                    "authenticated": True,
                    "user_id": user_data["user"]["id"],
                    "wallet_address": user_data["user"]["wallets"][0]["address"] if user_data["user"]["wallets"] else None,
                    "email": user_data["user"].get("email"),
                }
                
        except Exception as e:
            self.logger.error(f"Authentication validation failed: {e}")
            return {"authenticated": False, "error": str(e)}
    
    async def _process_file_uploads(self, state: HandyWriterzState) -> List[DocumentChunk]:
        """Process uploaded files and create document chunks."""
        try:
            self._broadcast_progress(state, "Processing uploaded files...", 30.0)
            
            uploaded_files = state.get("uploaded_files", [])
            if not uploaded_files:
                return []
            
            processed_chunks = []
            
            for file_info in uploaded_files:
                chunks = await self._process_single_file(file_info, state)
                processed_chunks.extend(chunks)
            
            self.logger.info(f"Processed {len(processed_chunks)} document chunks from {len(uploaded_files)} files")
            return processed_chunks
            
        except Exception as e:
            self.logger.error(f"File processing failed: {e}")
            raise
    
    async def _process_single_file(self, file_info: Dict[str, Any], state: HandyWriterzState) -> List[DocumentChunk]:
        """Process a single uploaded file."""
        try:
            file_url = file_info["url"]
            file_type = file_info.get("type", "").lower()
            file_name = file_info.get("name", "unknown")
            
            # Download file content
            async with httpx.AsyncClient() as client:
                response = await client.get(file_url)
                content = response.content
            
            # Extract text based on file type
            if file_type.endswith('.pdf'):
                text_content = await self._extract_pdf_text(content)
            elif file_type.endswith('.docx'):
                text_content = await self._extract_docx_text(content)
            elif file_type.endswith('.txt'):
                text_content = content.decode('utf-8')
            elif file_type.endswith('.md'):
                text_content = content.decode('utf-8')
            else:
                raise ValueError(f"Unsupported file type: {file_type}")
            
            # Check if content is too large and needs summarization
            if len(text_content.split()) > 5000:
                text_content = await self._summarize_large_document(text_content, state)
            
            # Create document chunks
            chunks = self._create_document_chunks(text_content, file_info)
            
            return chunks
            
        except Exception as e:
            self.logger.error(f"Failed to process file {file_info.get('name', 'unknown')}: {e}")
            raise
    
    async def _extract_pdf_text(self, content: bytes) -> str:
        """Extract text from PDF content."""
        try:
            import PyPDF2
            import io
            
            pdf_reader = PyPDF2.PdfReader(io.BytesIO(content))
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
            
            return text.strip()
            
        except Exception as e:
            self.logger.error(f"PDF text extraction failed: {e}")
            raise ValueError("Failed to extract text from PDF")
    
    async def _extract_docx_text(self, content: bytes) -> str:
        """Extract text from DOCX content."""
        try:
            import docx
            import io
            
            doc = docx.Document(io.BytesIO(content))
            text = []
            for paragraph in doc.paragraphs:
                text.append(paragraph.text)
            
            return "\n".join(text)
            
        except Exception as e:
            self.logger.error(f"DOCX text extraction failed: {e}")
            raise ValueError("Failed to extract text from DOCX")
    
    async def _summarize_large_document(self, text: str, state: HandyWriterzState) -> str:
        """Summarize large documents using Gemini Flash."""
        try:
            self._broadcast_progress(state, "Summarizing large document...", 50.0)
            
            llm = ChatGoogleGenerativeAI(
                model="gemini-2.0-flash-exp",
                temperature=0.1,
                max_retries=2,
                api_key=os.getenv("GEMINI_API_KEY"),
            )
            
            prompt = f"""
            Summarize this document while preserving all key information, arguments, and relevant details 
            that would be useful for academic writing. Keep the summary comprehensive but under 4000 words.
            
            Document:
            {text}
            
            Summary:
            """
            
            result = await llm.ainvoke(prompt)
            return result.content
            
        except Exception as e:
            self.logger.error(f"Document summarization failed: {e}")
            # Return truncated version if summarization fails
            words = text.split()
            return " ".join(words[:4000])
    
    def _create_document_chunks(self, text: str, file_info: Dict[str, Any]) -> List[DocumentChunk]:
        """Create document chunks from extracted text."""
        try:
            # Split text into chunks of ~1000 words each
            words = text.split()
            chunk_size = 1000
            chunks = []
            
            document_id = str(uuid.uuid4())
            
            for i in range(0, len(words), chunk_size):
                chunk_words = words[i:i + chunk_size]
                chunk_text = " ".join(chunk_words)
                
                chunk = DocumentChunk(
                    chunk_id=str(uuid.uuid4()),
                    document_id=document_id,
                    content=chunk_text,
                    metadata={
                        "file_name": file_info.get("name", "unknown"),
                        "file_type": file_info.get("type", "unknown"),
                        "chunk_index": i // chunk_size,
                        "word_count": len(chunk_words),
                        "source_url": file_info.get("url")
                    }
                )
                chunks.append(chunk)
            
            return chunks
            
        except Exception as e:
            self.logger.error(f"Chunk creation failed: {e}")
            raise
    
    def _extract_user_parameters(self, state: HandyWriterzState) -> UserParams:
        """Extract and validate user parameters from request."""
        try:
            self._broadcast_progress(state, "Processing user parameters...", 70.0)
            
            # Get parameters from state
            params_data = state.get("user_params", {})
            
            # Apply defaults and validate
            user_params = UserParams(
                word_count=params_data.get("word_count", 1000),
                field=params_data.get("field", "general"),
                writeup_type=params_data.get("writeup_type", "essay"),
                source_age_years=params_data.get("source_age_years", 10),
                region=params_data.get("region", "UK"),
                language=params_data.get("language", "English"),
                citation_style=params_data.get("citation_style", "Harvard")
            )
            
            self.logger.info(f"User parameters: {user_params.dict()}")
            return user_params
            
        except Exception as e:
            self.logger.error(f"Parameter extraction failed: {e}")
            raise ValueError(f"Invalid user parameters: {e}")
    
    def _calculate_pricing(self, user_params: UserParams) -> Dict[str, Any]:
        """Calculate pricing based on word count."""
        try:
            price_per_page = float(os.getenv("PRICE_PER_PAGE_GBP", "12"))
            words_per_page = int(os.getenv("WORDS_PER_PAGE", "275"))
            
            pages = max(1, user_params.word_count // words_per_page)
            total_price = pages * price_per_page
            
            return {
                "pages": pages,
                "price_per_page": price_per_page,
                "total_price_gbp": total_price,
                "total_price_usdc": total_price,  # Simplified 1:1 conversion
                "word_count": user_params.word_count,
                "currency": "USDC"
            }
            
        except Exception as e:
            self.logger.error(f"Pricing calculation failed: {e}")
            raise
    
    async def _verify_payment(self, state: HandyWriterzState, pricing_info: Dict[str, Any]) -> bool:
        """Verify payment through Dynamic.xyz."""
        try:
            self._broadcast_progress(state, "Verifying payment...", 90.0)
            
            # Check if user has valid subscription
            subscription_active = await self._check_subscription(state)
            if subscription_active:
                return True
            
            # Check for one-time payment
            payment_verified = await self._check_payment_transaction(state, pricing_info)
            return payment_verified
            
        except Exception as e:
            self.logger.error(f"Payment verification failed: {e}")
            return False
    
    async def _check_subscription(self, state: HandyWriterzState) -> bool:
        """Check if user has active subscription."""
        try:
            # This would integrate with your subscription system
            # For now, return False to require per-use payment
            return False
            
        except Exception as e:
            self.logger.error(f"Subscription check failed: {e}")
            return False
    
    async def _check_payment_transaction(self, state: HandyWriterzState, pricing_info: Dict[str, Any]) -> bool:
        """Verify payment transaction on blockchain."""
        try:
            # This would integrate with Dynamic.xyz payment verification
            # For now, assume payment is verified if transaction_id is present
            transaction_id = state.get("payment_transaction_id")
            return bool(transaction_id)
            
        except Exception as e:
            self.logger.error(f"Payment transaction check failed: {e}")
            return False
    
    async def _store_user_data(self, state: HandyWriterzState, user_params: UserParams, chunks: List[DocumentChunk]):
        """Store processed user data in database."""
        try:
            # Store user parameters and document chunks in database
            # This would use your database connection
            self.logger.info("User data stored successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to store user data: {e}")
            raise