import hashlib
import time
import json
import datetime
from infosec_banking.utils.colors import print_processing, print_success

def _canonical_json(data: dict) -> str:
    """Returns canonical JSON for consistent hashing"""
    return json.dumps(data, sort_keys=True, separators=(',', ':'))

class Block:
    """Represents a block in the blockchain"""
    
    def __init__(self, index, account_mask, encrypted_tx_hex, tx_hash, previous_hash, nonce=0, timestamp=None):
        self.index = index
        self.timestamp = timestamp if timestamp else datetime.datetime.now().isoformat()
        self.account_mask = account_mask
        self.encrypted_tx_hex = encrypted_tx_hex
        self.tx_hash = tx_hash
        self.previous_hash = previous_hash
        self.nonce = nonce
        self.hash = self.compute_hash()

    def compute_hash(self):
        """Computes block hash"""
        data_to_hash = {
            'index': self.index,
            'timestamp': self.timestamp,
            'account_mask': self.account_mask,
            'encrypted_tx_hex': self.encrypted_tx_hex,
            'tx_hash': self.tx_hash,
            'previous_hash': self.previous_hash,
            'nonce': self.nonce,
        }
        block_string = _canonical_json(data_to_hash).encode('utf-8')
        return hashlib.sha256(block_string).hexdigest()

    def mine_block(self, difficulty):
        """Mines block using Proof-of-Work"""
        target = '0' * difficulty
        print_processing(f"Mining block #{self.index}", end="")
        
        start_time = time.time()
        attempt = 0
        while self.hash[:difficulty] != target:
            self.nonce += 1
            self.hash = self.compute_hash()
            attempt += 1
            if attempt % 500 == 0:
                print_processing(f"Mining block #{self.index} ({attempt} attempts)", end="")
        
        end_time = time.time()
        print()
        print_success(f"Block #{self.index} mined! Hash: {self.hash[:12]}... (Nonce: {self.nonce}, Time: {end_time-start_time:.2f}s)")
        return self.hash

    def to_dict(self):
        """Converts block to dictionary"""
        return {
            'index': self.index,
            'timestamp': self.timestamp,
            'account_mask': self.account_mask,
            'encrypted_tx_hex': self.encrypted_tx_hex,
            'tx_hash': self.tx_hash,
            'previous_hash': self.previous_hash,
            'nonce': self.nonce,
            'hash': self.hash
        }

    @staticmethod
    def from_dict(data):
        """Creates block from dictionary"""
        block = Block(
            index=data['index'],
            account_mask=data['account_mask'],
            encrypted_tx_hex=data['encrypted_tx_hex'],
            tx_hash=data['tx_hash'],
            previous_hash=data['previous_hash'],
            nonce=data.get('nonce', 0),
            timestamp=data.get('timestamp')
        )
        block.hash = data.get('hash', block.compute_hash())
        return block
