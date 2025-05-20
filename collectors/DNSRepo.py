import requests
from re import findall
from colorama import Fore, Style
import os

def init(domain):
    DNSREPO = []

    print(Fore.CYAN + Style.BRIGHT + "[+]-Searching in DNSRepo..." + Style.RESET_ALL)

    url = f"https://dnsrepo.noc.org/?search=.{domain}"
    headers = {"user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:88.0) Gecko/20100101 Firefox/88.0"}

    try:
        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            subdomains = findall(r"([\w\d][\w\d\-\.]*\.{0})".format(domain.replace(".", r"\.")), response.text)
            DNSREPO.extend(subdomains)

            DNSREPO = set(DNSREPO)

            results_dir = f"Results/{domain}/Collectors"
            os.makedirs(results_dir, exist_ok=True)

            output_file = os.path.join(results_dir, "DNSRepo.txt")
            with open(output_file, "w") as file:
                for subdomain in DNSREPO:
                    file.write(subdomain + "\n")

            print(Fore.CYAN + f"  --> Subdomains saved to: {output_file}" + Style.RESET_ALL)
            print(Fore.WHITE + f"  --> subdomains found: " + Fore.GREEN + f"{len(DNSREPO)}" + Style.RESET_ALL)
            return DNSREPO

        else:
            print(Fore.RED + "  --> Something went wrong!" + Style.RESET_ALL)
            return []

    except requests.exceptions.RequestException as err:
        print(Fore.RED + f"  --> {err}" + Style.RESET_ALL)
        return []