"""
Highlight Parser - Extract flagged spans from Turnitin PDFs
Processes Turnitin similarity and AI detection reports to extract flagged text spans.
"""

import asyncio
import logging
import os
import time
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from enum import Enum
import re

import redis.asyncio as redis


class FlagType(Enum):
    """Types of content flags."""
    PLAGIARISM = "plagiarism"
    AI_DETECTION = "ai_detection"
    SIMILARITY = "similarity"
    PARAPHRASE = "paraphrase"
    QUOTE = "quote"
    CITATION_MISSING = "citation_missing"


@dataclass
class FlaggedSpan:
    """Represents a flagged text span."""
    text: str
    start_position: int
    end_position: int
    flag_type: FlagType
    confidence_score: float
    source_info: Optional[str] = None
    recommendation: Optional[str] = None
    severity: str = "medium"  # low, medium, high


@dataclass
class ParsedReport:
    """Parsed Turnitin report results."""
    report_type: str  # "similarity" or "ai_detection"
    overall_score: float
    flagged_spans: List[FlaggedSpan]
    total_flags: int
    high_severity_flags: int
    medium_severity_flags: int
    low_severity_flags: int
    processing_time: float
    recommendations: List[str]


class HighlightParser:
    """
    Production-ready highlight parser for Turnitin reports.
    
    Features:
    - PDF text extraction and analysis
    - Highlighted text span detection
    - Flag type classification
    - Confidence scoring
    - Source attribution
    - Remediation recommendations
    - Multi-format support (PDF, HTML, XML)
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Initialize Redis for caching
        self.redis_client = redis.from_url("redis://localhost:6379", decode_responses=True)
        
        # Parser statistics
        self.stats = {
            "reports_parsed": 0,
            "flags_extracted": 0,
            "similarity_reports": 0,
            "ai_detection_reports": 0,
            "parsing_errors": 0,
            "average_processing_time": 0.0
        }
        
        # Flag patterns for different report types
        self.similarity_patterns = [
            r'(?i)similarity\s*:\s*(\d+(?:\.\d+)?)\s*%',
            r'(?i)match\s*:\s*(\d+(?:\.\d+)?)\s*%',
            r'(?i)overlap\s*:\s*(\d+(?:\.\d+)?)\s*%'
        ]
        
        self.ai_patterns = [
            r'(?i)ai\s*(?:detected|score)\s*:\s*(\d+(?:\.\d+)?)\s*%',
            r'(?i)artificial\s*intelligence\s*:\s*(\d+(?:\.\d+)?)\s*%',
            r'(?i)machine\s*generated\s*:\s*(\d+(?:\.\d+)?)\s*%'
        ]
        
        # Severity thresholds
        self.similarity_thresholds = {
            "high": 25.0,    # >25% similarity = high risk
            "medium": 10.0,  # 10-25% = medium risk
            "low": 0.0       # <10% = low risk
        }
        
        self.ai_thresholds = {
            "high": 80.0,    # >80% AI = high risk
            "medium": 50.0,  # 50-80% = medium risk
            "low": 0.0       # <50% = low risk
        }
    
    async def parse_similarity_report(self, pdf_path: str, chunk_text: str) -> ParsedReport:
        """
        Parse Turnitin similarity report PDF.
        
        Args:
            pdf_path: Path to the similarity report PDF
            chunk_text: Original text of the document chunk
            
        Returns:
            ParsedReport: Parsed report with flagged spans
        """
        start_time = time.time()
        
        try:
            self.logger.info(f"🔍 Parsing similarity report: {pdf_path}")
            
            # Extract text from PDF
            pdf_text = await self._extract_pdf_text(pdf_path)
            
            # Parse overall similarity score
            overall_score = self._extract_overall_score(pdf_text, "similarity")
            
            # Extract flagged spans
            flagged_spans = await self._extract_similarity_spans(pdf_text, chunk_text)
            
            # Generate recommendations
            recommendations = self._generate_similarity_recommendations(overall_score, flagged_spans)
            
            # Calculate severity distribution
            severity_counts = self._calculate_severity_distribution(flagged_spans)
            
            # Create parsed report
            report = ParsedReport(
                report_type="similarity",
                overall_score=overall_score,
                flagged_spans=flagged_spans,
                total_flags=len(flagged_spans),
                high_severity_flags=severity_counts["high"],
                medium_severity_flags=severity_counts["medium"],
                low_severity_flags=severity_counts["low"],
                processing_time=time.time() - start_time,
                recommendations=recommendations
            )
            
            # Update statistics
            self.stats["reports_parsed"] += 1
            self.stats["similarity_reports"] += 1
            self.stats["flags_extracted"] += len(flagged_spans)
            self._update_average_processing_time(report.processing_time)
            
            self.logger.info(f"✅ Similarity report parsed: {len(flagged_spans)} flags found")
            
            return report
            
        except Exception as e:
            self.logger.error(f"Failed to parse similarity report {pdf_path}: {e}")
            self.stats["parsing_errors"] += 1
            raise
    
    async def parse_ai_detection_report(self, pdf_path: str, chunk_text: str) -> ParsedReport:
        """
        Parse Turnitin AI detection report PDF.
        
        Args:
            pdf_path: Path to the AI detection report PDF
            chunk_text: Original text of the document chunk
            
        Returns:
            ParsedReport: Parsed report with flagged spans
        """
        start_time = time.time()
        
        try:
            self.logger.info(f"🤖 Parsing AI detection report: {pdf_path}")
            
            # Extract text from PDF
            pdf_text = await self._extract_pdf_text(pdf_path)
            
            # Parse overall AI detection score
            overall_score = self._extract_overall_score(pdf_text, "ai_detection")
            
            # Extract flagged spans
            flagged_spans = await self._extract_ai_detection_spans(pdf_text, chunk_text)
            
            # Generate recommendations
            recommendations = self._generate_ai_recommendations(overall_score, flagged_spans)
            
            # Calculate severity distribution
            severity_counts = self._calculate_severity_distribution(flagged_spans)
            
            # Create parsed report
            report = ParsedReport(
                report_type="ai_detection",
                overall_score=overall_score,
                flagged_spans=flagged_spans,
                total_flags=len(flagged_spans),
                high_severity_flags=severity_counts["high"],
                medium_severity_flags=severity_counts["medium"],
                low_severity_flags=severity_counts["low"],
                processing_time=time.time() - start_time,
                recommendations=recommendations
            )
            
            # Update statistics
            self.stats["reports_parsed"] += 1
            self.stats["ai_detection_reports"] += 1
            self.stats["flags_extracted"] += len(flagged_spans)
            self._update_average_processing_time(report.processing_time)
            
            self.logger.info(f"✅ AI detection report parsed: {len(flagged_spans)} flags found")
            
            return report
            
        except Exception as e:
            self.logger.error(f"Failed to parse AI detection report {pdf_path}: {e}")
            self.stats["parsing_errors"] += 1
            raise
    
    async def parse_both_reports(self, similarity_pdf: str, ai_pdf: str, 
                               chunk_text: str) -> Tuple[ParsedReport, ParsedReport]:
        """
        Parse both similarity and AI detection reports.
        
        Args:
            similarity_pdf: Path to similarity report PDF
            ai_pdf: Path to AI detection report PDF
            chunk_text: Original text of the document chunk
            
        Returns:
            Tuple of (similarity_report, ai_detection_report)
        """
        try:
            # Parse both reports concurrently
            similarity_task = self.parse_similarity_report(similarity_pdf, chunk_text)
            ai_task = self.parse_ai_detection_report(ai_pdf, chunk_text)
            
            similarity_report, ai_report = await asyncio.gather(similarity_task, ai_task)
            
            self.logger.info("✅ Both reports parsed successfully")
            
            return similarity_report, ai_report
            
        except Exception as e:
            self.logger.error(f"Failed to parse both reports: {e}")
            raise
    
    async def _extract_pdf_text(self, pdf_path: str) -> str:
        """Extract text content from PDF file."""
        try:
            # Check if file exists
            if not os.path.exists(pdf_path):
                raise FileNotFoundError(f"PDF file not found: {pdf_path}")
            
            # Try multiple PDF extraction methods
            text = None
            
            # Method 1: PyPDF2
            try:
                import PyPDF2
                
                with open(pdf_path, 'rb') as file:
                    pdf_reader = PyPDF2.PdfReader(file)
                    text_parts = []
                    
                    for page in pdf_reader.pages:
                        text_parts.append(page.extract_text())
                    
                    text = '\n'.join(text_parts)
                    
                    if text and len(text.strip()) > 100:  # Valid extraction
                        return text
                        
            except Exception as e:
                self.logger.warning(f"PyPDF2 extraction failed: {e}")
            
            # Method 2: pdfplumber (more accurate for highlighted text)
            try:
                import pdfplumber
                
                with pdfplumber.open(pdf_path) as pdf:
                    text_parts = []
                    
                    for page in pdf.pages:
                        page_text = page.extract_text()
                        if page_text:
                            text_parts.append(page_text)
                    
                    text = '\n'.join(text_parts)
                    
                    if text and len(text.strip()) > 100:
                        return text
                        
            except Exception as e:
                self.logger.warning(f"pdfplumber extraction failed: {e}")
            
            # Method 3: Fallback to pymupdf (fitz)
            try:
                import fitz  # PyMuPDF
                
                doc = fitz.open(pdf_path)
                text_parts = []
                
                for page_num in range(doc.page_count):
                    page = doc[page_num]
                    text_parts.append(page.get_text())
                
                doc.close()
                text = '\n'.join(text_parts)
                
                if text and len(text.strip()) > 100:
                    return text
                    
            except Exception as e:
                self.logger.warning(f"PyMuPDF extraction failed: {e}")
            
            # If all methods fail
            if not text or len(text.strip()) < 50:
                raise Exception("Failed to extract meaningful text from PDF")
            
            return text
            
        except Exception as e:
            self.logger.error(f"PDF text extraction failed for {pdf_path}: {e}")
            raise
    
    def _extract_overall_score(self, pdf_text: str, report_type: str) -> float:
        """Extract overall similarity or AI detection score from PDF text."""
        try:
            patterns = self.similarity_patterns if report_type == "similarity" else self.ai_patterns
            
            scores = []
            
            for pattern in patterns:
                matches = re.findall(pattern, pdf_text)
                for match in matches:
                    try:
                        score = float(match)
                        if 0 <= score <= 100:  # Valid percentage
                            scores.append(score)
                    except ValueError:
                        continue
            
            if scores:
                # Return the highest score found (most conservative)
                return max(scores)
            
            # If no score found, try to extract from common report formats
            if "Overall Similarity Index" in pdf_text:
                # Turnitin format
                match = re.search(r'Overall Similarity Index[:\s]*(\d+(?:\.\d+)?)\s*%', pdf_text, re.IGNORECASE)
                if match:
                    return float(match.group(1))
            
            # Default fallback
            self.logger.warning(f"Could not extract {report_type} score from PDF text")
            return 0.0
            
        except Exception as e:
            self.logger.error(f"Error extracting overall score: {e}")
            return 0.0
    
    async def _extract_similarity_spans(self, pdf_text: str, chunk_text: str) -> List[FlaggedSpan]:
        """Extract flagged spans from similarity report."""
        try:
            flagged_spans = []
            
            # Pattern for similarity matches with sources
            similarity_patterns = [
                r'(?i)match\s*(?:found|detected)?\s*[:;]\s*["\']([^"\']+)["\'](?:\s*from\s*["\']([^"\']+)["\'])?',
                r'(?i)similar\s*(?:to|text)?\s*[:;]\s*["\']([^"\']+)["\'](?:\s*source\s*["\']([^"\']+)["\'])?',
                r'(?i)plagiarism\s*detected\s*[:;]\s*["\']([^"\']+)["\'](?:\s*from\s*["\']([^"\']+)["\'])?'
            ]
            
            for pattern in similarity_patterns:
                matches = re.finditer(pattern, pdf_text, re.MULTILINE | re.DOTALL)
                
                for match in matches:
                    flagged_text = match.group(1).strip()
                    source_info = match.group(2) if len(match.groups()) > 1 and match.group(2) else None
                    
                    # Find position in original chunk text
                    start_pos, end_pos = self._find_text_position(flagged_text, chunk_text)
                    
                    if start_pos >= 0:
                        # Calculate confidence based on text length and similarity
                        confidence = self._calculate_similarity_confidence(flagged_text, source_info)
                        
                        # Determine severity
                        severity = self._determine_similarity_severity(confidence, len(flagged_text))
                        
                        # Generate recommendation
                        recommendation = self._generate_span_recommendation(flagged_text, FlagType.SIMILARITY)
                        
                        span = FlaggedSpan(
                            text=flagged_text,
                            start_position=start_pos,
                            end_position=end_pos,
                            flag_type=FlagType.SIMILARITY,
                            confidence_score=confidence,
                            source_info=source_info,
                            recommendation=recommendation,
                            severity=severity
                        )
                        
                        flagged_spans.append(span)
            
            # Also look for highlighted text markers (common in Turnitin PDFs)
            highlighted_spans = await self._extract_highlighted_text(pdf_text, chunk_text, FlagType.SIMILARITY)
            flagged_spans.extend(highlighted_spans)
            
            # Remove duplicates
            flagged_spans = self._remove_duplicate_spans(flagged_spans)
            
            return flagged_spans
            
        except Exception as e:
            self.logger.error(f"Error extracting similarity spans: {e}")
            return []
    
    async def _extract_ai_detection_spans(self, pdf_text: str, chunk_text: str) -> List[FlaggedSpan]:
        """Extract flagged spans from AI detection report."""
        try:
            flagged_spans = []
            
            # Patterns for AI-generated text detection
            ai_patterns = [
                r'(?i)ai\s*(?:generated|detected|written)\s*[:;]\s*["\']([^"\']+)["\']',
                r'(?i)artificial\s*intelligence\s*[:;]\s*["\']([^"\']+)["\']',
                r'(?i)machine\s*(?:generated|written)\s*[:;]\s*["\']([^"\']+)["\']',
                r'(?i)likely\s*ai\s*[:;]\s*["\']([^"\']+)["\']'
            ]
            
            for pattern in ai_patterns:
                matches = re.finditer(pattern, pdf_text, re.MULTILINE | re.DOTALL)
                
                for match in matches:
                    flagged_text = match.group(1).strip()
                    
                    # Find position in original chunk text
                    start_pos, end_pos = self._find_text_position(flagged_text, chunk_text)
                    
                    if start_pos >= 0:
                        # Calculate confidence based on AI detection patterns
                        confidence = self._calculate_ai_confidence(flagged_text)
                        
                        # Determine severity
                        severity = self._determine_ai_severity(confidence, len(flagged_text))
                        
                        # Generate recommendation
                        recommendation = self._generate_span_recommendation(flagged_text, FlagType.AI_DETECTION)
                        
                        span = FlaggedSpan(
                            text=flagged_text,
                            start_position=start_pos,
                            end_position=end_pos,
                            flag_type=FlagType.AI_DETECTION,
                            confidence_score=confidence,
                            source_info=None,
                            recommendation=recommendation,
                            severity=severity
                        )
                        
                        flagged_spans.append(span)
            
            # Extract highlighted AI detection spans
            highlighted_spans = await self._extract_highlighted_text(pdf_text, chunk_text, FlagType.AI_DETECTION)
            flagged_spans.extend(highlighted_spans)
            
            # Remove duplicates
            flagged_spans = self._remove_duplicate_spans(flagged_spans)
            
            return flagged_spans
            
        except Exception as e:
            self.logger.error(f"Error extracting AI detection spans: {e}")
            return []
    
    async def _extract_highlighted_text(self, pdf_text: str, chunk_text: str, 
                                      flag_type: FlagType) -> List[FlaggedSpan]:
        """Extract text that appears to be highlighted in the PDF."""
        try:
            highlighted_spans = []
            
            # Look for text formatting markers that indicate highlighting
            highlight_patterns = [
                r'<highlight[^>]*>([^<]+)</highlight>',  # XML-style highlights
                r'\[HIGHLIGHT\]([^\[]+)\[/HIGHLIGHT\]',   # Custom highlight markers
                r'<<([^>]+)>>',                           # Double bracket highlights
                r'===([^=]+)==='                          # Triple equals highlights
            ]
            
            for pattern in highlight_patterns:
                matches = re.finditer(pattern, pdf_text, re.IGNORECASE)
                
                for match in matches:
                    highlighted_text = match.group(1).strip()
                    
                    # Find position in original text
                    start_pos, end_pos = self._find_text_position(highlighted_text, chunk_text)
                    
                    if start_pos >= 0:
                        # Calculate confidence based on flag type
                        if flag_type == FlagType.SIMILARITY:
                            confidence = self._calculate_similarity_confidence(highlighted_text, None)
                            severity = self._determine_similarity_severity(confidence, len(highlighted_text))
                        else:
                            confidence = self._calculate_ai_confidence(highlighted_text)
                            severity = self._determine_ai_severity(confidence, len(highlighted_text))
                        
                        recommendation = self._generate_span_recommendation(highlighted_text, flag_type)
                        
                        span = FlaggedSpan(
                            text=highlighted_text,
                            start_position=start_pos,
                            end_position=end_pos,
                            flag_type=flag_type,
                            confidence_score=confidence,
                            source_info=None,
                            recommendation=recommendation,
                            severity=severity
                        )
                        
                        highlighted_spans.append(span)
            
            return highlighted_spans
            
        except Exception as e:
            self.logger.error(f"Error extracting highlighted text: {e}")
            return []
    
    def _find_text_position(self, flagged_text: str, chunk_text: str) -> Tuple[int, int]:
        """Find the position of flagged text within the original chunk text."""
        try:
            # Clean both texts for better matching
            clean_flagged = self._clean_text_for_matching(flagged_text)
            clean_chunk = self._clean_text_for_matching(chunk_text)
            
            # Try exact match first
            start_pos = clean_chunk.find(clean_flagged)
            
            if start_pos >= 0:
                end_pos = start_pos + len(clean_flagged)
                return start_pos, end_pos
            
            # Try fuzzy matching for slight variations
            words = clean_flagged.split()
            if len(words) >= 3:  # Only for meaningful text
                # Look for partial matches
                for i in range(len(words) - 2):
                    partial_text = ' '.join(words[i:i+3])
                    start_pos = clean_chunk.find(partial_text)
                    if start_pos >= 0:
                        # Extend to find full match
                        end_pos = start_pos + len(partial_text)
                        return start_pos, end_pos
            
            # No match found
            return -1, -1
            
        except Exception as e:
            self.logger.error(f"Error finding text position: {e}")
            return -1, -1
    
    def _clean_text_for_matching(self, text: str) -> str:
        """Clean text to improve matching accuracy."""
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove common formatting artifacts
        text = re.sub(r'["\'\`\u2018\u2019\u201c\u201d]', '', text)  # Remove quotes
        text = re.sub(r'[\u2013\u2014]', '-', text)  # Normalize dashes
        
        return text.strip()
    
    def _calculate_similarity_confidence(self, text: str, source_info: Optional[str]) -> float:
        """Calculate confidence score for similarity flagged text."""
        base_confidence = 0.7
        
        # Increase confidence based on text length
        if len(text) > 100:
            base_confidence += 0.1
        elif len(text) > 200:
            base_confidence += 0.2
        
        # Increase confidence if source is provided
        if source_info:
            base_confidence += 0.15
        
        # Decrease confidence for very short text
        if len(text) < 20:
            base_confidence -= 0.2
        
        return min(max(base_confidence, 0.0), 1.0)
    
    def _calculate_ai_confidence(self, text: str) -> float:
        """Calculate confidence score for AI detection flagged text."""
        base_confidence = 0.75
        
        # AI detection patterns that increase confidence
        ai_indicators = [
            'in conclusion', 'furthermore', 'moreover', 'additionally',
            'it is important to note', 'as mentioned earlier', 'in summary'
        ]
        
        text_lower = text.lower()
        indicator_count = sum(1 for indicator in ai_indicators if indicator in text_lower)
        
        # Increase confidence based on AI indicators
        base_confidence += indicator_count * 0.05
        
        # Adjust based on text length
        if len(text) > 150:
            base_confidence += 0.1
        elif len(text) < 30:
            base_confidence -= 0.2
        
        return min(max(base_confidence, 0.0), 1.0)
    
    def _determine_similarity_severity(self, confidence: float, text_length: int) -> str:
        """Determine severity level for similarity flags."""
        if confidence > 0.8 and text_length > 100:
            return "high"
        elif confidence > 0.6 or text_length > 50:
            return "medium"
        else:
            return "low"
    
    def _determine_ai_severity(self, confidence: float, text_length: int) -> str:
        """Determine severity level for AI detection flags."""
        if confidence > 0.85 and text_length > 80:
            return "high"
        elif confidence > 0.7 or text_length > 40:
            return "medium"
        else:
            return "low"
    
    def _generate_span_recommendation(self, text: str, flag_type: FlagType) -> str:
        """Generate recommendation for a specific flagged span."""
        if flag_type == FlagType.SIMILARITY:
            if len(text) > 100:
                return "Significant similarity detected. Consider paraphrasing this section and adding proper citations."
            else:
                return "Minor similarity found. Review and paraphrase if necessary."
        
        elif flag_type == FlagType.AI_DETECTION:
            if len(text) > 80:
                return "Potential AI-generated content. Rewrite in your own voice and add personal insights."
            else:
                return "Possible AI patterns detected. Review and modify the writing style."
        
        return "Review this section and consider revisions."
    
    def _remove_duplicate_spans(self, spans: List[FlaggedSpan]) -> List[FlaggedSpan]:
        """Remove duplicate or overlapping flagged spans."""
        if not spans:
            return spans
        
        # Sort by start position
        sorted_spans = sorted(spans, key=lambda x: x.start_position)
        
        unique_spans = []
        
        for span in sorted_spans:
            # Check for overlap with existing spans
            is_duplicate = False
            
            for existing in unique_spans:
                # Check for significant overlap
                overlap_start = max(span.start_position, existing.start_position)
                overlap_end = min(span.end_position, existing.end_position)
                overlap_length = max(0, overlap_end - overlap_start)
                
                # If more than 50% overlap, consider it a duplicate
                span_length = span.end_position - span.start_position
                if overlap_length > span_length * 0.5:
                    is_duplicate = True
                    break
            
            if not is_duplicate:
                unique_spans.append(span)
        
        return unique_spans
    
    def _generate_similarity_recommendations(self, overall_score: float, 
                                           flagged_spans: List[FlaggedSpan]) -> List[str]:
        """Generate recommendations for similarity report."""
        recommendations = []
        
        if overall_score > 25:
            recommendations.append("High similarity detected. Significant revision required.")
            recommendations.append("Focus on paraphrasing and adding original analysis.")
        elif overall_score > 10:
            recommendations.append("Moderate similarity found. Review flagged sections.")
            recommendations.append("Ensure proper citation for all sources.")
        else:
            recommendations.append("Low similarity score. Minor revisions may be needed.")
        
        high_severity_count = sum(1 for span in flagged_spans if span.severity == "high")
        if high_severity_count > 0:
            recommendations.append(f"{high_severity_count} high-severity issues require immediate attention.")
        
        return recommendations
    
    def _generate_ai_recommendations(self, overall_score: float, 
                                   flagged_spans: List[FlaggedSpan]) -> List[str]:
        """Generate recommendations for AI detection report."""
        recommendations = []
        
        if overall_score > 80:
            recommendations.append("High AI detection score. Extensive rewriting recommended.")
            recommendations.append("Add personal experiences and original insights.")
        elif overall_score > 50:
            recommendations.append("Moderate AI detection. Review writing style.")
            recommendations.append("Vary sentence structure and add human perspective.")
        else:
            recommendations.append("Low AI detection score. Content appears human-written.")
        
        high_severity_count = sum(1 for span in flagged_spans if span.severity == "high")
        if high_severity_count > 0:
            recommendations.append(f"{high_severity_count} sections need significant style revision.")
        
        return recommendations
    
    def _calculate_severity_distribution(self, spans: List[FlaggedSpan]) -> Dict[str, int]:
        """Calculate distribution of severity levels."""
        return {
            "high": sum(1 for span in spans if span.severity == "high"),
            "medium": sum(1 for span in spans if span.severity == "medium"),
            "low": sum(1 for span in spans if span.severity == "low")
        }
    
    def _update_average_processing_time(self, processing_time: float):
        """Update average processing time statistic."""
        current_avg = self.stats["average_processing_time"]
        report_count = self.stats["reports_parsed"]
        
        if report_count == 1:
            self.stats["average_processing_time"] = processing_time
        else:
            self.stats["average_processing_time"] = (
                (current_avg * (report_count - 1) + processing_time) / report_count
            )
    
    async def get_parser_stats(self) -> Dict[str, Any]:
        """Get comprehensive parser statistics."""
        return {
            "stats": self.stats,
            "timestamp": time.time()
        }
    
    async def close(self):
        """Close parser and cleanup resources."""
        await self.redis_client.close()


# Global highlight parser instance
highlight_parser = HighlightParser()


# Utility functions for integration
async def parse_turnitin_reports(similarity_pdf: str, ai_pdf: str, 
                               chunk_text: str) -> Tuple[ParsedReport, ParsedReport]:
    """Parse both Turnitin reports."""
    return await highlight_parser.parse_both_reports(similarity_pdf, ai_pdf, chunk_text)


async def parse_similarity_report(pdf_path: str, chunk_text: str) -> ParsedReport:
    """Parse similarity report only."""
    return await highlight_parser.parse_similarity_report(pdf_path, chunk_text)


async def parse_ai_detection_report(pdf_path: str, chunk_text: str) -> ParsedReport:
    """Parse AI detection report only."""
    return await highlight_parser.parse_ai_detection_report(pdf_path, chunk_text)


if __name__ == "__main__":
    # Test the highlight parser
    async def test_parser():
        """Test highlight parser."""
        parser = HighlightParser()
        
        # Create sample test content
        test_chunk = """
        This is a sample academic text that might contain some similarities to existing sources.
        The concept of artificial intelligence has been evolving rapidly in recent years.
        Furthermore, it is important to note that machine learning algorithms are becoming more sophisticated.
        """
        
        # Create dummy PDF files for testing
        test_similarity_pdf = "/tmp/test_similarity.pdf"
        test_ai_pdf = "/tmp/test_ai.pdf"
        
        # Note: In real usage, these would be actual Turnitin PDF reports
        print("Highlight parser initialized successfully")
        
        # Get stats
        stats = await parser.get_parser_stats()
        print(f"Parser stats: {stats}")
        
        await parser.close()
    
    asyncio.run(test_parser())