import requests
from json import loads
from termcolor import colored
from configparser import RawConfigParser
from colorama import Fore, Style
import os

def init(domain, debug=False):
    AlienVault = []

    print(Fore.CYAN + Style.BRIGHT + "[+]-Searching in AlienVault..." + Style.RESET_ALL)

    url = f"https://otx.alienvault.com/api/v1/indicators/domain/{domain}/passive_dns"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:88.0) Gecko/20100101 Firefox/88.0"
    }

    try:
        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            data = loads(response.text)

            if "passive_dns" in data:
                for record in data["passive_dns"]:
                    hostname = record.get("hostname", "")
                    if domain in hostname:
                        AlienVault.append(hostname)

                AlienVault = set(AlienVault)

                for subdomain in AlienVault:
                    if debug:
                        print(Fore.GREEN + f"  [DEBUG] {subdomain}" + Style.RESET_ALL)

                results_dir = f"Results/{domain}/Collectors"
                os.makedirs(results_dir, exist_ok=True)

                output_file = os.path.join(results_dir, "AlienVault.txt")

                with open(output_file, "w") as file:
                    for subdomain in AlienVault:
                        file.write(subdomain + "\n")

                print(Fore.CYAN + f"  --> Subdomains saved to: {output_file}" + Style.RESET_ALL)

                print("  --> {0}: {1}".format(colored("Subdomains found", "white"), colored(len(AlienVault), "green")))
                return AlienVault
            else:
                print("  --> ", colored("No subdomains found.", "yellow"))
                return []

        elif response.status_code == 429:
            print("  --> ", colored("API rate limit exceeded.", "red"))
            return []

        else:
            print("  --> ", colored(f"Error: {response.status_code} - {response.text}", "red"))
            return []

    except requests.exceptions.RequestException as err:
        print("  --> ", colored(err, "red"))
        return []

    except requests.exceptions.HTTPError as errh:
        print("  --> ", colored(errh, "red"))
        return []

    except requests.exceptions.ConnectionError as errc:
        print("  --> ", colored(errc, "red"))
        return []

    except requests.exceptions.Timeout as errt:
        print("  --> ", colored(errt, "red"))
        return []

    except Exception:
        print("  --> ", colored("Something went wrong!", "red"))
        return []