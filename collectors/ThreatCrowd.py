import requests
from json import loads
from termcolor import colored
from colorama import Fore, Style


def init(domain):
    TC = []

    print(Fore.CYAN + Style.BRIGHT + "[+]-Searching in ThreatCrowd..." + Style.RESET_ALL)

    try:
        url = f"https://www.threatcrowd.org/searchApi/v2/domain/report/"
        params = {"domain": domain}
        response = requests.get(url, params=params, timeout=10)

        if response.status_code == 200:
            data = response.json()

            if data.get("response_code") == "1" and "subdomains" in data:
                subdomains = data["subdomains"]
                TC = set(subdomains)

                print("  --> {0}: {1}".format(colored("Subdomains found", "white"), colored(len(TC), "green")))
                return TC
            else:
                print(Fore.RED + "  --> No subdomains found or invalid response." + Style.RESET_ALL)
                return []

        else:
            print(Fore.RED + f"  --> Something went wrong! HTTP Status Code: {response.status_code}" + Style.RESET_ALL)
            print(Fore.RED + f"  --> Response Content: {response.text}" + Style.RESET_ALL)
            return []

    except requests.exceptions.RequestException as err:
        print(Fore.RED + f"  --> Request error: {err}" + Style.RESET_ALL)
        return []

    except Exception as e:
        print(Fore.RED + f"  --> Unexpected error: {e}" + Style.RESET_ALL)
        return []