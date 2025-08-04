"""
Automated Rewrite Cycle - 3-pass retry logic for Turnitin failures
Orchestrates the complete automated cycle from Turnitin failure to successful completion.
"""

import asyncio
import json
import logging
import time
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum

import redis.asyncio as redis

from src.db.database import get_database
from src.db.models import DocChunk, ChunkStatus
from src.agent.nodes.rewrite_o3 import O3RewriteAgent
# TODO: Consolidate Turnitin integration. Placeholder function names kept for compatibility.
from src.services.highlight_parser import parse_turnitin_reports


class RewriteStage(Enum):
    """Stages in the rewrite cycle."""
    TURNITIN_FAILED = "turnitin_failed"
    PARSING_REPORTS = "parsing_reports"
    GENERATING_REWRITE = "generating_rewrite"
    SUBMITTING_REWRITE = "submitting_rewrite"
    AWAITING_RESULTS = "awaiting_results"
    COMPLETED = "completed"
    FAILED_MAX_ATTEMPTS = "failed_max_attempts"
    ADMIN_REVIEW_NEEDED = "admin_review_needed"


@dataclass
class RewriteCycleConfig:
    """Configuration for rewrite cycle."""
    max_rewrite_attempts: int = 3
    turnitin_timeout_minutes: int = 30
    rewrite_timeout_minutes: int = 10
    similarity_threshold: float = 10.0  # Max allowed similarity %
    ai_threshold: float = 20.0  # Max allowed AI detection %
    admin_alert_threshold: int = 2  # Alert admin after 2 failures


@dataclass
class RewriteAttempt:
    """Single rewrite attempt data."""
    attempt_number: int
    original_content: str
    rewritten_content: str
    flags_addressed: List[Dict[str, Any]]
    similarity_score: float
    ai_score: float
    turnitin_submission_id: str
    started_at: float
    completed_at: Optional[float] = None
    success: bool = False
    error_message: Optional[str] = None


@dataclass
class RewriteCycleState:
    """Complete state of a rewrite cycle."""
    chunk_id: str
    lot_id: str
    current_stage: RewriteStage
    current_attempt: int
    max_attempts: int
    attempts: List[RewriteAttempt]
    original_content: str
    latest_content: str
    final_similarity_score: Optional[float] = None
    final_ai_score: Optional[float] = None
    started_at: float = 0.0
    completed_at: Optional[float] = None
    success: bool = False
    admin_notified: bool = False
    error_message: Optional[str] = None


