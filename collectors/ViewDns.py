import requests
from termcolor import colored
from colorama import Fore, Style
from configparser import RawConfigParser
import os

def init(ip, debug=False):
    VIEWDNS_RESULTS = []

    print(Fore.CYAN + Style.BRIGHT + "[+]-Searching in ViewDNS..." + Style.RESET_ALL)

    parser = RawConfigParser()
    parser.read("config.ini")
    VIEWDNS_API_KEY = parser.get("ViewDNS", "VIEWDNS_API_KEY")

    if not VIEWDNS_API_KEY:
        print("  -->", colored("No ViewDNS API key configured in config.ini", "red"))
        return []

    api_url = f"https://api.viewdns.info/reversedns/?ip={ip}&apikey={VIEWDNS_API_KEY}&output=json"

    try:
        response = requests.get(api_url)

        if response.status_code == 200:
            data = response.json()

            if "response" in data and "rdns" in data["response"]:
                rdns_records = data["response"]["rdns"]
                for record in rdns_records:
                    host = record.get("name")
                    if host:
                        VIEWDNS_RESULTS.append(host)
                        if debug:
                            print(Fore.GREEN + f"  [DEBUG] Found reverse DNS record: {host}" + Style.RESET_ALL)

            VIEWDNS_RESULTS = set(VIEWDNS_RESULTS)

            results_dir = f"Results/{ip}"
            os.makedirs(results_dir, exist_ok=True)

            output_file = os.path.join(results_dir, "ViewDNS.txt")
            with open(output_file, "w") as file:
                for record in VIEWDNS_RESULTS:
                    file.write(record + "\n")

            print(Fore.CYAN + f"  --> Reverse DNS records saved to: {output_file}" + Style.RESET_ALL)
            print("  --> {0}: {1}".format(colored("Reverse DNS records found", "white"), colored(len(VIEWDNS_RESULTS), "green")))
            return VIEWDNS_RESULTS

        else:
            print("  --> ", colored(f"Error: {response.status_code} - {response.text}", "red"))
            return []

    except requests.exceptions.RequestException as err:
        print("  --> ", colored(err, "red"))
        return []

    except Exception as e:
        print("  --> ", colored(f"Unexpected error: {e}", "red"))
        return []