"""
USDC escrow system for Turnitin Checker payments.
"""

import logging
from decimal import Decimal
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone

from web3 import Web3
from eth_account import Account
from eth_account.messages import encode_defunct

from ..models.turnitin import WalletEscrow, CheckerPayout, DocLot, PayoutStatus
from ..db.database import get_db_session

logger = logging.getLogger(__name__)


class USDCEscrowManager:
    """Manages USDC escrow for Turnitin checker payments."""
    
    def __init__(
        self, 
        rpc_url: str,
        usdc_contract_address: str,
        escrow_contract_address: str,
        private_key: str
    ):
        self.w3 = Web3(Web3.HTTPProvider(rpc_url))
        self.usdc_address = Web3.toChecksumAddress(usdc_contract_address)
        self.escrow_address = Web3.toChecksumAddress(escrow_contract_address)
        self.account = Account.from_key(private_key)
        
        # USDC contract ABI (simplified)
        self.usdc_abi = [
            {
                "constant": True,
                "inputs": [{"name": "_owner", "type": "address"}],
                "name": "balanceOf",
                "outputs": [{"name": "balance", "type": "uint256"}],
                "type": "function"
            },
            {
                "constant": False,
                "inputs": [
                    {"name": "_to", "type": "address"},
                    {"name": "_value", "type": "uint256"}
                ],
                "name": "transfer",
                "outputs": [{"name": "", "type": "bool"}],
                "type": "function"
            },
            {
                "constant": False,
                "inputs": [
                    {"name": "_from", "type": "address"},
                    {"name": "_to", "type": "address"},
                    {"name": "_value", "type": "uint256"}
                ],
                "name": "transferFrom",
                "outputs": [{"name": "", "type": "bool"}],
                "type": "function"
            },
            {
                "constant": True,
                "inputs": [
                    {"name": "_owner", "type": "address"},
                    {"name": "_spender", "type": "address"}
                ],
                "name": "allowance",
                "outputs": [{"name": "", "type": "uint256"}],
                "type": "function"
            }
        ]
        
        self.usdc_contract = self.w3.eth.contract(
            address=self.usdc_address,
            abi=self.usdc_abi
        )

    async def create_escrow(
        self, 
        user_wallet: str, 
        lot_id: str, 
        amount_usdc: Decimal,
        permit_signature: Optional[str] = None
    ) -> Dict[str, Any]:
        """Create escrow for a document lot."""
        
        try:
            # Convert USDC amount to wei (6 decimals for USDC)
            amount_wei = int(amount_usdc * 10**6)
            
            # Validate user has sufficient balance
            balance = await self._get_usdc_balance(user_wallet)
            if balance < amount_wei:
                raise ValueError(f"Insufficient USDC balance: {balance/10**6} < {amount_usdc}")
            
            # Create database record
            db = next(get_db_session())
            try:
                escrow = WalletEscrow(
                    user_wallet=user_wallet,
                    lot_id=lot_id,
                    amount_usdc=amount_usdc,
                    contract_address=self.escrow_address,
                    permit_signature=permit_signature
                )
                db.add(escrow)
                db.commit()
                
                # Execute blockchain transaction
                tx_hash = await self._transfer_to_escrow(
                    user_wallet, amount_wei, permit_signature
                )
                
                logger.info(f"Created escrow {escrow.id} for lot {lot_id}: {amount_usdc} USDC")
                
                return {
                    'escrow_id': escrow.id,
                    'transaction_hash': tx_hash,
                    'amount_usdc': float(amount_usdc),
                    'status': 'locked'
                }
                
            finally:
                db.close()
                
        except Exception as e:
            logger.error(f"Error creating escrow: {e}")
            raise

    async def release_payments(self, lot_id: str) -> List[Dict[str, Any]]:
        """Release payments to checkers for completed lot."""
        
        try:
            db = next(get_db_session())
            try:
                # Get pending payouts for this lot
                pending_payouts = db.query(CheckerPayout).join(
                    DocLot, CheckerPayout.chunk_id.in_(
                        db.query(DocLot.id).filter(DocLot.id == lot_id)
                    )
                ).filter(
                    CheckerPayout.status == PayoutStatus.PENDING
                ).all()
                
                if not pending_payouts:
                    return []
                
                results = []
                
                # Process each payout
                for payout in pending_payouts:
                    try:
                        tx_hash = await self._transfer_from_escrow(
                            payout.checker.wallet_address,
                            int(payout.amount_usdc * 10**6)
                        )
                        
                        # Update payout status
                        payout.status = PayoutStatus.PAID
                        payout.transaction_hash = tx_hash
                        payout.paid_at = datetime.now(timezone.utc)
                        
                        results.append({
                            'payout_id': payout.id,
                            'checker_wallet': payout.checker.wallet_address,
                            'amount_usdc': float(payout.amount_usdc),
                            'transaction_hash': tx_hash,
                            'status': 'paid'
                        })
                        
                        logger.info(f"Paid {payout.amount_usdc} USDC to {payout.checker.wallet_address}")
                        
                    except Exception as e:
                        # Mark payout as failed
                        payout.status = PayoutStatus.FAILED
                        payout.error_message = str(e)
                        
                        results.append({
                            'payout_id': payout.id,
                            'checker_wallet': payout.checker.wallet_address,
                            'amount_usdc': float(payout.amount_usdc),
                            'status': 'failed',
                            'error': str(e)
                        })
                        
                        logger.error(f"Failed to pay {payout.checker.wallet_address}: {e}")
                
                db.commit()
                return results
                
            finally:
                db.close()
                
        except Exception as e:
            logger.error(f"Error releasing payments for lot {lot_id}: {e}")
            raise

    async def _get_usdc_balance(self, wallet_address: str) -> int:
        """Get USDC balance for wallet address."""
        
        try:
            checksum_address = Web3.toChecksumAddress(wallet_address)
            balance = self.usdc_contract.functions.balanceOf(checksum_address).call()
            return balance
        except Exception as e:
            logger.error(f"Error getting USDC balance for {wallet_address}: {e}")
            raise

    async def _transfer_to_escrow(
        self, 
        from_wallet: str, 
        amount_wei: int, 
        permit_signature: Optional[str] = None
    ) -> str:
        """Transfer USDC from user wallet to escrow contract."""
        
        try:
            # Build transaction
            if permit_signature:
                # Use permit for gasless transaction
                return await self._execute_permit_transfer(
                    from_wallet, amount_wei, permit_signature
                )
            else:
                # Regular transferFrom (user must have approved escrow contract)
                return await self._execute_transfer_from(from_wallet, amount_wei)
                
        except Exception as e:
            logger.error(f"Error transferring to escrow: {e}")
            raise

    async def _transfer_from_escrow(self, to_wallet: str, amount_wei: int) -> str:
        """Transfer USDC from escrow to checker wallet."""
        
        try:
            checksum_to = Web3.toChecksumAddress(to_wallet)
            
            # Build transaction
            transaction = self.usdc_contract.functions.transfer(
                checksum_to, amount_wei
            ).buildTransaction({
                'from': self.account.address,
                'gas': 100000,
                'gasPrice': self.w3.toWei('20', 'gwei'),
                'nonce': self.w3.eth.get_transaction_count(self.account.address)
            })
            
            # Sign and send transaction
            signed_txn = self.w3.eth.account.sign_transaction(transaction, self.account.key)
            tx_hash = self.w3.eth.send_raw_transaction(signed_txn.rawTransaction)
            
            # Wait for confirmation
            receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
            
            if receipt.status == 1:
                logger.info(f"Successfully transferred {amount_wei/10**6} USDC to {to_wallet}")
                return tx_hash.hex()
            else:
                raise Exception(f"Transaction failed: {tx_hash.hex()}")
                
        except Exception as e:
            logger.error(f"Error transferring from escrow to {to_wallet}: {e}")
            raise

    async def _execute_permit_transfer(
        self, 
        from_wallet: str, 
        amount_wei: int, 
        permit_signature: str
    ) -> str:
        """Execute transfer using EIP-2612 permit (gasless)."""
        
        try:
            # In a real implementation, this would:
            # 1. Decode the permit signature
            # 2. Call USDC.permit() to approve the escrow contract
            # 3. Call escrow contract to transfer tokens
            
            # For demo purposes, return a mock transaction hash
            mock_tx_hash = f"0x{''.join(['%02x' % (i % 256) for i in range(32)])}"
            
            logger.info(f"Mock permit transfer: {amount_wei/10**6} USDC from {from_wallet}")
            return mock_tx_hash
            
        except Exception as e:
            logger.error(f"Error executing permit transfer: {e}")
            raise

    async def _execute_transfer_from(self, from_wallet: str, amount_wei: int) -> str:
        """Execute transferFrom (requires prior approval)."""
        
        try:
            checksum_from = Web3.toChecksumAddress(from_wallet)
            
            # Check allowance
            allowance = self.usdc_contract.functions.allowance(
                checksum_from, self.escrow_address
            ).call()
            
            if allowance < amount_wei:
                raise ValueError(f"Insufficient allowance: {allowance} < {amount_wei}")
            
            # Build transaction
            transaction = self.usdc_contract.functions.transferFrom(
                checksum_from, self.escrow_address, amount_wei
            ).buildTransaction({
                'from': self.account.address,
                'gas': 150000,
                'gasPrice': self.w3.toWei('20', 'gwei'),
                'nonce': self.w3.eth.get_transaction_count(self.account.address)
            })
            
            # Sign and send transaction
            signed_txn = self.w3.eth.account.sign_transaction(transaction, self.account.key)
            tx_hash = self.w3.eth.send_raw_transaction(signed_txn.rawTransaction)
            
            # Wait for confirmation
            receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
            
            if receipt.status == 1:
                logger.info(f"Successfully escrowed {amount_wei/10**6} USDC from {from_wallet}")
                return tx_hash.hex()
            else:
                raise Exception(f"Transaction failed: {tx_hash.hex()}")
                
        except Exception as e:
            logger.error(f"Error executing transferFrom: {e}")
            raise

    async def get_escrow_status(self, escrow_id: str) -> Dict[str, Any]:
        """Get status of an escrow."""
        
        try:
            db = next(get_db_session())
            try:
                escrow = db.query(WalletEscrow).filter(
                    WalletEscrow.id == escrow_id
                ).first()
                
                if not escrow:
                    raise ValueError(f"Escrow {escrow_id} not found")
                
                # Check if released
                is_released = escrow.released_at is not None
                
                return {
                    'escrow_id': escrow.id,
                    'lot_id': escrow.lot_id,
                    'user_wallet': escrow.user_wallet,
                    'amount_usdc': float(escrow.amount_usdc),
                    'locked_at': escrow.locked_at.isoformat(),
                    'released_at': escrow.released_at.isoformat() if is_released else None,
                    'status': 'released' if is_released else 'locked',
                    'contract_address': escrow.contract_address
                }
                
            finally:
                db.close()
                
        except Exception as e:
            logger.error(f"Error getting escrow status: {e}")
            raise

    async def calculate_required_escrow(self, word_count: int) -> Decimal:
        """Calculate required escrow amount for a document."""
        
        # Base calculation: 18 pence per 350-word chunk
        chunks_needed = (word_count + 349) // 350  # Round up
        pence_per_chunk = 18
        total_pence = chunks_needed * pence_per_chunk
        
        # Convert to USDC (simplified: 1 GBP = 1.25 USD)
        total_usdc = Decimal(str(total_pence / 100 * 1.25))
        
        # Add 10% buffer for gas fees and fluctuations
        buffered_amount = total_usdc * Decimal('1.1')
        
        return buffered_amount.quantize(Decimal('0.000001'))  # 6 decimal places

    async def batch_process_payouts(self, max_payouts: int = 50) -> List[Dict[str, Any]]:
        """Process pending payouts in batches."""
        
        try:
            db = next(get_db_session())
            try:
                # Get pending payouts
                pending_payouts = db.query(CheckerPayout).filter(
                    CheckerPayout.status == PayoutStatus.PENDING
                ).limit(max_payouts).all()
                
                if not pending_payouts:
                    return []
                
                results = []
                successful_count = 0
                
                for payout in pending_payouts:
                    try:
                        tx_hash = await self._transfer_from_escrow(
                            payout.checker.wallet_address,
                            int(payout.amount_usdc * 10**6)
                        )
                        
                        payout.status = PayoutStatus.PAID
                        payout.transaction_hash = tx_hash
                        payout.paid_at = datetime.now(timezone.utc)
                        
                        results.append({
                            'payout_id': payout.id,
                            'status': 'success',
                            'transaction_hash': tx_hash
                        })
                        
                        successful_count += 1
                        
                    except Exception as e:
                        payout.status = PayoutStatus.FAILED
                        payout.error_message = str(e)
                        
                        results.append({
                            'payout_id': payout.id,
                            'status': 'failed',
                            'error': str(e)
                        })
                
                db.commit()
                
                logger.info(f"Processed {len(results)} payouts: {successful_count} successful")
                return results
                
            finally:
                db.close()
                
        except Exception as e:
            logger.error(f"Error in batch payout processing: {e}")
            raise


