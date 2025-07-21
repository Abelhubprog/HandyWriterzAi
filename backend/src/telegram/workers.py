"""
Worker processes for Turnitin document processing.
"""

import asyncio
import logging
import uuid
from pathlib import Path
from typing import List, Dict, Any

from docx import Document
import PyPDF2
import aiofiles

logger = logging.getLogger(__name__)


class TurnitinWorker:
    """Worker for processing documents through Turnitin-like checks."""
    
    def __init__(self):
        self.chunk_size = 350  # words per chunk
        self.turnitin_api_url = "https://api.turnitin.com"  # Mock URL
        
    async def split_document(self, file_path: str) -> List[Dict[str, Any]]:
        """Split document into 350-word chunks."""
        
        try:
            # Extract text based on file type
            file_ext = Path(file_path).suffix.lower()
            
            if file_ext == '.docx':
                text = await self._extract_docx_text(file_path)
            elif file_ext == '.pdf':
                text = await self._extract_pdf_text(file_path)
            elif file_ext == '.txt':
                text = await self._extract_txt_text(file_path)
            else:
                raise ValueError(f"Unsupported file type: {file_ext}")
            
            # Split into chunks
            chunks = await self._split_text_into_chunks(text)
            
            logger.info(f"Split document into {len(chunks)} chunks")
            return chunks
            
        except Exception as e:
            logger.error(f"Error splitting document {file_path}: {e}")
            raise

    async def _extract_docx_text(self, file_path: str) -> str:
        """Extract text from DOCX file."""
        try:
            doc = Document(file_path)
            paragraphs = [paragraph.text for paragraph in doc.paragraphs]
            return '\n'.join(paragraphs)
        except Exception as e:
            logger.error(f"Error extracting DOCX text: {e}")
            raise

    async def _extract_pdf_text(self, file_path: str) -> str:
        """Extract text from PDF file."""
        try:
            text = ""
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                for page in pdf_reader.pages:
                    text += page.extract_text() + "\n"
            return text
        except Exception as e:
            logger.error(f"Error extracting PDF text: {e}")
            raise

    async def _extract_txt_text(self, file_path: str) -> str:
        """Extract text from TXT file."""
        try:
            async with aiofiles.open(file_path, 'r', encoding='utf-8') as file:
                return await file.read()
        except Exception as e:
            logger.error(f"Error extracting TXT text: {e}")
            raise

    async def _split_text_into_chunks(self, text: str) -> List[Dict[str, Any]]:
        """Split text into 350-word chunks."""
        
        words = text.split()
        chunks = []
        
        for i in range(0, len(words), self.chunk_size):
            chunk_words = words[i:i + self.chunk_size]
            chunk_text = ' '.join(chunk_words)
            
            chunks.append({
                'content': chunk_text,
                'word_count': len(chunk_words),
                'chunk_number': len(chunks) + 1
            })
        
        return chunks

    async def run_turnitin_check(self, text: str, chunk_id: str) -> Dict[str, Any]:
        """Run Turnitin-like check on text chunk."""
        
        try:
            # For demo purposes, we'll simulate Turnitin API calls
            # In production, this would integrate with actual Turnitin API
            
            logger.info(f"Starting Turnitin check for chunk {chunk_id}")
            
            # Simulate processing time
            await asyncio.sleep(2)
            
            # Mock Turnitin analysis
            result = await self._mock_turnitin_analysis(text, chunk_id)
            
            logger.info(f"Completed Turnitin check for chunk {chunk_id}")
            return result
            
        except Exception as e:
            logger.error(f"Error in Turnitin check for chunk {chunk_id}: {e}")
            raise

    async def _mock_turnitin_analysis(self, text: str, chunk_id: str) -> Dict[str, Any]:
        """Mock Turnitin analysis for development/testing."""
        
        import random
        import hashlib
        
        # Generate deterministic but random-looking scores based on text hash
        text_hash = hashlib.md5(text.encode()).hexdigest()
        random.seed(int(text_hash[:8], 16))
        
        # Generate scores (biased toward low scores for realistic results)
        similarity_score = random.betavariate(2, 5) * 100  # Biased toward low
        ai_score = random.betavariate(1.5, 4) * 100  # Biased toward low
        
        # Generate flagged text spans (randomly select phrases)
        words = text.split()
        flagged_text = []
        
        # Randomly flag some phrases if scores are high
        if similarity_score > 30 or ai_score > 25:
            num_flags = random.randint(1, 3)
            for _ in range(num_flags):
                start_idx = random.randint(0, max(0, len(words) - 10))
                end_idx = min(start_idx + random.randint(3, 8), len(words))
                phrase = ' '.join(words[start_idx:end_idx])
                flagged_text.append(phrase)
        
        # Generate mock PDF URLs (in production, these would be real file uploads)
        similarity_pdf_url = f"/api/files/turnitin/{chunk_id}_similarity.pdf"
        ai_pdf_url = f"/api/files/turnitin/{chunk_id}_ai_detection.pdf"
        
        # Create mock PDF files
        await self._create_mock_pdfs(
            text, chunk_id, similarity_score, ai_score, flagged_text
        )
        
        return {
            'similarity_score': round(similarity_score, 1),
            'ai_score': round(ai_score, 1),
            'flagged_text': flagged_text,
            'similarity_pdf_url': similarity_pdf_url,
            'ai_pdf_url': ai_pdf_url,
            'analysis_metadata': {
                'processed_at': asyncio.get_event_loop().time(),
                'word_count': len(words),
                'processing_version': '1.0'
            }
        }

    async def _create_mock_pdfs(
        self, 
        text: str, 
        chunk_id: str, 
        sim_score: float, 
        ai_score: float, 
        flagged_text: List[str]
    ):
        """Create mock Turnitin PDF reports."""
        
        try:
            # Ensure directories exist
            pdf_dir = Path("/tmp/turnitin_pdfs")
            pdf_dir.mkdir(exist_ok=True)
            
            # Create similarity report PDF
            sim_pdf_path = pdf_dir / f"{chunk_id}_similarity.pdf"
            await self._generate_similarity_pdf(
                text, sim_score, flagged_text, sim_pdf_path
            )
            
            # Create AI detection report PDF
            ai_pdf_path = pdf_dir / f"{chunk_id}_ai_detection.pdf"
            await self._generate_ai_pdf(
                text, ai_score, flagged_text, ai_pdf_path
            )
            
            logger.info(f"Created mock PDFs for chunk {chunk_id}")
            
        except Exception as e:
            logger.error(f"Error creating mock PDFs: {e}")
            # Don't raise - PDFs are optional for development

    async def _generate_similarity_pdf(
        self, 
        text: str, 
        score: float, 
        flagged_text: List[str], 
        output_path: Path
    ):
        """Generate mock similarity report PDF."""
        
        try:
            from reportlab.pdfgen import canvas
            from reportlab.lib.pagesizes import letter
            from reportlab.lib.colors import red, black
            
            c = canvas.Canvas(str(output_path), pagesize=letter)
            width, height = letter
            
            # Title
            c.setFont("Helvetica-Bold", 16)
            c.drawString(50, height - 50, "Turnitin Similarity Report")
            
            # Score
            c.setFont("Helvetica", 12)
            score_color = red if score > 20 else black
            c.setFillColor(score_color)
            c.drawString(50, height - 80, f"Overall Similarity: {score:.1f}%")
            
            # Text with highlighting
            c.setFillColor(black)
            c.setFont("Helvetica", 10)
            
            y_pos = height - 120
            words = text.split()
            line_words = []
            
            for word in words:
                # Check if word is in flagged text
                is_flagged = any(word in flag for flag in flagged_text)
                
                line_words.append((word, is_flagged))
                
                # Break line if too long
                if len(' '.join([w[0] for w in line_words])) > 80:
                    await self._draw_line_with_highlights(c, line_words, 50, y_pos)
                    y_pos -= 15
                    line_words = []
                    
                    if y_pos < 50:  # New page
                        c.showPage()
                        y_pos = height - 50
            
            # Draw remaining words
            if line_words:
                await self._draw_line_with_highlights(c, line_words, 50, y_pos)
            
            c.save()
            
        except ImportError:
            # reportlab not available, create simple text file
            async with aiofiles.open(output_path.with_suffix('.txt'), 'w') as f:
                await f.write(f"Similarity Report\nScore: {score:.1f}%\n\nText:\n{text}")

    async def _generate_ai_pdf(
        self, 
        text: str, 
        score: float, 
        flagged_text: List[str], 
        output_path: Path
    ):
        """Generate mock AI detection report PDF."""
        
        try:
            from reportlab.pdfgen import canvas
            from reportlab.lib.pagesizes import letter
            from reportlab.lib.colors import red, black
            
            c = canvas.Canvas(str(output_path), pagesize=letter)
            width, height = letter
            
            # Title
            c.setFont("Helvetica-Bold", 16)
            c.drawString(50, height - 50, "AI Detection Report")
            
            # Score
            c.setFont("Helvetica", 12)
            score_color = red if score > 25 else black
            c.setFillColor(score_color)
            c.drawString(50, height - 80, f"AI Detection Score: {score:.1f}%")
            
            # Analysis details
            c.setFillColor(black)
            c.setFont("Helvetica", 10)
            c.drawString(50, height - 110, f"Flagged Segments: {len(flagged_text)}")
            
            # List flagged text
            y_pos = height - 140
            for i, flag in enumerate(flagged_text[:5]):  # Max 5 examples
                c.drawString(70, y_pos, f"{i+1}. {flag[:60]}...")
                y_pos -= 15
            
            c.save()
            
        except ImportError:
            # reportlab not available, create simple text file
            async with aiofiles.open(output_path.with_suffix('.txt'), 'w') as f:
                await f.write(f"AI Detection Report\nScore: {score:.1f}%\n\nFlagged: {flagged_text}")

    async def _draw_line_with_highlights(self, canvas, line_words, x, y):
        """Draw a line with highlighted flagged words."""
        
        current_x = x
        
        for word, is_flagged in line_words:
            if is_flagged:
                # Highlight flagged words
                canvas.setFillColor("red")
                canvas.rect(current_x - 2, y - 2, len(word) * 6 + 4, 12, fill=1)
                canvas.setFillColor("white")
                canvas.drawString(current_x, y, word)
                canvas.setFillColor("black")
            else:
                canvas.drawString(current_x, y, word)
            
            current_x += len(word) * 6 + 6  # Approximate character width

    async def batch_process_chunks(self, chunks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Process multiple chunks in parallel."""
        
        # Limit concurrent processing
        semaphore = asyncio.Semaphore(5)
        
        async def process_single_chunk(chunk_data):
            async with semaphore:
                return await self.run_turnitin_check(
                    chunk_data['content'], 
                    chunk_data.get('id', str(uuid.uuid4()))
                )
        
        # Process all chunks
        tasks = [process_single_chunk(chunk) for chunk in chunks]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Filter out exceptions and log errors
        successful_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                logger.error(f"Error processing chunk {i}: {result}")
            else:
                successful_results.append(result)
        
        return successful_results


class DocumentSplitter:
    """Utility class for splitting documents into chunks."""
    
    @staticmethod
    async def split_by_paragraphs(text: str, max_words: int = 350) -> List[str]:
        """Split text by paragraphs, keeping under word limit."""
        
        paragraphs = text.split('\n\n')
        chunks = []
        current_chunk = []
        current_word_count = 0
        
        for paragraph in paragraphs:
            para_words = len(paragraph.split())
            
            if current_word_count + para_words <= max_words:
                current_chunk.append(paragraph)
                current_word_count += para_words
            else:
                # Finish current chunk
                if current_chunk:
                    chunks.append('\n\n'.join(current_chunk))
                
                # Start new chunk
                if para_words <= max_words:
                    current_chunk = [paragraph]
                    current_word_count = para_words
                else:
                    # Split large paragraph
                    sub_chunks = await DocumentSplitter._split_large_paragraph(
                        paragraph, max_words
                    )
                    chunks.extend(sub_chunks[:-1])
                    current_chunk = [sub_chunks[-1]] if sub_chunks else []
                    current_word_count = len(sub_chunks[-1].split()) if sub_chunks else 0
        
        # Add final chunk
        if current_chunk:
            chunks.append('\n\n'.join(current_chunk))
        
        return chunks
    
    @staticmethod
    async def _split_large_paragraph(paragraph: str, max_words: int) -> List[str]:
        """Split a large paragraph into smaller chunks."""
        
        words = paragraph.split()
        chunks = []
        
        for i in range(0, len(words), max_words):
            chunk_words = words[i:i + max_words]
            chunks.append(' '.join(chunk_words))
        
        return chunks