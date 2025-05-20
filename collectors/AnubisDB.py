import requests
from re import findall
from colorama import Fore, Style
import os

def init(domain):
    ANUBIS = []

    print(Fore.CYAN + Style.BRIGHT + "[+]-Searching in Anubis-DB..." + Style.RESET_ALL)

    url = f"https://anubisdb.com/anubis/subdomains/{domain}"
    headers = {"user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:88.0) Gecko/20100101 Firefox/88.0"}

    try:
        response = requests.post(url, headers=headers)

        if response.status_code == 200:
            subdomains = findall(r"([\w\d][\w\d\-\.]*\.{0})".format(domain.replace(".", r"\.")), response.text)
            ANUBIS.extend(subdomains)

            ANUBIS = set(ANUBIS)

            results_dir = f"Results/{domain}"
            os.makedirs(results_dir, exist_ok=True)

            output_file = os.path.join(results_dir, "AnubisDB.txt")
            with open(output_file, "w") as file:
                for subdomain in ANUBIS:
                    file.write(subdomain + "\n")

            print(Fore.CYAN + f"  --> Subdomains saved to: {output_file}" + Style.RESET_ALL)
            print(Fore.GREEN + f"  --> {len(ANUBIS)} subdomains found." + Style.RESET_ALL)
            return ANUBIS

        else:
            print(Fore.RED + "  --> Something went wrong!" + Style.RESET_ALL)
            return []

    except requests.exceptions.RequestException as err:
        print(Fore.RED + f"  --> {err}" + Style.RESET_ALL)
        return []