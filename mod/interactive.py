import sys
import signal
from colorama import Fore
from utils.ansi_code import *
from utils.proxy_utils import *
from utils.ascii_art import header
from utils.inpt_validators import *

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
    signal.signal(signal.SIGINT, handle_interrupt)

    clear_terminal()
    header()
    print(f"\n{CYAN}{'='*75}{RESET}")
    print(f"{CYAN}    Welcome to ProxyPulse [v1.0] Proxy Testing Tool - Interactive Mode{RESET}")
    print(f"{CYAN}{'='*75}{RESET}\n")

    file_path = get_user_input(
        f"{YELLOW}[{RED}?{RESET}{YELLOW}] Enter the path to the proxy list file (or leave blank to enter manually): {Fore.YELLOW}", 
        "", 
        validate_file_path
    )
    
    url = get_user_input(
        f"{YELLOW}[{RED}?{RESET}{YELLOW}] Enter the URL to test (default: {args.url}): {Fore.YELLOW}", 
        args.url,
        validate_url
    )
    
    timeout = get_user_input(
        f"{YELLOW}[{RED}?{RESET}{YELLOW}] Enter the timeout duration in seconds (default: {args.timeout}): {Fore.YELLOW}", 
        str(args.timeout),
        validate_positive_integer
    )
    timeout = int(timeout)
    
    workers = get_user_input(
        f"{YELLOW}[{RED}?{RESET}{YELLOW}] Enter the number of workers (default: {args.workers}): {Fore.YELLOW}", 
        str(args.workers),
        validate_positive_integer
    )
    workers = int(workers)
    
    socks = get_user_input(
        f"{YELLOW}[{RED}?{RESET}{YELLOW}] Test SOCKS5 proxies? (y/n, default: no): {Fore.YELLOW}", 
        "n",
        validate_yes_no
    ).lower() == 'y'
    
    output_file =  get_valid_output_file_name(
        f"{YELLOW}[{RED}?{RESET}{YELLOW}] Enter the output file name (default: working_proxies.txt): {Fore.YELLOW}"
    )
    proxy_list = []
    if file_path:
        proxy_list = read_proxies_from_file(file_path, socks)
    else:
        print(f"{Fore.YELLOW}\n[!] No file path provided. Please enter proxies manually.")
        while True:
            proxy = input(f"\n{YELLOW}Enter a proxy (or type 'done' to finish): {Fore.YELLOW}")
            if proxy.lower() == 'done':
                break
            proxy_list.append(proxy)
    
    print(f"\n{CYAN}Total proxies to test: {len(proxy_list)}{RESET}\n")
    
    working_proxies, failed_proxies = find_working_proxies(proxy_list, url, timeout, workers, socks)
    
    if failed_proxies:
        print(f"\n{RED}❌ Failed Proxies:{RESET}\n")
        for proxy, error in failed_proxies.items():
            print(f"{RED}  {proxy} - Error: {error}{RESET}")
        print("")
    
    if working_proxies:
        print(f"\n{GREEN}✅ Working Proxies ({len(working_proxies)}):{RESET}\n")
        for proxy in working_proxies:
            print(f"{MAGENTA}  {proxy}{RESET}")
        
        if output_file:
            write_success_proxies_to_file(working_proxies, output_file)
    else:
        print(f"{RED}❌ No working proxies found. The output file will not be created.{RESET}\n")
