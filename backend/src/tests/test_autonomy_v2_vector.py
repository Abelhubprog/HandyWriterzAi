from backend.src.autonomy_v2.memory.vector_repo import VectorRepo


def test_vector_upsert_and_search():
    run_id = "v2-vectest"
    repo = VectorRepo(run_id)

    import asyncio

    async def _run():
        await repo.upsert_chunks([
            {"text": "alpha test chunk", "url": "https://example.com/a"},
            {"text": "beta sample chunk", "url": "https://example.com/b"},
        ])
        res = await repo.search("alpha", k=5)
        return res

    res = asyncio.get_event_loop().run_until_complete(_run())
    assert isinstance(res, list)
    assert any("alpha" in r.get("text", "").lower() for r in res)
    assert any(r.get("url") for r in res)

