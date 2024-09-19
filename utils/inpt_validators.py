import os
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
            # print(f"\n{RED}❌ Error: File name cannot be empty.{RESET}\n")
            filename = "working_proxies.txt"
        
        if '.' in filename and not filename.endswith('.txt'):
            print(f"\n{RED}❌ Error: File name must end with '.txt'.{RESET}\n")
            continue
        
        if not filename.endswith('.txt'):
            print(f"\n{MAGENTA}[!] File name does not have a '.txt' extension. Adding '.txt' automatically.{RESET}\n")
            filename += '.txt'
        
        return filename

