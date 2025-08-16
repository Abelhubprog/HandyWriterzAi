"""
Production-ready Memory Integrator for HandyWriterzAI.
Implements advanced long-term memory with importance ranking, vector retrieval, and adaptive forgetting.
"""

import logging
import uuid
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Tuple
import asyncio
from sqlalchemy.orm import Session
from sqlalchemy import desc, and_, func, text
import numpy as np

from src.db.database import get_db_manager
from src.db.models import LongTermMemory, MemoryRetrieval, MemoryReflection, MemoryType
from src.services.embedding_service import get_embedding_service
from src.services.vector_storage import get_vector_storage
from src.models.openai import get_openai_client
from .memory_safety import get_memory_safety_service, MemorySafetyError

logger = logging.getLogger(__name__)


class MemoryIntegratorService:
    """Production-ready memory integration with intelligent retrieval and adaptive importance scoring."""
    
    def __init__(self):
        self.db_manager = get_db_manager()
        self.embedding_service = get_embedding_service()
        self.vector_storage = get_vector_storage()
        self.openai_client = get_openai_client()
        self.safety_service = get_memory_safety_service()
        
        # Memory configuration
        self.max_memories_per_user = 10000  # Configurable limit
        self.default_importance_threshold = 0.3
        self.retrieval_limit = 8  # Max memories to retrieve per query
        self.reflection_trigger_threshold = 3  # Trigger reflection every N conversations
        
        # Importance decay parameters
        self.importance_decay_rate = 0.95  # Weekly decay factor
        self.access_boost_factor = 1.1  # Boost for accessed memories
        self.novelty_boost_factor = 1.2  # Boost for novel information
        
        logger.info("MemoryIntegrator initialized with production configuration and safety controls")
    
    async def retrieve_memories(
        self,
        user_id: str,
        query: str,
        conversation_id: Optional[str] = None,
        memory_types: Optional[List[MemoryType]] = None,
        k: int = None,
        importance_threshold: float = None,
        include_context: bool = True
    ) -> List[Dict[str, Any]]:
        """
        Retrieve most relevant memories using hybrid semantic and importance ranking.
        
        Args:
            user_id: User identifier
            query: Search query text
            conversation_id: Optional conversation context
            memory_types: Filter by specific memory types
            k: Number of memories to return (default: self.retrieval_limit)
            importance_threshold: Minimum importance score (default: self.default_importance_threshold)
            include_context: Whether to include memory context
            
        Returns:
            List of memory dictionaries with relevance scores
        """
        try:
            k = k or self.retrieval_limit
            importance_threshold = importance_threshold or self.default_importance_threshold
            
            # Safety validation
            is_valid, issues = await self.safety_service.validate_retrieval_request(user_id, query, k)
            if not is_valid:
                raise MemorySafetyError(f"Retrieval validation failed: {', '.join(issues)}")
            
            # Track cost for retrieval operation
            await self.safety_service.track_operation_cost(user_id, 'vector_operation')
            
            # Generate query embedding
            query_embedding = await self.embedding_service.embed_query(
                query, query_type="academic_search"
            )
            
            # Track embedding cost
            estimated_tokens = len(query.split()) * 1.3  # Rough token estimate
            await self.safety_service.track_operation_cost(
                user_id, 'embedding', token_count=estimated_tokens
            )
            
            # Retrieve memories using vector similarity
            with self.db_manager.get_db_context() as db:
                # Base query with vector similarity
                base_query = db.query(
                    LongTermMemory,
                    (1 - LongTermMemory.embedding.cosine_distance(query_embedding)).label("similarity")
                ).filter(
                    LongTermMemory.user_id == uuid.UUID(user_id),
                    LongTermMemory.importance_score >= importance_threshold,
                    LongTermMemory.embedding.is_not(None)
                )
                
                # Apply memory type filters
                if memory_types:
                    base_query = base_query.filter(LongTermMemory.memory_type.in_(memory_types))
                
                # Execute query with hybrid ranking (similarity + importance + recency)
                results = base_query.order_by(
                    # Hybrid scoring: 0.4 * similarity + 0.4 * importance + 0.2 * recency_factor
                    desc(
                        0.4 * (1 - LongTermMemory.embedding.cosine_distance(query_embedding)) +
                        0.4 * LongTermMemory.importance_score +
                        0.2 * func.extract('epoch', LongTermMemory.last_accessed) / 86400.0  # Days since epoch
                    )
                ).limit(k * 2).all()  # Get more results for re-ranking
                
                # Re-rank with temporal and access patterns
                ranked_memories = await self._rerank_memories(results, query, conversation_id)
                
                # Log retrieval for analytics
                await self._log_memory_retrievals(
                    [memory for memory, _ in ranked_memories[:k]], 
                    user_id, 
                    conversation_id, 
                    query
                )
                
                # Format results
                formatted_memories = []
                for (memory, similarity), rank in zip(ranked_memories[:k], range(k)):
                    memory_dict = {
                        "id": str(memory.id),
                        "content": memory.content,
                        "memory_type": memory.memory_type.value,
                        "importance_score": memory.importance_score,
                        "similarity_score": float(similarity),
                        "access_frequency": memory.access_frequency,
                        "last_accessed": memory.last_accessed.isoformat(),
                        "created_at": memory.created_at.isoformat(),
                        "tags": memory.tags or [],
                        "rank_position": rank
                    }
                    
                    if include_context and memory.context:
                        memory_dict["context"] = memory.context
                    
                    formatted_memories.append(memory_dict)
                
                logger.info(f"Retrieved {len(formatted_memories)} memories for user {user_id}")
                return formatted_memories
                
        except Exception as e:
            logger.error(f"Memory retrieval failed for user {user_id}: {e}")
            raise
    
    async def write_memory(
        self,
        user_id: str,
        content: str,
        memory_type: MemoryType,
        conversation_id: Optional[str] = None,
        importance_score: Optional[float] = None,
        tags: Optional[List[str]] = None,
        context: Optional[Dict[str, Any]] = None,
        source_summary: Optional[str] = None
    ) -> str:
        """
        Write a new memory or update existing similar memory.
        
        Args:
            user_id: User identifier
            content: Memory content text
            memory_type: Type of memory being stored
            conversation_id: Associated conversation
            importance_score: Initial importance (auto-calculated if None)
            tags: Memory tags for categorization
            context: Additional context information
            source_summary: How this memory was created
            
        Returns:
            Memory ID
        """
        try:
            # Safety validation
            is_valid, issues = await self.safety_service.validate_memory_content(content, user_id)
            if not is_valid:
                raise MemorySafetyError(f"Memory content validation failed: {', '.join(issues)}")
            
            # Sanitize content for PII
            sanitized_content = self.safety_service.sanitize_content(content)
            
            # Calculate importance score if not provided
            if importance_score is None:
                importance_score = await self._calculate_importance_score(
                    sanitized_content, memory_type, user_id, conversation_id
                )
            
            # Generate embedding
            embedding = await self.embedding_service.embed_text(
                sanitized_content, prefix=f"{memory_type.value.title()} memory: "
            )
            
            # Track embedding cost
            estimated_tokens = len(sanitized_content.split()) * 1.3
            await self.safety_service.track_operation_cost(
                user_id, 'embedding', token_count=estimated_tokens
            )
            
            # Check for similar existing memories to avoid duplication
            existing_memory_id = await self._check_for_similar_memory(
                user_id, sanitized_content, embedding, similarity_threshold=0.9
            )
            
            if existing_memory_id:
                # Update existing memory instead of creating duplicate
                await self._update_existing_memory(
                    existing_memory_id, sanitized_content, importance_score, tags, context
                )
                return existing_memory_id
            
            # Create new memory
            with self.db_manager.get_db_context() as db:
                memory = LongTermMemory(
                    user_id=uuid.UUID(user_id),
                    conversation_id=uuid.UUID(conversation_id) if conversation_id else None,
                    content=sanitized_content,
                    memory_type=memory_type,
                    importance_score=min(max(importance_score, 0.0), 1.0),  # Clamp to [0, 1]
                    embedding=embedding,
                    tags=tags or [],
                    context=context or {},
                    source_summary=source_summary
                )
                
                db.add(memory)
                db.flush()
                
                memory_id = str(memory.id)
                
                # Track storage cost
                storage_bytes = len(sanitized_content.encode('utf-8')) + len(str(context or {}).encode('utf-8'))
                await self.safety_service.track_operation_cost(
                    user_id, 'storage', storage_bytes=storage_bytes
                )
                
                # Enforce memory limits
                await self._enforce_memory_limits(user_id, db)
                
                logger.info(f"Created memory {memory_id} for user {user_id} with importance {importance_score:.3f}")
                return memory_id
                
        except Exception as e:
            logger.error(f"Memory writing failed for user {user_id}: {e}")
            raise
    
    async def reflect_and_extract_memories(
        self,
        user_id: str,
        conversation_id: str,
        conversation_context: str,
        user_response: str
    ) -> List[str]:
        """
        Use AI reflection to extract novel, useful memories from conversation.
        
        Args:
            user_id: User identifier
            conversation_id: Conversation identifier
            conversation_context: Full conversation context
            user_response: Final assistant response
            
        Returns:
            List of created memory IDs
        """
        try:
            # Create reflection prompt
            reflection_prompt = f"""
            Analyze this conversation and my response to identify novel, useful information that should be remembered for future interactions with this user.

            Conversation Context:
            {conversation_context[-2000:]}  # Last 2000 chars

            My Response:
            {user_response[-1000:]}  # Last 1000 chars

            Extract 0-4 memories that are:
            1. Novel (not obvious common knowledge)
            2. Useful for future academic writing assistance
            3. Specific to this user's needs, preferences, or context
            4. Likely to be relevant in future conversations

            For each memory, provide:
            - memory_type: episodic, semantic, procedural, preference, or contextual
            - content: 1-2 sentences describing what to remember
            - importance: 0.1-1.0 based on likely future usefulness
            - tags: 2-3 relevant tags

            Respond in JSON format:
            {{
                "memories": [
                    {{
                        "memory_type": "preference",
                        "content": "User prefers Harvard citation style for business papers",
                        "importance": 0.8,
                        "tags": ["citation", "business", "preference"]
                    }}
                ]
            }}
            """
            
            # Check rate limits for reflection
            limits = await self.safety_service.check_user_limits(user_id)
            if not limits["within_daily_cost_limit"]:
                logger.warning(f"User {user_id} has exceeded daily cost limit, skipping reflection")
                return []
            
            # Get reflection from AI
            response = await self.openai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": reflection_prompt}],
                temperature=0.3,
                max_tokens=1000
            )
            
            reflection_response = response.choices[0].message.content.strip()
            
            # Track reflection cost
            input_tokens = len(reflection_prompt.split()) * 1.3
            output_tokens = len(reflection_response.split()) * 1.3
            await self.safety_service.track_operation_cost(
                user_id, 'reflection', 
                input_tokens=input_tokens, 
                output_tokens=output_tokens
            )
            
            # Parse response and extract memories
            import json
            try:
                reflection_data = json.loads(reflection_response)
                extracted_memories = reflection_data.get("memories", [])
            except json.JSONDecodeError:
                logger.warning(f"Failed to parse reflection response: {reflection_response}")
                extracted_memories = []
            
            # Store reflection record
            with self.db_manager.get_db_context() as db:
                reflection = MemoryReflection(
                    user_id=uuid.UUID(user_id),
                    conversation_id=uuid.UUID(conversation_id),
                    reflection_prompt=reflection_prompt,
                    reflection_response=reflection_response,
                    extracted_memories=extracted_memories,
                    confidence_score=len(extracted_memories) / 4.0  # Simple confidence based on count
                )
                db.add(reflection)
            
            # Create memories from reflection
            created_memory_ids = []
            for memory_data in extracted_memories:
                try:
                    memory_type = MemoryType(memory_data.get("memory_type", "semantic"))
                    memory_id = await self.write_memory(
                        user_id=user_id,
                        content=memory_data["content"],
                        memory_type=memory_type,
                        conversation_id=conversation_id,
                        importance_score=memory_data.get("importance", 0.5),
                        tags=memory_data.get("tags", []),
                        source_summary="AI reflection extraction"
                    )
                    created_memory_ids.append(memory_id)
                except Exception as e:
                    logger.warning(f"Failed to create reflected memory: {e}")
            
            logger.info(f"Reflection created {len(created_memory_ids)} memories for user {user_id}")
            return created_memory_ids
            
        except Exception as e:
            logger.error(f"Memory reflection failed for user {user_id}: {e}")
            return []
    
    async def maintain_memories(self, user_id: Optional[str] = None, batch_size: int = 1000):
        """
        Perform memory maintenance: decay importance, update access patterns, cleanup old memories.
        
        Args:
            user_id: Specific user to maintain (None for all users)
            batch_size: Number of memories to process per batch
        """
        try:
            with self.db_manager.get_db_context() as db:
                # Get memories to maintain
                base_query = db.query(LongTermMemory)
                if user_id:
                    base_query = base_query.filter(LongTermMemory.user_id == uuid.UUID(user_id))
                
                # Process in batches
                offset = 0
                updated_count = 0
                cleaned_count = 0
                
                while True:
                    memories = base_query.offset(offset).limit(batch_size).all()
                    if not memories:
                        break
                    
                    for memory in memories:
                        # Calculate time-based importance decay
                        days_since_accessed = (datetime.utcnow() - memory.last_accessed).days
                        if days_since_accessed > 7:  # Weekly decay
                            weeks_passed = days_since_accessed // 7
                            decay_factor = self.importance_decay_rate ** weeks_passed
                            new_importance = memory.importance_score * decay_factor
                            
                            # Apply access frequency boost
                            if memory.access_frequency > 0:
                                frequency_boost = min(1.1, 1 + (memory.access_frequency * 0.01))
                                new_importance *= frequency_boost
                            
                            memory.importance_score = max(new_importance, 0.01)  # Minimum threshold
                            updated_count += 1
                        
                        # Clean up very old, low-importance memories
                        if (memory.importance_score < 0.1 and 
                            (datetime.utcnow() - memory.created_at).days > 90):
                            db.delete(memory)
                            cleaned_count += 1
                    
                    offset += batch_size
                
                logger.info(f"Memory maintenance: updated {updated_count}, cleaned {cleaned_count} memories")
                
        except Exception as e:
            logger.error(f"Memory maintenance failed: {e}")
            raise
    
    async def get_memory_statistics(self, user_id: str) -> Dict[str, Any]:
        """Get memory statistics for a user."""
        try:
            with self.db_manager.get_db_context() as db:
                stats = db.query(
                    func.count(LongTermMemory.id).label("total_memories"),
                    func.avg(LongTermMemory.importance_score).label("avg_importance"),
                    func.max(LongTermMemory.importance_score).label("max_importance"),
                    func.sum(LongTermMemory.access_frequency).label("total_accesses")
                ).filter(LongTermMemory.user_id == uuid.UUID(user_id)).first()
                
                # Memory type distribution
                type_distribution = db.query(
                    LongTermMemory.memory_type,
                    func.count(LongTermMemory.id).label("count")
                ).filter(
                    LongTermMemory.user_id == uuid.UUID(user_id)
                ).group_by(LongTermMemory.memory_type).all()
                
                return {
                    "total_memories": stats.total_memories or 0,
                    "average_importance": float(stats.avg_importance or 0),
                    "max_importance": float(stats.max_importance or 0),
                    "total_accesses": stats.total_accesses or 0,
                    "type_distribution": {
                        mem_type.value: count for mem_type, count in type_distribution
                    }
                }
                
        except Exception as e:
            logger.error(f"Failed to get memory statistics for user {user_id}: {e}")
            return {}
    
    # Private helper methods
    
    async def _rerank_memories(
        self, 
        initial_results: List[Tuple[LongTermMemory, float]], 
        query: str, 
        conversation_id: Optional[str]
    ) -> List[Tuple[LongTermMemory, float]]:
        """Re-rank memories using advanced scoring."""
        try:
            scored_memories = []
            current_time = datetime.utcnow()
            
            for memory, similarity in initial_results:
                # Time-based recency score
                days_old = (current_time - memory.created_at).days
                recency_score = max(0.1, 1 / (1 + days_old * 0.01))
                
                # Access pattern score
                access_score = min(1.0, memory.access_frequency * 0.1)
                
                # Conversation context boost
                context_boost = 1.0
                if conversation_id and memory.conversation_id:
                    if str(memory.conversation_id) == conversation_id:
                        context_boost = 1.3  # Same conversation boost
                
                # Combined score
                final_score = (
                    0.4 * similarity +
                    0.3 * memory.importance_score +
                    0.15 * recency_score +
                    0.1 * access_score +
                    0.05 * context_boost
                )
                
                scored_memories.append((memory, final_score))
            
            # Sort by final score
            scored_memories.sort(key=lambda x: x[1], reverse=True)
            return scored_memories
            
        except Exception as e:
            logger.error(f"Memory re-ranking failed: {e}")
            return initial_results
    
    async def _calculate_importance_score(
        self, 
        content: str, 
        memory_type: MemoryType, 
        user_id: str, 
        conversation_id: Optional[str]
    ) -> float:
        """Calculate initial importance score for new memory."""
        try:
            base_score = 0.5  # Default baseline
            
            # Type-based scoring
            type_multipliers = {
                MemoryType.PREFERENCE: 0.8,     # High importance for user preferences
                MemoryType.PROCEDURAL: 0.7,     # Skills and processes are valuable
                MemoryType.SEMANTIC: 0.6,       # Facts and knowledge
                MemoryType.EPISODIC: 0.5,       # Specific experiences
                MemoryType.CONTEXTUAL: 0.4      # Context-dependent information
            }
            
            base_score *= type_multipliers.get(memory_type, 0.5)
            
            # Content length factor (longer = potentially more detailed/important)
            length_factor = min(1.2, 1 + len(content) / 1000)
            base_score *= length_factor
            
            # Novelty factor (check against existing memories)
            novelty_factor = await self._calculate_novelty_factor(user_id, content)
            base_score *= novelty_factor
            
            return min(max(base_score, 0.1), 1.0)  # Clamp to [0.1, 1.0]
            
        except Exception as e:
            logger.error(f"Importance calculation failed: {e}")
            return 0.5  # Default fallback
    
    async def _calculate_novelty_factor(self, user_id: str, content: str) -> float:
        """Calculate novelty factor by comparing to existing memories."""
        try:
            # Generate embedding for comparison
            content_embedding = await self.embedding_service.embed_text(content)
            
            with self.db_manager.get_db_context() as db:
                # Find most similar existing memory
                similar_memories = db.query(
                    LongTermMemory,
                    (1 - LongTermMemory.embedding.cosine_distance(content_embedding)).label("similarity")
                ).filter(
                    LongTermMemory.user_id == uuid.UUID(user_id),
                    LongTermMemory.embedding.is_not(None)
                ).order_by(
                    desc(1 - LongTermMemory.embedding.cosine_distance(content_embedding))
                ).limit(1).all()
                
                if not similar_memories:
                    return 1.2  # Very novel if no existing memories
                
                max_similarity = similar_memories[0][1]
                novelty_factor = 1.0 - (max_similarity * 0.5)  # Reduce based on similarity
                return max(novelty_factor, 0.3)  # Minimum novelty factor
                
        except Exception as e:
            logger.error(f"Novelty calculation failed: {e}")
            return 1.0
    
    async def _check_for_similar_memory(
        self, 
        user_id: str, 
        content: str, 
        embedding: List[float], 
        similarity_threshold: float = 0.9
    ) -> Optional[str]:
        """Check if similar memory already exists."""
        try:
            with self.db_manager.get_db_context() as db:
                similar_memory = db.query(
                    LongTermMemory,
                    (1 - LongTermMemory.embedding.cosine_distance(embedding)).label("similarity")
                ).filter(
                    LongTermMemory.user_id == uuid.UUID(user_id),
                    LongTermMemory.embedding.is_not(None),
                    (1 - LongTermMemory.embedding.cosine_distance(embedding)) >= similarity_threshold
                ).first()
                
                if similar_memory:
                    return str(similar_memory[0].id)
                return None
                
        except Exception as e:
            logger.error(f"Similar memory check failed: {e}")
            return None
    
    async def _update_existing_memory(
        self, 
        memory_id: str, 
        new_content: str, 
        importance_score: float,
        tags: Optional[List[str]], 
        context: Optional[Dict[str, Any]]
    ):
        """Update existing memory with new information."""
        try:
            with self.db_manager.get_db_context() as db:
                memory = db.query(LongTermMemory).filter(
                    LongTermMemory.id == uuid.UUID(memory_id)
                ).first()
                
                if memory:
                    # Merge content (keep both if different)
                    if memory.content.lower() != new_content.lower():
                        memory.content = f"{memory.content}\n\nUpdate: {new_content}"
                    
                    # Update importance (take maximum)
                    memory.importance_score = max(memory.importance_score, importance_score)
                    
                    # Merge tags
                    if tags:
                        existing_tags = set(memory.tags or [])
                        existing_tags.update(tags)
                        memory.tags = list(existing_tags)
                    
                    # Update context
                    if context:
                        memory.context = {**(memory.context or {}), **context}
                    
                    memory.updated_at = datetime.utcnow()
                    
                    logger.info(f"Updated existing memory {memory_id}")
                
        except Exception as e:
            logger.error(f"Memory update failed for {memory_id}: {e}")
    
    async def _log_memory_retrievals(
        self, 
        memories: List[LongTermMemory], 
        user_id: str, 
        conversation_id: Optional[str], 
        query: str
    ):
        """Log memory retrievals for analytics and importance updates."""
        try:
            with self.db_manager.get_db_context() as db:
                for rank, memory in enumerate(memories):
                    # Update memory access statistics
                    memory.access_frequency += 1
                    memory.last_accessed = datetime.utcnow()
                    
                    # Create retrieval log
                    retrieval = MemoryRetrieval(
                        memory_id=memory.id,
                        user_id=uuid.UUID(user_id),
                        conversation_id=uuid.UUID(conversation_id) if conversation_id else None,
                        query_context=query[:500],  # Truncate long queries
                        rank_position=rank
                    )
                    db.add(retrieval)
                
        except Exception as e:
            logger.error(f"Memory retrieval logging failed: {e}")
    
    async def _enforce_memory_limits(self, user_id: str, db: Session):
        """Enforce per-user memory limits by removing least important old memories."""
        try:
            # Count current memories
            memory_count = db.query(func.count(LongTermMemory.id)).filter(
                LongTermMemory.user_id == uuid.UUID(user_id)
            ).scalar()
            
            if memory_count > self.max_memories_per_user:
                # Remove excess memories (least important, oldest first)
                excess_count = memory_count - self.max_memories_per_user
                
                memories_to_remove = db.query(LongTermMemory).filter(
                    LongTermMemory.user_id == uuid.UUID(user_id)
                ).order_by(
                    LongTermMemory.importance_score.asc(),
                    LongTermMemory.created_at.asc()
                ).limit(excess_count).all()
                
                for memory in memories_to_remove:
                    db.delete(memory)
                
                logger.info(f"Removed {excess_count} old memories for user {user_id}")
                
        except Exception as e:
            logger.error(f"Memory limit enforcement failed for user {user_id}: {e}")


# Global service instance
_memory_integrator = None

def get_memory_integrator() -> MemoryIntegratorService:
    """Get or create memory integrator service instance."""
    global _memory_integrator
    if _memory_integrator is None:
        _memory_integrator = MemoryIntegratorService()
    return _memory_integrator
