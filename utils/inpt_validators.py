import os
import re
from .ansi_code import *
from urllib.parse import urlparse

def validate_file_path(file_path):
    if file_path:
        if not os.path.isfile(file_path):
            print(f"\n{RED}❌ Error: The file '{file_path}' does not exist.{RESET}\n")
            return False
        if not os.access(file_path, os.R_OK):
            print(f"\n{RED}❌ Error: The file '{file_path}' is not readable.{RESET}\n")
            return False
        if not file_path.lower().endswith('.txt'):
            print(f"\n{RED}❌ Error: The file '{file_path}' must be a '.txt' file.{RESET}\n")
            return False
    else:
        print(f"\n{RED}❌ Error: File path cannot be empty.{RESET}\n")
    return True

def validate_filename(filename):
    if not filename:
        print(f"\n{RED}❌ Error: File name cannot be empty.{RESET}\n")
        return False
    invalid_chars = r'<>:"/\|?*'
    if any(char in filename for char in invalid_chars):
        print(f"\n{RED}❌ Error: File name contains invalid characters: {invalid_chars}.{RESET}\n")
        return False
    return True

def validate_positive_integer(value):
    try:
        num = int(value)
        if num <= 0:
            print(f"\n{RED}❌ Error: Value must be a positive integer.{RESET}\n")
            return False
        return True
    except ValueError:
        print(f"\n{RED}❌ Error: Value must be an integer.{RESET}\n")
        return False

def validate_url(url):
    try:
        result = urlparse(url)
        if not (result.scheme and result.netloc):
            print(f"\n{RED}❌ Error: The URL '{url}' is invalid. It must include a scheme (e.g., 'http') and a network location.{RESET}\n")
            return False
        return True
    except Exception:
        print(f"\n{RED}❌ Error: The URL '{url}' is invalid.{RESET}\n")
        return False

def validate_yes_no(user_input):
    if user_input not in ['y', 'n']:
        print(f"\n{RED}❌ Error: Input must be 'y' or 'n'.{RESET}\n")
        return False
    return True

def get_valid_output_file_name(prompt):
    while True:
        filename = input(prompt).strip()
        
        if not filename:
            filename = "working_proxies.txt"
        
        if '.' in filename and not filename.endswith('.txt'):
            print(f"\n{RED}❌ Error: File name must end with '.txt'.{RESET}\n")
            continue
        
        if not filename.endswith('.txt'):
            print(f"\n{MAGENTA}[!] File name does not have a '.txt' extension. Adding '.txt' automatically.{RESET}\n")
            filename += '.txt'
        
        return filename

def validate_and_format_proxies(proxy_list, socks=False):
    """
    Validates and formats proxy strings.
    Supported formats:
      - ip:port
      - http://ip:port
      - https://ip:port
      - socks5://ip:port
    """

    valid_proxies = []

    proxy_pattern = re.compile(
        r'^(?:http://|https://|socks5://)?'
        r'(\d{1,3}(?:\.\d{1,3}){3})'
        r':(\d{2,5})$'
    )

    for proxy in proxy_list:
        proxy = proxy.strip()
        if not proxy:
            continue

        match = proxy_pattern.match(proxy)
        if not match:
            continue

        ip, port = match.groups()

        # Port range check
        if not (1 <= int(port) <= 65535):
            continue

        if socks:
            formatted_proxy = f"socks5://{ip}:{port}"
        else:
            formatted_proxy = f"http://{ip}:{port}"

        valid_proxies.append(formatted_proxy)

    return valid_proxies
