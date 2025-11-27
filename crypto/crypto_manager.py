import hashlib
import os
import time
from infosec_banking.utils.colors import print_processing, print_success, print_error, print_warning
from infosec_banking.config import AES_KEY_SIZE, AES_IV_SIZE

USE_AES = False
try:
    from Crypto.Cipher import AES
    from Crypto.Util.Padding import pad, unpad
    USE_AES = True
except ImportError:
    pass

class VigenereCipher:
    """INSECURE FALLBACK: Vigenère cipher for demo purposes"""
    FALLBACK_KEY = b'BANKINGLEDGERKEY'

    @staticmethod
    def _prepare_key(key: bytes, length: int) -> str:
        key_str = key.decode('utf-8', errors='ignore')
        key_alpha = ''.join(filter(str.isalpha, key_str)).upper()
        if not key_alpha:
            key_alpha = 'KEY'
        key_repeated = (key_alpha * (length // len(key_alpha) + 1))[:length]
        return key_repeated

    @staticmethod
    def encrypt(plaintext: str, key_bytes: bytes) -> bytes:
        result = []
        key_repeated = VigenereCipher._prepare_key(key_bytes, len(plaintext))
        
        for i, char in enumerate(plaintext):
            if char.isalpha():
                shift = ord(key_repeated[i % len(key_repeated)]) - ord('A')
                start = ord('A') if char.isupper() else ord('a')
                encrypted_char = chr(start + (ord(char) - start + shift) % 26)
                result.append(encrypted_char)
            else:
                result.append(char)
        return "".join(result).encode('utf-8')

    @staticmethod
    def decrypt(ciphertext_bytes: bytes, key_bytes: bytes) -> str:
        ciphertext = ciphertext_bytes.decode('utf-8', errors='ignore')
        result = []
        key_repeated = VigenereCipher._prepare_key(key_bytes, len(ciphertext))

        for i, char in enumerate(ciphertext):
            if char.isalpha():
                shift = ord(key_repeated[i % len(key_repeated)]) - ord('A')
                start = ord('A') if char.isupper() else ord('a')
                decrypted_char = chr(start + (ord(char) - start - shift + 26) % 26)
                result.append(decrypted_char)
            else:
                result.append(char)
        return "".join(result)

class CryptoManager:
    """Manages encryption and decryption"""
    
    @staticmethod
    def derive_key(password: str) -> bytes:
        print_processing("Deriving encryption key...")
        time.sleep(0.1)
        key_hash = hashlib.sha256(password.encode()).digest()
        print_success("Key derived")
        return key_hash

    @staticmethod
    def encrypt(plaintext: str, key_bytes: bytes) -> bytes:
        print_processing("Encrypting transaction...")
        time.sleep(0.1)
        if USE_AES:
            try:
                iv = os.urandom(AES_IV_SIZE)
                cipher = AES.new(key_bytes, AES.MODE_CBC, iv)
                padded_data = pad(plaintext.encode('utf-8'), AES.block_size)
                ciphertext = cipher.encrypt(padded_data)
                print_success("Encryption complete (AES-256-CBC)")
                return iv + ciphertext
            except Exception as e:
                print_error(f"AES encryption failed: {e}")
                raise
        else:
            result = VigenereCipher.encrypt(plaintext, VigenereCipher.FALLBACK_KEY)
            print_success("Encryption complete (Vigenère)")
            return result

    @staticmethod
    def decrypt(iv_plus_ct: bytes, key_bytes: bytes) -> str:
        print_processing("Decrypting transaction...")
        time.sleep(0.1)
        if USE_AES:
            if len(iv_plus_ct) < AES_IV_SIZE:
                raise ValueError("Ciphertext too short for IV")
            iv = iv_plus_ct[:AES_IV_SIZE]
            ciphertext = iv_plus_ct[AES_IV_SIZE:]
            try:
                cipher = AES.new(key_bytes, AES.MODE_CBC, iv)
                decrypted_padded = cipher.decrypt(ciphertext)
                plaintext = unpad(decrypted_padded, AES.block_size).decode('utf-8')
                print_success("Decryption successful")
                return plaintext
            except Exception as e:
                raise ValueError(f"Decryption failed: {e}")
        else:
            result = VigenereCipher.decrypt(iv_plus_ct, VigenereCipher.FALLBACK_KEY)
            print_success("Decryption successful")
            return result
