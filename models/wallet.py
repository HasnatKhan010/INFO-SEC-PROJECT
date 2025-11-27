import os
from infosec_banking.crypto.rsa_manager import RSAManager
from infosec_banking.crypto.certificate import Certificate
from infosec_banking.utils.colors import print_success, print_info

class Wallet:
    """User Wallet managing RSA Keys and Certificate"""
    
    def __init__(self, user_id):
        self.user_id = user_id
        self.private_key = None
        self.public_key = None
        self.certificate = None
        self._load_or_generate_keys()

    def _load_or_generate_keys(self):
        """Loads keys from local storage or generates new ones"""
        # In a real app, these would be encrypted on disk. 
        # For this demo, we'll generate fresh ones in memory if not found, 
        # or we could save them to a 'keystore' folder.
        # Let's use a simple keystore folder.
        
        key_dir = f"data/keystore/{self.user_id}"
        priv_path = f"{key_dir}/private.pem"
        pub_path = f"{key_dir}/public.pem"
        
        if os.path.exists(priv_path):
            with open(priv_path, 'r') as f: self.private_key = f.read()
            with open(pub_path, 'r') as f: self.public_key = f.read()
            # print_info(f"Loaded keys for {self.user_id}")
        else:
            # print_info(f"Generating new keys for {self.user_id}...")
            self.private_key, self.public_key = RSAManager.generate_key_pair()
            os.makedirs(key_dir, exist_ok=True)
            with open(priv_path, 'w') as f: f.write(self.private_key)
            with open(pub_path, 'w') as f: f.write(self.public_key)
            # print_success(f"Keys saved for {self.user_id}")
        
        # Load Certificate if exists
        cert_path = f"{key_dir}/certificate.json"
        if os.path.exists(cert_path):
            try:
                import json
                with open(cert_path, 'r') as f:
                    cert_data = json.load(f)
                    self.certificate = Certificate.from_dict(cert_data)
            except Exception as e:
                print_info(f"Could not load certificate: {e}")

    def set_certificate(self, cert):
        """Sets the user's digital certificate and saves it"""
        self.certificate = cert
        
        # Save to disk
        key_dir = f"data/keystore/{self.user_id}"
        cert_path = f"{key_dir}/certificate.json"
        try:
            import json
            with open(cert_path, 'w') as f:
                json.dump(cert.to_dict(), f, indent=4)
        except Exception as e:
            print_error(f"Failed to save certificate: {e}")

    def sign_data(self, data):
        """Signs arbitrary data"""
        return RSAManager.sign(self.private_key, data)
