"""
Telegram Gateway - Automated Turnitin document uploads
Handles document submission to Turnitin via Telegram bot and retrieves reports.
"""

import asyncio
import json
import logging
import os
import time
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum
import uuid

import aiohttp
import aiofiles
import redis.asyncio as redis



class TurnitinStatus(Enum):
    """Turnitin submission statuses."""
    PENDING = "pending"
    UPLOADING = "uploading"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    TIMEOUT = "timeout"


@dataclass
class TelegramConfig:
    """Telegram bot configuration."""
    bot_token: str = ""
    chat_id: str = ""  # Chat ID for Turnitin uploads
    api_base_url: str = "https://api.telegram.org/bot"
    upload_timeout: int = 300  # 5 minutes
    processing_timeout: int = 1800  # 30 minutes
    max_file_size: int = 50 * 1024 * 1024  # 50MB
    poll_interval: int = 30  # Poll every 30 seconds


@dataclass
class TurnitinSubmission:
    """Turnitin submission data."""
    chunk_id: str
    submission_id: str
    document_path: str
    submitted_at: float
    status: TurnitinStatus
    similarity_pdf_url: Optional[str] = None
    ai_pdf_url: Optional[str] = None
    similarity_score: Optional[float] = None
    ai_score: Optional[float] = None
    error_message: Optional[str] = None


