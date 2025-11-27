import time
import os
import sys
import pickle
import socket
from infosec_banking.utils.colors import Colors, print_header

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from infosec_banking.core.client import BankingClient

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def run_dashboard():
    client = BankingClient(port=5005)
    
    while True:
        try:
            resp = client.send_request({"action": "GET_CHAIN"})
            if resp['status'] == 'success':
                chain = resp['chain']
                clear_screen()
                print_header("REAL-TIME BLOCKCHAIN MONITOR")
                print(f"{Colors.BOLD}Network Status: {Colors.GREEN}ONLINE{Colors.ENDC}")
                print(f"Total Blocks:   {len(chain)}")
                print("-" * 80)
                print(f"{'Block #':<8} | {'Hash':<20} | {'Tx Hash':<20} | {'Miner'}")
                print("-" * 80)
                
                for block in chain:
                    b_hash = block['hash'][:18] + "..." if len(block['hash']) > 18 else block['hash']
                    tx_hash = block['tx_hash'][:18] + "..." if len(block['tx_hash']) > 18 else block['tx_hash']
                    miner = block['account_mask']
                    
                    print(f"{block['index']:<8} | {Colors.CYAN}{b_hash:<20}{Colors.ENDC} | {Colors.YELLOW}{tx_hash:<20}{Colors.ENDC} | {miner}")
                
                print("-" * 80)
                print(f"\n{Colors.BLINK}Waiting for new blocks...{Colors.ENDC}")
            else:
                print(f"Error: {resp.get('message')}")
        except Exception as e:
            clear_screen()
            print_header("REAL-TIME BLOCKCHAIN MONITOR")
            print(f"{Colors.BOLD}Network Status: {Colors.RED}OFFLINE{Colors.ENDC}")
            print(f"Error: {e}")
        
        time.sleep(2)

if __name__ == "__main__":
    run_dashboard()
