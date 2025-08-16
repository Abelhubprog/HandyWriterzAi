SYSTEM
Implement memory repositories with minimal working logic. Keep chunking and embeddings consistent with existing services.

USER
Objective: Implement:
- memory/episodic_repo.py: write_event(run_id, role, content), list_events(run_id)
- memory/semantic_repo.py: distill/run summaries
- memory/vector_repo.py: upsert_chunks([{text,url}]) using services/embedding_service.py and vector_storage.py

Constraints:
- Respect existing embedding/pgvector config and batching sizes.
- Ensure writes are idempotent.

TODOs:
1) Implement episodic repo against episodic_logs.
2) Implement vector repo using existing embedding_service and vector_storage (or add adapters).
3) Update agents/researcher.py to actually call web_search.py and upsert_chunks() then annotate sources in Observation.

Acceptance:
- Diffs for memory modules + researcher updates.
- A small test that upserts and retrieves one chunk.

SYSTEM
Implement vector memory and connect the Researcher to ingest sources and attach citations.

USER
Tasks:
1) Implement `backend/src/autonomy_v2/memory/vector_repo.py`:
   - upsert_chunks(run_id, chunks:[{text, url?}]) using existing services/embedding_service.py and services/vector_storage.py
   - search(query, k=5) returning [{text,url,score}]
2) Implement `backend/src/autonomy_v2/memory/semantic_repo.py`:
   - distill(run_id, notes: str) → store a short note in autonomy_semantic_notes (embedding optional first pass)
3) Update `backend/src/autonomy_v2/agents/researcher.py`:
   - on expand/initial research: call tools/web_search.search, upsert results into vector_repo, return Observation with sources (URLs).
4) Update `backend/src/autonomy_v2/agents/executor.py`:
   - when executing “research” step, call vector_repo.search first; if weak results, call web_search and upsert; always populate Observation.sources.

Acceptance:
- Diffs for both repos and agent updates.
- A simple test under backend/src/tests or autonomy_v2/evaluation: upsert two chunks and confirm search returns them with scores.