# Utility functions
def create_permit_signature(
    wallet_private_key: str,
    spender_address: str,
    amount: int,
    deadline: int,
    nonce: int
) -> str:
    """Create EIP-2612 permit signature for gasless USDC approval."""
    
    # This is a simplified implementation
    # In production, use the full EIP-2612 implementation
    
    account = Account.from_key(wallet_private_key)
    
    # Create the message hash according to EIP-2612
    domain_separator = "0x..." # USDC domain separator
    type_hash = "0x..." # Permit typehash
    
    # For demo purposes, return a mock signature
    message = f"permit:{spender_address}:{amount}:{deadline}:{nonce}"
    message_hash = encode_defunct(text=message)
    signature = account.sign_message(message_hash)
    
    return signature.signature.hex()


# Example usage
async def setup_escrow_manager():
    """Setup escrow manager with environment variables."""
    import os
    
    return USDCEscrowManager(
        rpc_url=os.getenv('RPC_URL', 'https://polygon-rpc.com'),
        usdc_contract_address=os.getenv('USDC_CONTRACT', '0x2791bca1f2de4661ed88a30c99a7a9449aa84174'),
        escrow_contract_address=os.getenv('ESCROW_CONTRACT', '0x...'),
        private_key=os.getenv('ESCROW_PRIVATE_KEY')
    )