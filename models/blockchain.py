import hashlib
from infosec_banking.models.block import Block
from infosec_banking.models.transaction import Transaction
from infosec_banking.storage.storage_manager import StorageManager
from infosec_banking.utils.colors import print_header, print_error, print_success, print_warning, print_info
from infosec_banking.config import LEDGER_FILE, DIFFICULTY

import threading

class Blockchain:
    """Manages the blockchain"""
    
    def __init__(self, ca, difficulty=DIFFICULTY):
        self.chain = []
        self.difficulty = difficulty
        self.ca = ca # Reference to Certificate Authority for validation
        self.lock = threading.Lock()
        self.load()
        if not self.chain:
            self._create_genesis_block()

    def _create_genesis_block(self):
        """Creates genesis block"""
        print_header("Initializing Blockchain")
        genesis_block = Block(
            index=0,
            account_mask="SYS***",
            encrypted_tx_hex=hashlib.sha256(b'GENESIS').hexdigest(),
            tx_hash=hashlib.sha256(b'GENESIS').hexdigest(),
            previous_hash="0" * 64,
            nonce=0
        )
        genesis_block.mine_block(self.difficulty)
        self.chain.append(genesis_block)
        self.save()

    @property
    def last_block(self):
        """Returns last block"""
        return self.chain[-1]

    def add_block(self, account_mask, encrypted_tx_hex, tx_hash):
        """Adds new block to chain"""
        with self.lock:
            new_block = Block(
                index=len(self.chain),
                account_mask=account_mask,
                encrypted_tx_hex=encrypted_tx_hex,
                tx_hash=tx_hash,
                previous_hash=self.last_block.hash
            )
            new_block.mine_block(self.difficulty)
            self.chain.append(new_block)
            self.save()
            return new_block.index

    def save(self):
        """Saves blockchain to file"""
        chain_list = [block.to_dict() for block in self.chain]
        StorageManager.atomic_write_json(LEDGER_FILE, chain_list)

    def load(self):
        """Loads blockchain from file"""
        chain_list = StorageManager.load_json(LEDGER_FILE, default_data=[])
        self.chain = []
        for block_data in chain_list:
            try:
                block = Block.from_dict(block_data)
                self.chain.append(block)
            except KeyError as e:
                print_error(f"Skipped corrupted block: Missing {e}")

        print_info(f"Loaded {len(self.chain)} blocks from ledger")

    def is_valid(self, verbose=True):
        """Verifies blockchain integrity"""
        if verbose:
            print_header("Verifying Blockchain Integrity")
        
        for i in range(1, len(self.chain)):
            current_block = self.chain[i]
            previous_block = self.chain[i-1]
            
            recomputed_hash = current_block.compute_hash()

            if current_block.hash != recomputed_hash:
                if verbose:
                    print_error(f"Block #{i} hash mismatch - TAMPERED")
                return False, i

            if current_block.previous_hash != previous_block.hash:
                if verbose:
                    print_error(f"Block #{i} chain link broken - TAMPERED")
                return False, i

            target = '0' * self.difficulty
            if current_block.hash[:self.difficulty] != target:
                if verbose:
                    print_error(f"Block #{i} failed PoW check - TAMPERED")
                return False, i

        if verbose:
            print_success("All blocks verified - Blockchain is valid")
        return True, -1
