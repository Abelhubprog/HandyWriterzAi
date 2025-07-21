"""
Telegram gateway for automated Turnitin processing.
"""

import asyncio
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional, Dict, Any, List
import uuid

from telethon import TelegramClient, events
from telethon.tl.types import DocumentAttributeFilename

from ..db.database import get_db_session
from ..models.turnitin import DocChunk, Submission, ChunkStatus
from .workers import TurnitinWorker

logger = logging.getLogger(__name__)


class TelegramGateway:
    """Telegram bot for automated Turnitin checking."""
    
    def __init__(
        self, 
        api_id: str, 
        api_hash: str, 
        bot_token: str,
        session_name: str = "turnitin_bot"
    ):
        self.api_id = api_id
        self.api_hash = api_hash
        self.bot_token = bot_token
        self.session_name = session_name
        
        self.client: Optional[TelegramClient] = None
        self.worker = TurnitinWorker()
        self.active_sessions: Dict[int, Dict[str, Any]] = {}  # user_id -> session data
        
    async def start(self):
        """Start the Telegram bot."""
        try:
            self.client = TelegramClient(
                self.session_name, 
                self.api_id, 
                self.api_hash
            )
            
            await self.client.start(bot_token=self.bot_token)
            logger.info("Telegram gateway started successfully")
            
            # Register event handlers
            self._register_handlers()
            
            # Start background tasks
            asyncio.create_task(self._cleanup_expired_sessions())
            
        except Exception as e:
            logger.error(f"Failed to start Telegram gateway: {e}")
            raise

    async def stop(self):
        """Stop the Telegram bot."""
        if self.client:
            await self.client.disconnect()
            logger.info("Telegram gateway stopped")

    def _register_handlers(self):
        """Register Telegram event handlers."""
        
        @self.client.on(events.NewMessage(pattern='/start'))
        async def start_handler(event):
            await self._handle_start(event)
        
        @self.client.on(events.NewMessage(pattern='/check'))
        async def check_handler(event):
            await self._handle_check_command(event)
        
        @self.client.on(events.NewMessage(pattern='/status'))
        async def status_handler(event):
            await self._handle_status(event)
        
        @self.client.on(events.NewMessage(pattern='/cancel'))
        async def cancel_handler(event):
            await self._handle_cancel(event)
        
        @self.client.on(events.NewMessage)
        async def message_handler(event):
            await self._handle_message(event)

    async def _handle_start(self, event):
        """Handle /start command."""
        user_id = event.sender_id
        
        welcome_msg = """
🤖 **HandyWriterz Turnitin Bot**

I can help you check documents for plagiarism and AI detection using Turnitin.

**Commands:**
• `/check` - Start a new Turnitin check
• `/status` - Check status of your submissions
• `/cancel` - Cancel current operation

To get started, use `/check` and follow the prompts.
        """
        
        await event.respond(welcome_msg, parse_mode='markdown')

    async def _handle_check_command(self, event):
        """Handle /check command to start new check."""
        user_id = event.sender_id
        
        # Check if user has active session
        if user_id in self.active_sessions:
            await event.respond(
                "⚠️ You already have an active check in progress. "
                "Use `/cancel` to cancel it or `/status` to check progress."
            )
            return
        
        # Initialize new session
        session_id = str(uuid.uuid4())
        self.active_sessions[user_id] = {
            'session_id': session_id,
            'state': 'awaiting_document',
            'started_at': datetime.now(timezone.utc),
            'chunks': []
        }
        
        await event.respond(
            "📄 **New Turnitin Check**\n\n"
            "Please upload your document (.docx, .pdf, or .txt file)\n"
            "Max file size: 10MB"
        )

    async def _handle_status(self, event):
        """Handle /status command."""
        user_id = event.sender_id
        
        if user_id not in self.active_sessions:
            await event.respond("❌ No active check found. Use `/check` to start a new one.")
            return
        
        session = self.active_sessions[user_id]
        
        status_msg = f"""
📊 **Check Status**

Session ID: `{session['session_id'][:8]}...`
State: {session['state'].replace('_', ' ').title()}
Started: {session['started_at'].strftime('%Y-%m-%d %H:%M:%S')} UTC

Chunks processed: {len([c for c in session['chunks'] if c.get('completed')])} / {len(session['chunks'])}
        """
        
        await event.respond(status_msg, parse_mode='markdown')

    async def _handle_cancel(self, event):
        """Handle /cancel command."""
        user_id = event.sender_id
        
        if user_id not in self.active_sessions:
            await event.respond("❌ No active check to cancel.")
            return
        
        del self.active_sessions[user_id]
        await event.respond("✅ Check cancelled successfully.")

    async def _handle_message(self, event):
        """Handle general messages based on session state."""
        user_id = event.sender_id
        
        # Ignore commands
        if event.message.text and event.message.text.startswith('/'):
            return
        
        # Check if user has active session
        if user_id not in self.active_sessions:
            await event.respond(
                "Use `/check` to start a new Turnitin check."
            )
            return
        
        session = self.active_sessions[user_id]
        state = session['state']
        
        try:
            if state == 'awaiting_document':
                await self._handle_document_upload(event, session)
            elif state == 'processing':
                await event.respond("⏳ Processing in progress. Please wait...")
            else:
                await event.respond("❓ Unknown state. Use `/cancel` to reset.")
                
        except Exception as e:
            logger.error(f"Error handling message for user {user_id}: {e}")
            await event.respond(
                "❌ An error occurred. Please try again or use `/cancel` to reset."
            )

    async def _handle_document_upload(self, event, session):
        """Handle document upload."""
        if not event.message.document:
            await event.respond(
                "❌ Please upload a document file (.docx, .pdf, or .txt)"
            )
            return
        
        document = event.message.document
        
        # Check file size (10MB limit)
        if document.size > 10 * 1024 * 1024:
            await event.respond("❌ File too large. Maximum size is 10MB.")
            return
        
        # Get filename
        filename = "document"
        for attr in document.attributes:
            if isinstance(attr, DocumentAttributeFilename):
                filename = attr.file_name
                break
        
        # Check file type
        allowed_extensions = ['.docx', '.pdf', '.txt']
        file_ext = Path(filename).suffix.lower()
        
        if file_ext not in allowed_extensions:
            await event.respond(
                f"❌ Unsupported file type: {file_ext}\n"
                f"Allowed types: {', '.join(allowed_extensions)}"
            )
            return
        
        # Update session state
        session['state'] = 'processing'
        session['filename'] = filename
        session['file_size'] = document.size
        
        await event.respond("📥 Downloading and processing document...")
        
        try:
            # Download file
            file_path = f"/tmp/turnitin_{session['session_id']}_{filename}"
            await self.client.download_media(document, file_path)
            
            # Process document
            await self._process_document(event, session, file_path)
            
        except Exception as e:
            logger.error(f"Error processing document: {e}")
            await event.respond("❌ Error processing document. Please try again.")
            session['state'] = 'awaiting_document'

    async def _process_document(self, event, session, file_path: str):
        """Process uploaded document through Turnitin workflow."""
        
        try:
            # Extract text and split into chunks
            chunks_data = await self.worker.split_document(file_path)
            
            await event.respond(
                f"📑 Document split into {len(chunks_data)} chunks.\n"
                "Starting Turnitin analysis..."
            )
            
            # Create database records
            db = next(get_db_session())
            try:
                # Create doc lot
                from ..models.turnitin import DocLot
                
                lot = DocLot(
                    user_id=str(event.sender_id),
                    title=session['filename'],
                    word_count=sum(chunk['word_count'] for chunk in chunks_data),
                    status='processing'
                )
                db.add(lot)
                db.flush()
                
                # Create chunks
                chunk_records = []
                for i, chunk_data in enumerate(chunks_data):
                    chunk = DocChunk(
                        lot_id=lot.id,
                        chunk_number=i + 1,
                        content=chunk_data['content'],
                        word_count=chunk_data['word_count'],
                        status=ChunkStatus.OPEN
                    )
                    db.add(chunk)
                    chunk_records.append(chunk)
                
                db.commit()
                
                # Update session
                session['lot_id'] = lot.id
                session['chunks'] = [
                    {'id': chunk.id, 'completed': False} 
                    for chunk in chunk_records
                ]
                
                # Start automated processing
                await self._start_automated_processing(event, session, chunk_records)
                
            finally:
                db.close()
                
        except Exception as e:
            logger.error(f"Error in document processing: {e}")
            await event.respond("❌ Error processing document.")
            raise

    async def _start_automated_processing(self, event, session, chunks: List[DocChunk]):
        """Start automated Turnitin processing for chunks."""
        
        session['state'] = 'running_turnitin'
        
        # Process chunks in parallel (limited concurrency)
        semaphore = asyncio.Semaphore(3)  # Max 3 concurrent
        tasks = []
        
        for chunk in chunks:
            task = asyncio.create_task(
                self._process_chunk_turnitin(semaphore, event, session, chunk)
            )
            tasks.append(task)
        
        # Update user on progress
        await event.respond(
            f"🔍 Running Turnitin analysis on {len(chunks)} chunks...\n"
            "This may take a few minutes."
        )
        
        # Wait for all chunks to complete
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Check results and send final report
        await self._send_final_report(event, session, results)

    async def _process_chunk_turnitin(self, semaphore, event, session, chunk: DocChunk):
        """Process a single chunk through Turnitin."""
        
        async with semaphore:
            try:
                # Simulate Turnitin processing (replace with actual implementation)
                result = await self.worker.run_turnitin_check(
                    chunk.content,
                    chunk.id
                )
                
                # Update database with results
                db = next(get_db_session())
                try:
                    db_chunk = db.query(DocChunk).filter(DocChunk.id == chunk.id).first()
                    if db_chunk:
                        db_chunk.turnitin_sim_score = result['similarity_score']
                        db_chunk.turnitin_ai_score = result['ai_score']
                        db_chunk.flagged_spans = result['flagged_text']
                        db_chunk.status = ChunkStatus.DONE
                        db_chunk.completed_at = datetime.now(timezone.utc)
                        
                        # Create submission record
                        submission = Submission(
                            chunk_id=chunk.id,
                            checker_id="system",  # System-generated
                            similarity_pdf_url=result['similarity_pdf_url'],
                            ai_pdf_url=result['ai_pdf_url'],
                            similarity_score=result['similarity_score'],
                            ai_score=result['ai_score'],
                            flagged_text=result['flagged_text'],
                            approved=True  # Auto-approve system submissions
                        )
                        db.add(submission)
                        db.commit()
                
                    # Update session
                    for session_chunk in session['chunks']:
                        if session_chunk['id'] == chunk.id:
                            session_chunk['completed'] = True
                            break
                            
                finally:
                    db.close()
                
                return result
                
            except Exception as e:
                logger.error(f"Error processing chunk {chunk.id}: {e}")
                return {'error': str(e)}

    async def _send_final_report(self, event, session, results):
        """Send final Turnitin report to user."""
        
        try:
            # Count successful vs failed
            successful = len([r for r in results if isinstance(r, dict) and 'error' not in r])
            failed = len(results) - successful
            
            if failed == 0:
                # All successful
                session['state'] = 'completed'
                
                # Calculate overall scores
                all_results = [r for r in results if isinstance(r, dict) and 'error' not in r]
                avg_sim = sum(r['similarity_score'] for r in all_results) / len(all_results)
                avg_ai = sum(r['ai_score'] for r in all_results) / len(all_results)
                
                report = f"""
✅ **Turnitin Analysis Complete**

📊 **Overall Results:**
• Similarity Score: {avg_sim:.1f}%
• AI Detection Score: {avg_ai:.1f}%
• Chunks Processed: {successful}/{len(results)}

📋 **Summary:**
• Total Word Count: {session.get('total_words', 'N/A')}
• Processing Time: {(datetime.now(timezone.utc) - session['started_at']).total_seconds():.0f}s

📄 **Detailed Report:**
Session ID: `{session['session_id']}`
Use this ID to download full reports from the dashboard.
                """
                
                await event.respond(report, parse_mode='markdown')
                
            else:
                # Some failed
                await event.respond(
                    f"⚠️ **Partial Completion**\n\n"
                    f"✅ Successful: {successful}\n"
                    f"❌ Failed: {failed}\n\n"
                    f"Please check the dashboard for details."
                )
            
            # Clean up session
            del self.active_sessions[event.sender_id]
            
        except Exception as e:
            logger.error(f"Error sending final report: {e}")
            await event.respond("❌ Error generating final report.")

    async def _cleanup_expired_sessions(self):
        """Background task to clean up expired sessions."""
        while True:
            try:
                current_time = datetime.now(timezone.utc)
                expired_users = []
                
                for user_id, session in self.active_sessions.items():
                    # Sessions expire after 1 hour
                    if (current_time - session['started_at']).total_seconds() > 3600:
                        expired_users.append(user_id)
                
                # Clean up expired sessions
                for user_id in expired_users:
                    del self.active_sessions[user_id]
                    logger.info(f"Cleaned up expired session for user {user_id}")
                
                # Sleep for 5 minutes
                await asyncio.sleep(300)
                
            except Exception as e:
                logger.error(f"Error in session cleanup: {e}")
                await asyncio.sleep(60)  # Retry after 1 minute


# Example usage
async def run_telegram_gateway():
    """Run the Telegram gateway."""
    import os
    
    gateway = TelegramGateway(
        api_id=os.getenv('TELEGRAM_API_ID'),
        api_hash=os.getenv('TELEGRAM_API_HASH'),
        bot_token=os.getenv('TELEGRAM_BOT_TOKEN')
    )
    
    try:
        await gateway.start()
        logger.info("Telegram gateway is running...")
        await gateway.client.run_until_disconnected()
    finally:
        await gateway.stop()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(run_telegram_gateway())