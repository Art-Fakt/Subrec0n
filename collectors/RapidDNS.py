import requests
from re import findall
from termcolor import colored
from colorama import Fore, Style
import os

def init(domain, debug=False):
    RAPIDNS = []

    print(Fore.CYAN + Style.BRIGHT + "[+]-Searching in RapidDNS..." + Style.RESET_ALL)

    headers = {"user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:88.0) Gecko/20100101 Firefox/88.0"}
    url = f"https://rapiddns.io/subdomain/{domain}?full=1&down=1"

    try:
        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            subdomains = findall(r"([\w\d][\w\d\-\.]*\.{0})".format(domain.replace(".", r"\.")), response.text)
            RAPIDNS.extend(subdomains)

            RAPIDNS = set(RAPIDNS) 

            for subdomain in RAPIDNS:
                if debug:
                    print(Fore.GREEN + f"  [DEBUG] {subdomain}" + Style.RESET_ALL)

            results_dir = f"Results/{domain}/Collectors"
            os.makedirs(results_dir, exist_ok=True)

            output_file = os.path.join(results_dir, "RapidDNS.txt")

            with open(output_file, "w") as file:
                for subdomain in RAPIDNS:
                    file.write(subdomain + "\n")

            print(Fore.CYAN + f"  --> Subdomains saved to: {output_file}" + Style.RESET_ALL)

            print("  --> {0}: {1}".format(colored("Subdomains found", "white"), colored(len(RAPIDNS), "green")))
            return RAPIDNS

        else:
            print("  --> ", colored("Something went wrong!", "red"))
            return []

    except requests.exceptions.RequestException as err:
        print("  --> ", colored(err, "red"))
        return []

    except Exception:
        print("  --> ", colored("Something went wrong!", "red"))
        return []