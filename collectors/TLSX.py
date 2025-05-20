import subprocess
import os
from termcolor import colored
from colorama import Fore, Style

def init(domain):
    TLSX_RESULTS = []

    print(Fore.CYAN + Style.BRIGHT + "[+]-Running TLSX for subdomain enumeration..." + Style.RESET_ALL)

    tlsx_threads = 50  
    tls_ports = "443,8443"
    input_file = "lists/subdomains.txt"
    results_dir = f"Results/{domain}/Collectors"
    output_file = f"{results_dir}/tlsx.txt"

    os.makedirs(results_dir, exist_ok=True)

    try:
        tlsx_command = [
            "tlsx",
            "-san",
            "-cn",
            "-silent",
            "-ro",
            "-c", str(tlsx_threads),
            "-p", tls_ports,
            "-o", output_file
        ]

        tlsx_command.append(f"<{input_file}")

        result = subprocess.run(" ".join(tlsx_command), shell=True, stderr=subprocess.PIPE, text=True)

        if result.returncode != 0:
            print("  --> ", colored(f"Error executing tlsx: {result.stderr.strip()}", "red"))
            return []

        try:
            with open(output_file, "r") as f:
                for line in f:
                    line = line.strip()
                    if line and domain in line:
                        TLSX_RESULTS.append(line)

            TLSX_RESULTS = set(TLSX_RESULTS)

            print("  --> {0}: {1}".format(colored("Subdomains found", "white"), colored(len(TLSX_RESULTS), "green")))
            return TLSX_RESULTS

        except FileNotFoundError:
            print("  --> ", colored(f"Output file {output_file} not found.", "red"))
            return []

    except Exception as e:
        print("  --> ", colored(f"Unexpected error: {e}", "red"))
        return []