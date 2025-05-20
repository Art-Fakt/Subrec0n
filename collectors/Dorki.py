import requests
from termcolor import colored
from configparser import RawConfigParser
from colorama import Fore, Style
import os

def init(domain, debug=False):
    DorkiResults = []

    print(Fore.CYAN + Style.BRIGHT + "\n[!]-BONUS-Searching in Dorki..." + Style.RESET_ALL)

    parser = RawConfigParser()
    parser.read("config.ini")
    DORKI_TOKEN = parser.get("Dorki", "DORKI_TOKEN")
    DORKI_SECRET = parser.get("Dorki", "DORKI_SECRET")

    if DORKI_TOKEN == "" or DORKI_SECRET == "":
        print("  -->", colored("No Dorki API credentials configured", "red"))
        return []

    url = "https://dorki.attaxa.com/api/search"
    params = {"q": f"site:{domain}"}
    headers = {
        "Authorization": f"Bearer {DORKI_TOKEN}",
        "X-Secret-Key": DORKI_SECRET
    }

    try:
        response = requests.get(url, params=params, headers=headers)

        if response.status_code == 200:
            data = response.json()

            if "results" in data:
                for result in data["results"]:
                    if isinstance(result, dict) and "subdomain" in result:
                        subdomain = result["subdomain"]
                        DorkiResults.append(subdomain)
                        if debug:
                            print(Fore.GREEN + f"  [DEBUG] Found subdomain: {subdomain}" + Style.RESET_ALL)

                DorkiResults = set(DorkiResults)
                
                results_dir = f"Results/{domain}"
                os.makedirs(results_dir, exist_ok=True)

                output_file = os.path.join(results_dir, "Dorki.txt")

                with open(output_file, "w") as file:
                    for subdomain in DorkiResults:
                        file.write(subdomain + "\n")

                print("  --> {0}: {1}".format(colored("Elements found", "white"), colored(len(DorkiResults), "green")))
                return DorkiResults
            else:
                print("  --> ", colored("No elements found.", "yellow"))
                return []

        elif response.status_code == 429:
            print("  --> ", colored("API rate limit exceeded.", "red"))
            return []

        else:
            print("  --> ", colored(f"Error: {response.status_code} - {response.text}", "red"))
            return []

    except requests.exceptions.RequestException as err:
        print("  --> ", colored(err, "red"))
        return []

    except Exception as e:
        print("  --> ", colored(f"Something went wrong: {e}", "red"))
        return []