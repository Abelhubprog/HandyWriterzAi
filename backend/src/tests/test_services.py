import pytest
from backend.src.services.model_service import model_service, BudgetExceeded
from backend.src.services.chunk_splitter import chunk_splitter
from backend.src.services.embedding_service import embedding_service
from backend.src.services.vector_storage import vector_storage
from backend.src.api.schemas.worker import ChunkMessage

def test_get_model():
    client = model_service.get("writer")
    assert client is not None
    assert client.model_id == "gemini-pro-25"

def test_price_guard():
    with pytest.raises(BudgetExceeded):
        model_service.price_guard.charge("writer", "gemini-pro-25", {"input": 1000000, "output": 1000000}, model_service.price_table)

@pytest.mark.asyncio
async def test_chunk_splitter():
    chunks = await chunk_splitter._split_simple_word_count("This is a test.", "test_lot")
    assert len(chunks) > 0
    assert chunks[0].word_count > 0

@pytest.mark.asyncio
async def test_embedding_service():
    embedding = await embedding_service.embed_text("This is a test.")
    assert len(embedding) == 1536

@pytest.mark.asyncio
async def test_vector_storage():
    await vector_storage.store_chunks("test_file", ["chunk1", "chunk2"], [[0.1, 0.2], [0.3, 0.4]])
    results = await vector_storage.retrieve_chunks([0.1, 0.2])
    assert len(results) > 0

def test_chunk_message_schema():
    data = {"doc_id": "123", "chunk_id": 1, "text": "test", "embedding": [0.1, 0.2]}
    msg = ChunkMessage.model_validate(data)
    assert msg.doc_id == "123"
    assert msg.chunk_id == 1
    assert msg.text == "test"
    assert msg.embedding == [0.1, 0.2]
