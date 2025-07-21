import pytest
import asyncio
from pathlib import Path
from docx import Document as DocxDocument
from fpdf import FPDF

from src.services.chunk_splitter import ChunkSplitter, SplitConfig, SplitStrategy

# Sample academic text to be used in test documents
ACADEMIC_TEXT = """
The study of artificial intelligence (AI) has profound implications for modern society.
As noted by Turing (1950), the fundamental question is not whether machines can think, but whether they can imitate human intelligence convincingly. This has led to numerous developments in machine learning and natural language processing.

Recent advancements in large language models (LLMs) have accelerated this field significantly. For instance, the transformer architecture (Vaswani et al., 2017) has become a cornerstone of modern NLP. These models can generate coherent and contextually relevant text, raising ethical questions about their use in academic and professional writing. It is crucial to establish clear guidelines for their application (Johnson & Lee, 2023).

Methodologically, our research employs a qualitative analysis of 50 peer-reviewed articles published between 2020 and 2024. The primary goal is to identify emerging themes in AI ethics. This approach allows for a deep, nuanced understanding of the subject matter. We believe this work contributes significantly to the ongoing discourse.
"""

@pytest.fixture
def temp_test_docs(tmp_path: Path) -> Path:
    """Create temporary test documents (PDF and DOCX) for testing."""
    # Create DOCX
    docx_path = tmp_path / "test_document.docx"
    doc = DocxDocument()
    doc.add_paragraph(ACADEMIC_TEXT)
    doc.save(docx_path)

    # Create PDF
    pdf_path = tmp_path / "test_document.pdf"
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.multi_cell(0, 10, ACADEMIC_TEXT)
    pdf.output(pdf_path)

    return tmp_path

@pytest.mark.asyncio
async def test_split_document_with_agentic_doc_pdf(temp_test_docs: Path):
    """
    Tests the chunk splitter's PDF processing using the new agentic-doc pipeline.
    """
    pdf_path = temp_test_docs / "test_document.pdf"
    
    # Configure the splitter to use a smart strategy
    config = SplitConfig(strategy=SplitStrategy.CITATION_AWARE)
    splitter = ChunkSplitter(config=config)

    # Act
    result = await splitter.split_document(
        file_path=str(pdf_path),
        file_type='pdf',
        document_title="Test PDF Document",
        user_id="test_user"
    )

    # Assert
    assert result is not None
    assert result.total_chunks > 0
    assert result.total_words > 100
    # Check that a smart strategy was chosen, not a simple fallback
    assert result.strategy_used in [SplitStrategy.CITATION_AWARE, SplitStrategy.PARAGRAPH_BOUNDARY]
    # Assert that the quality of the split is high
    assert result.split_quality_score > 0.7

    # Clean up the splitter's resources if it has a close method
    if hasattr(splitter, 'close'):
        await splitter.close()

@pytest.mark.asyncio
async def test_split_document_with_agentic_doc_docx(temp_test_docs: Path):
    """
    Tests the chunk splitter's DOCX processing using the new agentic-doc pipeline.
    """
    docx_path = temp_test_docs / "test_document.docx"

    # Configure the splitter
    config = SplitConfig(strategy=SplitStrategy.PARAGRAPH_BOUNDARY)
    splitter = ChunkSplitter(config=config)

    # Act
    result = await splitter.split_document(
        file_path=str(docx_path),
        file_type='docx',
        document_title="Test DOCX Document",
        user_id="test_user"
    )

    # Assert
    assert result is not None
    assert result.total_chunks > 0
    assert result.total_words > 100
    assert result.strategy_used == SplitStrategy.PARAGRAPH_BOUNDARY
    assert result.split_quality_score > 0.8  # Expect high quality for clean paragraph splitting

    # Clean up
    if hasattr(splitter, 'close'):
        await splitter.close()
