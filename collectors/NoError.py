import subprocess
from termcolor import colored
from colorama import Fore, Style
import os

def init(domain):
    NOERROR_RESULTS = []

    print(Fore.CYAN + Style.BRIGHT + "[+]-Running DNSX for NOERROR subdomain enumeration..." + Style.RESET_ALL)

    resolvers = "lists/resolvers.txt"
    wordlist = "lists/subdomains.txt" 
    output_file = f"Results/{domain}/Collectors/subs_noerror.txt" 
    os.makedirs(".tmp", exist_ok=True)

    try:
        dnsx_command = [
            "dnsx",
            "-d", domain,
            "-r", resolvers,
            "-silent",
            "-rcode", "noerror",
            "-w", wordlist
        ]

        dnsx_command_str = " ".join(dnsx_command) + f" | cut -d' ' -f1 | anew -q {output_file} >/dev/null"

        result = subprocess.run(dnsx_command_str, shell=True, stderr=subprocess.PIPE, text=True)

        if result.returncode != 0:
            print("  --> ", colored(f"Error executing dnsx: {result.stderr.strip()}", "red"))
            return []

        try:
            with open(output_file, "r") as f:
                for line in f:
                    line = line.strip()
                    if line and domain in line:
                        NOERROR_RESULTS.append(line)

            NOERROR_RESULTS = set(NOERROR_RESULTS)

            print("  --> {0}: {1}".format(colored("Subdomains found", "white"), colored(len(NOERROR_RESULTS), "green")))
            return NOERROR_RESULTS

        except FileNotFoundError:
            print("  --> ", colored(f"Output file {output_file} not found.", "red"))
            return []

    except Exception as e:
        print("  --> ", colored(f"Unexpected error: {e}", "red"))
        return []