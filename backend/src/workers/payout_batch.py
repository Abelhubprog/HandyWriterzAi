import os
import schedule
import time
from sqlalchemy import create_engine, select, update
from sqlalchemy.orm import sessionmaker
# Assuming your models are defined in db.models
from db.models import CheckerPayout, Checker
# Assuming you have an escrow utility
# from lib.escrow import releaseUSDC

# --- Configuration ---
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@host:port/database")
ESCROW_CONTRACT_ADDR = os.getenv("ESCROW_CONTRACT_ADDR")

# --- Database Setup ---
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def process_pending_payouts():
    """
    Processes all pending checker payouts.
    - Fetches pending payouts.
    - Calls the escrow contract to release funds.
    - Updates the payout status to 'paid' or 'failed'.
    """
    db = SessionLocal()
    try:
        # Select pending payouts and join with checker to get wallet address
        stmt = (
            select(CheckerPayout, Checker.wallet_address)
            .join(Checker, CheckerPayout.checker_id == Checker.id)
            .where(CheckerPayout.status == 'pending')
        )
        pending_payouts = db.execute(stmt).all()

        if not pending_payouts:
            print("No pending payouts to process.")
            return

        print(f"Found {len(pending_payouts)} pending payouts to process.")

        for payout, wallet_address in pending_payouts:
            print(f"Processing payout {payout.id} for checker {payout.checker_id} to wallet {wallet_address} for amount {payout.amount_pence} pence.")

            try:
                # --- Escrow Integration (Stubbed) ---
                # In a real implementation, you would call your escrow contract function here.
                # This function would need to handle the conversion from pence to the
                # appropriate token denomination.
                # For example:
                # tx_hash = releaseUSDC(ESCROW_CONTRACT_ADDR, wallet_address, payout.amount_pence)
                # For this stub, we'll just simulate a success.
                print(f"TODO: Call escrow contract {ESCROW_CONTRACT_ADDR} to release {payout.amount_pence} pence to {wallet_address}")
                tx_hash = f"0x_simulated_tx_{payout.id}"
                # --- End Escrow Integration ---

                # Update the payout status to 'paid' and store the transaction hash
                update_stmt = (
                    update(CheckerPayout)
                    .where(CheckerPayout.id == payout.id)
                    .values(status='paid', transaction_hash=tx_hash)
                )
                db.execute(update_stmt)
                print(f"Successfully processed payout {payout.id}. Tx: {tx_hash}")

            except Exception as e:
                # If the escrow call fails, mark the payout as 'failed'
                print(f"Failed to process payout {payout.id} for checker {payout.checker_id}. Error: {e}")
                update_stmt = (
                    update(CheckerPayout)
                    .where(CheckerPayout.id == payout.id)
                    .values(status='failed')
                )
                db.execute(update_stmt)

        db.commit()

    except Exception as e:
        print(f"An error occurred during the payout batch process: {e}")
        db.rollback()
    finally:
        db.close()

def run_scheduler():
    """Sets up and runs the job scheduler."""
    # Schedule the job to run every day at a specific time, e.g., 2 AM
    schedule.every().day.at("02:00").do(process_pending_payouts)
    print("Payout batch scheduler started. Will run every day at 2:00 AM.")

    while True:
        schedule.run_pending()
        time.sleep(60) # Check every minute

if __name__ == "__main__":
    print("Starting payout batch worker...")
    # For testing, you can run the process directly
    # process_pending_payouts()
    run_scheduler()