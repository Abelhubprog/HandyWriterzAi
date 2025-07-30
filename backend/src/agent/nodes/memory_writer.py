import json
from datetime import datetime
from typing import Dict, Any
from opentelemetry import trace

tracer = trace.get_tracer(__name__)

from ..base import BaseNode
from ..handywriterz_state import HandyWriterzState
from src.services.supabase_service import get_supabase_client

class MemoryWriter(BaseNode):
    """
    A node that analyzes the final draft to create or update a user's
    writing fingerprint (memory) and stores it in Supabase.
    """

    def __init__(self, name: str):
        super().__init__(name)
        self.supabase = get_supabase_client()

    def execute(self, state: HandyWriterzState) -> Dict[str, Any]:
        """
        Analyzes the draft, calculates fingerprint metrics, and saves to Supabase.
        """
        with tracer.start_as_current_span("memory_writer_node") as span:
            span.set_attribute("user_id", state.get("user_id"))
            print("🧠 Executing MemoryWriter Node")
        final_draft = state.get("final_draft_content")
        user_id = state.get("user_id")

        if not final_draft or not user_id:
            print("⚠️ MemoryWriter: Missing final_draft or user_id, skipping.")
            return {}

        try:
            # 1. Calculate fingerprint metrics
            fingerprint = self._calculate_fingerprint(final_draft)
            print(f"Calculated fingerprint for user {user_id}: {fingerprint}")

            # 2. Get existing fingerprint from Supabase
            existing_record = self.supabase.table("memories").select("*").eq("user_id", user_id).single().execute()
            
            if existing_record.data:
                # 3a. Merge with existing fingerprint (moving average)
                updated_fingerprint = self._merge_fingerprints(
                    json.loads(existing_record.data['fingerprint_json']), 
                    fingerprint
                )
                print(f"Merged fingerprint: {updated_fingerprint}")
                self.supabase.table("memories").update({
                    "fingerprint_json": json.dumps(updated_fingerprint),
                    "updated_at": datetime.utcnow().isoformat()
                }).eq("user_id", user_id).execute()
            else:
                # 3b. Create new fingerprint record
                updated_fingerprint = fingerprint
                self.supabase.table("memories").insert({
                    "user_id": user_id,
                    "fingerprint_json": json.dumps(updated_fingerprint),
                    "created_at": datetime.utcnow().isoformat(),
                    "updated_at": datetime.utcnow().isoformat()
                }).execute()

            print(f"✅ Successfully wrote memory for user {user_id}")
            return {"writing_fingerprint": updated_fingerprint}

        except Exception as e:
            print(f"❌ MemoryWriter Error: {e}")
            # Non-critical error, so we don't block the workflow
            return {"writing_fingerprint": None}

    def _calculate_fingerprint(self, text: str) -> Dict[str, Any]:
        """Calculates writing style metrics from a given text."""
        words = text.split()
        sentences = text.split('.')
        word_count = len(words)
        sentence_count = len(sentences)

        if word_count == 0 or sentence_count == 0:
            return {
                "avg_sentence_len": 0,
                "lexical_diversity": 0,
                "citation_density": 0,
            }

        # Average sentence length
        avg_sentence_len = word_count / sentence_count

        # Lexical diversity (Type-Token Ratio)
        lexical_diversity = len(set(words)) / word_count if word_count > 0 else 0
        
        # Citation density (simple placeholder)
        citations = text.count("(") + text.count("[")
        citation_density = citations / sentence_count if sentence_count > 0 else 0

        return {
            "avg_sentence_len": round(avg_sentence_len, 2),
            "lexical_diversity": round(lexical_diversity, 3),
            "citation_density": round(citation_density, 3),
        }

    def _merge_fingerprints(self, old_fp: Dict, new_fp: Dict, alpha: float = 0.3) -> Dict:
        """
        Merges new fingerprint into old one using an exponential moving average.
        alpha is the weight given to the new value.
        """
        merged = {}
        for key in old_fp:
            if key in new_fp:
                merged[key] = round((1 - alpha) * old_fp[key] + alpha * new_fp[key], 3)
            else:
                merged[key] = old_fp[key]
        return merged