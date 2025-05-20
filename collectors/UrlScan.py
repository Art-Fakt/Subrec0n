import requests
from json import loads, dumps
from termcolor import colored
from colorama import Fore, Style
from configparser import RawConfigParser
import os

def init(domain, debug=False):
    URLSCAN = []

    print(Fore.CYAN + Style.BRIGHT + f"\n[!]-BONUS-Small research in Urlscan.io..." + Style.RESET_ALL)

    parser = RawConfigParser()
    parser.read("config.ini")
    URLSCAN_API_KEY = parser.get("URLScan", "URLSCAN_API_KEY")

    if not URLSCAN_API_KEY:
        print("  -->", colored("No UrlScan API key configured in config.ini", "red"))
        return []

    headers = {
        "API-Key": URLSCAN_API_KEY,
        "Content-Type": "application/json"
    }
    data = {
        "url": f"https://{domain}",
        "visibility": "public"
    }

    try:
        response = requests.post("https://urlscan.io/api/v1/scan/", headers=headers, data=dumps(data))

        if response.status_code == 200:
            scan_result = response.json()
            print(Fore.GREEN + f"  [INFO] Scan submitted successfully. Scan ID: {scan_result.get('uuid')}" + Style.RESET_ALL)

            result_url = scan_result.get("result")
            if result_url:
                print(Fore.GREEN + f"  [INFO] Results available at: {result_url}" + Style.RESET_ALL)

                URLSCAN.append(domain)

                #results_dir = f"Results/{domain}/Collectors"
                #os.makedirs(results_dir, exist_ok=True)

                #output_file = os.path.join(results_dir, "URLSCAN.txt")
                #with open(output_file, "w") as file:
                    #for subdomain in URLSCAN:
                        #file.write(subdomain + "\n")
                        
                print(Fore.CYAN + f"  --> Check the generated Link !" + Style.RESET_ALL)
                # print("  --> {0}: {1}".format(colored("Subdomains found", "white"), colored(len(URLSCAN), "green")))
                return URLSCAN
            else:
                print(Fore.YELLOW + "  [WARNING] No result URL returned by UrlScan.io." + Style.RESET_ALL)
                return []
        else:
            print("  --> ", colored(f"Error: {response.status_code} - {response.text}", "red"))
            return []

    except requests.exceptions.RequestException as err:
        print("  --> ", colored(err, "red"))
        return []

    except Exception as e:
        print("  --> ", colored(f"Unexpected error: {e}", "red"))
        return []