class TelegramGateway:
    """
    Production-ready Telegram gateway for Turnitin integration.
    
    Features:
    - Automated document upload to Telegram
    - Turnitin report retrieval via bot
    - Real-time status tracking
    - Retry logic and error handling
    - File format conversion
    - Report parsing and extraction
    - Queue management
    """
    
    def __init__(self, config: Optional[TelegramConfig] = None):
        self.config = config or TelegramConfig()
        self.logger = logging.getLogger(__name__)
        
        # Initialize Redis for queue and status tracking
        self.redis_client = redis.from_url("redis://localhost:6379", decode_responses=True)
        
        # Active submissions tracking
        self.active_submissions: Dict[str, TurnitinSubmission] = {}
        
        # Gateway statistics
        self.stats = {
            "submissions_total": 0,
            "submissions_successful": 0,
            "submissions_failed": 0,
            "similarity_reports_received": 0,
            "ai_reports_received": 0,
            "average_processing_time": 0.0
        }
        
        self.running = False
        
    async def start_gateway(self):
        """Start the Telegram gateway service."""
        self.running = True
        self.logger.info("📱 Telegram Gateway starting...")
        
        # Validate configuration
        if not self.config.bot_token or not self.config.chat_id:
            self.logger.error("❌ Telegram bot token and chat ID are required")
            return False
        
        # Test bot connection
        if not await self._test_bot_connection():
            self.logger.error("❌ Failed to connect to Telegram bot")
            return False
        
        # Start background workers
        asyncio.create_task(self._process_submission_queue())
        asyncio.create_task(self._monitor_submissions())
        asyncio.create_task(self._update_bot_messages())
        
        self.logger.info("✅ Telegram Gateway operational")
        return True
        
    async def stop_gateway(self):
        """Stop the Telegram gateway service."""
        self.running = False
        
        # Cancel active submissions
        for submission in self.active_submissions.values():
            submission.status = TurnitinStatus.FAILED
            submission.error_message = "Gateway shutdown"
        
        await self.redis_client.close()
        self.logger.info("🔄 Telegram Gateway stopped")
        
    async def submit_document(self, chunk_id: str, document_content: str, 
                            filename: str = None) -> str:
        """
        Submit document chunk to Turnitin via Telegram.
        
        Args:
            chunk_id: ID of the document chunk
            document_content: Content of the document
            filename: Optional filename for the document
            
        Returns:
            str: Submission ID for tracking
        """
        try:
            submission_id = str(uuid.uuid4())
            
            # Create temporary file
            temp_filename = filename or f"chunk_{chunk_id}.docx"
            temp_path = await self._create_temp_document(document_content, temp_filename)
            
            # Create submission record
            submission = TurnitinSubmission(
                chunk_id=chunk_id,
                submission_id=submission_id,
                document_path=temp_path,
                submitted_at=time.time(),
                status=TurnitinStatus.PENDING
            )
            
            # Store in Redis queue
            await self.redis_client.lpush(
                "turnitin_queue",
                json.dumps({
                    "chunk_id": chunk_id,
                    "submission_id": submission_id,
                    "document_path": temp_path,
                    "submitted_at": time.time()
                })
            )
            
            # Track submission
            self.active_submissions[submission_id] = submission
            
            # Store submission in Redis for persistence
            await self.redis_client.hset(
                f"submission:{submission_id}",
                mapping={
                    "chunk_id": chunk_id,
                    "status": submission.status.value,
                    "submitted_at": submission.submitted_at,
                    "document_path": temp_path
                }
            )
            
            # Set expiration for cleanup
            await self.redis_client.expire(f"submission:{submission_id}", 3600)  # 1 hour
            
            self.stats["submissions_total"] += 1
            
            self.logger.info(f"📄 Document submission queued: {submission_id} for chunk {chunk_id}")
            
            return submission_id
            
        except Exception as e:
            self.logger.error(f"Failed to submit document for chunk {chunk_id}: {e}")
            raise
    
    async def get_submission_status(self, submission_id: str) -> Optional[Dict[str, Any]]:
        """Get current status of a Turnitin submission."""
        try:
            # Check active submissions first
            if submission_id in self.active_submissions:
                submission = self.active_submissions[submission_id]
                return {
                    "submission_id": submission_id,
                    "chunk_id": submission.chunk_id,
                    "status": submission.status.value,
                    "submitted_at": submission.submitted_at,
                    "similarity_score": submission.similarity_score,
                    "ai_score": submission.ai_score,
                    "similarity_pdf_url": submission.similarity_pdf_url,
                    "ai_pdf_url": submission.ai_pdf_url,
                    "error_message": submission.error_message,
                    "processing_time": time.time() - submission.submitted_at
                }
            
            # Check Redis storage
            submission_data = await self.redis_client.hgetall(f"submission:{submission_id}")
            if submission_data:
                return {
                    "submission_id": submission_id,
                    "chunk_id": submission_data.get("chunk_id"),
                    "status": submission_data.get("status"),
                    "submitted_at": float(submission_data.get("submitted_at", 0)),
                    "similarity_score": float(submission_data.get("similarity_score", 0)) if submission_data.get("similarity_score") else None,
                    "ai_score": float(submission_data.get("ai_score", 0)) if submission_data.get("ai_score") else None,
                    "similarity_pdf_url": submission_data.get("similarity_pdf_url"),
                    "ai_pdf_url": submission_data.get("ai_pdf_url"),
                    "error_message": submission_data.get("error_message")
                }
            
            return None
            
        except Exception as e:
            self.logger.error(f"Failed to get submission status for {submission_id}: {e}")
            return None
    
    async def _process_submission_queue(self):
        """Process the Turnitin submission queue."""
        while self.running:
            try:
                # Get next submission from queue
                queue_item = await self.redis_client.brpop("turnitin_queue", timeout=5)
                
                if not queue_item:
                    continue
                
                _, item_data = queue_item
                submission_data = json.loads(item_data)
                
                submission_id = submission_data["submission_id"]
                chunk_id = submission_data["chunk_id"]
                document_path = submission_data["document_path"]
                
                self.logger.info(f"🔄 Processing Turnitin submission: {submission_id}")
                
                # Upload document to Telegram
                success = await self._upload_to_telegram(submission_id, document_path)
                
                if success:
                    # Update submission status
                    if submission_id in self.active_submissions:
                        self.active_submissions[submission_id].status = TurnitinStatus.UPLOADING
                    
                    await self.redis_client.hset(
                        f"submission:{submission_id}",
                        "status", TurnitinStatus.UPLOADING.value
                    )
                    
                    self.logger.info(f"📤 Document uploaded to Telegram: {submission_id}")
                else:
                    # Mark as failed
                    await self._mark_submission_failed(submission_id, "Failed to upload to Telegram")
                
                # Clean up temporary file
                try:
                    os.unlink(document_path)
                except:
                    pass
                
            except Exception as e:
                self.logger.error(f"Error processing submission queue: {e}")
                await asyncio.sleep(10)
    
    async def _upload_to_telegram(self, submission_id: str, document_path: str) -> bool:
        """Upload document to Telegram chat."""
        try:
            url = f"{self.config.api_base_url}{self.config.bot_token}/sendDocument"
            
            # Prepare file upload
            async with aiofiles.open(document_path, 'rb') as file:
                file_content = await file.read()
            
            filename = os.path.basename(document_path)
            
            # Create form data
            data = aiohttp.FormData()
            data.add_field('chat_id', self.config.chat_id)
            data.add_field('document', file_content, 
                          filename=filename, 
                          content_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document')
            data.add_field('caption', f"📄 Turnitin Check - Submission ID: {submission_id}")
            
            # Upload with timeout
            timeout = aiohttp.ClientTimeout(total=self.config.upload_timeout)
            
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.post(url, data=data) as response:
                    if response.status == 200:
                        response_data = await response.json()
                        
                        # Store message ID for tracking
                        message_id = response_data.get("result", {}).get("message_id")
                        if message_id:
                            await self.redis_client.hset(
                                f"submission:{submission_id}",
                                "telegram_message_id", str(message_id)
                            )
                        
                        return True
                    else:
                        error_text = await response.text()
                        self.logger.error(f"Telegram upload failed: {response.status} - {error_text}")
                        return False
            
        except asyncio.TimeoutError:
            self.logger.error(f"Telegram upload timeout for submission {submission_id}")
            return False
        except Exception as e:
            self.logger.error(f"Telegram upload error for submission {submission_id}: {e}")
            return False
    
    async def _monitor_submissions(self):
        """Monitor active submissions for timeouts and status updates."""
        while self.running:
            try:
                current_time = time.time()
                expired_submissions = []
                
                for submission_id, submission in self.active_submissions.items():
                    age = current_time - submission.submitted_at
                    
                    # Check for timeout
                    if submission.status in [TurnitinStatus.PENDING, TurnitinStatus.UPLOADING]:
                        if age > self.config.upload_timeout:
                            expired_submissions.append((submission_id, "Upload timeout"))
                    elif submission.status == TurnitinStatus.PROCESSING:
                        if age > self.config.processing_timeout:
                            expired_submissions.append((submission_id, "Processing timeout"))
                
                # Handle expired submissions
                for submission_id, reason in expired_submissions:
                    await self._mark_submission_failed(submission_id, reason)
                
                await asyncio.sleep(self.config.poll_interval)
                
            except Exception as e:
                self.logger.error(f"Error monitoring submissions: {e}")
                await asyncio.sleep(60)
    
    async def _update_bot_messages(self):
        """Check for new messages from Telegram bot (Turnitin reports)."""
        while self.running:
            try:
                # Get updates from Telegram bot
                updates = await self._get_telegram_updates()
                
                for update in updates:
                    await self._process_telegram_update(update)
                
                await asyncio.sleep(10)  # Poll every 10 seconds
                
            except Exception as e:
                self.logger.error(f"Error updating bot messages: {e}")
                await asyncio.sleep(30)
    
    async def _get_telegram_updates(self) -> List[Dict]:
        """Get updates from Telegram bot."""
        try:
            url = f"{self.config.api_base_url}{self.config.bot_token}/getUpdates"
            
            # Get last update offset
            last_offset = await self.redis_client.get("telegram_last_offset")
            
            params = {
                "timeout": 5,
                "allowed_updates": ["message", "document"]
            }
            
            if last_offset:
                params["offset"] = int(last_offset) + 1
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        updates = data.get("result", [])
                        
                        # Update offset
                        if updates:
                            latest_update_id = max(update["update_id"] for update in updates)
                            await self.redis_client.set("telegram_last_offset", latest_update_id)
                        
                        return updates
                    else:
                        self.logger.warning(f"Failed to get Telegram updates: {response.status}")
                        return []
            
        except Exception as e:
            self.logger.error(f"Error getting Telegram updates: {e}")
            return []
    
    async def _process_telegram_update(self, update: Dict):
        """Process individual Telegram update (potential Turnitin report)."""
        try:
            message = update.get("message", {})
            
            # Check if message contains documents (potential reports)
            if "document" in message:
                await self._process_document_message(message)
            elif "text" in message:
                await self._process_text_message(message)
                
        except Exception as e:
            self.logger.error(f"Error processing Telegram update: {e}")
    
    async def _process_document_message(self, message: Dict):
        """Process document message (potential Turnitin report)."""
        try:
            document = message["document"]
            caption = message.get("caption", "")
            
            # Check if this is a Turnitin report
            if "turnitin" in caption.lower() or "similarity" in caption.lower() or "ai" in caption.lower():
                
                # Extract submission ID from caption
                submission_id = self._extract_submission_id(caption)
                
                if submission_id and submission_id in self.active_submissions:
                    # Download and process the report
                    file_id = document["file_id"]
                    filename = document.get("file_name", "report.pdf")
                    
                    report_url = await self._download_telegram_file(file_id)
                    
                    if report_url:
                        await self._process_turnitin_report(submission_id, report_url, filename)
                        
                        self.logger.info(f"📊 Turnitin report received for submission {submission_id}")
                
        except Exception as e:
            self.logger.error(f"Error processing document message: {e}")
    
    async def _process_text_message(self, message: Dict):
        """Process text message (potential status update)."""
        try:
            text = message.get("text", "")
            
            # Look for submission status updates
            if "submission" in text.lower() and "id:" in text.lower():
                submission_id = self._extract_submission_id(text)
                
                if submission_id and submission_id in self.active_submissions:
                    # Parse status from message
                    if "processing" in text.lower():
                        self.active_submissions[submission_id].status = TurnitinStatus.PROCESSING
                        await self.redis_client.hset(
                            f"submission:{submission_id}",
                            "status", TurnitinStatus.PROCESSING.value
                        )
                    elif "completed" in text.lower():
                        self.active_submissions[submission_id].status = TurnitinStatus.COMPLETED
                        await self.redis_client.hset(
                            f"submission:{submission_id}",
                            "status", TurnitinStatus.COMPLETED.value
                        )
                        
        except Exception as e:
            self.logger.error(f"Error processing text message: {e}")
    
    async def _download_telegram_file(self, file_id: str) -> Optional[str]:
        """Download file from Telegram and return URL."""
        try:
            # Get file info
            url = f"{self.config.api_base_url}{self.config.bot_token}/getFile"
            params = {"file_id": file_id}
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        file_path = data["result"]["file_path"]
                        
                        # Download file
                        download_url = f"https://api.telegram.org/file/bot{self.config.bot_token}/{file_path}"
                        
                        async with session.get(download_url) as download_response:
                            if download_response.status == 200:
                                # Save to temporary location
                                temp_filename = f"/tmp/{file_id}_{int(time.time())}.pdf"
                                
                                async with aiofiles.open(temp_filename, 'wb') as f:
                                    async for chunk in download_response.content.iter_chunked(8192):
                                        await f.write(chunk)
                                
                                return temp_filename
            
            return None
            
        except Exception as e:
            self.logger.error(f"Error downloading Telegram file {file_id}: {e}")
            return None
    
    async def _process_turnitin_report(self, submission_id: str, report_path: str, filename: str):
        """Process downloaded Turnitin report."""
        try:
            submission = self.active_submissions.get(submission_id)
            if not submission:
                return
            
            # Determine report type from filename
            is_similarity_report = "similarity" in filename.lower()
            is_ai_report = "ai" in filename.lower() or "artificial" in filename.lower()
            
            # Store report URL
            if is_similarity_report:
                submission.similarity_pdf_url = report_path
                self.stats["similarity_reports_received"] += 1
            elif is_ai_report:
                submission.ai_pdf_url = report_path
                self.stats["ai_reports_received"] += 1
            
            # Update Redis
            update_data = {}
            if is_similarity_report:
                update_data["similarity_pdf_url"] = report_path
            elif is_ai_report:
                update_data["ai_pdf_url"] = report_path
            
            await self.redis_client.hset(f"submission:{submission_id}", mapping=update_data)
            
            # Check if we have both reports
            if submission.similarity_pdf_url and submission.ai_pdf_url:
                submission.status = TurnitinStatus.COMPLETED
                await self.redis_client.hset(
                    f"submission:{submission_id}",
                    "status", TurnitinStatus.COMPLETED.value
                )
                
                # Calculate processing time
                processing_time = time.time() - submission.submitted_at
                self._update_average_processing_time(processing_time)
                
                self.stats["submissions_successful"] += 1
                
                self.logger.info(f"✅ Turnitin submission completed: {submission_id}")
                
        except Exception as e:
            self.logger.error(f"Error processing Turnitin report: {e}")
    
    async def _mark_submission_failed(self, submission_id: str, error_message: str):
        """Mark submission as failed."""
        try:
            if submission_id in self.active_submissions:
                self.active_submissions[submission_id].status = TurnitinStatus.FAILED
                self.active_submissions[submission_id].error_message = error_message
            
            await self.redis_client.hset(
                f"submission:{submission_id}",
                mapping={
                    "status": TurnitinStatus.FAILED.value,
                    "error_message": error_message
                }
            )
            
            self.stats["submissions_failed"] += 1
            
            self.logger.warning(f"❌ Turnitin submission failed: {submission_id} - {error_message}")
            
        except Exception as e:
            self.logger.error(f"Error marking submission as failed: {e}")
    
    async def _create_temp_document(self, content: str, filename: str) -> str:
        """Create temporary document file."""
        try:
            # Create temp directory if it doesn't exist
            temp_dir = "/tmp/turnitin_docs"
            os.makedirs(temp_dir, exist_ok=True)
            
            # Generate unique filename
            temp_filename = f"{temp_dir}/{int(time.time())}_{filename}"
            
            # Write content to file
            if filename.endswith('.docx'):
                # Create DOCX file
                from docx import Document
                doc = Document()
                
                # Split content into paragraphs
                paragraphs = content.split('\n\n')
                for paragraph in paragraphs:
                    if paragraph.strip():
                        doc.add_paragraph(paragraph.strip())
                
                doc.save(temp_filename)
            else:
                # Plain text file
                async with aiofiles.open(temp_filename, 'w', encoding='utf-8') as f:
                    await f.write(content)
            
            return temp_filename
            
        except Exception as e:
            self.logger.error(f"Error creating temp document: {e}")
            raise
    
    async def _test_bot_connection(self) -> bool:
        """Test connection to Telegram bot."""
        try:
            url = f"{self.config.api_base_url}{self.config.bot_token}/getMe"
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    if response.status == 200:
                        data = await response.json()
                        bot_info = data.get("result", {})
                        self.logger.info(f"✅ Connected to Telegram bot: {bot_info.get('username', 'Unknown')}")
                        return True
                    else:
                        self.logger.error(f"Failed to connect to Telegram bot: {response.status}")
                        return False
            
        except Exception as e:
            self.logger.error(f"Error testing bot connection: {e}")
            return False
    
    def _extract_submission_id(self, text: str) -> Optional[str]:
        """Extract submission ID from text."""
        import re
        
        # Look for UUID pattern
        uuid_pattern = r'[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}'
        match = re.search(uuid_pattern, text, re.IGNORECASE)
        
        if match:
            return match.group(0)
        
        return None
    
    def _update_average_processing_time(self, processing_time: float):
        """Update average processing time statistic."""
        current_avg = self.stats["average_processing_time"]
        successful_count = self.stats["submissions_successful"]
        
        if successful_count == 1:
            self.stats["average_processing_time"] = processing_time
        else:
            self.stats["average_processing_time"] = (
                (current_avg * (successful_count - 1) + processing_time) / successful_count
            )
    
    async def get_gateway_stats(self) -> Dict[str, Any]:
        """Get comprehensive gateway statistics."""
        return {
            "stats": self.stats,
            "active_submissions": len(self.active_submissions),
            "queue_length": await self.redis_client.llen("turnitin_queue"),
            "config": {
                "upload_timeout": self.config.upload_timeout,
                "processing_timeout": self.config.processing_timeout,
                "poll_interval": self.config.poll_interval
            },
            "status": "running" if self.running else "stopped",
            "timestamp": time.time()
        }
    
    async def cleanup_old_submissions(self, max_age_hours: int = 24):
        """Clean up old submissions and temporary files."""
        try:
            current_time = time.time()
            cleanup_count = 0
            
            for submission_id in list(self.active_submissions.keys()):
                submission = self.active_submissions[submission_id]
                age_hours = (current_time - submission.submitted_at) / 3600
                
                if age_hours > max_age_hours:
                    # Clean up temporary files
                    if submission.similarity_pdf_url and os.path.exists(submission.similarity_pdf_url):
                        os.unlink(submission.similarity_pdf_url)
                    if submission.ai_pdf_url and os.path.exists(submission.ai_pdf_url):
                        os.unlink(submission.ai_pdf_url)
                    
                    # Remove from active submissions
                    del self.active_submissions[submission_id]
                    cleanup_count += 1
            
            self.logger.info(f"🧹 Cleaned up {cleanup_count} old submissions")
            
        except Exception as e:
            self.logger.error(f"Error cleaning up old submissions: {e}")


# Global Telegram gateway instance
telegram_gateway = TelegramGateway()


# Utility functions for integration
async def submit_to_turnitin(chunk_id: str, document_content: str, 
                           filename: str = None) -> str:
    """Submit document to Turnitin via Telegram."""
    return await telegram_gateway.submit_document(chunk_id, document_content, filename)


async def get_turnitin_status(submission_id: str) -> Optional[Dict[str, Any]]:
    """Get Turnitin submission status."""
    return await telegram_gateway.get_submission_status(submission_id)


if __name__ == "__main__":
    # Test the Telegram gateway
    async def test_gateway():
        """Test Telegram gateway."""
        gateway = TelegramGateway()
        
        # Start gateway
        await gateway.start_gateway()
        
        # Test document submission
        test_content = "This is a test document for Turnitin checking."
        submission_id = await gateway.submit_document("test_chunk_1", test_content)
        
        print(f"Submission ID: {submission_id}")
        
        # Check status
        await asyncio.sleep(5)
        status = await gateway.get_submission_status(submission_id)
        print(f"Status: {status}")
        
        # Get stats
        stats = await gateway.get_gateway_stats()
        print(f"Gateway stats: {stats}")
        
        await gateway.stop_gateway()
    
    asyncio.run(test_gateway())