class AutomatedRewriteCycle:
    """
    Production-ready automated rewrite cycle orchestrator.

    Features:
    - 3-pass automatic retry logic
    - Turnitin integration with timeout handling
    - OpenAI O3 rewrite agent integration
    - Comprehensive failure handling
    - Admin escalation for persistent failures
    - Real-time progress tracking
    - Quality threshold validation
    """

    def __init__(self, config: Optional[RewriteCycleConfig] = None):
        self.config = config or RewriteCycleConfig()
        self.logger = logging.getLogger(__name__)

        # Initialize Redis for state tracking
        self.redis_client = redis.from_url("redis://localhost:6379", decode_responses=True)

        # Initialize agents and services
        self.rewrite_agent = O3RewriteAgent()

        # Active cycles tracking
        self.active_cycles: Dict[str, RewriteCycleState] = {}

        # Background task management
        self.background_tasks: List[asyncio.Task] = []

        # Cycle statistics
        self.stats = {
            "cycles_started": 0,
            "cycles_completed": 0,
            "cycles_failed": 0,
            "total_attempts": 0,
            "successful_attempts": 0,
            "admin_escalations": 0,
            "average_attempts_to_success": 0.0,
            "average_cycle_duration": 0.0
        }

        self.running = False

    async def start_cycle_manager(self):
        """Start the rewrite cycle management system."""
        self.running = True
        self.logger.info("🔄 Automated Rewrite Cycle Manager starting...")

        # Start background workers and store task references
        self.background_tasks = [
            asyncio.create_task(self._monitor_turnitin_results()),
            asyncio.create_task(self._process_rewrite_queue()),
            asyncio.create_task(self._cleanup_completed_cycles())
        ]

        self.logger.info("✅ Rewrite Cycle Manager operational")

    async def stop_cycle_manager(self):
        """Stop the rewrite cycle manager."""
        self.running = False

        # Cancel background tasks gracefully
        for task in self.background_tasks:
            if not task.done():
                task.cancel()

        # Wait for tasks to complete cancellation
        if self.background_tasks:
            try:
                await asyncio.gather(*self.background_tasks, return_exceptions=True)
            except Exception as e:
                self.logger.warning(f"Exception during task cleanup: {e}")

        self.background_tasks.clear()

        # Cancel active cycles gracefully
        for cycle_state in self.active_cycles.values():
            cycle_state.error_message = "System shutdown"
            await self._complete_cycle(cycle_state.chunk_id, False)

        await self.redis_client.close()
        self.logger.info("🔄 Rewrite Cycle Manager stopped")

    async def initiate_rewrite_cycle(self, chunk_id: str, similarity_pdf: str,
                                   ai_pdf: str, original_content: str) -> bool:
        """
        Initiate automated rewrite cycle for a failed Turnitin check.

        Args:
            chunk_id: ID of the chunk that failed Turnitin
            similarity_pdf: Path to similarity report PDF
            ai_pdf: Path to AI detection report PDF
            original_content: Original content of the chunk

        Returns:
            bool: True if cycle initiated successfully
        """
        try:
            self.logger.info(f"🔄 Initiating rewrite cycle for chunk {chunk_id}")

            # Get lot information
            with get_database() as db:
                chunk = db.query(DocChunk).filter(DocChunk.id == chunk_id).first()
                if not chunk:
                    self.logger.error(f"Chunk {chunk_id} not found")
                    return False

                lot_id = chunk.lot_id

            # Create cycle state
            cycle_state = RewriteCycleState(
                chunk_id=chunk_id,
                lot_id=lot_id,
                current_stage=RewriteStage.PARSING_REPORTS,
                current_attempt=0,
                max_attempts=self.config.max_rewrite_attempts,
                attempts=[],
                original_content=original_content,
                latest_content=original_content,
                started_at=time.time()
            )

            # Store cycle state
            self.active_cycles[chunk_id] = cycle_state
            await self._save_cycle_state(cycle_state)

            # Start the cycle
            await self._execute_rewrite_cycle(chunk_id, similarity_pdf, ai_pdf)

            self.stats["cycles_started"] += 1

            return True

        except Exception as e:
            self.logger.error(f"Failed to initiate rewrite cycle for chunk {chunk_id}: {e}")
            return False

    async def _execute_rewrite_cycle(self, chunk_id: str, similarity_pdf: str, ai_pdf: str):
        """Execute the complete rewrite cycle."""
        try:
            cycle_state = self.active_cycles.get(chunk_id)
            if not cycle_state:
                self.logger.error(f"No cycle state found for chunk {chunk_id}")
                return

            # Stage 1: Parse Turnitin reports
            self.logger.info(f"📊 Parsing Turnitin reports for chunk {chunk_id}")
            cycle_state.current_stage = RewriteStage.PARSING_REPORTS
            await self._save_cycle_state(cycle_state)

            similarity_report, ai_report = await parse_turnitin_reports(
                similarity_pdf, ai_pdf, cycle_state.latest_content
            )

            # Check if content actually needs rewriting
            if (similarity_report.overall_score <= self.config.similarity_threshold and
                ai_report.overall_score <= self.config.ai_threshold):

                self.logger.info(f"✅ Content already meets thresholds for chunk {chunk_id}")
                await self._complete_cycle(chunk_id, True)
                return

            # Start rewrite attempts
            for attempt_num in range(1, self.config.max_rewrite_attempts + 1):
                success = await self._execute_rewrite_attempt(
                    chunk_id, attempt_num, similarity_report, ai_report
                )

                if success:
                    await self._complete_cycle(chunk_id, True)
                    return

                # Check if we should continue
                if attempt_num >= self.config.max_rewrite_attempts:
                    await self._handle_max_attempts_reached(chunk_id)
                    return

                # Wait before next attempt
                await asyncio.sleep(30)

        except Exception as e:
            self.logger.error(f"Error executing rewrite cycle for chunk {chunk_id}: {e}")
            cycle_state = self.active_cycles.get(chunk_id)
            if cycle_state:
                cycle_state.error_message = str(e)
                await self._complete_cycle(chunk_id, False)

    async def _execute_rewrite_attempt(self, chunk_id: str, attempt_num: int,
                                     similarity_report, ai_report) -> bool:
        """Execute a single rewrite attempt."""
        try:
            cycle_state = self.active_cycles.get(chunk_id)
            if not cycle_state:
                return False

            self.logger.info(f"✏️ Starting rewrite attempt {attempt_num} for chunk {chunk_id}")

            # Update cycle state
            cycle_state.current_attempt = attempt_num
            cycle_state.current_stage = RewriteStage.GENERATING_REWRITE
            await self._save_cycle_state(cycle_state)

            # Prepare flags for rewrite agent
            all_flags = []
            all_flags.extend([
                {
                    "text": span.text,
                    "start": span.start_position,
                    "end": span.end_position,
                    "type": "similarity",
                    "confidence": span.confidence_score,
                    "source": span.source_info
                }
                for span in similarity_report.flagged_spans
            ])

            all_flags.extend([
                {
                    "text": span.text,
                    "start": span.start_position,
                    "end": span.end_position,
                    "type": "ai_detection",
                    "confidence": span.confidence_score
                }
                for span in ai_report.flagged_spans
            ])

            # Create attempt record
            attempt = RewriteAttempt(
                attempt_number=attempt_num,
                original_content=cycle_state.latest_content,
                rewritten_content="",
                flags_addressed=all_flags,
                similarity_score=0.0,
                ai_score=0.0,
                turnitin_submission_id="",
                started_at=time.time()
            )

            # Execute rewrite using O3 agent
            rewrite_state = {
                "flagged_content": cycle_state.latest_content,
                "content_flags": all_flags,
                "chunk_id": chunk_id,
                "rewrite_pass": attempt_num
            }

            rewrite_result = await self.rewrite_agent.execute(rewrite_state, {})

            if not rewrite_result.get("rewrite_result"):
                attempt.error_message = "Rewrite agent failed"
                cycle_state.attempts.append(attempt)
                return False

            rewritten_content = rewrite_result["rewrite_result"]["rewritten_text"]
            attempt.rewritten_content = rewritten_content

            # Update latest content
            cycle_state.latest_content = rewritten_content

            # Stage 2: Submit to Turnitin
            cycle_state.current_stage = RewriteStage.SUBMITTING_REWRITE
            await self._save_cycle_state(cycle_state)

            # Temporarily bypass direct submission; integration will be wired via queue/worker
            submission_id = f"pending:{chunk_id}:{attempt_num}"
            attempt.turnitin_submission_id = submission_id

            # Stage 3: Wait for results
            cycle_state.current_stage = RewriteStage.AWAITING_RESULTS
            await self._save_cycle_state(cycle_state)

            # Wait for Turnitin results (stubbed status fetch until integration is finalized)
            success = False

            # Record attempt
            cycle_state.attempts.append(attempt)
            self.stats["total_attempts"] += 1

            if success:
                self.stats["successful_attempts"] += 1

                # Update final scores
                cycle_state.final_similarity_score = attempt.similarity_score
                cycle_state.final_ai_score = attempt.ai_score

                self.logger.info(f"✅ Rewrite attempt {attempt_num} successful for chunk {chunk_id}")
                return True
            else:
                self.logger.warning(f"❌ Rewrite attempt {attempt_num} failed for chunk {chunk_id}")
                return False

        except Exception as e:
            self.logger.error(f"Error in rewrite attempt {attempt_num} for chunk {chunk_id}: {e}")
            return False

    async def _wait_for_turnitin_results(self, chunk_id: str, submission_id: str,
                                       attempt: RewriteAttempt) -> bool:
        """Wait for Turnitin results and evaluate success."""
        try:
            timeout = time.time() + (self.config.turnitin_timeout_minutes * 60)

            while time.time() < timeout:
                # Check submission status
                status = await get_turnitin_status(submission_id)

                if not status:
                    await asyncio.sleep(30)
                    continue

                if status["status"] == "completed":
                    # Reports are ready
                    similarity_score = status.get("similarity_score", 100.0)
                    ai_score = status.get("ai_score", 100.0)

                    attempt.similarity_score = similarity_score
                    attempt.ai_score = ai_score
                    attempt.completed_at = time.time()

                    # Check if thresholds are met
                    if (similarity_score <= self.config.similarity_threshold and
                        ai_score <= self.config.ai_threshold):

                        attempt.success = True

                        # Update database
                        await self._update_chunk_content(chunk_id, attempt.rewritten_content)

                        return True
                    else:
                        attempt.success = False
                        self.logger.info(f"📊 Thresholds not met: Similarity {similarity_score}%, AI {ai_score}%")
                        return False

                elif status["status"] == "failed":
                    attempt.error_message = status.get("error_message", "Turnitin processing failed")
                    return False

                # Still processing, wait
                await asyncio.sleep(30)

            # Timeout reached
            attempt.error_message = "Turnitin processing timeout"
            return False

        except Exception as e:
            self.logger.error(f"Error waiting for Turnitin results: {e}")
            attempt.error_message = str(e)
            return False

    async def _handle_max_attempts_reached(self, chunk_id: str):
        """Handle when maximum rewrite attempts are reached."""
        try:
            cycle_state = self.active_cycles.get(chunk_id)
            if not cycle_state:
                return

            cycle_state.current_stage = RewriteStage.FAILED_MAX_ATTEMPTS

            # Check if admin notification is needed
            if not cycle_state.admin_notified:
                await self._notify_admin_failure(chunk_id, cycle_state)
                cycle_state.admin_notified = True
                self.stats["admin_escalations"] += 1

            # Update chunk status to need admin review
            with get_database() as db:
                chunk = db.query(DocChunk).filter(DocChunk.id == chunk_id).first()
                if chunk:
                    chunk.status = ChunkStatus.TELEGRAM_FAILED  # Mark as needs admin attention
                    db.commit()

            await self._complete_cycle(chunk_id, False)

        except Exception as e:
            self.logger.error(f"Error handling max attempts for chunk {chunk_id}: {e}")

    async def _notify_admin_failure(self, chunk_id: str, cycle_state: RewriteCycleState):
        """Notify admin of persistent rewrite failure."""
        try:
            # Send notification to admin
            message = f"""
            🚨 ADMIN ALERT: Rewrite Cycle Failed

            Chunk ID: {chunk_id}
            Lot ID: {cycle_state.lot_id}
            Attempts Made: {len(cycle_state.attempts)}
            Duration: {(time.time() - cycle_state.started_at) / 60:.1f} minutes

            Latest Scores:
            - Similarity: {cycle_state.attempts[-1].similarity_score if cycle_state.attempts else 'N/A'}%
            - AI Detection: {cycle_state.attempts[-1].ai_score if cycle_state.attempts else 'N/A'}%

            Manual intervention required.
            """

            # Log admin alert
            self.logger.critical(f"🚨 Admin intervention needed for chunk {chunk_id}")

            # Store in Redis for admin dashboard
            await self.redis_client.lpush(
                "admin_alerts",
                json.dumps({
                    "type": "rewrite_failure",
                    "chunk_id": chunk_id,
                    "lot_id": cycle_state.lot_id,
                    "message": message,
                    "timestamp": time.time(),
                    "attempts": len(cycle_state.attempts)
                })
            )

            # Keep only last 100 alerts
            await self.redis_client.ltrim("admin_alerts", 0, 99)

        except Exception as e:
            self.logger.error(f"Error notifying admin of failure for chunk {chunk_id}: {e}")

    async def _update_chunk_content(self, chunk_id: str, new_content: str):
        """Update chunk content in database after successful rewrite."""
        try:
            with get_database() as db:
                chunk = db.query(DocChunk).filter(DocChunk.id == chunk_id).first()
                if chunk:
                    chunk.content = new_content
                    chunk.status = ChunkStatus.DONE
                    chunk.updated_at = datetime.utcnow()
                    db.commit()

                    self.logger.info(f"💾 Updated chunk {chunk_id} with rewritten content")

        except Exception as e:
            self.logger.error(f"Error updating chunk content for {chunk_id}: {e}")

    async def _complete_cycle(self, chunk_id: str, success: bool):
        """Complete a rewrite cycle."""
        try:
            cycle_state = self.active_cycles.get(chunk_id)
            if not cycle_state:
                return

            cycle_state.success = success
            cycle_state.completed_at = time.time()
            cycle_state.current_stage = RewriteStage.COMPLETED

            # Update statistics
            if success:
                self.stats["cycles_completed"] += 1

                # Update average attempts to success
                successful_cycles = self.stats["cycles_completed"]
                current_avg = self.stats["average_attempts_to_success"]
                attempts = len(cycle_state.attempts)

                self.stats["average_attempts_to_success"] = (
                    (current_avg * (successful_cycles - 1) + attempts) / successful_cycles
                )

            else:
                self.stats["cycles_failed"] += 1

            # Update average cycle duration
            duration = cycle_state.completed_at - cycle_state.started_at
            total_cycles = self.stats["cycles_completed"] + self.stats["cycles_failed"]
            current_avg_duration = self.stats["average_cycle_duration"]

            self.stats["average_cycle_duration"] = (
                (current_avg_duration * (total_cycles - 1) + duration) / total_cycles
            )

            # Save final state
            await self._save_cycle_state(cycle_state)

            # Schedule cleanup
            await self.redis_client.setex(f"cycle_cleanup:{chunk_id}", 3600, "scheduled")  # 1 hour

            self.logger.info(f"🏁 Rewrite cycle completed for chunk {chunk_id}: {'Success' if success else 'Failed'}")

        except Exception as e:
            self.logger.error(f"Error completing cycle for chunk {chunk_id}: {e}")

    async def _save_cycle_state(self, cycle_state: RewriteCycleState):
        """Save cycle state to Redis."""
        try:
            state_data = {
                "chunk_id": cycle_state.chunk_id,
                "lot_id": cycle_state.lot_id,
                "current_stage": cycle_state.current_stage.value,
                "current_attempt": cycle_state.current_attempt,
                "max_attempts": cycle_state.max_attempts,
                "started_at": cycle_state.started_at,
                "completed_at": cycle_state.completed_at,
                "success": cycle_state.success,
                "admin_notified": cycle_state.admin_notified,
                "error_message": cycle_state.error_message,
                "final_similarity_score": cycle_state.final_similarity_score,
                "final_ai_score": cycle_state.final_ai_score,
                "attempts": [
                    {
                        "attempt_number": attempt.attempt_number,
                        "started_at": attempt.started_at,
                        "completed_at": attempt.completed_at,
                        "success": attempt.success,
                        "similarity_score": attempt.similarity_score,
                        "ai_score": attempt.ai_score,
                        "error_message": attempt.error_message,
                        "turnitin_submission_id": attempt.turnitin_submission_id
                    }
                    for attempt in cycle_state.attempts
                ]
            }

            await self.redis_client.hset(
                f"rewrite_cycle:{cycle_state.chunk_id}",
                mapping={k: json.dumps(v) if not isinstance(v, (str, int, float, bool, type(None))) else str(v)
                        for k, v in state_data.items()}
            )

            # Set expiration
            await self.redis_client.expire(f"rewrite_cycle:{cycle_state.chunk_id}", 86400)  # 24 hours

        except Exception as e:
            self.logger.error(f"Error saving cycle state for chunk {cycle_state.chunk_id}: {e}")

    async def _monitor_turnitin_results(self):
        """Monitor Turnitin results for active cycles."""
        while self.running:
            try:
                # Check active cycles awaiting results
                cycles_to_check = [
                    cycle for cycle in self.active_cycles.values()
                    if cycle.current_stage == RewriteStage.AWAITING_RESULTS
                ]

                for cycle_state in cycles_to_check:
                    if cycle_state.attempts:
                        latest_attempt = cycle_state.attempts[-1]

                        # Check if attempt has been waiting too long
                        if (time.time() - latest_attempt.started_at >
                            self.config.turnitin_timeout_minutes * 60):

                            self.logger.warning(f"⏰ Turnitin timeout for chunk {cycle_state.chunk_id}")
                            latest_attempt.error_message = "Turnitin timeout"

                            # Continue to next attempt or fail
                            if cycle_state.current_attempt < self.config.max_rewrite_attempts:
                                cycle_state.current_stage = RewriteStage.GENERATING_REWRITE
                            else:
                                await self._handle_max_attempts_reached(cycle_state.chunk_id)

                await asyncio.sleep(60)  # Check every minute

            except Exception as e:
                self.logger.error(f"Error monitoring Turnitin results: {e}")
                await asyncio.sleep(60)

    async def _process_rewrite_queue(self):
        """Process queued rewrite requests."""
        while self.running:
            try:
                # Check for new rewrite requests
                queue_item = await self.redis_client.brpop("rewrite_queue", timeout=5)

                if queue_item:
                    _, item_data = queue_item
                    request_data = json.loads(item_data)

                    chunk_id = request_data["chunk_id"]
                    similarity_pdf = request_data["similarity_pdf"]
                    ai_pdf = request_data["ai_pdf"]
                    original_content = request_data["original_content"]

                    await self.initiate_rewrite_cycle(
                        chunk_id, similarity_pdf, ai_pdf, original_content
                    )

            except Exception as e:
                self.logger.error(f"Error processing rewrite queue: {e}")
                await asyncio.sleep(30)

    async def _cleanup_completed_cycles(self):
        """Clean up completed cycles periodically."""
        while self.running:
            try:
                current_time = time.time()
                cycles_to_remove = []

                for chunk_id, cycle_state in self.active_cycles.items():
                    # Remove completed cycles after 1 hour
                    if (cycle_state.completed_at and
                        current_time - cycle_state.completed_at > 3600):
                        cycles_to_remove.append(chunk_id)

                for chunk_id in cycles_to_remove:
                    del self.active_cycles[chunk_id]
                    self.logger.info(f"🧹 Cleaned up completed cycle for chunk {chunk_id}")

                await asyncio.sleep(1800)  # Clean up every 30 minutes

            except Exception as e:
                self.logger.error(f"Error cleaning up cycles: {e}")
                await asyncio.sleep(1800)

    async def get_cycle_status(self, chunk_id: str) -> Optional[Dict[str, Any]]:
        """Get current status of a rewrite cycle."""
        try:
            cycle_state = self.active_cycles.get(chunk_id)

            if cycle_state:
                return {
                    "chunk_id": chunk_id,
                    "current_stage": cycle_state.current_stage.value,
                    "current_attempt": cycle_state.current_attempt,
                    "max_attempts": cycle_state.max_attempts,
                    "attempts_made": len(cycle_state.attempts),
                    "started_at": cycle_state.started_at,
                    "success": cycle_state.success,
                    "final_similarity_score": cycle_state.final_similarity_score,
                    "final_ai_score": cycle_state.final_ai_score,
                    "error_message": cycle_state.error_message
                }

            # Check Redis for historical data
            state_data = await self.redis_client.hgetall(f"rewrite_cycle:{chunk_id}")
            if state_data:
                return {
                    "chunk_id": chunk_id,
                    "current_stage": state_data.get("current_stage"),
                    "success": state_data.get("success") == "True",
                    "completed_at": float(state_data.get("completed_at", 0)) if state_data.get("completed_at") != "None" else None,
                    "error_message": state_data.get("error_message") if state_data.get("error_message") != "None" else None
                }

            return None

        except Exception as e:
            self.logger.error(f"Error getting cycle status for chunk {chunk_id}: {e}")
            return None

    async def get_system_stats(self) -> Dict[str, Any]:
        """Get comprehensive rewrite cycle statistics."""
        return {
            "stats": self.stats,
            "active_cycles": len(self.active_cycles),
            "config": {
                "max_rewrite_attempts": self.config.max_rewrite_attempts,
                "similarity_threshold": self.config.similarity_threshold,
                "ai_threshold": self.config.ai_threshold,
                "turnitin_timeout_minutes": self.config.turnitin_timeout_minutes
            },
            "timestamp": time.time()
        }


