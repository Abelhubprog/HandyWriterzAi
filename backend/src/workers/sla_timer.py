"""
SLA Timer System - 15-minute countdown enforcement for checker claims
Monitors checker claims and automatically resets expired ones.
"""

import asyncio
import time
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from dataclasses import dataclass

import redis.asyncio as redis

from db.database import get_database
from db.models import DocChunk, Checker, ChunkStatus
from src.services.notification_service import NotificationService


@dataclass
class SLATimerConfig:
    """SLA timer configuration."""
    timeout_minutes: int = 15
    warning_minutes: int = 10  # Warning at 10 minutes
    check_interval_seconds: int = 30
    max_penalty_points: int = 3
    penalty_duration_hours: int = 24


class SLATimerSystem:
    """
    Production-ready SLA timer system for enforcing 15-minute checker timeouts.
    
    Features:
    - Automatic timeout enforcement
    - Warning notifications at 10 minutes
    - Penalty system for repeated violations
    - Redis-based real-time monitoring
    - WhatsApp notification integration
    - Comprehensive logging and metrics
    """
    
    def __init__(self, config: Optional[SLATimerConfig] = None):
        self.config = config or SLATimerConfig()
        self.logger = logging.getLogger(__name__)
        
        # Initialize Redis for real-time tracking
        self.redis_client = redis.from_url("redis://localhost:6379", decode_responses=True)
        
        # Initialize notification service
        self.notification_service = NotificationService()
        
        # Active timers tracking
        self.active_timers: Dict[str, asyncio.Task] = {}
        
        # SLA metrics
        self.metrics = {
            "timers_started": 0,
            "timers_expired": 0,
            "timers_completed": 0,
            "warnings_sent": 0,
            "penalties_applied": 0
        }
        
        self.running = False
        
    async def start_timer_system(self):
        """Start the SLA timer monitoring system."""
        self.running = True
        self.logger.info("🕐 SLA Timer System starting...")
        
        # Start the main monitoring loop
        asyncio.create_task(self._monitor_active_claims())
        
        # Start metrics reporting
        asyncio.create_task(self._report_metrics())
        
        self.logger.info("✅ SLA Timer System operational")
        
    async def stop_timer_system(self):
        """Stop the SLA timer system."""
        self.running = False
        
        # Cancel all active timers
        for timer_task in self.active_timers.values():
            timer_task.cancel()
        
        self.active_timers.clear()
        await self.redis_client.close()
        
        self.logger.info("🔄 SLA Timer System stopped")
        
    async def start_checker_timer(self, chunk_id: str, checker_id: str, 
                                  claim_timestamp: Optional[float] = None) -> bool:
        """
        Start SLA timer for a checker claim.
        
        Args:
            chunk_id: ID of the claimed chunk
            checker_id: ID of the checker who claimed it
            claim_timestamp: When the claim was made (defaults to now)
            
        Returns:
            bool: True if timer started successfully
        """
        try:
            claim_time = claim_timestamp or time.time()
            expires_at = claim_time + (self.config.timeout_minutes * 60)
            
            # Store timer info in Redis
            timer_data = {
                "chunk_id": chunk_id,
                "checker_id": checker_id,
                "claim_time": claim_time,
                "expires_at": expires_at,
                "warning_sent": False,
                "status": "active"
            }
            
            await self.redis_client.hset(
                f"sla_timer:{chunk_id}",
                mapping=timer_data
            )
            
            # Set expiration on the Redis key
            await self.redis_client.expire(
                f"sla_timer:{chunk_id}",
                self.config.timeout_minutes * 60 + 300  # Extra 5 minutes buffer
            )
            
            # Start the timer task
            timer_key = f"{chunk_id}:{checker_id}"
            if timer_key in self.active_timers:
                self.active_timers[timer_key].cancel()
            
            self.active_timers[timer_key] = asyncio.create_task(
                self._run_timer(chunk_id, checker_id, expires_at)
            )
            
            self.metrics["timers_started"] += 1
            
            self.logger.info(f"⏰ SLA timer started for chunk {chunk_id} by checker {checker_id}")
            
            # Send claim notification
            await self._send_claim_notification(chunk_id, checker_id, expires_at)
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to start SLA timer for chunk {chunk_id}: {e}")
            return False
    
    async def complete_timer(self, chunk_id: str, checker_id: str) -> bool:
        """
        Complete SLA timer when checker submits work.
        
        Args:
            chunk_id: ID of the chunk
            checker_id: ID of the checker
            
        Returns:
            bool: True if timer completed successfully
        """
        try:
            timer_key = f"{chunk_id}:{checker_id}"
            
            # Cancel the timer task
            if timer_key in self.active_timers:
                self.active_timers[timer_key].cancel()
                del self.active_timers[timer_key]
            
            # Update Redis status
            await self.redis_client.hset(
                f"sla_timer:{chunk_id}",
                "status", "completed"
            )
            
            # Clean up timer data after delay
            await self.redis_client.expire(f"sla_timer:{chunk_id}", 3600)  # Keep for 1 hour
            
            self.metrics["timers_completed"] += 1
            
            self.logger.info(f"✅ SLA timer completed for chunk {chunk_id} by checker {checker_id}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to complete SLA timer for chunk {chunk_id}: {e}")
            return False
    
    async def _run_timer(self, chunk_id: str, checker_id: str, expires_at: float):
        """Run the actual timer countdown for a specific claim."""
        try:
            current_time = time.time()
            warning_time = expires_at - (self.config.warning_minutes * 60)
            
            # Wait until warning time
            if current_time < warning_time:
                await asyncio.sleep(warning_time - current_time)
                
                # Check if timer is still active
                timer_data = await self.redis_client.hgetall(f"sla_timer:{chunk_id}")
                if timer_data.get("status") == "active":
                    await self._send_warning_notification(chunk_id, checker_id)
                    await self.redis_client.hset(f"sla_timer:{chunk_id}", "warning_sent", "true")
                    self.metrics["warnings_sent"] += 1
            
            # Wait until expiration time
            current_time = time.time()
            if current_time < expires_at:
                await asyncio.sleep(expires_at - current_time)
            
            # Check if timer expired
            timer_data = await self.redis_client.hgetall(f"sla_timer:{chunk_id}")
            if timer_data.get("status") == "active":
                await self._handle_timer_expiration(chunk_id, checker_id)
                
        except asyncio.CancelledError:
            # Timer was cancelled (normal completion)
            pass
        except Exception as e:
            self.logger.error(f"Timer error for chunk {chunk_id}: {e}")
    
    async def _handle_timer_expiration(self, chunk_id: str, checker_id: str):
        """Handle when a timer expires (15 minutes elapsed)."""
        try:
            self.logger.warning(f"⏰ SLA timer EXPIRED for chunk {chunk_id} by checker {checker_id}")
            
            # Reset chunk status in database
            with get_database() as db:
                chunk = db.query(DocChunk).filter(DocChunk.id == chunk_id).first()
                if chunk and chunk.status == ChunkStatus.CHECKING:
                    chunk.status = ChunkStatus.OPEN
                    chunk.checker_id = None
                    chunk.timer_expires = None
                    db.commit()
                    
                    self.logger.info(f"🔄 Chunk {chunk_id} reset to OPEN status")
            
            # Apply penalty to checker
            await self._apply_checker_penalty(checker_id)
            
            # Update Redis status
            await self.redis_client.hset(
                f"sla_timer:{chunk_id}",
                mapping={
                    "status": "expired",
                    "expired_at": time.time()
                }
            )
            
            # Send expiration notification
            await self._send_expiration_notification(chunk_id, checker_id)
            
            # Clean up timer
            timer_key = f"{chunk_id}:{checker_id}"
            if timer_key in self.active_timers:
                del self.active_timers[timer_key]
            
            self.metrics["timers_expired"] += 1
            
        except Exception as e:
            self.logger.error(f"Failed to handle timer expiration for chunk {chunk_id}: {e}")
    
    async def _apply_checker_penalty(self, checker_id: str):
        """Apply penalty points to checker for SLA violation."""
        try:
            with get_database() as db:
                checker = db.query(Checker).filter(Checker.id == checker_id).first()
                if checker:
                    # Add penalty point
                    penalty_points = getattr(checker, 'penalty_points', 0) + 1
                    
                    # Temporarily disable checker if too many penalties
                    if penalty_points >= self.config.max_penalty_points:
                        penalty_until = datetime.utcnow() + timedelta(hours=self.config.penalty_duration_hours)
                        checker.penalty_until = penalty_until
                        penalty_points = 0  # Reset after suspension
                        
                        self.logger.warning(f"🚫 Checker {checker_id} suspended until {penalty_until}")
                    
                    checker.penalty_points = penalty_points
                    checker.rating_score = max(0, (checker.rating_score or 0) - 1)
                    db.commit()
                    
                    self.metrics["penalties_applied"] += 1
                    
        except Exception as e:
            self.logger.error(f"Failed to apply penalty to checker {checker_id}: {e}")
    
    async def _send_claim_notification(self, chunk_id: str, checker_id: str, expires_at: float):
        """Send notification when checker claims a chunk."""
        try:
            expires_in_minutes = int((expires_at - time.time()) / 60)
            
            message = f"You have claimed chunk {chunk_id}. You have {expires_in_minutes} minutes to complete the review."
            
            await self.notification_service.send_whatsapp_message(
                checker_id=checker_id,
                message=message,
                message_type="claim_notification"
            )
            
        except Exception as e:
            self.logger.error(f"Failed to send claim notification: {e}")
    
    async def _send_warning_notification(self, chunk_id: str, checker_id: str):
        """Send warning notification at 10-minute mark."""
        try:
            message = f"⚠️ Warning: You have 5 minutes remaining to complete chunk {chunk_id} review!"
            
            await self.notification_service.send_whatsapp_message(
                checker_id=checker_id,
                message=message,
                message_type="warning_notification"
            )
            
            self.logger.info(f"📢 Warning notification sent for chunk {chunk_id} to checker {checker_id}")
            
        except Exception as e:
            self.logger.error(f"Failed to send warning notification: {e}")
    
    async def _send_expiration_notification(self, chunk_id: str, checker_id: str):
        """Send notification when timer expires."""
        try:
            message = f"❌ Time expired for chunk {chunk_id}. The chunk has been released back to the pool. A penalty point has been applied to your account."
            
            await self.notification_service.send_whatsapp_message(
                checker_id=checker_id,
                message=message,
                message_type="expiration_notification"
            )
            
            self.logger.info(f"📢 Expiration notification sent for chunk {chunk_id} to checker {checker_id}")
            
        except Exception as e:
            self.logger.error(f"Failed to send expiration notification: {e}")
    
    async def _monitor_active_claims(self):
        """Monitor all active claims and ensure timers are running."""
        while self.running:
            try:
                await asyncio.sleep(self.config.check_interval_seconds)
                
                # Check for claims in database that might not have timers
                with get_database() as db:
                    active_chunks = db.query(DocChunk).filter(
                        DocChunk.status == ChunkStatus.CHECKING,
                        DocChunk.timer_expires.isnot(None)
                    ).all()
                    
                    for chunk in active_chunks:
                        timer_key = f"{chunk.id}:{chunk.checker_id}"
                        
                        # Check if timer exists in Redis
                        timer_exists = await self.redis_client.exists(f"sla_timer:{chunk.id}")
                        
                        if not timer_exists and timer_key not in self.active_timers:
                            # Timer missing, restart it
                            if chunk.timer_expires and chunk.timer_expires > datetime.utcnow():
                                claim_time = time.time() - (self.config.timeout_minutes * 60 - 
                                           (chunk.timer_expires - datetime.utcnow()).total_seconds())
                                await self.start_checker_timer(
                                    str(chunk.id), 
                                    str(chunk.checker_id), 
                                    claim_time
                                )
                                self.logger.info(f"🔄 Restarted missing timer for chunk {chunk.id}")
                            else:
                                # Timer already expired, handle it
                                await self._handle_timer_expiration(str(chunk.id), str(chunk.checker_id))
                
            except Exception as e:
                self.logger.error(f"Error in timer monitoring loop: {e}")
                await asyncio.sleep(60)  # Wait longer on error
    
    async def _report_metrics(self):
        """Report SLA timer metrics periodically."""
        while self.running:
            try:
                await asyncio.sleep(300)  # Report every 5 minutes
                
                self.logger.info(f"📊 SLA Timer Metrics: {self.metrics}")
                
                # Store metrics in Redis for dashboard
                await self.redis_client.hset(
                    "sla_timer_metrics",
                    mapping={
                        **self.metrics,
                        "active_timers": len(self.active_timers),
                        "timestamp": time.time()
                    }
                )
                
            except Exception as e:
                self.logger.error(f"Error reporting SLA metrics: {e}")
                await asyncio.sleep(60)
    
    async def get_timer_status(self, chunk_id: str) -> Optional[Dict]:
        """Get current timer status for a chunk."""
        try:
            timer_data = await self.redis_client.hgetall(f"sla_timer:{chunk_id}")
            
            if not timer_data:
                return None
            
            current_time = time.time()
            expires_at = float(timer_data.get("expires_at", 0))
            
            return {
                "chunk_id": chunk_id,
                "checker_id": timer_data.get("checker_id"),
                "claim_time": float(timer_data.get("claim_time", 0)),
                "expires_at": expires_at,
                "remaining_seconds": max(0, expires_at - current_time),
                "warning_sent": timer_data.get("warning_sent") == "true",
                "status": timer_data.get("status", "unknown")
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get timer status for chunk {chunk_id}: {e}")
            return None
    
    async def get_checker_active_timers(self, checker_id: str) -> List[Dict]:
        """Get all active timers for a specific checker."""
        try:
            active_timers = []
            
            # Scan for all timer keys
            async for key in self.redis_client.scan_iter(match="sla_timer:*"):
                timer_data = await self.redis_client.hgetall(key)
                
                if (timer_data.get("checker_id") == checker_id and 
                    timer_data.get("status") == "active"):
                    
                    chunk_id = key.split(":", 1)[1]
                    timer_status = await self.get_timer_status(chunk_id)
                    if timer_status:
                        active_timers.append(timer_status)
            
            return active_timers
            
        except Exception as e:
            self.logger.error(f"Failed to get active timers for checker {checker_id}: {e}")
            return []
    
    async def get_system_metrics(self) -> Dict:
        """Get comprehensive SLA timer system metrics."""
        try:
            metrics = await self.redis_client.hgetall("sla_timer_metrics")
            
            return {
                "current_metrics": self.metrics,
                "stored_metrics": metrics,
                "active_timers_count": len(self.active_timers),
                "system_status": "running" if self.running else "stopped",
                "config": {
                    "timeout_minutes": self.config.timeout_minutes,
                    "warning_minutes": self.config.warning_minutes,
                    "check_interval_seconds": self.config.check_interval_seconds,
                    "max_penalty_points": self.config.max_penalty_points
                }
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get system metrics: {e}")
            return {"error": str(e)}


# Global SLA timer instance
sla_timer_system = SLATimerSystem()


# Utility functions for integration with checker API
async def start_sla_timer(chunk_id: str, checker_id: str) -> bool:
    """Start SLA timer for a checker claim."""
    return await sla_timer_system.start_checker_timer(chunk_id, checker_id)


async def complete_sla_timer(chunk_id: str, checker_id: str) -> bool:
    """Complete SLA timer when work is submitted."""
    return await sla_timer_system.complete_timer(chunk_id, checker_id)


async def get_sla_timer_status(chunk_id: str) -> Optional[Dict]:
    """Get current SLA timer status for a chunk."""
    return await sla_timer_system.get_timer_status(chunk_id)


async def get_checker_sla_timers(checker_id: str) -> List[Dict]:
    """Get all active SLA timers for a checker."""
    return await sla_timer_system.get_checker_active_timers(checker_id)


# Background task to start the SLA timer system
async def start_sla_timer_background():
    """Start the SLA timer system as a background task."""
    try:
        await sla_timer_system.start_timer_system()
    except Exception as e:
        logging.getLogger(__name__).error(f"Failed to start SLA timer system: {e}")


if __name__ == "__main__":
    # For testing the SLA timer system
    import uvloop
    
    async def test_sla_system():
        """Test the SLA timer system."""
        timer_system = SLATimerSystem()
        await timer_system.start_timer_system()
        
        # Test timer start
        await timer_system.start_checker_timer("test_chunk_1", "test_checker_1")
        
        # Wait and check status
        await asyncio.sleep(5)
        status = await timer_system.get_timer_status("test_chunk_1")
        print(f"Timer status: {status}")
        
        # Complete timer
        await timer_system.complete_timer("test_chunk_1", "test_checker_1")
        
        await timer_system.stop_timer_system()
    
    uvloop.install()
    asyncio.run(test_sla_system())