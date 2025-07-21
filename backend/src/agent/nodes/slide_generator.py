"""Slide Generator node for auto-slide and infographic creation."""

import re
from typing import Dict, Any, List
from langchain_core.runnables import RunnableConfig

from src.agent.base import BaseNode
from ...agent.handywriterz_state import HandyWriterzState


class SlideGeneratorNode(BaseNode):
    """Generates slide presentations and infographics from written content."""

    def __init__(self):
        super().__init__("slide_generator", timeout_seconds=60.0, max_retries=2)

    async def execute(self, state: HandyWriterzState, config: RunnableConfig) -> Dict[str, Any]:
        """Generate slides and infographics from current draft."""
        try:
            current_draft = state.get("current_draft", "")
            user_params = state.get("user_params", {})

            if not current_draft:
                return {"slides_generated": False}

            # Extract key sections and content
            sections = self._extract_sections(current_draft)

            # Generate slide content
            slide_data = await self._generate_slide_content(sections, user_params)

            # Generate infographic data
            infographic_data = await self._generate_infographic_data(sections, user_params)

            # Create PowerPoint-compatible structure
            pptx_structure = self._create_pptx_structure(slide_data)

            # Create infographic structure (for tools like Canva API)
            infographic_structure = self._create_infographic_structure(infographic_data)

            self._broadcast_progress(state, f"Generated {len(slide_data)} slides and infographic", 100.0)

            # Generate the .pptx file
            pptx_path = self._create_pptx_presentation(pptx_structure)

            # Upload to Supabase and get URL
            # In a real implementation, you would use a Supabase client here.
            # For now, we'll just use the local path as a placeholder.
            supabase_url = f"/uploads/{os.path.basename(pptx_path)}"

            # Emit WebSocket event
            # In a real app, you would use a WebSocket manager.
            logger.info(f"Emitting derivative_ready event for slides: {supabase_url}")

            return {
                "slides_generated": True,
                "slide_data": slide_data,
                "infographic_data": infographic_data,
                "pptx_structure": pptx_structure,
                "infographic_structure": infographic_structure,
                "slide_count": len(slide_data),
                "download_url": supabase_url
            }

        except Exception as e:
            self.logger.error(f"Slide generation failed: {e}")
            raise

    def _extract_sections(self, draft: str) -> List[Dict[str, Any]]:
        """Extract structured sections from the draft."""
        sections = []

        # Split by common academic section headers
        section_patterns = [
            r'#{1,3}\s*(.+?)(?=\n)',  # Markdown headers
            r'(\d+\.\s*.+?)(?=\n)',   # Numbered sections
            r'([A-Z][A-Z\s]{3,}?)(?=\n)',  # ALL CAPS headers
        ]

        # Try to split by paragraphs if no clear headers
        paragraphs = [p.strip() for p in draft.split('\n\n') if p.strip()]

        for i, paragraph in enumerate(paragraphs):
            # Check if this looks like a header
            is_header = any(re.match(pattern, paragraph) for pattern in section_patterns)

            if is_header or len(paragraph.split()) < 15:  # Short paragraphs might be headers
                # This might be a section header
                if i + 1 < len(paragraphs):
                    sections.append({
                        "title": paragraph.strip(),
                        "content": paragraphs[i + 1] if i + 1 < len(paragraphs) else "",
                        "type": "header_content"
                    })
            else:
                # This is content, check if it has key points
                key_points = self._extract_key_points(paragraph)
                sections.append({
                    "title": self._generate_title_from_content(paragraph),
                    "content": paragraph,
                    "key_points": key_points,
                    "type": "content_section"
                })

        return sections[:15]  # Limit to 15 sections max

    def _extract_key_points(self, content: str) -> List[str]:
        """Extract key points from content section."""
        sentences = [s.strip() for s in content.split('.') if s.strip()]
        key_points = []

        # Look for sentences with strong academic indicators
        strong_indicators = [
            "research shows", "evidence suggests", "findings indicate",
            "study found", "data reveals", "analysis demonstrates",
            "importantly", "significantly", "notably"
        ]

        for sentence in sentences[:5]:  # Max 5 key points per section
            sentence_lower = sentence.lower()
            if any(indicator in sentence_lower for indicator in strong_indicators):
                key_points.append(sentence + ".")
            elif len(sentence.split()) >= 8 and len(sentence.split()) <= 25:
                # Good length for a bullet point
                key_points.append(sentence + ".")

        # If no strong indicators, take first few substantial sentences
        if not key_points:
            for sentence in sentences[:3]:
                if len(sentence.split()) >= 6:
                    key_points.append(sentence + ".")

        return key_points

    def _generate_title_from_content(self, content: str) -> str:
        """Generate a title from content section."""
        # Extract first sentence and shorten it
        first_sentence = content.split('.')[0].strip()

        # Remove common academic starters
        starters_to_remove = [
            "Furthermore", "However", "Moreover", "Additionally",
            "In addition", "Therefore", "Consequently", "As a result"
        ]

        for starter in starters_to_remove:
            if first_sentence.startswith(starter):
                first_sentence = first_sentence[len(starter):].strip().lstrip(',').strip()

        # Limit to reasonable title length
        words = first_sentence.split()
        if len(words) > 8:
            return " ".join(words[:8]) + "..."

        return first_sentence

    async def _generate_slide_content(self, sections: List[Dict], user_params: Dict) -> List[Dict[str, Any]]:
        """Generate structured slide content."""
        slides = []
        field = user_params.get("field", "general")

        # Title slide
        slides.append({
            "slide_number": 1,
            "type": "title",
            "title": user_params.get("title", "Academic Research Presentation"),
            "subtitle": f"{field.title()} Research Overview",
            "author": "HandyWriterz Academic Assistant",
            "layout": "title_slide"
        })

        # Introduction slide
        if sections:
            first_section = sections[0]
            slides.append({
                "slide_number": 2,
                "type": "content",
                "title": "Introduction",
                "content": first_section.get("content", "")[:300] + "...",
                "bullet_points": first_section.get("key_points", [])[:3],
                "layout": "content_with_bullets"
            })

        # Content slides
        for i, section in enumerate(sections[1:8], 3):  # Max 6 content slides
            slide_title = section.get("title", f"Key Point {i-2}")

            slides.append({
                "slide_number": i,
                "type": "content",
                "title": slide_title,
                "content": section.get("content", "")[:200] + "..." if len(section.get("content", "")) > 200 else section.get("content", ""),
                "bullet_points": section.get("key_points", [])[:4],
                "layout": "content_with_bullets"
            })

        # Key findings slide
        key_findings = []
        for section in sections:
            key_findings.extend(section.get("key_points", [])[:2])

        if key_findings:
            slides.append({
                "slide_number": len(slides) + 1,
                "type": "summary",
                "title": "Key Findings",
                "bullet_points": key_findings[:6],
                "layout": "bullet_summary"
            })

        # Conclusion slide
        slides.append({
            "slide_number": len(slides) + 1,
            "type": "conclusion",
            "title": "Conclusion",
            "content": "Research demonstrates significant implications for academic understanding.",
            "layout": "simple_content"
        })

        return slides

    async def _generate_infographic_data(self, sections: List[Dict], user_params: Dict) -> Dict[str, Any]:
        """Generate data for infographic creation."""
        # Extract statistics and key numbers
        statistics = self._extract_statistics(sections)

        # Extract key processes or steps
        processes = self._extract_processes(sections)

        # Extract comparisons
        comparisons = self._extract_comparisons(sections)

        return {
            "title": user_params.get("title", "Research Overview"),
            "field": user_params.get("field", "general"),
            "statistics": statistics,
            "processes": processes,
            "comparisons": comparisons,
            "key_takeaways": [section.get("key_points", [])[:1] for section in sections[:4]],
            "visual_theme": self._determine_visual_theme(user_params.get("field", "general")),
            "color_scheme": self._get_field_colors(user_params.get("field", "general"))
        }

    def _extract_statistics(self, sections: List[Dict]) -> List[Dict[str, Any]]:
        """Extract numerical statistics from content."""
        statistics = []

        # Pattern for percentages, numbers with units, etc.
        stat_patterns = [
            r'(\d+(?:\.\d+)?%)',  # Percentages
            r'(\d+(?:,\d{3})*(?:\.\d+)?)\s*(people|patients|students|participants|cases)',
            r'(\d+(?:\.\d+)?)\s*(times|fold|percent)',
            r'(\$\d+(?:,\d{3})*(?:\.\d+)?(?:\s*(?:million|billion|thousand))?)'
        ]

        for section in sections:
            content = section.get("content", "")
            for pattern in stat_patterns:
                matches = re.findall(pattern, content, re.IGNORECASE)
                for match in matches[:2]:  # Max 2 stats per section
                    if isinstance(match, tuple):
                        stat_text = " ".join(match)
                    else:
                        stat_text = match

                    statistics.append({
                        "value": stat_text,
                        "context": self._get_stat_context(content, stat_text),
                        "section": section.get("title", "Unknown")
                    })

        return statistics[:6]  # Max 6 statistics

    def _extract_processes(self, sections: List[Dict]) -> List[Dict[str, Any]]:
        """Extract step-by-step processes."""
        processes = []

        process_indicators = [
            "first", "second", "third", "next", "then", "finally",
            "step 1", "step 2", "phase 1", "phase 2"
        ]

        for section in sections:
            content = section.get("content", "").lower()
            if any(indicator in content for indicator in process_indicators):
                # This section likely contains a process
                steps = self._extract_steps_from_content(section.get("content", ""))
                if steps:
                    processes.append({
                        "title": section.get("title", "Process"),
                        "steps": steps
                    })

        return processes[:2]  # Max 2 processes

    def _extract_steps_from_content(self, content: str) -> List[str]:
        """Extract process steps from content."""
        sentences = [s.strip() for s in content.split('.') if s.strip()]
        steps = []

        step_indicators = [
            "first", "second", "third", "next", "then", "finally",
            "initially", "subsequently", "thereafter"
        ]

        for sentence in sentences:
            sentence_lower = sentence.lower()
            if any(indicator in sentence_lower for indicator in step_indicators):
                # Clean up the step
                step = sentence.strip()
                for indicator in step_indicators:
                    if step.lower().startswith(indicator):
                        step = step[len(indicator):].strip().lstrip(',').strip()
                        break

                if len(step) > 10:  # Meaningful step
                    steps.append(step)

        return steps[:5]  # Max 5 steps

    def _extract_comparisons(self, sections: List[Dict]) -> List[Dict[str, Any]]:
        """Extract comparison data."""
        comparisons = []

        comparison_indicators = [
            "compared to", "versus", "vs", "while", "whereas",
            "in contrast", "however", "on the other hand"
        ]

        for section in sections:
            content = section.get("content", "")
            content_lower = content.lower()

            if any(indicator in content_lower for indicator in comparison_indicators):
                # This section contains comparisons
                comparison = self._parse_comparison(content)
                if comparison:
                    comparisons.append(comparison)

        return comparisons[:3]  # Max 3 comparisons

    def _parse_comparison(self, content: str) -> Dict[str, Any]:
        """Parse comparison from content."""
        # Simple comparison extraction
        sentences = [s.strip() for s in content.split('.') if s.strip()]

        for sentence in sentences:
            if any(indicator in sentence.lower() for indicator in ["compared to", "versus", "vs"]):
                parts = re.split(r'\b(?:compared to|versus|vs)\b', sentence, flags=re.IGNORECASE)
                if len(parts) == 2:
                    return {
                        "item_a": parts[0].strip(),
                        "item_b": parts[1].strip(),
                        "context": sentence
                    }

        return None

    def _get_stat_context(self, content: str, stat: str) -> str:
        """Get context around a statistic."""
        sentences = content.split('.')
        for sentence in sentences:
            if stat in sentence:
                return sentence.strip() + "."
        return ""

    def _determine_visual_theme(self, field: str) -> str:
        """Determine visual theme based on academic field."""
        themes = {
            "nursing": "healthcare",
            "medicine": "medical",
            "law": "professional",
            "business": "corporate",
            "education": "academic",
            "social_work": "community"
        }
        return themes.get(field.lower(), "academic")

    def _get_field_colors(self, field: str) -> Dict[str, str]:
        """Get color scheme for field."""
        color_schemes = {
            "nursing": {"primary": "#0077BE", "secondary": "#28A745", "accent": "#FFC107"},
            "medicine": {"primary": "#DC143C", "secondary": "#FFFFFF", "accent": "#FF6B6B"},
            "law": {"primary": "#1E3A8A", "secondary": "#D4AF37", "accent": "#FFFFFF"},
            "business": {"primary": "#1F2937", "secondary": "#3B82F6", "accent": "#10B981"},
            "education": {"primary": "#7C3AED", "secondary": "#F59E0B", "accent": "#EF4444"},
            "social_work": {"primary": "#059669", "secondary": "#F97316", "accent": "#8B5CF6"}
        }
        return color_schemes.get(field.lower(), {"primary": "#1E40AF", "secondary": "#64748B", "accent": "#F59E0B"})

    def _create_pptx_structure(self, slide_data: List[Dict]) -> Dict[str, Any]:
        """Create PowerPoint-compatible structure."""
        return {
            "presentation": {
                "title": slide_data[0].get("title", "Presentation") if slide_data else "Presentation",
                "slide_count": len(slide_data),
                "theme": "academic_professional",
                "slides": slide_data
            },
            "export_formats": ["pptx", "pdf", "html"],
            "template_options": {
                "font_family": "Arial",
                "font_size_title": 28,
                "font_size_content": 18,
                "font_size_bullets": 16
            }
        }

    def _create_infographic_structure(self, infographic_data: Dict) -> Dict[str, Any]:
        """Create infographic structure for design tools."""
        return {
            "format": "infographic",
            "dimensions": {"width": 800, "height": 1200},
            "sections": [
                {
                    "type": "header",
                    "content": infographic_data.get("title", "Research Overview"),
                    "position": {"x": 0, "y": 0, "width": 800, "height": 100}
                },
                {
                    "type": "statistics",
                    "content": infographic_data.get("statistics", []),
                    "position": {"x": 50, "y": 120, "width": 700, "height": 300}
                },
                {
                    "type": "process",
                    "content": infographic_data.get("processes", []),
                    "position": {"x": 50, "y": 440, "width": 700, "height": 400}
                },
                {
                    "type": "key_takeaways",
                    "content": infographic_data.get("key_takeaways", []),
                    "position": {"x": 50, "y": 860, "width": 700, "height": 200}
                }
            ],
            "styling": {
                "colors": infographic_data.get("color_scheme", {}),
                "theme": infographic_data.get("visual_theme", "academic"),
                "fonts": ["Arial", "Helvetica", "Open Sans"]
            },
            "export_formats": ["png", "jpg", "svg", "pdf"]
        }

    def _create_pptx_presentation(self, pptx_structure: Dict[str, Any]) -> str:
        """Create a .pptx presentation from the structured data."""
        from pptx import Presentation

        prs = Presentation()

        # Title Slide
        title_slide_layout = prs.slide_layouts[0]
        slide = prs.slides.add_slide(title_slide_layout)
        title = slide.shapes.title
        subtitle = slide.placeholders[1]
        title.text = pptx_structure["presentation"]["slides"][0]["title"]
        subtitle.text = pptx_structure["presentation"]["slides"][0]["subtitle"]

        # Content Slides
        for slide_data in pptx_structure["presentation"]["slides"][1:]:
            content_slide_layout = prs.slide_layouts[1]
            slide = prs.slides.add_slide(content_slide_layout)
            title = slide.shapes.title
            body = slide.shapes.placeholders[1]
            title.text = slide_data["title"]

            tf = body.text_frame
            tf.clear()

            if slide_data.get("content"):
                p = tf.add_paragraph()
                p.text = slide_data["content"]
                p.level = 0

            for bullet_point in slide_data.get("bullet_points", []):
                p = tf.add_paragraph()
                p.text = bullet_point
                p.level = 1

        # Save presentation
        import os
        import uuid

        upload_dir = os.getenv("UPLOAD_DIR", "/tmp/uploads")
        os.makedirs(upload_dir, exist_ok=True)
        file_path = os.path.join(upload_dir, f"presentation_{uuid.uuid4()}.pptx")
        prs.save(file_path)

        return file_path
