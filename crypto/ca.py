import os
import json
import uuid
from infosec_banking.crypto.rsa_manager import RSAManager
from infosec_banking.crypto.certificate import Certificate
from infosec_banking.storage.storage_manager import StorageManager
from infosec_banking.utils.colors import print_success, print_info, print_warning

CA_KEY_FILE = 'data/ca_key.pem'
CERT_STORE_FILE = 'data/certificates.json'

import threading

class CertificateAuthority:
    """Certificate Authority (CA) for issuing and verifying certificates"""

    def __init__(self, issuer_name="InfoSec Bank Root CA"):
        self.issuer_name = issuer_name
        self.private_key = None
        self.public_key = None
        self.issued_certificates = {}
        self.lock = threading.Lock()
        self._load_or_generate_keys()
        self._load_certificates()

    def _load_or_generate_keys(self):
        """Loads CA keys or generates them if not found"""
        if os.path.exists(CA_KEY_FILE):
            with open(CA_KEY_FILE, 'r') as f:
                self.private_key = f.read()
            # Derive public key from private
            from Crypto.PublicKey import RSA
            key = RSA.import_key(self.private_key)
            self.public_key = key.publickey().export_key().decode('utf-8')
            print_info("Loaded CA Root Keys")
        else:
            print_warning("Generating new CA Root Keys...")
            self.private_key, self.public_key = RSAManager.generate_key_pair(4096)
            # Ensure directory exists
            os.makedirs(os.path.dirname(CA_KEY_FILE), exist_ok=True)
            with open(CA_KEY_FILE, 'w') as f:
                f.write(self.private_key)
            print_success("CA Root Keys Generated and Saved")

    def _load_certificates(self):
        """Loads issued certificates from storage"""
        data = StorageManager.load_json(CERT_STORE_FILE, default_data={})
        for serial, cert_data in data.items():
            try:
                self.issued_certificates[serial] = Certificate.from_dict(cert_data)
            except Exception as e:
                from infosec_banking.utils.colors import print_warning
                print_warning(f"Skipping corrupted certificate {serial}: {e}")

    def _save_certificates(self):
        """Saves issued certificates to storage"""
        data = {serial: cert.to_dict() for serial, cert in self.issued_certificates.items()}
        StorageManager.atomic_write_json(CERT_STORE_FILE, data)

    def issue_certificate(self, user_id, user_public_key):
        """Issues a new digital certificate for a user"""
        with self.lock:
            # Check if user already has a cert (optional, but good for cleanup)
            # For now, we allow multiple certs or just generate a new one
            
            serial_number = str(uuid.uuid4())
            cert = Certificate(
                serial_number=serial_number,
                subject=user_id,
                issuer=self.issuer_name,
                public_key=user_public_key
            )
            
            # Sign the certificate
            data_to_sign = cert.get_data_to_sign()
            cert.signature = RSAManager.sign(self.private_key, data_to_sign)
            
            self.issued_certificates[serial_number] = cert
            self._save_certificates()
            print_success(f"Issued Certificate for '{user_id}' (Serial: {serial_number[:8]}...)")
            return cert

    def verify_certificate(self, certificate):
        """Verifies a certificate's signature against the CA's public key"""
        if isinstance(certificate, dict):
            certificate = Certificate.from_dict(certificate)
            
        data_to_verify = certificate.get_data_to_sign()
        return RSAManager.verify(self.public_key, data_to_verify, certificate.signature)

    def get_certificate(self, serial_number):
        return self.issued_certificates.get(serial_number)
