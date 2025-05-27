import requests
from re import findall
from json import loads
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

    ZOOM = []

    print(Fore.CYAN + Style.BRIGHT + "[+]-Searching in ZoomEye..." + Style.RESET_ALL)

    parser = RawConfigParser()
    parser.read("config.ini")
    ZOOMEYE_API_KEY = parser.get("ZoomEye", "ZOOMEYE_API_KEY")

    if ZOOMEYE_API_KEY == "":
        print("  --> ", colored("No ZoomEye API key configured", "red"))
        return []

    headers = {"user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:88.0) Gecko/20100101 Firefox/88.0", "API-KEY": ZOOMEYE_API_KEY}
    testFlag = True
    page = 1

    try:
        while testFlag:
            url = f"https://api.zoomeye.org/host/search?query=hostname:{domain}&page={page}"
            response = requests.get(url, headers=headers)

            if response.status_code == 200 and loads(response.text)["available"] > 0:
                subdomains = findall(r"[-\.\w\d]+\.{0}".format(domain.replace(".", r"\.")), response.text)

                if subdomains:
                    for subdomain in subdomains:
                        ZOOM.append(subdomain)

                page += 1
            else:
                testFlag = False

        ZOOM = set(ZOOM)

        if ZOOM:
            results_dir = f"Results/{domain}/Collectors"
            os.makedirs(results_dir, exist_ok=True)

            output_file = os.path.join(results_dir, "ZoomEye.txt")

            with open(output_file, "w") as file:
                for subdomain in ZOOM:
                    file.write(subdomain + "\n")

            print(Fore.CYAN + f"  --> Subdomains saved to: {output_file}" + Style.RESET_ALL)
            print("  --> {0}: {1}".format(colored("Subdomains found", "white"), colored(len(ZOOM), "green")))
        else:
            print("  --> {0}: {1}".format(colored("Subdomains found", "white"), colored(len(ZOOM), "green")))

            with open(tmp_file, "w") as f:
                f.write("done\n")

        return list(ZOOM)

    except requests.exceptions.RequestException as err:
        print("  --> ", colored(err, "red"))
        return []

    except Exception as e:
        print("  --> ", colored(f"Something went wrong: {e}", "red"))
        return []