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

    proxy_list = []
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
        
        if 'short' in kwargs and 'long' in kwargs:
            parser.add_argument(f'-{kwargs["short"]}', f'--{kwargs["long"]}', **{k: v for k, v in kwargs.items() if k not in ['short', 'long']})
        elif 'long' in kwargs:
            parser.add_argument(f'--{kwargs["long"]}', **{k: v for k, v in kwargs.items() if k != 'long'})
        elif 'short' in kwargs:
            parser.add_argument(f'-{kwargs["short"]}', **{k: v for k, v in kwargs.items() if k != 'short'})
            
    args = parser.parse_args()

    if args.mode not in ['interactive', 'command']:
        print(f"{RED}● Error: Invalid mode specified. Valid options are 'interactive' or 'command'.{RESET}\n")
        sys.exit()

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

        elif args.proxies:
            proxy_list = parse_proxies_from_argument(args.proxies, args.socks)
        else:
            print(f"{RED}❌ Important-Message: No proxy list provided!{RESET}\n")
            return
        
        print(f"\n{CYAN}Total proxies to test: {len(proxy_list)}{RESET}\n")
        
        try:
            working_proxies, failed_proxies = find_working_proxies(proxy_list, args.url, args.timeout, args.workers, args.socks)
        except ValueError as e:
            print(f"{RED}Error: {str(e)}{RESET}")
            return
        
        if failed_proxies:
            print(f"\n{RED}❌ Failed Proxies:{RESET}\n")
            for proxy, error in failed_proxies.items():
                print(f"{RED}  {proxy} - Error: {error}{RESET}")
            print("")

        if working_proxies:
            print(f"\n{GREEN}✅ Working Proxies ({len(working_proxies)}):{RESET}\n")
            for proxy in working_proxies:
                print(f"{MAGENTA}  {proxy}{RESET}")
            
            if args.output:
                write_success_proxies_to_file(working_proxies, args.output)
        else:
            print(f"{RED}❌ No working proxies found. The output file will not be created.{RESET}")

if __name__ == "__main__":
    main()
