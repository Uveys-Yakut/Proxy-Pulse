import sys
import signal
from utils.ansi_code import *
from utils.proxy_utils import *
from utils.ascii_art import header
from utils.inpt_validators import *  # Burada validate_yes_no'yu da getiriyoruz.

def handle_interrupt(signal, frame):
    print(f"\n\n{RED}Program interrupted by user. Exiting...{RESET}\n")
    sys.exit(0)

def get_user_input(prompt, default_value, validate_func=None):
    try:
        user_input = input(prompt).strip()
        
        if not user_input:
            return default_value
        
        if validate_func and not validate_func(user_input):
            return get_user_input(prompt, default_value, validate_func)
        
        return user_input
    except EOFError:
        return default_value

def interactive(args):
    signal.signal(signal.SIGINT, handle_interrupt)  # Set up signal handler for Ctrl+C

    clear_terminal()
    header()
    print(f"\n{CYAN}{'='*75}{RESET}")
    print(f"{CYAN}    Welcome to ProxyPulse [v1.0] Proxy Testing Tool - Interactive Mode{RESET}")
    print(f"{CYAN}{'='*75}{RESET}\n")

    file_path = get_user_input(
        f"{YELLOW}[{RED}?{RESET}{YELLOW}] Enter the path to the proxy list file (or leave blank to enter manually): {RESET}", 
        "", 
        validate_file_path
    )
    
    url = get_user_input(
        f"{YELLOW}[{RED}?{RESET}{YELLOW}] Enter the URL to test (default: {args.url}): {RESET}", 
        args.url,
        validate_url
    )
    
    timeout = get_user_input(
        f"{YELLOW}[{RED}?{RESET}{YELLOW}] Enter the timeout duration in seconds (default: {args.timeout}): {RESET}", 
        str(args.timeout),
        validate_positive_integer
    )
    timeout = int(timeout)  # Convert to integer after validation
    
    workers = get_user_input(
        f"{YELLOW}[{RED}?{RESET}{YELLOW}] Enter the number of workers (default: {args.workers}): {RESET}", 
        str(args.workers),
        validate_positive_integer
    )
    workers = int(workers)  # Convert to integer after validation
    
    socks = get_user_input(
        f"{YELLOW}[{RED}?{RESET}{YELLOW}] Test SOCKS5 proxies? (y/n, default: no): {RESET}", 
        "n",
        validate_yes_no  # Burada doğrulama fonksiyonu olarak validate_yes_no kullanılıyor.
    ).lower() == 'y'
    
    output_file =  get_valid_output_file_name(
        f"{YELLOW}[{RED}?{RESET}{YELLOW}] Enter the output file name (default: working_proxies.txt): {RESET}"
    )
    proxy_list = []
    if file_path:
        proxy_list = read_proxies_from_file(file_path, socks)
    else:
        print(f"{YELLOW}No file path provided. Please enter proxies manually.{RESET}")
        while True:
            proxy = input(f"{YELLOW}Enter a proxy (or type 'done' to finish): {RESET}")
            if proxy.lower() == 'done':
                break
            proxy_list.append(proxy)
    
    print(f"\n{CYAN}Total proxies to test: {len(proxy_list)}{RESET}\n")
    
    working_proxies, failed_proxies = find_working_proxies(proxy_list, url, timeout, workers, socks)
    
    if working_proxies:
        print(f"\n{GREEN}✅ Working Proxies ({len(working_proxies)}):{RESET}\n")
        for proxy in working_proxies:
            print(f"{MAGENTA}  {proxy}{RESET}")
        
        # Başarılı proxy'ler varsa dosyaya yaz
        if output_file:
            write_success_proxies_to_file(working_proxies, output_file)
    else:
        # Eğer başarılı proxy yoksa dosya oluşturma
        print(f"{RED}❌ No working proxies found. The output file will not be created.{RESET}\n")
    
    if failed_proxies:
        print(f"\n{RED}❌ Failed Proxies:{RESET}\n")
        for proxy, error in failed_proxies.items():
            print(f"{RED}  {proxy} - Error: {error}{RESET}")
        print("")
