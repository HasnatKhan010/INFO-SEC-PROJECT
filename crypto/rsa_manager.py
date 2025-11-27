import base64
from Crypto.PublicKey import RSA
from Crypto.Signature import pkcs1_15
from Crypto.Cipher import PKCS1_OAEP
from Crypto.Hash import SHA256
from infosec_banking.utils.colors import print_error, print_success

class RSAManager:
    """Manages RSA Key Generation, Signing, Verification, and Encryption"""

    @staticmethod
    def generate_key_pair(bits=2048):
        """Generates an RSA key pair"""
        key = RSA.generate(bits)
        private_key = key.export_key().decode('utf-8')
        public_key = key.publickey().export_key().decode('utf-8')
        return private_key, public_key

    @staticmethod
    def sign(private_key_pem, data):
        """Signs data with a private key"""
        try:
            if isinstance(data, str):
                data = data.encode('utf-8')
            
            key = RSA.import_key(private_key_pem)
            h = SHA256.new(data)
            signature = pkcs1_15.new(key).sign(h)
            return base64.b64encode(signature).decode('utf-8')
        except Exception as e:
            print_error(f"Signing failed: {e}")
            return None

    @staticmethod
    def verify(public_key_pem, data, signature_b64):
        """Verifies a signature with a public key"""
        try:
            if isinstance(data, str):
                data = data.encode('utf-8')
                
            key = RSA.import_key(public_key_pem)
            h = SHA256.new(data)
            signature = base64.b64decode(signature_b64)
            
            pkcs1_15.new(key).verify(h, signature)
            return True
        except (ValueError, TypeError):
            return False
        except Exception as e:
            print_error(f"Verification error: {e}")
            return False

    @staticmethod
    def encrypt(public_key_pem, data):
        """Encrypts data with a public key (RSA-OAEP)"""
        try:
            if isinstance(data, str):
                data = data.encode('utf-8')
            
            key = RSA.import_key(public_key_pem)
            cipher = PKCS1_OAEP.new(key)
            ciphertext = cipher.encrypt(data)
            return base64.b64encode(ciphertext).decode('utf-8')
        except Exception as e:
            print_error(f"RSA Encryption failed: {e}")
            return None

    @staticmethod
    def decrypt(private_key_pem, ciphertext_b64):
        """Decrypts data with a private key (RSA-OAEP)"""
        try:
            ciphertext = base64.b64decode(ciphertext_b64)
            key = RSA.import_key(private_key_pem)
            cipher = PKCS1_OAEP.new(key)
            plaintext = cipher.decrypt(ciphertext)
            return plaintext.decode('utf-8')
        except Exception as e:
            print_error(f"RSA Decryption failed: {e}")
            return None
