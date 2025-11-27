import time
import sys
import os
import uuid

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from infosec_banking.core.client import BankingClient
from infosec_banking.models.wallet import Wallet
from infosec_banking.models.transaction import Transaction
from infosec_banking.crypto.certificate import Certificate
from infosec_banking.utils.colors import Colors, print_header, print_info, print_error, print_success, print_warning, print_processing
from infosec_banking.demo import demo_run

def main():
    client = BankingClient(port=5005)
    current_wallet = None

    while True:
        print_header("RSA/PKI BANKING CLIENT")
        
        # Check Server Status
        server_status = f"{Colors.RED}Offline{Colors.ENDC}"
        try:
            # Simple ping (get chain length or just connect)
            resp = client.send_request({"action": "GET_CHAIN"})
            if resp.get('status') == 'success':
                server_status = f"{Colors.GREEN}Online (Port {client.port}){Colors.ENDC}"
        except:
            pass

        print(f"Server Status: {server_status}")

        if current_wallet:
            print(f"Wallet:        {Colors.GREEN}{current_wallet.user_id}{Colors.ENDC}")
            print(f"Public Key:    {current_wallet.public_key[:30]}...")
            if current_wallet.certificate:
                 print(f"Certificate:   {Colors.GREEN}Verified (Serial: {current_wallet.certificate.serial_number[:8]}...){Colors.ENDC}")
            else:
                 print(f"Certificate:   {Colors.RED}Not Registered{Colors.ENDC}")
        else:
            print(f"Wallet:        {Colors.YELLOW}Not Loaded{Colors.ENDC}")
        
        print("-" * 60)
        print("1. Create/Load Wallet")
        print("2. Register with CA (Get Certificate)")
        print("3. Check Balance")
        print("4. Send Signed Transaction")
        print("5. View Blockchain")
        print("9. Run Automated Demo")
        print("0. Exit")
        print("-" * 60)

        choice = input("Enter choice: ").strip()

        if choice == '1':
            user_id = input("Enter User ID: ").strip()
            if user_id:
                print_processing(f"Loading/Generating Keys for {user_id}...")
                current_wallet = Wallet(user_id)
                print_success(f"Wallet loaded for {user_id}")
        
        elif choice == '2':
            if not current_wallet:
                print_error("Please load a wallet first.")
                continue
            
            print_processing("Sending CSR (Certificate Signing Request) to CA...")
            resp = client.send_request({
                "action": "REGISTER",
                "user_id": current_wallet.user_id,
                "public_key": current_wallet.public_key
            })
            
            if resp['status'] == 'success':
                current_wallet.set_certificate(resp['certificate'])
                print_success(f"Certificate Issued! Serial: {current_wallet.certificate.serial_number}")
            else:
                print_error(f"Registration Failed: {resp.get('message')}")

        elif choice == '3':
            if not current_wallet:
                print_error("Please load a wallet first.")
                continue
            
            # In this demo, balance is just a placeholder or requires scanning
            # We'll just ping the server
            resp = client.send_request({"action": "GET_BALANCE"})
            print_info(f"Server Response: {resp}")

        elif choice == '4':
            if not current_wallet or not current_wallet.certificate:
                print_error("You must have a Wallet AND a Certificate to transact.")
                continue
            
            recipient = input("Recipient ID: ").strip()
            
            # 1. Get Recipient's Certificate (for Encryption)
            print_processing(f"Fetching Certificate for {recipient}...")
            resp = client.send_request({"action": "GET_CERTIFICATE", "user_id": recipient})
            if resp['status'] != 'success':
                print_error(f"Recipient not found: {resp.get('message')}")
                continue
            
            recipient_cert = Certificate.from_dict(resp['certificate'])
            print_success(f"Got Certificate for {recipient} (Serial: {recipient_cert.serial_number[:8]}...)")

            try:
                amount = float(input("Amount: "))
                memo = input("Memo (Will be Encrypted): ")
                
                tx = Transaction(
                    tx_id=str(uuid.uuid4())[:8],
                    sender_cert=current_wallet.certificate,
                    receiver_id=recipient,
                    amount=amount,
                    type="transfer",
                    memo=memo
                )
                
                # 2. Hybrid Encryption
                print_header("ENCRYPTION PROCESS")
                print_info(f"Original Memo: {memo}")
                
                print_processing("Generating AES-256 Session Key...")
                time.sleep(0.5)
                
                print_processing("Encrypting Memo with AES...")
                tx.encrypt_memo(recipient_cert.public_key)
                time.sleep(0.5)
                
                print(f"{Colors.CYAN}AES IV:         {tx.iv}{Colors.ENDC}")
                print(f"{Colors.CYAN}Encrypted Memo: {tx.memo[:30]}...{Colors.ENDC}")
                print(f"{Colors.CYAN}Encrypted Key:  {tx.encrypted_aes_key[:30]}...{Colors.ENDC}")
                print_success("Hybrid Encryption Complete!")

                # 3. Sign
                print_processing("Signing with Private Key...")
                tx.sign(current_wallet.private_key)
                print_success("Signature Applied.")
                
                # 4. Send
                print_processing("Broadcasting...")
                resp = client.send_request({
                    "action": "SEND_TRANSACTION",
                    "transaction": tx.to_dict()
                })
                
                if resp['status'] == 'success':
                    print_success(f"Success: {resp['message']}")
                else:
                    print_error(f"Failed: {resp['message']}")
                    
            except ValueError:
                print_error("Invalid amount")

        elif choice == '5':
            resp = client.send_request({"action": "GET_CHAIN"})
            if resp['status'] == 'success':
                chain = resp['chain']
                print(f"\n{Colors.BOLD}Blockchain Ledger ({len(chain)} blocks){Colors.ENDC}")
                for block in chain:
                    print(f"Block #{block['index']} | Hash: {block['hash'][:10]}... | Tx: {block['tx_hash'][:10]}...")
            else:
                print_error(f"Error: {resp.get('message')}")
            input("\nPress Enter to continue...")

        elif choice == '9':
            demo_run()

        elif choice == '0':
            print_info("Goodbye!")
            break
        
        else:
            print_warning("Invalid choice")
        
        time.sleep(0.5)

if __name__ == "__main__":
    main()
