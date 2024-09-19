import sys
import argparse
from colorama import init, Fore, Style
from termcolor import colored
from utils.proxy_utils import *
from utils.inpt_validators import *
from utils.ascii_art import header
from mod.interactive import interactive
from utils.proxy_utils import load_arguments_from_json

init(autoreset=True)

class ColoredHelpFormatter(argparse.HelpFormatter):
    def _format_action(self, action):
        parts = super()._format_action(action).split("\n")
        if not parts:
            return ""
        parts[0] = colored(parts[0], 'cyan')
        
        if len(parts) > 1:
            parts[1] = colored(parts[1], 'yellow')
        return "\n".join(parts)

def main():
    clear_terminal()
    header()
    print(f"\n{CYAN}{'='*75}{RESET}")
    print(f"{CYAN}    Welcome to ProxyPulse [v1.0] Proxy Testing Tool - Command Mode{RESET}")
    print(f"{CYAN}{'='*75}{RESET}\n")

    args_config = load_arguments_from_json("utils/data/commands.json")
    
    parser = argparse.ArgumentParser(
        prog="ProxyPulse",
        add_help=False,
        formatter_class=ColoredHelpFormatter
    )

    for arg in args_config:
        kwargs = {}
        if 'short' in arg:
            kwargs['short'] = arg['short']
        if 'long' in arg:
            kwargs['long'] = arg['long']
        if 'default' in arg:
            kwargs['default'] = arg['default']
        if 'type' in arg:
            kwargs['type'] = eval(arg['type'])
        if 'action' in arg:
            kwargs['action'] = arg['action']
        if 'help' in arg:
            kwargs['help'] = arg['help']
        
        # Argümanları ekle
        if 'short' in kwargs and 'long' in kwargs:
            parser.add_argument(f'-{kwargs["short"]}', f'--{kwargs["long"]}', **{k: v for k, v in kwargs.items() if k not in ['short', 'long']})
        elif 'long' in kwargs:
            parser.add_argument(f'--{kwargs["long"]}', **{k: v for k, v in kwargs.items() if k != 'long'})
        elif 'short' in kwargs:
            parser.add_argument(f'-{kwargs["short"]}', **{k: v for k, v in kwargs.items() if k != 'short'})
    
    args = parser.parse_args()

    help_text = parser.format_help()

    help_text = help_text.replace('options:', f'{BLUE}options:{RESET}')
    help_text = help_text.replace('usage:', f'{BLUE}usage:{RESET}{GREEN}')
    help_text = help_text.replace('ProxyPulse [v1.0] Proxy Testing Tool', f'{BLUE}ProxyPulse [v1.0] Proxy Testing Tool{RESET}')
    for arg in args_config:
        if 'help' in arg:
            help_text = help_text.replace(f'{arg["help"]}', f'{GREEN}{arg["help"]}{RESET}')
    
    if args.mode == 'interactive':
        interactive(args)
    else:
        if args.help:
            print(help_text)
            return sys.exit()
        
        # Argüman doğrulama
        if args.file and not validate_file_path(args.file):
            return
        
        if args.output:
            if '.' in args.output:
                ext = args.output.rsplit('.', 1)[1].lower()
                if ext != 'txt':
                    print(f"\n{RED}❌ Error: File name must have a '.txt' extension.{RESET}\n")
                    sys.exit()
            else:
                print(f"\n{MAGENTA}[!] File name does not have a '.txt' extension. Adding '.txt' automatically.{RESET}\n")
                args.output += '.txt'
        
        if not validate_url(args.url):
            return
        
        if not validate_positive_integer(args.timeout):
            return
        
        if not validate_positive_integer(args.workers):
            return

        if args.file:
            proxy_list = read_proxies_from_file(args.file, args.socks)
        elif not args.proxies:
            print(f"{Fore.RED}❌ Important-Message: No proxy list provided!{Style.RESET_ALL}\n")
            return

        if not proxy_list:
            print(f"{Fore.RED}Error: Proxy list is empty or invalid!{Style.RESET_ALL}")
            return
        
        print(f"\n{Fore.CYAN}Total proxies to test: {len(proxy_list)}{Style.RESET_ALL}\n")
        
        try:
            working_proxies, failed_proxies = find_working_proxies(proxy_list, args.url, args.timeout, args.workers, args.socks)
        except ValueError as e:
            print(f"{Fore.RED}Error: {str(e)}{Style.RESET_ALL}")
            return
        
        if working_proxies:
            print(f"\n{Fore.GREEN}✅ Working Proxies ({len(working_proxies)}):{Style.RESET_ALL}\n")
            for proxy in working_proxies:
                print(f"{Fore.MAGENTA}  {proxy}{Style.RESET_ALL}")
            
            if args.output:
                write_success_proxies_to_file(working_proxies, args.output)
        else:
            print(f"{Fore.RED}❌ No working proxies found. The output file will not be created.{Style.RESET_ALL}")

        if failed_proxies:
            print(f"\n{Fore.RED}❌ Failed Proxies:{Style.RESET_ALL}\n")
            for proxy, error in failed_proxies.items():
                print(f"{Fore.RED}  {proxy} - Error: {error}{Style.RESET_ALL}")
            print("")

if __name__ == "__main__":
    main()