# Global rewrite cycle instance
rewrite_cycle_manager = AutomatedRewriteCycle()


# Utility functions for integration
async def start_rewrite_cycle(chunk_id: str, similarity_pdf: str,
                            ai_pdf: str, original_content: str) -> bool:
    """Start automated rewrite cycle for a chunk."""
    return await rewrite_cycle_manager.initiate_rewrite_cycle(
        chunk_id, similarity_pdf, ai_pdf, original_content
    )


async def get_rewrite_cycle_status(chunk_id: str) -> Optional[Dict[str, Any]]:
    """Get status of rewrite cycle for a chunk."""
    return await rewrite_cycle_manager.get_cycle_status(chunk_id)


# Queue function for integration with checker workflow
async def queue_rewrite_request(chunk_id: str, similarity_pdf: str,
                              ai_pdf: str, original_content: str):
    """Queue a rewrite request for processing."""
    redis_client = redis.from_url("redis://localhost:6379", decode_responses=True)

    try:
        request_data = {
            "chunk_id": chunk_id,
            "similarity_pdf": similarity_pdf,
            "ai_pdf": ai_pdf,
            "original_content": original_content,
            "queued_at": time.time()
        }

        await redis_client.lpush("rewrite_queue", json.dumps(request_data))

    finally:
        await redis_client.close()


if __name__ == "__main__":
    # Test the rewrite cycle
    async def test_rewrite_cycle():
        """Test rewrite cycle manager."""
        manager = AutomatedRewriteCycle()

        await manager.start_cycle_manager()

        # Test cycle initiation
        success = await manager.initiate_rewrite_cycle(
            "test_chunk_1",
            "/tmp/similarity.pdf",
            "/tmp/ai.pdf",
            "This is test content that needs rewriting."
        )

        print(f"Cycle started: {success}")

        # Check status
        await asyncio.sleep(5)
        status = await manager.get_cycle_status("test_chunk_1")
        print(f"Cycle status: {status}")

        # Get stats
        stats = await manager.get_system_stats()
        print(f"System stats: {stats}")

        await manager.stop_cycle_manager()

    asyncio.run(test_rewrite_cycle())
