import datetime
import json
import hashlib
import os
import base64
from infosec_banking.crypto.rsa_manager import RSAManager
from infosec_banking.crypto.crypto_manager import CryptoManager
from infosec_banking.crypto.certificate import Certificate

class Transaction:
    """Represents a financial transaction with Digital Signature and Hybrid Encryption"""
    
    def __init__(self, tx_id, sender_cert, receiver_id, amount, type, memo, timestamp=None, signature=None, encrypted_aes_key=None, iv=None):
        self.tx_id = tx_id
        self.sender_cert = sender_cert # Certificate Object or Dict
        self.receiver_id = receiver_id
        self.amount = float(amount)
        self.type = type
        self.memo = memo # This will be ciphertext if encrypted
        self.timestamp = timestamp if timestamp else datetime.datetime.now().isoformat()
        self.signature = signature
        self.encrypted_aes_key = encrypted_aes_key # RSA-Encrypted AES Key
        self.iv = iv # AES IV

    def to_dict(self):
        """Converts transaction to dictionary"""
        cert_data = self.sender_cert
        if hasattr(self.sender_cert, 'to_dict'):
            cert_data = self.sender_cert.to_dict()

        return {
            'tx_id': self.tx_id,
            'sender_cert': cert_data,
            'receiver_id': self.receiver_id,
            'amount': self.amount,
            'type': self.type,
            'memo': self.memo,
            'timestamp': self.timestamp,
            'signature': self.signature,
            'encrypted_aes_key': self.encrypted_aes_key,
            'iv': self.iv
        }

    @staticmethod
    def from_dict(data):
        """Creates transaction from dictionary"""
        return Transaction(
            tx_id=data['tx_id'],
            sender_cert=data['sender_cert'],
            receiver_id=data['receiver_id'],
            amount=data['amount'],
            type=data['type'],
            memo=data['memo'],
            timestamp=data['timestamp'],
            signature=data.get('signature'),
            encrypted_aes_key=data.get('encrypted_aes_key'),
            iv=data.get('iv')
        )

    def get_data_to_sign(self):
        """Returns canonical JSON for signing (excluding signature itself)"""
        cert_data = self.sender_cert
        if hasattr(self.sender_cert, 'to_dict'):
            cert_data = self.sender_cert.to_dict()

        data = {
            'tx_id': self.tx_id,
            'sender_cert': cert_data,
            'receiver_id': self.receiver_id,
            'amount': self.amount,
            'type': self.type,
            'memo': self.memo,
            'timestamp': self.timestamp,
            'encrypted_aes_key': self.encrypted_aes_key,
            'iv': self.iv
        }
        return json.dumps(data, sort_keys=True, separators=(',', ':'))

    def sign(self, private_key_pem):
        """Signs the transaction"""
        data = self.get_data_to_sign()
        self.signature = RSAManager.sign(private_key_pem, data)

    def is_valid(self, ca):
        """Verifies transaction signature and certificate"""
        if self.type == 'deposit' and self.sender_cert == 'SYSTEM':
            return True # System deposits are trusted/internal
            
        if not self.signature:
            return False

        # 1. Verify Certificate
        cert_obj = self.sender_cert
        if isinstance(cert_obj, dict):
            cert_obj = Certificate.from_dict(cert_obj)
        
        if not ca.verify_certificate(cert_obj):
            print(f"Invalid Certificate for {cert_obj.subject}")
            return False

        # 2. Verify Transaction Signature using Cert's Public Key
        data = self.get_data_to_sign()
        return RSAManager.verify(cert_obj.public_key, data, self.signature)

    def encrypt_memo(self, receiver_public_key_pem):
        """Hybrid Encrypts the memo: AES(memo) + RSA(aes_key)"""
        # 1. Generate AES Key (32 bytes for AES-256)
        aes_key = os.urandom(32)
        
        # 2. Encrypt Memo with AES
        # CryptoManager.encrypt returns iv + ciphertext
        encrypted_data = CryptoManager.encrypt(self.memo, aes_key)
        self.iv = base64.b64encode(encrypted_data[:16]).decode('utf-8') # Extract IV
        self.memo = base64.b64encode(encrypted_data[16:]).decode('utf-8') # Store Ciphertext in memo field
        
        # 3. Encrypt AES Key with Receiver's RSA Public Key
        self.encrypted_aes_key = RSAManager.encrypt(receiver_public_key_pem, aes_key)

    def decrypt_memo(self, receiver_private_key_pem):
        """Hybrid Decrypts the memo"""
        if not self.encrypted_aes_key:
            return self.memo # Not encrypted
            
        try:
            # 1. Decrypt AES Key with RSA
            aes_key = RSAManager.decrypt(receiver_private_key_pem, self.encrypted_aes_key)
            if not aes_key:
                return "[Decryption Failed: Invalid Key]"
                
            # 2. Decrypt Memo with AES
            iv = base64.b64decode(self.iv)
            ciphertext = base64.b64decode(self.memo)
            
            # CryptoManager expects IV + Ciphertext
            plaintext = CryptoManager.decrypt(iv + ciphertext, aes_key)
            return plaintext
        except Exception as e:
            return f"[Decryption Error: {e}]"
