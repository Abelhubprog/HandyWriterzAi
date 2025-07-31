"""Source Filter node for evidence validation and hover card data storage."""

import json
import time
import redis.asyncio as redis
from typing import Dict, Any, List, Optional
from datetime import datetime

from ..base import BaseNode, NodeError
from ..handywriterz_state import HandyWriterzState


class SourceFilterNode(BaseNode):
    """Production-ready source filter with advanced evidence validation and storage."""

    def __init__(self):
        super().__init__("source_filter", timeout_seconds=60.0, max_retries=3)

        # Advanced filtering configuration
        self.min_credibility_threshold = 0.65
        self.max_sources_per_request = 25
        self.evidence_quality_threshold = 0.70
        self.academic_boost_factor = 1.2

        # Redis connection for evidence storage
        self.redis_client = None
        self._initialize_redis_connection()

        # Academic domain indicators
        self.academic_domains = {
            '.edu', '.ac.uk', '.gov', 'pubmed', 'jstor', 'springer',
            'wiley', 'elsevier', 'nature', 'science', 'ncbi', 'nih',
            'ieee', 'acm', 'scholar.google', 'researchgate'
        }

        # Field-specific credibility mappings
        self.field_credibility_sources = {
            "nursing": ["nursingworld.org", "aacnnursing.org", "cochrane.org", "pubmed"],
            "law": ["westlaw", "lexisnexis", "justia", "law.com", "supremecourt.gov"],
            "medicine": ["medscape", "uptodate", "bmj", "nejm", "pubmed", "cochrane"],
            "social_work": ["nasw.org", "cswe.org", "socialworkers.org"],
            "psychology": ["apa.org", "pubmed", "psycnet.apa.org"],
            "business": ["harvard.edu", "wharton.upenn.edu", "gsb.stanford.edu"]
        }

    def _initialize_redis_connection(self):
        """Initialize Redis connection for evidence storage."""
        try:
            import os
            redis_url = os.getenv("REDIS_URL", "redis://localhost:6379")
            self.redis_client = redis.from_url(redis_url, decode_responses=True)
            self.logger.info("Redis connection initialized for evidence storage")
        except Exception as e:
            self.logger.warning(f"Redis initialization failed: {e}. Using fallback storage.")
            self.redis_client = None

    async def execute(self, state: HandyWriterzState, config: Dict[str, Any] | None = None) -> Dict[str, Any]:
        """Filter sources with advanced validation and evidence mapping."""
        start_time = time.time()

        try:
            self.logger.info("🔍 Source Filter: Starting advanced source validation")
            self._broadcast_progress(state, "Analyzing source quality and credibility", 5)

            # Get all search results from different agents
            raw_search_results = state.get("raw_search_results", [])
            user_params = state.get("user_params", {})

            if not raw_search_results:
                self.logger.warning("No search results found for filtering")
                return {
                    "filtered_sources": [],
                    "evidence_map": {},
                    "source_count": 0,
                    "filtering_metadata": {
                        "duration": time.time() - start_time,
                        "warning": "No sources to filter"
                    }
                }

            self.logger.info(f"Processing {len(raw_search_results)} sources for filtering")

            # Phase 1: Advanced source filtering
            filtered_sources = await self._advanced_source_filtering(raw_search_results, user_params)
            self._broadcast_progress(state, "Source credibility analysis completed", 35)

            # Phase 2: Evidence extraction and validation
            evidence_enhanced_sources = await self._extract_and_validate_evidence(filtered_sources)
            self._broadcast_progress(state, "Evidence extraction completed", 60)

            # Phase 3: Quality scoring and ranking
            quality_ranked_sources = await self._quality_scoring_and_ranking(evidence_enhanced_sources, user_params)
            self._broadcast_progress(state, "Quality scoring completed", 75)

            # Phase 4: Evidence mapping for hover cards
            evidence_map = await self._create_advanced_evidence_map(quality_ranked_sources)
            self._broadcast_progress(state, "Evidence mapping completed", 90)

            # Phase 5: Persistent storage
            await self._store_evidence_data_advanced(evidence_map, state.get("user_id", ""))
            self._broadcast_progress(state, "Evidence data stored", 95)

            # Compile results
            filtering_metadata = {
                "total_input_sources": len(raw_search_results),
                "filtered_source_count": len(quality_ranked_sources),
                "evidence_points": sum(len(src.get("evidence_paragraphs", [])) for src in quality_ranked_sources),
                "average_credibility": sum(src.get("credibility_score", 0) for src in quality_ranked_sources) / len(quality_ranked_sources) if quality_ranked_sources else 0,
                "filtering_duration": time.time() - start_time,
                "quality_threshold_used": self.min_credibility_threshold
            }

            self._broadcast_progress(state, f"🔍 Filtered {len(quality_ranked_sources)} high-quality sources", 100)

            self.logger.info(f"Source filtering completed in {time.time() - start_time:.2f}s")

            return {
                "filtered_sources": quality_ranked_sources,
                "evidence_map": evidence_map,
                "source_count": len(quality_ranked_sources),
                "filtering_metadata": filtering_metadata
            }

        except Exception as e:
            self.logger.error(f"Source filtering failed: {e}")
            # Emit a standard error progress message without unsupported kwarg
            self._broadcast_progress(state, f"Source filtering error: {str(e)}")
            raise NodeError(f"Source filtering execution failed: {e}", self.name)
        finally:
            # Ensure state is updated even if errors occur
            try:
                state["filtered_sources"] = quality_ranked_sources
                state["evidence_map"] = evidence_map
            except Exception:
                pass

    async def _advanced_source_filtering(self, raw_search_results: List[Dict], parameters: Dict) -> List[Dict]:
        """Filter sources based on credibility and relevance."""
        field = parameters.get("field", "general")
        citation_style = parameters.get("citation_style", "harvard")
        word_count = parameters.get("word_count", 2000)

        # Calculate required source count based on word count
        min_sources = max(5, word_count // 400)  # 1 source per ~400 words minimum
        max_sources = min(20, word_count // 200)  # 1 source per ~200 words maximum

        filtered = []

        for source in raw_search_results:
            # Skip if missing essential data
            if not source.get("url") or not source.get("title"):
                continue

            # Calculate credibility score
            credibility_score = self._calculate_credibility(source, field)

            # Skip low-credibility sources
            if credibility_score < 0.6:
                continue

            # Extract key evidence paragraphs
            evidence_paragraphs = self._extract_evidence_paragraphs(source)

            # Enhance source with metadata
            enhanced_source = {
                **source,
                "credibility_score": credibility_score,
                "evidence_paragraphs": evidence_paragraphs,
                "citation_format": self._format_citation(source, citation_style),
                "field_relevance": self._assess_field_relevance(source, field),
                "timestamp": time.time()
            }

            filtered.append(enhanced_source)

        # Sort by credibility and relevance
        filtered.sort(key=lambda x: (x["credibility_score"] + x["field_relevance"]) / 2, reverse=True)

        # Return optimal number of sources
        return filtered[:max_sources]

    def _calculate_credibility(self, source: Dict, field: str) -> float:
        """Calculate source credibility score (0-1)."""
        url = source.get("url", "").lower()
        domain = url.split("//")[-1].split("/")[0] if "//" in url else ""

        # Academic and institutional domains
        academic_indicators = [
            ".edu", ".ac.uk", ".gov", "pubmed", "jstor", "springer",
            "wiley", "elsevier", "nature", "science", "ncbi", "nih"
        ]

        # Field-specific credible sources
        field_sources = {
            "nursing": ["nursingworld.org", "aacnnursing.org", "cochrane.org"],
            "law": ["westlaw", "lexisnexis", "justia", "law.com"],
            "medicine": ["medscape", "uptodate", "bmj", "nejm"],
            "social_work": ["nasw.org", "cswe.org", "socialworkers.org"]
        }

        score = 0.5  # Base score

        # Academic domain bonus
        if any(indicator in domain for indicator in academic_indicators):
            score += 0.3

        # Field-specific bonus
        field_domains = field_sources.get(field, [])
        if any(domain_name in domain for domain_name in field_domains):
            score += 0.2

        # Publication date penalty (older sources lose credibility)
        pub_date = source.get("published_date", "")
        if pub_date:
            try:
                # Simple year extraction and age penalty
                year = int(pub_date[:4]) if len(pub_date) >= 4 else 2020
                current_year = 2024
                age = current_year - year
                if age > 5:
                    score -= min(0.2, age * 0.02)
            except:
                pass

        # Content quality indicators
        content = source.get("content", "") + source.get("snippet", "")
        if "peer-reviewed" in content.lower():
            score += 0.1
        if "doi:" in content.lower():
            score += 0.1

        return min(1.0, max(0.0, score))

    def _extract_evidence_paragraphs(self, source: Dict) -> List[Dict]:
        """Extract key evidence paragraphs from source content."""
        content = source.get("content", "") or source.get("snippet", "")
        if not content:
            return []

        # Split into paragraphs
        paragraphs = [p.strip() for p in content.split('\n\n') if p.strip()]

        evidence_paragraphs = []
        for i, paragraph in enumerate(paragraphs[:5]):  # Limit to first 5 paragraphs
            # Score paragraph relevance
            relevance_score = self._score_paragraph_relevance(paragraph)

            if relevance_score > 0.6:  # Only include relevant paragraphs
                evidence_paragraphs.append({
                    "text": paragraph,
                    "position": i,
                    "relevance_score": relevance_score,
                    "key_phrases": self._extract_key_phrases(paragraph)
                })

        return evidence_paragraphs

    def _score_paragraph_relevance(self, paragraph: str) -> float:
        """Score paragraph relevance for academic writing."""
        paragraph_lower = paragraph.lower()

        # Evidence indicators
        evidence_indicators = [
            "research shows", "study found", "evidence suggests", "findings indicate",
            "data reveals", "analysis demonstrates", "according to", "statistics show"
        ]

        # Academic language indicators
        academic_indicators = [
            "furthermore", "however", "therefore", "consequently", "moreover",
            "empirical", "methodology", "systematic", "significant"
        ]

        score = 0.3  # Base score

        # Evidence presence
        evidence_count = sum(1 for indicator in evidence_indicators
                           if indicator in paragraph_lower)
        score += min(0.4, evidence_count * 0.1)

        # Academic language
        academic_count = sum(1 for indicator in academic_indicators
                           if indicator in paragraph_lower)
        score += min(0.3, academic_count * 0.05)

        # Length penalty for very short paragraphs
        if len(paragraph.split()) < 20:
            score -= 0.2

        return min(1.0, max(0.0, score))

    def _extract_key_phrases(self, paragraph: str) -> List[str]:
        """Extract key phrases for hover card display."""
        # Simple key phrase extraction
        words = paragraph.lower().split()
        phrases = []

        # Look for common academic phrases
        academic_phrases = [
            "research shows", "study found", "evidence suggests", "data indicates",
            "analysis reveals", "findings demonstrate", "according to research"
        ]

        for phrase in academic_phrases:
            if phrase in paragraph.lower():
                phrases.append(phrase)

        return phrases[:3]  # Limit to 3 key phrases

    def _assess_field_relevance(self, source: Dict, field: str) -> float:
        """Assess how relevant source is to specified field."""
        content = (source.get("content", "") + " " +
                  source.get("title", "") + " " +
                  source.get("snippet", "")).lower()

        field_keywords = {
            "nursing": ["patient", "healthcare", "clinical", "nursing", "medical", "treatment"],
            "law": ["legal", "court", "statute", "regulation", "judicial", "litigation"],
            "medicine": ["medical", "clinical", "patient", "diagnosis", "treatment", "therapeutic"],
            "social_work": ["social", "community", "intervention", "client", "welfare", "support"],
            "business": ["business", "management", "corporate", "financial", "market", "strategy"],
            "education": ["education", "learning", "student", "teaching", "academic", "curriculum"]
        }

        keywords = field_keywords.get(field, ["academic", "research", "study"])

        relevance_score = 0.0
        for keyword in keywords:
            if keyword in content:
                relevance_score += 0.15

        return min(1.0, relevance_score)

    def _format_citation(self, source: Dict, style: str) -> str:
        """Format citation in specified style."""
        title = source.get("title", "Untitled")
        url = source.get("url", "")
        date = source.get("published_date", "")
        author = source.get("author", "Unknown Author")

        if style.lower() == "harvard":
            return f"{author} ({date[:4] if date else 'n.d.'}). {title}. Retrieved from {url}"
        elif style.lower() == "apa":
            return f"{author} ({date[:4] if date else 'n.d.'}). {title}. Retrieved from {url}"
        elif style.lower() == "mla":
            return f"{author}. \"{title}.\" Web. {date if date else 'n.d.'} <{url}>."
        else:  # Chicago
            return f"{author}. \"{title}.\" Accessed {date if date else 'n.d.'}. {url}."

    def _create_evidence_map(self, filtered_sources: List[Dict]) -> Dict[str, Any]:
        """Create evidence mapping for hover cards."""
        evidence_map = {}

        for i, source in enumerate(filtered_sources):
            source_id = f"source_{i}"

            # Store evidence data for each source, including the paragraph
            evidence_map[source_id] = {
                "source_info": {
                    "title": source.get("title", ""),
                    "url": source.get("url", ""),
                    "author": source.get("author", "Unknown Author"),
                    "date": source.get("published_date", ""),
                    "credibility_score": source.get("credibility_score", 0.0)
                },
                "evidence_paragraphs": [
                    {
                        "paragraph": p.get("text", ""),
                        "evidence": p.get("text", "") # Storing the full paragraph as evidence for now
                    }
                    for p in source.get("evidence_paragraphs", [])
                ],
                "citation": source.get("citation_format", ""),
                "key_points": self._extract_key_points(source)
            }

        return evidence_map

    def _extract_key_points(self, source: Dict) -> List[str]:
        """Extract key points for hover card summary."""
        evidence_paragraphs = source.get("evidence_paragraphs", [])
        key_points = []

        for paragraph in evidence_paragraphs[:3]:  # Top 3 paragraphs
            text = paragraph.get("text", "")
            # Extract first sentence as key point
            sentences = text.split(". ")
            if sentences and len(sentences[0]) > 20:
                key_points.append(sentences[0] + ".")

        return key_points

    async def _extract_and_validate_evidence(self, filtered_sources: List[Dict]) -> List[Dict]:
        """Extract and validate evidence from filtered sources."""
        enhanced_sources = []

        for source in filtered_sources:
            try:
                # Enhanced evidence extraction
                evidence_data = await self._advanced_evidence_extraction(source)

                # Validate evidence quality
                if evidence_data and evidence_data.get("quality_score", 0) >= self.evidence_quality_threshold:
                    source.update({
                        "evidence_paragraphs": evidence_data.get("paragraphs", []),
                        "evidence_quality_score": evidence_data.get("quality_score", 0),
                        "key_insights": evidence_data.get("insights", []),
                        "evidence_timestamp": datetime.utcnow().isoformat()
                    })
                    enhanced_sources.append(source)

            except Exception as e:
                self.logger.warning(f"Evidence extraction failed for source: {e}")
                continue

        return enhanced_sources

    async def _advanced_evidence_extraction(self, source: Dict) -> Optional[Dict]:
        """Advanced evidence extraction with quality validation."""
        content = source.get("content", "") or source.get("snippet", "") or source.get("abstract", "")
        if not content:
            return None

        # Split into meaningful segments
        segments = self._smart_text_segmentation(content)

        evidence_paragraphs = []
        insights = []

        for i, segment in enumerate(segments[:7]):  # Process up to 7 segments
            # Enhanced relevance scoring
            relevance_score = self._advanced_paragraph_scoring(segment)

            if relevance_score > 0.65:  # Higher threshold for quality
                paragraph_data = {
                    "text": segment,
                    "position": i,
                    "relevance_score": relevance_score,
                    "key_phrases": self._extract_advanced_key_phrases(segment),
                    "evidence_type": self._classify_evidence_type(segment),
                    "academic_indicators": self._identify_academic_indicators(segment)
                }
                evidence_paragraphs.append(paragraph_data)

                # Extract insights
                segment_insights = self._extract_insights(segment)
                insights.extend(segment_insights)

        # Calculate overall quality score
        quality_score = self._calculate_evidence_quality(evidence_paragraphs, insights)

        return {
            "paragraphs": evidence_paragraphs,
            "insights": insights[:5],  # Top 5 insights
            "quality_score": quality_score
        }

    async def _quality_scoring_and_ranking(self, evidence_enhanced_sources: List[Dict], user_params: Dict) -> List[Dict]:
        """Advanced quality scoring and ranking of sources."""
        scored_sources = []

        for source in evidence_enhanced_sources:
            # Calculate comprehensive quality score
            quality_metrics = await self._calculate_comprehensive_quality(source, user_params)

            # Add quality metrics to source
            source.update({
                "comprehensive_quality_score": quality_metrics["overall_score"],
                "quality_breakdown": quality_metrics["breakdown"],
                "ranking_factors": quality_metrics["factors"],
                "academic_alignment": quality_metrics["academic_alignment"]
            })

            scored_sources.append(source)

        # Sort by comprehensive quality score
        scored_sources.sort(
            key=lambda x: x.get("comprehensive_quality_score", 0),
            reverse=True
        )

        # Limit to maximum sources
        return scored_sources[:self.max_sources_per_request]

    async def _create_advanced_evidence_map(self, quality_ranked_sources: List[Dict]) -> Dict[str, Any]:
        """Create advanced evidence mapping for hover cards."""
        evidence_map = {}

        for i, source in enumerate(quality_ranked_sources):
            source_id = f"source_{i+1}"

            # Comprehensive evidence mapping
            evidence_map[source_id] = {
                "source_metadata": {
                    "title": source.get("title", ""),
                    "url": source.get("url", ""),
                    "authors": source.get("authors", []),
                    "publication_date": source.get("publication_date", ""),
                    "source_type": source.get("source_type", "unknown"),
                    "doi": source.get("doi", ""),
                    "citation_count": source.get("citation_count", 0)
                },
                "quality_metrics": {
                    "credibility_score": source.get("credibility_score", 0),
                    "relevance_score": source.get("relevance_score", 0),
                    "evidence_quality_score": source.get("evidence_quality_score", 0),
                    "comprehensive_quality_score": source.get("comprehensive_quality_score", 0),
                    "academic_alignment": source.get("academic_alignment", 0)
                },
                "evidence_content": {
                    "evidence_paragraphs": source.get("evidence_paragraphs", []),
                    "key_insights": source.get("key_insights", []),
                    "key_quotes": self._extract_key_quotes(source),
                    "statistical_data": self._extract_statistical_data(source)
                },
                "citation_data": {
                    "citation_formats": source.get("citation_format", {}),
                    "recommended_use": self._determine_advanced_recommended_use(source),
                    "citation_context": self._generate_citation_context(source)
                },
                "hover_card_data": {
                    "summary": self._generate_hover_summary(source),
                    "key_points": self._extract_advanced_key_points(source),
                    "credibility_indicators": self._extract_credibility_indicators(source),
                    "usage_recommendations": self._generate_usage_recommendations(source)
                }
            }

        return evidence_map

    async def _store_evidence_data_advanced(self, evidence_map: Dict, user_id: str):
        """Store evidence data with advanced persistence."""
        try:
            timestamp = int(time.time())
            evidence_key = f"evidence_map:{user_id}:{timestamp}"

            if self.redis_client:
                # Store in Redis with 2-hour TTL
                await self.redis_client.setex(
                    evidence_key,
                    7200,  # 2 hours
                    json.dumps(evidence_map, indent=2)
                )

                # Also store metadata for retrieval
                metadata_key = f"evidence_metadata:{user_id}"
                metadata = {
                    "latest_key": evidence_key,
                    "timestamp": timestamp,
                    "source_count": len(evidence_map),
                    "created_at": datetime.utcnow().isoformat()
                }

                await self.redis_client.setex(
                    metadata_key,
                    7200,
                    json.dumps(metadata)
                )

                self.logger.info(f"Evidence data stored in Redis: {evidence_key}")
            else:
                # Fallback: log comprehensive evidence data
                self.logger.info(
                    f"Evidence storage (fallback): {len(evidence_map)} sources "
                    f"for user {user_id} at {timestamp}"
                )

        except Exception as e:
            self.logger.error(f"Failed to store evidence data: {e}")

    # Advanced helper methods for enhanced source filtering

    def _smart_text_segmentation(self, content: str) -> List[str]:
        """Smart text segmentation for better evidence extraction."""
        # Split by double newlines first
        paragraphs = content.split('\n\n')

        segments = []
        for para in paragraphs:
            para = para.strip()
            if len(para) > 50:  # Minimum meaningful length
                # Further split long paragraphs by sentences
                sentences = para.split('. ')
                if len(sentences) > 3:
                    # Group sentences into meaningful segments
                    current_segment = []
                    for sentence in sentences:
                        current_segment.append(sentence)
                        if len(' '.join(current_segment)) > 200:  # Optimal segment length
                            segments.append('. '.join(current_segment) + '.')
                            current_segment = []

                    if current_segment:
                        segments.append('. '.join(current_segment))
                else:
                    segments.append(para)

        return segments[:10]  # Limit segments

    def _advanced_paragraph_scoring(self, paragraph: str) -> float:
        """Advanced paragraph relevance scoring."""
        paragraph_lower = paragraph.lower()
        score = 0.3  # Base score

        # Evidence strength indicators
        strong_evidence = [
            "study found", "research shows", "data indicates", "evidence suggests",
            "analysis reveals", "findings demonstrate", "results show", "statistics indicate",
            "peer-reviewed", "systematic review", "meta-analysis", "clinical trial"
        ]

        # Academic language indicators
        academic_language = [
            "furthermore", "however", "therefore", "consequently", "moreover",
            "empirical", "methodology", "systematic", "significant", "correlation",
            "hypothesis", "theoretical", "framework", "analysis", "investigation"
        ]

        # Score based on evidence strength
        strong_count = sum(1 for indicator in strong_evidence if indicator in paragraph_lower)
        score += min(0.4, strong_count * 0.1)

        # Score based on academic language
        academic_count = sum(1 for indicator in academic_language if indicator in paragraph_lower)
        score += min(0.2, academic_count * 0.03)

        # Penalty for very short paragraphs
        word_count = len(paragraph.split())
        if word_count < 15:
            score -= 0.3
        elif word_count < 30:
            score -= 0.1

        # Bonus for optimal length
        if 50 <= word_count <= 150:
            score += 0.1

        return min(1.0, max(0.0, score))

    def _extract_advanced_key_phrases(self, paragraph: str) -> List[str]:
        """Extract advanced key phrases for academic content."""

        phrases = []
        paragraph_lower = paragraph.lower()

        # Academic methodology phrases
        methodology_phrases = [
            "systematic review", "meta-analysis", "randomized controlled trial",
            "longitudinal study", "cross-sectional study", "case study",
            "qualitative analysis", "quantitative analysis", "mixed methods"
        ]

        # Check for all phrase types
        for phrase in methodology_phrases:
            if phrase in paragraph_lower:
                phrases.append(phrase)

        return phrases[:5]  # Limit to top 5

    def _classify_evidence_type(self, paragraph: str) -> str:
        """Classify the type of evidence in the paragraph."""
        paragraph_lower = paragraph.lower()

        if any(term in paragraph_lower for term in ["meta-analysis", "systematic review"]):
            return "systematic_review"
        elif any(term in paragraph_lower for term in ["randomized", "controlled trial", "rct"]):
            return "experimental"
        elif any(term in paragraph_lower for term in ["survey", "questionnaire", "interview"]):
            return "survey_research"
        else:
            return "general_evidence"

    def _identify_academic_indicators(self, paragraph: str) -> List[str]:
        """Identify academic quality indicators in paragraph."""
        indicators = []
        paragraph_lower = paragraph.lower()

        indicator_mapping = {
            "peer_reviewed": ["peer-reviewed", "peer reviewed"],
            "empirical_data": ["empirical", "data shows", "findings indicate"],
            "statistical_analysis": ["statistical", "significance", "p-value", "confidence"],
            "methodology_described": ["methodology", "method", "procedure", "protocol"]
        }

        for indicator_type, keywords in indicator_mapping.items():
            if any(keyword in paragraph_lower for keyword in keywords):
                indicators.append(indicator_type)

        return indicators

    def _extract_insights(self, segment: str) -> List[str]:
        """Extract key insights from text segment."""
        insights = []

        # Look for conclusion indicators
        conclusion_patterns = [
            r'therefore[,\s]+(.*?)(?:\.|$)',
            r'thus[,\s]+(.*?)(?:\.|$)',
            r'findings suggest[,\s]+(.*?)(?:\.|$)'
        ]

        import re
        for pattern in conclusion_patterns:
            matches = re.findall(pattern, segment, re.IGNORECASE)
            insights.extend([match.strip() for match in matches if len(match.strip()) > 20])

        return insights[:3]  # Limit to top 3

    def _calculate_evidence_quality(self, evidence_paragraphs: List[Dict], insights: List[str]) -> float:
        """Calculate overall evidence quality score."""
        if not evidence_paragraphs:
            return 0.0

        # Average relevance score
        avg_relevance = sum(p.get("relevance_score", 0) for p in evidence_paragraphs) / len(evidence_paragraphs)

        # Evidence diversity score
        evidence_types = set(p.get("evidence_type", "general") for p in evidence_paragraphs)
        diversity_score = min(1.0, len(evidence_types) / 4.0)

        # Academic indicators score
        total_indicators = sum(len(p.get("academic_indicators", [])) for p in evidence_paragraphs)
        indicators_score = min(1.0, total_indicators / 10.0)

        # Combined score with weights
        quality_score = (
            avg_relevance * 0.5 +
            diversity_score * 0.3 +
            indicators_score * 0.2
        )

        return quality_score

    async def _calculate_comprehensive_quality(self, source: Dict, user_params: Dict) -> Dict[str, Any]:
        """Calculate comprehensive quality metrics for source."""

        # Base scores
        credibility = source.get("credibility_score", 0.5)
        relevance = source.get("field_relevance", 0.5)
        evidence_quality = source.get("evidence_quality_score", 0.5)

        # Academic alignment assessment
        field = user_params.get("field", "general")
        academic_alignment = self._assess_field_relevance(source, field)

        # Calculate weighted overall score
        overall_score = (
            credibility * 0.3 +
            relevance * 0.3 +
            evidence_quality * 0.25 +
            academic_alignment * 0.15
        )

        return {
            "overall_score": overall_score,
            "breakdown": {
                "credibility": credibility,
                "relevance": relevance,
                "evidence_quality": evidence_quality,
                "academic_alignment": academic_alignment
            },
            "factors": {
                "high_credibility": credibility > 0.8,
                "high_relevance": relevance > 0.8,
                "quality_evidence": evidence_quality > 0.7,
                "field_aligned": academic_alignment > 0.7
            },
            "academic_alignment": academic_alignment
        }

    def _extract_key_quotes(self, source: Dict) -> List[str]:
        """Extract key quotes from source content."""
        content = source.get("content", "") or source.get("abstract", "")
        if not content:
            return []

        import re
        # Look for quoted material
        quotes = re.findall(r'"([^"]{30,200})"', content)
        return quotes[:3]  # Top 3 quotes

    def _extract_statistical_data(self, source: Dict) -> List[Dict[str, str]]:
        """Extract statistical data from source."""
        content = source.get("content", "") or source.get("abstract", "")
        if not content:
            return []

        import re
        statistical_data = []

        # Extract percentages
        percentage_matches = re.findall(r'(\d+\.?\d*)\s*percent|\d+\.?\d*%', content, re.IGNORECASE)
        for match in percentage_matches[:2]:
            statistical_data.append({"type": "percentage", "value": match})

        return statistical_data

    def _determine_advanced_recommended_use(self, source: Dict) -> str:
        """Determine advanced recommended use for source."""
        quality_score = source.get("comprehensive_quality_score", 0)

        if quality_score > 0.8:
            return "Primary evidence - High quality"
        elif quality_score > 0.7:
            return "Supporting evidence"
        else:
            return "Background information"

    def _generate_citation_context(self, source: Dict) -> str:
        """Generate citation context for source."""
        source_type = source.get("source_type", "unknown")

        if source_type == "journal":
            return "Use as primary academic reference"
        elif source_type == "conference":
            return "Cite for current research developments"
        else:
            return "Use with appropriate context"

    def _generate_hover_summary(self, source: Dict) -> str:
        """Generate hover card summary."""
        title = source.get("title", "Unknown")
        authors = source.get("authors", [])

        author_text = f"by {', '.join(authors[:2])}" if authors else "Unknown author"
        if len(authors) > 2:
            author_text += " et al."

        return f"{title} {author_text}"

    def _extract_advanced_key_points(self, source: Dict) -> List[str]:
        """Extract advanced key points for hover display."""
        evidence_paragraphs = source.get("evidence_paragraphs", [])
        insights = source.get("key_insights", [])

        key_points = []

        # Extract from top evidence paragraphs
        for paragraph in evidence_paragraphs[:2]:
            text = paragraph.get("text", "")
            if text:
                # Extract first meaningful sentence
                sentences = text.split(". ")
                if sentences and len(sentences[0]) > 30:
                    key_points.append(sentences[0] + ".")

        # Add insights
        key_points.extend(insights[:2])

        return key_points[:4]  # Max 4 key points

    def _extract_credibility_indicators(self, source: Dict) -> List[str]:
        """Extract credibility indicators for display."""
        indicators = []

        if source.get("source_type") == "journal":
            indicators.append("Peer-reviewed journal")

        if source.get("doi"):
            indicators.append("DOI assigned")

        credibility = source.get("credibility_score", 0)
        if credibility > 0.8:
            indicators.append("High credibility")

        return indicators[:3]  # Max 3 indicators

    def _generate_usage_recommendations(self, source: Dict) -> List[str]:
        """Generate usage recommendations for source."""
        recommendations = []

        quality_score = source.get("comprehensive_quality_score", 0)

        if quality_score > 0.8:
            recommendations.append("Suitable for primary evidence")

        source_type = source.get("source_type", "unknown")
        if source_type == "journal":
            recommendations.append("Academic standard citation")

        return recommendations[:3]  # Max 3 recommendations
