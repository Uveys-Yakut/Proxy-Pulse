import os
import json
import random
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
from .ansi_code import *

def clear_terminal():
    os.system('cls' if os.name == 'nt' else 'clear')

def load_arguments_from_json(file_path):
    with open(file_path, 'r') as f:
        config = json.load(f)
    
    return config["arguments"]

def write_success_proxies_to_file(proxies, file_path):
    try:
        with open(file_path, 'w') as file:
            for proxy in proxies:
                file.write(f"{proxy}\n")
        print(f"\n{GREEN}✅ Proxies saved to {file_path}{RESET}\n")
    except Exception as e:
        print(f"\n{RED}❌ Error saving proxies: {str(e)}{RESET}\n")
        
def test_proxy(proxy, test_url, timeout, is_socks):
    proxy_type = 'HTTP' if not is_socks else 'SOCKS5'
    
    try:
        proxies = {
            "http": proxy,
            "https": proxy,
        }
        response = requests.get(test_url, proxies=proxies, timeout=timeout)
        
        if response.status_code == 200:
            return (proxy, True, proxy_type)
        else:
            return (proxy, False, f"HTTP {response.status_code}")
    except requests.exceptions.Timeout:
        return (proxy, False, "Timeout")
    except requests.exceptions.TooManyRedirects:
        return (proxy, False, "Redirects")
    except requests.exceptions.RequestException as e:
        return (proxy, False, "Request Error")

def read_proxies_from_file(filepath, is_socks):
    if not os.path.exists(filepath):
        print(f"{RED}❌ File not found{RESET}")
        return []
    
    with open(filepath, 'r') as file:
        proxies = file.read().splitlines()
    
    proxies = [proxy.strip() for proxy in proxies if proxy.strip()]
    
    if is_socks:
        if not all(proxy.startswith('socks5://') for proxy in proxies):
            print(f"{RED}❌ SOCKS5 proxies required{RESET}")
            return []
    else:
        if any(proxy.startswith('socks5://') for proxy in proxies):
            print(f"{RED}❌ HTTP/HTTPS only{RESET}")
            return []
    
    return proxies

def find_working_proxies(proxy_list, url, timeout, workers, socks):
    working_proxies = []
    failed_proxies = {}
    
    with ThreadPoolExecutor(max_workers=workers) as executor:
        future_to_proxy = {executor.submit(test_proxy, proxy, url, timeout, socks): proxy for proxy in proxy_list}
        
        for future in as_completed(future_to_proxy):
            proxy = future_to_proxy[future]
            try:
                result = future.result()
                if result[1]:
                    print(f"{GREEN}✅ Success ({result[2]}): {result[0]}{RESET}\n")
                    working_proxies.append(result[0])
                else:
                    print(f"{RED}❌ Failed ({result[2]}): {result[0]}{RESET}\n")
                    failed_proxies[result[0]] = result[2]
            except Exception as e:
                failed_proxies[proxy] = "Error"
    
    return working_proxies, failed_proxies
