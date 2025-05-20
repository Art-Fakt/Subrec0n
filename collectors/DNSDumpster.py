import requests
from json import dumps
from termcolor import colored
from colorama import Fore, Style
from configparser import RawConfigParser
import os

def init(domain, debug=False):
    DNSDUMPSTER = []

    print(Fore.CYAN + Style.BRIGHT + "[+]-Searching in DNSDumpster..." + Style.RESET_ALL)

    parser = RawConfigParser()
    parser.read("config.ini")
    DNSDUMPSTER_API_KEY = parser.get("DNSDumpster", "DNSDUMPSTER_API_KEY")

    if not DNSDUMPSTER_API_KEY:
        print("  -->", colored("No DNSDumpster API key configured in config.ini", "red"))
        return []

    headers = {
        "X-API-Key": DNSDUMPSTER_API_KEY
    }
    url = f"https://api.dnsdumpster.com/domain/{domain}"

    try:
        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            data = response.json()

            for record in data.get("a", []):
                host = record.get("host")
                if host:
                    DNSDUMPSTER.append(host)
                    if debug:
                        print(Fore.GREEN + f"  [DEBUG] Found A record: {host}" + Style.RESET_ALL)

            for record in data.get("ns", []):
                host = record.get("host")
                if host:
                    DNSDUMPSTER.append(host)
                    if debug:
                        print(Fore.GREEN + f"  [DEBUG] Found NS record: {host}" + Style.RESET_ALL)

            DNSDUMPSTER = set(DNSDUMPSTER)

            results_dir = f"Results/{domain}/Collectors"
            os.makedirs(results_dir, exist_ok=True)

            output_file = os.path.join(results_dir, "DNSDumpster.txt")
            with open(output_file, "w") as file:
                for subdomain in DNSDUMPSTER:
                    file.write(subdomain + "\n")

            print(Fore.CYAN + f"  --> Subdomains saved to: {output_file}" + Style.RESET_ALL)
            print("  --> {0}: {1}".format(colored("Subdomains found", "white"), colored(len(DNSDUMPSTER), "green")))
            return DNSDUMPSTER

        else:
            print("  --> ", colored(f"Error: {response.status_code} - {response.text}", "red"))
            return []

    except requests.exceptions.RequestException as err:
        print("  --> ", colored(err, "red"))
        return []

    except Exception as e:
        print("  --> ", colored(f"Unexpected error: {e}", "red"))
        return []