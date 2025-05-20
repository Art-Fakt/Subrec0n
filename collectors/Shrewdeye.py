import requests
from json import loads
from termcolor import colored
from colorama import Fore, Style
import os

def init(domain, debug=False):
    SDE = []

    print(Fore.CYAN + Style.BRIGHT + "[+]-Searching in Shrewdeye.app..." + Style.RESET_ALL)

    parameters = {"q": "%.{0}".format(domain), "output": "json"}
    headers = {
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:88.0) Gecko/20100101 Firefox/88.0",
        "content-type": "application/json"
    }

    try:
        response = requests.get(f"https://shrewdeye.app/api/v1/domains/{domain}/resources", params=parameters, headers=headers)

        if debug:
            print(Fore.YELLOW + f"[DEBUG] HTTP Status Code: {response.status_code}" + Style.RESET_ALL)
            print(Fore.YELLOW + f"[DEBUG] Response Content: {response.text}" + Style.RESET_ALL)

        if response.status_code == 200:
            data = loads(response.text)

            for d in data:
                if "\n" in d["name_value"]:
                    values = d["name_value"].split("\n")

                    for value in values:
                        if not value.startswith("*"):
                            SDE.append(value)

                else:
                    if not d["name_value"].startswith("*"):
                        SDE.append(d["name_value"])

            SDE = set(SDE)

            for subdomain in SDE:
                if debug:
                    print(Fore.GREEN + f"[DEBUG] Found subdomain: {subdomain}" + Style.RESET_ALL)

            results_dir = f"Results/{domain}/Collectors"
            os.makedirs(results_dir, exist_ok=True)

            output_file = os.path.join(results_dir, "Shrewdeye.txt")

            with open(output_file, "w") as file:
                for subdomain in SDE:
                    file.write(subdomain + "\n")

            print(Fore.CYAN + f"  --> Subdomains saved to: {output_file}" + Style.RESET_ALL)
            print("  --> {0}: {1}".format(colored("Subdomains found", "white"), colored(len(SDE), "green")))
            return SDE

        else:
            print(Fore.RED + f"[ERROR] HTTP Status Code: {response.status_code}" + Style.RESET_ALL)
            print(Fore.RED + f"[ERROR] Response Content: {response.text}" + Style.RESET_ALL)
            print("  -->", colored("Something went wrong!", "red"))
            return []

    except requests.exceptions.RequestException as err:
        print(Fore.RED + f"[EXCEPTION] RequestException: {err}" + Style.RESET_ALL)
        return []

    except Exception as e:
        print(Fore.RED + f"[EXCEPTION] Unexpected error: {e}" + Style.RESET_ALL)
        return []