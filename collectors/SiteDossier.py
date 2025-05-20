import requests
import re
from termcolor import colored
from colorama import Fore, Style
from utilities.ScanHelpers import domainHas2Levels

def init(domain):
    SiteDossier = []

    print(Fore.CYAN + Style.BRIGHT + "[+]-Searching in SiteDossier.com..." + Style.RESET_ALL)

    data = ""
    page = 1

    try:
        while "No data currently available." not in data:
            url = f"http://www.sitedossier.com/parentdomain/{domain}/{page}"
            response = requests.get(url)

            if "your IP has been blacklisted" in response.text:
                print(Fore.RED + "[-] Your IP has been blacklisted by SiteDossier." + Style.RESET_ALL)
                return []

            data = response.text
            page += 100

            pattern = r'(?!2?F)[a-zA-Z0-9\-\.]*\.' + re.escape(domain.split('.')[0]) + r'\.' + re.escape(domain.split('.')[1])
            if domainHas2Levels(domain):
                pattern = r'(?!2?F)[a-zA-Z0-9\-\.]*\.' + re.escape(domain.split('.')[0]) + r'\.' + re.escape(domain.split('.')[1]) + r'\.' + re.escape(domain.split('.')[2])

            for subdomain in re.findall(pattern, data):
                if subdomain not in SiteDossier:
                    SiteDossier.append(subdomain)

    except requests.exceptions.RequestException as err:
        print(Fore.RED + f"[-] RequestException: {err}" + Style.RESET_ALL)
        return []

    except Exception as e:
        print(Fore.RED + f"[-] An error occurred: {e}" + Style.RESET_ALL)
        return []

    SiteDossier = set(SiteDossier)

    print("  --> {0}: {1}".format(colored("Subdomains found", "white"), colored(len(SiteDossier), "green")))
    return SiteDossier
