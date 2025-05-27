import requests
from termcolor import colored
from configparser import RawConfigParser
from colorama import Fore, Style
import os

def init(domain, debug=False):

    tmp_dir = f"Results/{domain}.tmp"
    os.makedirs(tmp_dir, exist_ok=True)
    tmp_file = os.path.join(tmp_dir, f"{__name__.split('.')[-1]}.done")

    if os.path.exists(tmp_file):
        print(f"[WARN] Skipping {__name__.split('.')[-1]}: already done.")
        return []

    ST = []

    print(Fore.CYAN + Style.BRIGHT + "[+]-Searching in SecurityTrails..." + Style.RESET_ALL)

    parser = RawConfigParser()
    parser.read("config.ini")
    ST_API_KEY = parser.get("SecurityTrails", "ST_API_KEY")

    if ST_API_KEY == "":
        print("  -->", colored("No SecurityTrails API key configured", "red"))
        return []

    else:
        url = f"https://api.securitytrails.com/v1/domain/{domain}/subdomains"
        headers = {
            "apikey": f"{ST_API_KEY}",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:88.0) Gecko/20100101 Firefox/88.0"
        }

        try:
            response = requests.get(url, headers=headers)

            if response.status_code == 429:
                print("  -->", colored("API limit exceeded.", "red"))
                return []

            if response.status_code != 200:
                print("  -->", colored(f"Error: {response.status_code} - {response.text}", "red"))
                return []

            try:
                data = response.json()
                for subdomain in data.get("subdomains", []):
                    ST.append(f"{subdomain}.{domain}")

                ST = set(ST)

                for subdomain in ST:
                    if debug:
                        print(Fore.GREEN + f"  [DEBUG] {subdomain}" + Style.RESET_ALL)

                results_dir = f"Results/{domain}/Collectors"
                os.makedirs(results_dir, exist_ok=True)

                output_file = os.path.join(results_dir, "SecurityTrails.txt")

                with open(output_file, "w") as file:
                    for subdomain in ST:
                        file.write(subdomain + "\n")

                print(Fore.CYAN + f"  --> Subdomains saved to: {output_file}" + Style.RESET_ALL)
                
                print("  --> {0}: {1}".format(colored("Subdomains found", "white"), colored(len(ST), "green")))

                with open(tmp_file, "w") as f:
                    f.write("done\n")

                return ST

            except KeyError as errk:
                print("  -->", colored(errk, "red"))
                return []

        except requests.exceptions.RequestException as err:
            print("  -->", colored(err, "red"))
            return []

        except requests.exceptions.HTTPError as errh:
            print("  -->", colored(errh, "red"))
            return []

        except requests.exceptions.ConnectionError as errc:
            print("  -->", colored(errc, "red"))
            return []

        except requests.exceptions.Timeout as errt:
            print("  -->", colored(errt, "red"))
            return []

        except Exception:
            print("  -->", colored("Something went wrong!", "red"))
            return []