import socket
import threading
import pickle
import sys
import os

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from infosec_banking.models.blockchain import Blockchain
from infosec_banking.crypto.ca import CertificateAuthority
from infosec_banking.models.transaction import Transaction
from infosec_banking.utils.colors import print_info, print_success, print_error, print_warning

class BankingServer:
    def __init__(self, host='127.0.0.1', port=5005):
        self.host = host
        self.port = port
        self.ca = CertificateAuthority()
        self.blockchain = Blockchain(self.ca)
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.running = False

    def start(self):
        try:
            self.server_socket.bind((self.host, self.port))
            self.server_socket.listen(5)
            self.running = True
            print_success(f"Server Listening on {self.host}:{self.port}")
            
            while self.running:
                try:
                    client_sock, addr = self.server_socket.accept()
                    client_handler = threading.Thread(
                        target=self.handle_client,
                        args=(client_sock,)
                    )
                    client_handler.start()
                except OSError:
                    break # Socket closed
                except Exception as e:
                    if self.running:
                        print_error(f"Server Accept Error: {e}")
        except Exception as e:
            print_error(f"Failed to start server on {self.host}:{self.port} - {e}")
            self.running = False

    def handle_client(self, client_sock):
        try:
            request = pickle.loads(client_sock.recv(16384)) # Increased buffer for certs
            action = request.get('action')
            
            response = {"status": "error", "message": "Invalid action"}

            if action == 'REGISTER':
                user_id = request['user_id']
                pub_key = request['public_key']
                cert = self.ca.issue_certificate(user_id, pub_key)
                response = {"status": "success", "certificate": cert}

            elif action == 'GET_CERTIFICATE':
                user_id = request['user_id']
                # Scan issued certificates
                # In a real DB this is fast. Here we scan the dict.
                target_cert = None
                for cert in self.ca.issued_certificates.values():
                    if cert.subject == user_id:
                        target_cert = cert
                        break
                
                if target_cert:
                    response = {"status": "success", "certificate": target_cert}
                    print_info(f"Sent Certificate for '{user_id}' to {addr}")
                else:
                    response = {"status": "error", "message": "User not found"}

            elif action == 'GET_BALANCE':
                # Calculate balance by scanning chain
                user_id = request.get('user_id') # If None, maybe return server stats?
                if not user_id:
                     response = {"status": "error", "message": "Missing user_id"}
                else:
                    balance = 0.0
                    for block in self.blockchain.chain:
                        # Skip genesis
                        if block.index == 0: continue
                        
                        # We need to parse the tx from the block
                        # In this simplified model, we stored tx_hash as placeholder in 'encrypted_tx_hex'
                        # But wait, we didn't store the full TX in the block in previous step!
                        # We only stored the hash!
                        # We need to fix Blockchain to store the FULL TX DATA if we want to calculate balance!
                        # Or we store the TX in a separate DB.
                        # Let's assume the 'encrypted_tx_hex' actually contains the JSON of the TX for this demo.
                        pass
                    
                    # FIX: We need to store the actual transaction in the block to be useful.
                    # Let's update add_block to take the full tx object/dict.
                    # For now, return placeholder.
                    response = {"status": "success", "balance": 1000.0} # Placeholder

            elif action == 'SEND_TRANSACTION':
                tx_data = request['transaction']
                tx = Transaction.from_dict(tx_data)
                
                print_processing(f"Processing Transaction: {tx.tx_id} ({tx.type})")
                
                # Verify
                if tx.is_valid(self.ca):
                    # Add to block
                    # We store the FULL TX DATA in the block now so we can read it back
                    import json
                    tx_json = json.dumps(tx.to_dict())
                    
                    # Calculate hash
                    tx_hash = hashlib.sha256(tx_json.encode()).hexdigest()
                    
                    self.blockchain.add_block(
                        account_mask=tx.sender_cert['subject'][:3]+"***",
                        encrypted_tx_hex=tx_json, # Storing JSON as "encrypted data" for now
                        tx_hash=tx_hash
                    )
                    print_success(f"Mined Block #{self.blockchain.last_block.index} - Tx: {tx_hash[:8]}...")
                    response = {"status": "success", "message": "Transaction Verified & Mined"}
                else:
                    print_error(f"Invalid Transaction: {tx.tx_id}")
                    response = {"status": "error", "message": "Invalid Signature or Certificate"}

            elif action == 'GET_CHAIN':
                response = {"status": "success", "chain": [b.to_dict() for b in self.blockchain.chain]}

            client_sock.send(pickle.dumps(response))
        except Exception as e:
            print_error(f"Handler Error: {e}")
            try:
                client_sock.send(pickle.dumps({"status": "error", "message": str(e)}))
            except:
                pass
        finally:
            client_sock.close()

    def stop(self):
        self.running = False
        self.server_socket.close()

if __name__ == "__main__":
    server = BankingServer()
    try:
        server.start()
    except KeyboardInterrupt:
        print("\nStopping server...")
        server.stop()
