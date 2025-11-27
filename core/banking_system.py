import hashlib
import os
import time
import json
from infosec_banking.models.user_manager import UserManager
from infosec_banking.models.blockchain import Blockchain
from infosec_banking.models.transaction import Transaction
from infosec_banking.crypto.crypto_manager import CryptoManager
from infosec_banking.storage.storage_manager import StorageManager
from infosec_banking.utils.colors import print_header, print_processing, print_success, print_error

def _mask_account(account_id: str) -> str:
    """Masks an account ID for privacy"""
    if len(account_id) < 4:
        return account_id
    return account_id[:2] + '*' * (len(account_id) - 4) + account_id[-2:]

def _canonical_json(data: dict) -> str:
    """Returns canonical JSON for consistent hashing"""
    return json.dumps(data, sort_keys=True, separators=(',', ':'))

class BankingSystem:
    """Main banking system"""
    
    def __init__(self):
        self.user_manager = UserManager()
        self.blockchain = Blockchain()

    def get_logged_in_user(self):
        """Returns logged in user"""
        return self.user_manager.logged_in_user_id

    def _execute_transaction_flow(self, user_id, password, type, to_id, amount, memo):
        """Executes transaction flow"""
        print_header(f"Processing {type.upper()}")
        
        print_processing("Step 1: Verifying password...")
        time.sleep(0.1)
        
        if not self.user_manager.verify_password(user_id, password):
            print_error("Invalid password")
            StorageManager.log_operation(user_id, f"Failed {type}: invalid password", "FAIL")
            return False, "Invalid password."

        print_processing("Step 2: Validating transaction...")
        time.sleep(0.1)
        if type in ('withdraw', 'transfer') and self.user_manager.get_balance(user_id) < amount:
            print_error(f"Insufficient balance (Have: ${self.user_manager.get_balance(user_id):.2f}, Need: ${amount:.2f})")
            StorageManager.log_operation(user_id, f"Failed {type}: insufficient funds", "FAIL")
            return False, "Insufficient balance."
        
        print_processing("Step 3: Preparing transaction record...")
        time.sleep(0.1)
        tx_id = hashlib.sha256(os.urandom(8)).hexdigest()[:16]
        from_id = user_id if type != 'deposit' else 'SYSTEM'
        final_to_id = to_id if type != 'withdraw' else 'SYSTEM'
        
        tx = Transaction(tx_id, from_id, final_to_id, amount, type, memo)
        tx_json = _canonical_json(tx.to_dict())
        print_success(f"Transaction ID: {tx_id}")
        
        print_processing("Step 4: Deriving encryption key...")
        time.sleep(0.1)
        key_bytes = CryptoManager.derive_key(password)
        
        print_processing("Step 5: Encrypting transaction...")
        time.sleep(0.1)
        encrypted_tx_bytes = CryptoManager.encrypt(tx_json, key_bytes)
        
        print_processing("Step 6: Creating transaction hash...")
        time.sleep(0.1)
        encrypted_tx_hex = encrypted_tx_bytes.hex()
        tx_hash = hashlib.sha256(encrypted_tx_bytes).hexdigest()
        print_success(f"TX Hash: {tx_hash[:16]}...")

        print_processing("Step 7: Creating and mining block...")
        time.sleep(0.1)
        account_mask = _mask_account(user_id)
        block_index = self.blockchain.add_block(account_mask, encrypted_tx_hex, tx_hash)

        print_processing("Step 8: Updating balances...")
        time.sleep(0.1)
        if type == 'deposit':
            self.user_manager.update_balance(user_id, amount)
            print_success(f"Added ${amount:.2f}")
        elif type == 'withdraw':
            self.user_manager.update_balance(user_id, -amount)
            print_success(f"Removed ${amount:.2f}")
        elif type == 'transfer':
            if not self.user_manager.update_balance(user_id, -amount):
                print_error("Sender balance update failed")
                return False, "Transfer failed."
            if not self.user_manager.update_balance(to_id, amount):
                print_error("Receiver balance update failed - ROLLING BACK")
                self.user_manager.update_balance(user_id, amount)
                self.user_manager.save()
                return False, "Transfer failed at receiver update."
            print_success(f"${amount:.2f} transferred from {user_id} to {to_id}")
        
        self.user_manager.save()
        print_success(f"Transaction complete in Block #{block_index}")
        StorageManager.log_operation(user_id, f"{type}: ${amount:.2f}", "SUCCESS")
        return True, f"Success! Block #{block_index}"

    def deposit(self, user_id, password, amount, memo=""):
        """Deposits funds"""
        if amount <= 0:
            print_error("Amount must be positive")
            return False, "Deposit amount must be positive."
        return self._execute_transaction_flow(user_id, password, 'deposit', user_id, amount, memo)

    def withdraw(self, user_id, password, amount, memo=""):
        """Withdraws funds"""
        if amount <= 0:
            print_error("Amount must be positive")
            return False, "Withdrawal amount must be positive."
        return self._execute_transaction_flow(user_id, password, 'withdraw', user_id, amount, memo)

    def transfer(self, from_id, password, to_id, amount, memo=""):
        """Transfers funds"""
        if amount <= 0:
            print_error("Amount must be positive")
            return False, "Transfer amount must be positive."
        if from_id == to_id:
            print_error("Cannot transfer to self")
            return False, "Cannot transfer to yourself."
        if to_id not in self.user_manager.users:
            print_error(f"User '{to_id}' does not exist")
            return False, "Recipient ID does not exist."
        return self._execute_transaction_flow(from_id, password, 'transfer', to_id, amount, memo)

    def view_history(self, user_id, password):
        """Views transaction history"""
        print_header(f"Transaction History for {user_id}")
        
        if not self.user_manager.verify_password(user_id, password):
            print_error("Invalid password")
            return None, "Invalid password"

        print_processing("Deriving encryption key...")
        time.sleep(0.1)
        key_bytes = CryptoManager.derive_key(password)
        history = []
        
        print_processing("Scanning ledger...")
        time.sleep(0.2)

        for block in self.blockchain.chain:
            if block.index == 0:
                continue
            
            if not block.account_mask == _mask_account(user_id):
                continue 

            is_valid_tx_hash = False
            decrypted_tx = None
            
            try:
                encrypted_tx_bytes = bytes.fromhex(block.encrypted_tx_hex)
                computed_tx_hash = hashlib.sha256(encrypted_tx_bytes).hexdigest()
                if computed_tx_hash != block.tx_hash:
                    raise Exception("Hash mismatch")
                is_valid_tx_hash = True
                
                decrypted_json_str = CryptoManager.decrypt(encrypted_tx_bytes, key_bytes)
                decrypted_tx = json.loads(decrypted_json_str)

            except Exception as e:
                status = f"ERROR: {str(e)[:30]}"
                decrypted_tx = {"memo": "Decryption failed"}
                is_valid_tx_hash = False
            
            status = "[OK] Valid" if is_valid_tx_hash else "[X] Tampered"
            
            history.append({
                'block_index': block.index,
                'status': status,
                'tx_id': decrypted_tx.get('tx_id', 'N/A')[:8],
                'type': decrypted_tx.get('type', 'N/A'),
                'amount': decrypted_tx.get('amount', 0.0),
                'from': decrypted_tx.get('from_id', 'N/A'),
                'to': decrypted_tx.get('to_id', 'N/A'),
                'memo': decrypted_tx.get('memo', '')[:20],
            })

        print_success(f"Found {len(history)} transactions\n")
        return history, ""

    def verify_chain(self):
        """Verifies blockchain"""
        is_valid, index = self.blockchain.is_valid(verbose=True)
        if is_valid:
            print_success("Ledger is secure and unmodified")
        else:
            print_error(f"TAMPERING detected at block #{index}")
        return is_valid
