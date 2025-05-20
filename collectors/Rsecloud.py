import requests
from bs4 import BeautifulSoup
from termcolor import colored
from colorama import Fore, Style
from configparser import RawConfigParser
import os

def init(domain, debug=False):
    RSE = []

    print(Fore.CYAN + Style.BRIGHT + "[+]-Searching in RseCloud..." + Style.RESET_ALL)

    parser = RawConfigParser()
    parser.read("config.ini")
    RSECLOUD_KEY = parser.get("Rsecloud", "RSECLOUD_KEY")

    if not RSECLOUD_KEY:
        print("  -->", colored("No Rsecloud API key configured in config.ini", "red"))
        return []

    headers = {
        "X-API-Key": RSECLOUD_KEY
    }
    url = f"https://app.rsecloud.com/subdomain_scanning/overview?search={domain}&sort_by=created_at&order=desc"

    if debug:
        print(Fore.YELLOW + f"[DEBUG] URL: {url}" + Style.RESET_ALL)
        print(Fore.YELLOW + f"[DEBUG] Headers: {headers}" + Style.RESET_ALL)

    try:
        response = requests.get(url, headers=headers)

        if debug:
            print(Fore.YELLOW + f"[DEBUG] HTTP Status Code: {response.status_code}" + Style.RESET_ALL)
            print(Fore.YELLOW + f"[DEBUG] Response Content: {response.text[:500]}" + Style.RESET_ALL)  # Limiter l'affichage pour éviter de surcharger

        if response.status_code == 200:
            try:
                soup = BeautifulSoup(response.text, 'html.parser')

                for td in soup.find_all('td', class_='subdomain'):
                    subdomain = td.text.strip()
                    if subdomain:
                        RSE.append(subdomain)
                        if debug:
                            print(Fore.GREEN + f"  [DEBUG] Found subdomain: {subdomain}" + Style.RESET_ALL)

                RSE = set(RSE)

                results_dir = f"Results/{domain}/Collectors"
                os.makedirs(results_dir, exist_ok=True)

                output_file = os.path.join(results_dir, "RseCloud.txt")
                with open(output_file, "w") as file:
                    for subdomain in RSE:
                        file.write(subdomain + "\n")

                print(Fore.CYAN + f"  --> Subdomains saved to: {output_file}" + Style.RESET_ALL)
                print("  --> {0}: {1}".format(colored("Subdomains found", "white"), colored(len(RSE), "green")))
                return RSE

            except Exception as e:
                print(Fore.RED + "[ERROR] Failed to parse HTML response." + Style.RESET_ALL)
                print(Fore.RED + f"[ERROR] Exception: {e}" + Style.RESET_ALL)
                return []

        else:
            print(Fore.RED + f"[ERROR] HTTP Status Code: {response.status_code}" + Style.RESET_ALL)
            print(Fore.RED + f"[ERROR] Response Content: {response.text[:500]}" + Style.RESET_ALL)  # Limiter l'affichage
            return []

    except requests.exceptions.RequestException as err:
        print(Fore.RED + f"[EXCEPTION] RequestException: {err}" + Style.RESET_ALL)
        return []

    except Exception as e:
        print(Fore.RED + f"[EXCEPTION] Unexpected error: {e}" + Style.RESET_ALL)
        return []