import threading
import time
import sys
import os
import uuid

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from infosec_banking.core.server import BankingServer
from infosec_banking.core.client import BankingClient
from infosec_banking.models.wallet import Wallet
from infosec_banking.models.transaction import Transaction
from infosec_banking.utils.colors import Colors, print_header, print_success, print_error, print_info, print_warning, print_processing

def run_server():
    server = BankingServer(port=5005)
    server.start()

def demo_run():
    print_header("RSA/PKI SECURE BANKING DEMO")
    
    # 1. Start Server
    print_processing("Starting Secure Banking Server...")
    server_thread = threading.Thread(target=run_server, daemon=True)
    server_thread.start()
    time.sleep(1) # Wait for startup
    
    client = BankingClient(port=5005)

    # 2. User Registration (PKI)
    print_header("PHASE 1: PKI REGISTRATION")
    
    # Alice
    print_info("Generating RSA Keys for Alice...")
    alice_wallet = Wallet("Alice")
    print_info("Requesting Certificate from CA...")
    resp = client.send_request({
        "action": "REGISTER",
        "user_id": "Alice",
        "public_key": alice_wallet.public_key
    })
    
    if resp.get('status') != 'success':
        print_error(f"Alice Registration Failed: {resp.get('message')}")
        return

    alice_wallet.set_certificate(resp['certificate'])
    print_success(f"Alice Registered! Cert Serial: {alice_wallet.certificate.serial_number[:8]}...")

    # Bob
    print_info("Generating RSA Keys for Bob...")
    bob_wallet = Wallet("Bob")
    resp = client.send_request({
        "action": "REGISTER",
        "user_id": "Bob",
        "public_key": bob_wallet.public_key
    })

    if resp.get('status') != 'success':
        print_error(f"Bob Registration Failed: {resp.get('message')}")
        return

    bob_wallet.set_certificate(resp['certificate'])
    print_success(f"Bob Registered! Cert Serial: {bob_wallet.certificate.serial_number[:8]}...")

    # 3. Secure Transaction
    print_header("PHASE 2: HYBRID ENCRYPTED TRANSACTION")
    
    print_info("Alice creating transaction: 100.00 -> Bob")
    tx = Transaction(
        tx_id=str(uuid.uuid4())[:8],
        sender_cert=alice_wallet.certificate,
        receiver_id="Bob",
        amount=100.00,
        type="transfer",
        memo="Top Secret Payment"
    )
    
    # Hybrid Encryption
    print_processing("Encrypting Memo with AES + RSA...")
    # We need Bob's Public Key. In demo we have it in bob_wallet.
    # In real life we'd fetch it from CA.
    tx.encrypt_memo(bob_wallet.public_key)
    print_success(f"Memo Encrypted! Ciphertext: {tx.memo[:20]}...")
    print_success(f"AES Key Encrypted! RSA-KEM: {tx.encrypted_aes_key[:20]}...")

    print_processing("Alice Signing Transaction with Private Key...")
    tx.sign(alice_wallet.private_key)
    print_success(f"Transaction Signed! Signature: {tx.signature[:20]}...")
    
    print_processing("Sending to Network...")
    resp = client.send_request({
        "action": "SEND_TRANSACTION",
        "transaction": tx.to_dict()
    })
    
    if resp['status'] == 'success':
        print_success(f"Network Response: {resp['message']}")
    else:
        print_error(f"Transaction Failed: {resp['message']}")

    # 4. Tampering Attack
    print_header("PHASE 3: TAMPERING ATTACK SIMULATION")
    
    print_warning("Attacker intercepts transaction and modifies amount...")
    tx.amount = 999999.00 # Modify payload
    # Signature is NOT updated (Attacker doesn't have Alice's Key)
    
    print_processing("Re-broadcasting Tampered Transaction...")
    resp = client.send_request({
        "action": "SEND_TRANSACTION",
        "transaction": tx.to_dict()
    })
    
    if resp['status'] == 'error':
        print_success(f"Attack Blocked! Server Response: {resp['message']}")
    else:
        print_error("Attack Succeeded (This should not happen!)")

    print_header("DEMO COMPLETE")

if __name__ == "__main__":
    demo_run()
