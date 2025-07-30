from typing import Dict, Any
from src.agent.base import BaseNode
from ...agent.handywriterz_state import HandyWriterzState
from utils.arweave import upload_to_arweave

class Arweave(BaseNode):
    """
    A node that uploads the final document to Arweave to create an
    immutable authorship proof.
    """

    def __init__(self, name: str):
        super().__init__(name)

    async def execute(self, state: HandyWriterzState) -> Dict[str, Any]:
        """
        Uploads the final DOCX to Arweave and returns the transaction ID.
        """
        print("🔗 Executing Arweave Node")
        final_docx = state.get("final_docx_content") # Assuming the docx content is in the state

        if not final_docx:
            print("⚠️ Arweave: Missing final_docx_content, skipping.")
            return {}

        try:
            transaction_id = await upload_to_arweave(final_docx)

            if transaction_id:
                print(f"✅ Successfully uploaded to Arweave. Tx ID: {transaction_id}")
                return {"arweave_transaction_id": transaction_id}
            else:
                print("❌ Arweave upload returned no transaction ID.")
                return {"arweave_transaction_id": None}

        except Exception as e:
            print(f"❌ Arweave Error: {e}")
            return {"arweave_transaction_id": None}