"""Privacy Manager node for consent-aware vector segregation."""

import json
import time
import hashlib
from typing import Dict, Any, List
from langchain_core.runnables import RunnableConfig

from src.agent.base import BaseNode
from ...agent.handywriterz_state import HandyWriterzState


class PrivacyManagerNode(BaseNode):
    """Manages consent-aware private/public vector segregation."""
    
    def __init__(self):
        super().__init__("privacy_manager", timeout_seconds=30.0, max_retries=2)
    
    async def execute(self, state: HandyWriterzState, config: RunnableConfig) -> Dict[str, Any]:
        """Process content for privacy-aware vector storage."""
        try:
            current_draft = state.get("current_draft", "")
            user_params = state.get("user_params", {})
            user_id = state.get("user_id", "")
            sources = state.get("verified_sources", [])
            
            if not current_draft or not user_id:
                return {"privacy_processed": False}
            
            # Get user consent preferences
            consent_data = await self._get_user_consent(user_id)
            
            # Classify content for privacy
            content_classification = self._classify_content_privacy(current_draft, user_params)
            
            # Segregate vectors by privacy level
            vector_segregation = await self._segregate_vectors(
                current_draft, sources, content_classification, consent_data
            )
            
            # Create anonymized versions for public use
            anonymized_content = self._create_anonymized_content(
                current_draft, content_classification, consent_data
            )
            
            # Store vectors in appropriate databases
            storage_results = await self._store_segregated_vectors(
                vector_segregation, user_id, consent_data
            )
            
            self._broadcast_progress(state, "Privacy-aware vector segregation completed", 100.0)
            
            return {
                "privacy_processed": True,
                "consent_level": consent_data.get("level", "private"),
                "classification": content_classification,
                "vector_segregation": vector_segregation,
                "anonymized_content": anonymized_content,
                "storage_results": storage_results
            }
            
        except Exception as e:
            self.logger.error(f"Privacy management failed: {e}")
            raise
    
    async def _get_user_consent(self, user_id: str) -> Dict[str, Any]:
        """Retrieve user consent preferences."""
        # TODO(fill-secret): Implement database query for user consent
        # For now, return default private settings
        
        default_consent = {
            "user_id": user_id,
            "level": "private",  # "private", "anonymous", "public"
            "preferences": {
                "allow_public_vectors": False,
                "allow_anonymized_sharing": False,
                "allow_aggregate_analytics": True,
                "allow_model_improvement": False,
                "data_retention_days": 90
            },
            "sensitive_fields": ["personal_info", "academic_institution", "research_data"],
            "last_updated": time.time(),
            "consent_version": "1.0"
        }
        
        # In production:
        # consent_data = await database.get_user_consent(user_id)
        # return consent_data or default_consent
        
        self.logger.info(f"Retrieved consent for user {user_id}: {default_consent['level']}")
        return default_consent
    
    def _classify_content_privacy(self, content: str, user_params: Dict) -> Dict[str, Any]:
        """Classify content by privacy sensitivity."""
        classification = {
            "privacy_level": "private",  # private, sensitive, public
            "sensitive_elements": [],
            "personal_identifiers": [],
            "academic_identifiers": [],
            "shareable_elements": [],
            "risk_score": 0.0
        }
        
        # Check for personal identifiers
        personal_patterns = [
            r'\b[A-Z][a-z]+ [A-Z][a-z]+\b',  # Names
            r'\b\d{3}-\d{2}-\d{4}\b',        # SSN pattern
            r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',  # Email
            r'\b\d{3}-\d{3}-\d{4}\b',        # Phone numbers
        ]
        
        for pattern in personal_patterns:
            import re
            matches = re.findall(pattern, content)
            if matches:
                classification["personal_identifiers"].extend(matches)
                classification["risk_score"] += 0.3
        
        # Check for academic identifiers
        academic_patterns = [
            r'University of [A-Z][a-z]+',
            r'[A-Z][a-z]+ University',
            r'Professor [A-Z][a-z]+',
            r'Dr\. [A-Z][a-z]+',
            r'Department of [A-Z][a-z]+'
        ]
        
        for pattern in academic_patterns:
            matches = re.findall(pattern, content)
            if matches:
                classification["academic_identifiers"].extend(matches)
                classification["risk_score"] += 0.2
        
        # Check for sensitive field-specific content
        field = user_params.get("field", "general")
        sensitive_keywords = self._get_sensitive_keywords_by_field(field)
        
        content_lower = content.lower()
        for keyword in sensitive_keywords:
            if keyword in content_lower:
                classification["sensitive_elements"].append(keyword)
                classification["risk_score"] += 0.1
        
        # Determine overall privacy level
        if classification["risk_score"] > 0.5:
            classification["privacy_level"] = "sensitive"
        elif classification["risk_score"] > 0.2:
            classification["privacy_level"] = "private"
        elif len(classification["personal_identifiers"]) == 0 and len(classification["academic_identifiers"]) == 0:
            classification["privacy_level"] = "public"
        
        # Identify shareable elements (non-sensitive academic content)
        classification["shareable_elements"] = self._extract_shareable_elements(content, classification)
        
        return classification
    
    def _get_sensitive_keywords_by_field(self, field: str) -> List[str]:
        """Get field-specific sensitive keywords."""
        sensitive_keywords = {
            "nursing": [
                "patient", "medical record", "diagnosis", "treatment plan",
                "hipaa", "confidential", "private health"
            ],
            "medicine": [
                "patient data", "clinical trial", "medical history", "diagnosis",
                "treatment outcome", "case study", "medical record"
            ],
            "law": [
                "client", "confidential", "privileged", "case details",
                "legal strategy", "settlement", "attorney-client"
            ],
            "social_work": [
                "client information", "case file", "family details",
                "intervention plan", "confidential session"
            ],
            "psychology": [
                "patient session", "therapy notes", "psychological assessment",
                "confidential", "case study", "treatment plan"
            ]
        }
        
        return sensitive_keywords.get(field.lower(), [])
    
    def _extract_shareable_elements(self, content: str, classification: Dict) -> List[Dict[str, Any]]:
        """Extract elements that can be shared based on classification."""
        shareable = []
        
        # Split content into sentences
        sentences = [s.strip() for s in content.split('.') if s.strip()]
        
        for sentence in sentences:
            # Check if sentence contains sensitive elements
            is_safe = True
            
            for identifier in classification.get("personal_identifiers", []):
                if identifier in sentence:
                    is_safe = False
                    break
            
            for identifier in classification.get("academic_identifiers", []):
                if identifier in sentence:
                    is_safe = False
                    break
            
            # Check for sensitive keywords
            sentence_lower = sentence.lower()
            for sensitive in classification.get("sensitive_elements", []):
                if sensitive in sentence_lower:
                    is_safe = False
                    break
            
            if is_safe and len(sentence.split()) > 5:  # Meaningful sentences only
                shareable.append({
                    "text": sentence + ".",
                    "type": "academic_content",
                    "confidence": 0.8
                })
        
        return shareable
    
    async def _segregate_vectors(self, content: str, sources: List[Dict], 
                                classification: Dict, consent: Dict) -> Dict[str, Any]:
        """Segregate content into appropriate vector databases."""
        segregation = {
            "private_vectors": [],
            "anonymized_vectors": [],
            "public_vectors": [],
            "aggregate_vectors": []
        }
        
        privacy_level = classification.get("privacy_level", "private")
        consent_level = consent.get("level", "private")
        
        # Always store in private database
        segregation["private_vectors"] = await self._create_private_vectors(content, sources)
        
        # Store anonymized vectors if consent allows
        if consent.get("preferences", {}).get("allow_anonymized_sharing", False):
            anonymized_content = self._anonymize_content(content, classification)
            segregation["anonymized_vectors"] = await self._create_anonymized_vectors(
                anonymized_content, sources
            )
        
        # Store public vectors if content is suitable and consent allows
        if (privacy_level == "public" and 
            consent.get("preferences", {}).get("allow_public_vectors", False)):
            shareable_elements = classification.get("shareable_elements", [])
            if shareable_elements:
                segregation["public_vectors"] = await self._create_public_vectors(
                    shareable_elements, sources
                )
        
        # Create aggregate vectors for analytics if consent allows
        if consent.get("preferences", {}).get("allow_aggregate_analytics", True):
            segregation["aggregate_vectors"] = await self._create_aggregate_vectors(
                content, classification, consent
            )
        
        return segregation
    
    async def _create_private_vectors(self, content: str, sources: List[Dict]) -> List[Dict[str, Any]]:
        """Create vectors for private storage."""
        # TODO(fill-secret): Implement actual vector creation with embeddings
        
        chunks = self._chunk_content(content)
        vectors = []
        
        for i, chunk in enumerate(chunks):
            vector_data = {
                "id": f"private_vector_{i}",
                "content": chunk,
                "embedding": None,  # Would be actual embedding vector
                "metadata": {
                    "type": "private",
                    "chunk_index": i,
                    "source_count": len(sources),
                    "timestamp": time.time()
                },
                "privacy_level": "private",
                "access_control": "user_only"
            }
            vectors.append(vector_data)
        
        return vectors
    
    async def _create_anonymized_vectors(self, anonymized_content: str, sources: List[Dict]) -> List[Dict[str, Any]]:
        """Create anonymized vectors for research use."""
        chunks = self._chunk_content(anonymized_content)
        vectors = []
        
        for i, chunk in enumerate(chunks):
            vector_data = {
                "id": f"anon_vector_{i}",
                "content": chunk,
                "embedding": None,  # Would be actual embedding vector
                "metadata": {
                    "type": "anonymized",
                    "chunk_index": i,
                    "anonymization_level": "high",
                    "timestamp": time.time()
                },
                "privacy_level": "anonymized",
                "access_control": "research_only"
            }
            vectors.append(vector_data)
        
        return vectors
    
    async def _create_public_vectors(self, shareable_elements: List[Dict], sources: List[Dict]) -> List[Dict[str, Any]]:
        """Create public vectors from shareable content."""
        vectors = []
        
        for i, element in enumerate(shareable_elements):
            vector_data = {
                "id": f"public_vector_{i}",
                "content": element.get("text", ""),
                "embedding": None,  # Would be actual embedding vector
                "metadata": {
                    "type": "public",
                    "element_type": element.get("type", "academic_content"),
                    "confidence": element.get("confidence", 0.8),
                    "timestamp": time.time()
                },
                "privacy_level": "public",
                "access_control": "public_research"
            }
            vectors.append(vector_data)
        
        return vectors
    
    async def _create_aggregate_vectors(self, content: str, classification: Dict, consent: Dict) -> List[Dict[str, Any]]:
        """Create aggregate vectors for analytics."""
        # Create aggregated, statistical representations
        aggregate_data = {
            "field": consent.get("field", "general"),
            "privacy_score": classification.get("risk_score", 0.0),
            "content_length": len(content.split()),
            "writing_metrics": self._extract_writing_metrics(content),
            "timestamp": time.time()
        }
        
        return [{
            "id": f"aggregate_vector_{hashlib.md5(str(time.time()).encode()).hexdigest()[:8]}",
            "content": json.dumps(aggregate_data),
            "embedding": None,  # Would be actual embedding vector
            "metadata": {
                "type": "aggregate",
                "anonymized": True,
                "statistical_only": True
            },
            "privacy_level": "aggregate",
            "access_control": "analytics_only"
        }]
    
    def _chunk_content(self, content: str, chunk_size: int = 500) -> List[str]:
        """Split content into chunks for vector creation."""
        words = content.split()
        chunks = []
        
        for i in range(0, len(words), chunk_size):
            chunk = " ".join(words[i:i + chunk_size])
            chunks.append(chunk)
        
        return chunks
    
    def _anonymize_content(self, content: str, classification: Dict) -> str:
        """Create anonymized version of content using Presidio."""
        from presidio_analyzer import AnalyzerEngine
        from presidio_anonymizer import AnonymizerEngine
        from presidio_anonymizer.entities import OperatorConfig

        analyzer = AnalyzerEngine()
        anonymizer = AnonymizerEngine()

        # Analyze the text for PII entities
        analyzer_results = analyzer.analyze(text=content, language="en")

        # Anonymize the text
        anonymized_result = anonymizer.anonymize(
            text=content,
            analyzer_results=analyzer_results,
            operators={"DEFAULT": OperatorConfig("replace", {"new_value": "[REDACTED]"})}
        )
        
        return anonymized_result.text
    
    def _create_anonymized_content(self, content: str, classification: Dict, consent: Dict) -> Dict[str, Any]:
        """Create anonymized content for sharing."""
        if not consent.get("preferences", {}).get("allow_anonymized_sharing", False):
            return {"content": None, "reason": "User consent not provided"}
        
        anonymized_text = self._anonymize_content(content, classification)
        
        return {
            "content": anonymized_text,
            "anonymization_level": "high",
            "original_length": len(content),
            "anonymized_length": len(anonymized_text),
            "redactions_count": len(classification.get("personal_identifiers", [])) + 
                              len(classification.get("academic_identifiers", [])),
            "created_at": time.time()
        }
    
    def _extract_writing_metrics(self, content: str) -> Dict[str, Any]:
        """Extract writing metrics for aggregate analytics."""
        words = content.split()
        sentences = [s for s in content.split('.') if s.strip()]
        
        return {
            "word_count": len(words),
            "sentence_count": len(sentences),
            "avg_sentence_length": len(words) / max(len(sentences), 1),
            "paragraph_count": len([p for p in content.split('\n\n') if p.strip()]),
            "complexity_score": self._calculate_complexity_score(content)
        }
    
    def _calculate_complexity_score(self, content: str) -> float:
        """Calculate a simple complexity score for analytics."""
        words = content.split()
        long_words = [w for w in words if len(w) > 6]
        
        if not words:
            return 0.0
        
        complexity = len(long_words) / len(words)
        return min(1.0, complexity * 2)  # Normalize to 0-1 range
    
    async def _store_segregated_vectors(self, segregation: Dict, user_id: str, consent: Dict) -> Dict[str, Any]:
        """Store vectors in appropriate databases based on privacy level."""
        results = {
            "private_stored": 0,
            "anonymized_stored": 0,
            "public_stored": 0,
            "aggregate_stored": 0,
            "storage_locations": {}
        }
        
        # Store private vectors
        private_vectors = segregation.get("private_vectors", [])
        if private_vectors:
            # TODO(fill-secret): Store in private vector database
            results["private_stored"] = len(private_vectors)
            results["storage_locations"]["private"] = f"private_db:{user_id}"
            self.logger.info(f"Stored {len(private_vectors)} private vectors for user {user_id}")
        
        # Store anonymized vectors
        anon_vectors = segregation.get("anonymized_vectors", [])
        if anon_vectors and consent.get("preferences", {}).get("allow_anonymized_sharing"):
            # TODO(fill-secret): Store in anonymized vector database
            results["anonymized_stored"] = len(anon_vectors)
            results["storage_locations"]["anonymized"] = "anonymized_research_db"
            self.logger.info(f"Stored {len(anon_vectors)} anonymized vectors")
        
        # Store public vectors
        public_vectors = segregation.get("public_vectors", [])
        if public_vectors and consent.get("preferences", {}).get("allow_public_vectors"):
            # TODO(fill-secret): Store in public vector database
            results["public_stored"] = len(public_vectors)
            results["storage_locations"]["public"] = "public_research_db"
            self.logger.info(f"Stored {len(public_vectors)} public vectors")
        
        # Store aggregate vectors
        agg_vectors = segregation.get("aggregate_vectors", [])
        if agg_vectors and consent.get("preferences", {}).get("allow_aggregate_analytics"):
            # TODO(fill-secret): Store in analytics database
            results["aggregate_stored"] = len(agg_vectors)
            results["storage_locations"]["aggregate"] = "analytics_db"
            self.logger.info(f"Stored {len(agg_vectors)} aggregate vectors")
        
        return results