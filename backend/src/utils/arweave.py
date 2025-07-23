import os
import hashlib
from arweave.arweave_lib import Wallet, Transaction

# TODO( fill-secret ): Load Arweave private key from environment
ARWEAVE_WALLET_FILE = os.getenv("ARWEAVE_WALLET_FILE")

def get_arweave_wallet() -> Wallet:
    """Loads the Arweave wallet from a file."""
    if not ARWEAVE_WALLET_FILE:
        raise ValueError("ARWEAVE_WALLET_FILE environment variable not set.")
    return Wallet(ARWEAVE_WALLET_FILE)

def hash_data(data: bytes) -> str:
    """Creates a SHA-256 hash of the given data."""
    return hashlib.sha256(data).hexdigest()

def create_arweave_transaction(data: bytes, wallet: Wallet) -> Transaction:
    """Creates an Arweave transaction for the given data."""
    tx = Transaction(wallet, data=data)
    tx.add_tag('Content-Type', 'application/octet-stream')
    tx.add_tag('App-Name', 'HandyWriterz')
    tx.add_tag('App-Version', '2.0.0')
    tx.add_tag('Content-Hash', hash_data(data))
    return tx

async def upload_to_arweave(data: bytes) -> str:
    """
    Hashes the data, creates an Arweave transaction, signs it, and uploads it.
    Returns the transaction ID.
    """
    try:
        wallet = get_arweave_wallet()
        transaction = create_arweave_transaction(data, wallet)
        transaction.sign()
        await transaction.send()
        return transaction.id
    except Exception as e:
        print(f"❌ Arweave upload failed: {e}")
        return ""