class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def print_header(text):
    print(f"\n{Colors.BOLD}{Colors.CYAN}{'='*70}\n{text.center(70)}\n{'='*70}{Colors.ENDC}\n")

def print_success(text):
    print(f"{Colors.GREEN}[OK] {text}{Colors.ENDC}")

def print_error(text):
    print(f"{Colors.RED}[X] {text}{Colors.ENDC}")

def print_info(text):
    print(f"{Colors.BLUE}[i] {text}{Colors.ENDC}")

def print_warning(text):
    print(f"{Colors.YELLOW}[!] {text}{Colors.ENDC}")

def print_processing(text, end="\r"):
    print(f"{Colors.CYAN}[*] {text}{Colors.ENDC}", end=end, flush=True)
