import subprocess
from termcolor import colored
from colorama import Fore, Style
import os

def init(domain):
    ANALYTICS_RESULTS = []

    print(Fore.CYAN + Style.BRIGHT + "[+]-Running AnalyticsRelationships for finding domain relationships..." + Style.RESET_ALL)

    output_file = f"Results/{domain}/Collectors/analytics.txt"
    os.makedirs("Results", exist_ok=True) 

    try:
        analytics_command = [
            "analyticsrelationships",
            "-ch", domain
        ]

        analytics_command_str = " ".join(analytics_command) + f" > {output_file}"

        result = subprocess.run(analytics_command_str, shell=True, stderr=subprocess.PIPE, text=True)

        if result.returncode != 0:
            print("  --> ", colored(f"Error executing analyticsrelationships: {result.stderr.strip()}", "red"))
            return []

        try:
            with open(output_file, "r") as f:
                for line in f:
                    line = line.strip()
                    if line and domain in line:
                        ANALYTICS_RESULTS.append(line)

            ANALYTICS_RESULTS = set(ANALYTICS_RESULTS) 

            print("  --> {0}: {1}".format(colored("Relationships found", "white"), colored(len(ANALYTICS_RESULTS), "green")))
            return ANALYTICS_RESULTS

        except FileNotFoundError:
            print("  --> ", colored(f"Output file {output_file} not found.", "red"))
            return []

    except Exception as e:
        print("  --> ", colored(f"Unexpected error: {e}", "red"))
        return []