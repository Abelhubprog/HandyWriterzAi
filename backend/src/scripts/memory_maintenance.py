#!/usr/bin/env python3
"""
Memory Maintenance Script for HandyWriterzAI.
Performs scheduled maintenance on the memory system including importance decay,
cleanup of old memories, and optimization of vector indexes.
"""

import asyncio
import logging
import sys
import os
from datetime import datetime, timedelta
from typing import Optional
import argparse

# Add the backend src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from services.memory_integrator import get_memory_integrator
from db.database import get_db_manager
from db.models import LongTermMemory, MemoryRetrieval

logger = logging.getLogger(__name__)

class MemoryMaintenanceManager:
    """Comprehensive memory maintenance operations."""
    
    def __init__(self):
        self.memory_service = get_memory_integrator()
        self.db_manager = get_db_manager()
        
    async def run_full_maintenance(self, user_id: Optional[str] = None):
        """Run complete maintenance cycle."""
        logger.info("Starting full memory maintenance cycle")
        
        try:
            # 1. Update importance scores with time decay
            await self._decay_importance_scores(user_id)
            
            # 2. Clean up old, low-importance memories
            await self._cleanup_old_memories(user_id)
            
            # 3. Update access patterns
            await self._update_access_patterns(user_id)
            
            # 4. Optimize vector indexes
            await self._optimize_vector_indexes()
            
            # 5. Generate maintenance report
            report = await self._generate_maintenance_report(user_id)
            
            logger.info("Memory maintenance completed successfully")
            return report
            
        except Exception as e:
            logger.error(f"Memory maintenance failed: {e}")
            raise
    
    async def _decay_importance_scores(self, user_id: Optional[str] = None):
        """Apply time-based importance decay to memories."""
        logger.info("Applying importance decay to memories")
        
        try:
            with self.db_manager.get_db_context() as db:
                # Get memories older than 1 week
                cutoff_date = datetime.utcnow() - timedelta(days=7)
                
                query = db.query(LongTermMemory).filter(
                    LongTermMemory.last_accessed < cutoff_date
                )
                
                if user_id:
                    query = query.filter(LongTermMemory.user_id == user_id)
                
                memories = query.all()
                updated_count = 0
                
                for memory in memories:
                    # Calculate decay based on age
                    days_old = (datetime.utcnow() - memory.last_accessed).days
                    weeks_old = max(1, days_old // 7)
                    
                    # Apply exponential decay (5% per week)
                    decay_factor = 0.95 ** weeks_old
                    new_importance = memory.importance_score * decay_factor
                    
                    # Apply access frequency boost
                    if memory.access_frequency > 0:
                        frequency_boost = min(1.1, 1 + (memory.access_frequency * 0.01))
                        new_importance *= frequency_boost
                    
                    # Update if significantly changed
                    if abs(memory.importance_score - new_importance) > 0.01:
                        memory.importance_score = max(new_importance, 0.01)  # Min threshold
                        updated_count += 1
                
                logger.info(f"Updated importance scores for {updated_count} memories")
                
        except Exception as e:
            logger.error(f"Importance decay failed: {e}")
            raise
    
    async def _cleanup_old_memories(self, user_id: Optional[str] = None):
        """Remove old, low-importance memories to free storage."""
        logger.info("Cleaning up old memories")
        
        try:
            with self.db_manager.get_db_context() as db:
                # Remove memories that are very old and have low importance
                cutoff_date = datetime.utcnow() - timedelta(days=90)
                
                query = db.query(LongTermMemory).filter(
                    LongTermMemory.created_at < cutoff_date,
                    LongTermMemory.importance_score < 0.1
                )
                
                if user_id:
                    query = query.filter(LongTermMemory.user_id == user_id)
                
                old_memories = query.all()
                
                # Also clean up memories that haven't been accessed in 6 months
                never_accessed_cutoff = datetime.utcnow() - timedelta(days=180)
                never_accessed_query = db.query(LongTermMemory).filter(
                    LongTermMemory.last_accessed < never_accessed_cutoff,
                    LongTermMemory.access_frequency == 0,
                    LongTermMemory.importance_score < 0.3
                )
                
                if user_id:
                    never_accessed_query = never_accessed_query.filter(LongTermMemory.user_id == user_id)
                
                never_accessed_memories = never_accessed_query.all()
                
                # Combine and remove
                memories_to_remove = list(set(old_memories + never_accessed_memories))
                
                for memory in memories_to_remove:
                    db.delete(memory)
                
                logger.info(f"Cleaned up {len(memories_to_remove)} old memories")
                
        except Exception as e:
            logger.error(f"Memory cleanup failed: {e}")
            raise
    
    async def _update_access_patterns(self, user_id: Optional[str] = None):
        """Update memory access patterns based on retrieval logs."""
        logger.info("Updating memory access patterns")
        
        try:
            with self.db_manager.get_db_context() as db:
                # Boost importance for frequently retrieved memories
                from sqlalchemy import func
                
                # Get retrieval statistics for recent activity
                recent_cutoff = datetime.utcnow() - timedelta(days=30)
                
                retrieval_stats = db.query(
                    MemoryRetrieval.memory_id,
                    func.count(MemoryRetrieval.id).label('recent_retrievals'),
                    func.avg(MemoryRetrieval.similarity_score).label('avg_similarity')
                ).filter(
                    MemoryRetrieval.retrieved_at > recent_cutoff
                ).group_by(MemoryRetrieval.memory_id).all()
                
                updated_count = 0
                
                for stat in retrieval_stats:
                    memory = db.query(LongTermMemory).filter(
                        LongTermMemory.id == stat.memory_id
                    ).first()
                    
                    if memory and (not user_id or str(memory.user_id) == user_id):
                        # Boost importance for frequently retrieved memories
                        if stat.recent_retrievals >= 3:
                            importance_boost = min(0.1, stat.recent_retrievals * 0.02)
                            memory.importance_score = min(1.0, memory.importance_score + importance_boost)
                            updated_count += 1
                
                logger.info(f"Updated access patterns for {updated_count} memories")
                
        except Exception as e:
            logger.error(f"Access pattern update failed: {e}")
            raise
    
    async def _optimize_vector_indexes(self):
        """Optimize vector database indexes for better performance."""
        logger.info("Optimizing vector indexes")
        
        try:
            with self.db_manager.get_db_context() as db:
                # Reindex vector tables for optimal performance
                db.execute("REINDEX INDEX ix_memory_embedding_hnsw;")
                db.execute("VACUUM ANALYZE long_term_memory;")
                db.execute("VACUUM ANALYZE memory_retrievals;")
                
                logger.info("Vector index optimization completed")
                
        except Exception as e:
            logger.warning(f"Vector index optimization failed (may not be PostgreSQL): {e}")
    
    async def _generate_maintenance_report(self, user_id: Optional[str] = None) -> dict:
        """Generate maintenance report with statistics."""
        logger.info("Generating maintenance report")
        
        try:
            with self.db_manager.get_db_context() as db:
                from sqlalchemy import func
                
                # Overall statistics
                base_query = db.query(LongTermMemory)
                if user_id:
                    base_query = base_query.filter(LongTermMemory.user_id == user_id)
                
                total_memories = base_query.count()
                
                avg_importance = db.query(func.avg(LongTermMemory.importance_score)).scalar() or 0
                
                # Memory age distribution
                now = datetime.utcnow()
                recent_memories = base_query.filter(
                    LongTermMemory.created_at > now - timedelta(days=7)
                ).count()
                
                old_memories = base_query.filter(
                    LongTermMemory.created_at < now - timedelta(days=90)
                ).count()
                
                # Access statistics
                total_accesses = db.query(func.sum(LongTermMemory.access_frequency)).scalar() or 0
                
                # Retrieval statistics (last 30 days)
                recent_retrievals = db.query(MemoryRetrieval).filter(
                    MemoryRetrieval.retrieved_at > now - timedelta(days=30)
                ).count()
                
                report = {
                    "maintenance_timestamp": now.isoformat(),
                    "user_id": user_id,
                    "total_memories": total_memories,
                    "average_importance": float(avg_importance),
                    "recent_memories_7_days": recent_memories,
                    "old_memories_90_days": old_memories,
                    "total_memory_accesses": total_accesses,
                    "recent_retrievals_30_days": recent_retrievals,
                    "maintenance_status": "completed"
                }
                
                logger.info(f"Maintenance report generated: {total_memories} memories processed")
                return report
                
        except Exception as e:
            logger.error(f"Report generation failed: {e}")
            return {"error": str(e), "maintenance_status": "failed"}


async def main():
    """Main entry point for maintenance script."""
    parser = argparse.ArgumentParser(description="Memory Maintenance Script")
    parser.add_argument("--user-id", help="Run maintenance for specific user")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose logging")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be done without making changes")
    
    args = parser.parse_args()
    
    # Configure logging
    log_level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Initialize maintenance manager
    maintenance_manager = MemoryMaintenanceManager()
    
    try:
        if args.dry_run:
            logger.info("DRY RUN MODE: No changes will be made")
            # In dry run, we would show what would be done
            # For now, just log the intent
            logger.info(f"Would run maintenance for {'all users' if not args.user_id else f'user {args.user_id}'}")
            return
        
        # Run maintenance
        report = await maintenance_manager.run_full_maintenance(args.user_id)
        
        # Print report
        print("\n=== MEMORY MAINTENANCE REPORT ===")
        for key, value in report.items():
            print(f"{key}: {value}")
        print("================================\n")
        
    except Exception as e:
        logger.error(f"Maintenance script failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())