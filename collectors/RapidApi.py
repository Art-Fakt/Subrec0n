import requests
from termcolor import colored
from configparser import RawConfigParser
from colorama import Fore, Style
import os

def init(domain, debug=False):
    RapidApiResults = []

    print(Fore.CYAN + Style.BRIGHT + "[+]-Searching in RapidAPI Subdomain Finder..." + Style.RESET_ALL)

    # Lecture des clés API depuis config.ini
    parser = RawConfigParser()
    parser.read("config.ini")
    RAPIDAPI_KEY = parser.get("RapidAPI", "RAPIDAPI_KEY")

    if RAPIDAPI_KEY == "":
        print("  -->", colored("No RapidAPI key configured", "red"))
        return []

    # Configuration de l'URL, des paramètres et des en-têtes
    url = "https://subdomain-finder5.p.rapidapi.com/subdomain-finder"
    querystring = {"domain": domain}
    headers = {
        "x-rapidapi-key": RAPIDAPI_KEY,
        "x-rapidapi-host": "subdomain-finder5.p.rapidapi.com"
    }

    try:
        response = requests.get(url, headers=headers, params=querystring)

        if response.status_code == 200:
            data = response.json()

            if "subdomains" in data:
                RapidApiResults.extend(data["subdomains"])
                RapidApiResults = set(RapidApiResults)

                results_dir = f"Results/{domain}/Collectors"
                os.makedirs(results_dir, exist_ok=True)

                output_file = os.path.join(results_dir, "RapidApi.txt")

                with open(output_file, "w") as file:
                    for subdomain in RapidApiResults:
                        file.write(subdomain + "\n")

                print(Fore.CYAN + f"  --> Subdomains saved to: {output_file}" + Style.RESET_ALL)
                print("  --> {0}: {1}".format(colored("Subdomains found", "white"), colored(len(RapidApiResults), "green")))
                return RapidApiResults
            else:
                print("  -->", colored("No subdomains found.", "yellow"))
                return []

        elif response.status_code == 429:
            print("  -->", colored("API rate limit exceeded.", "red"))
            return []

        else:
            print("  -->", colored(f"Error: {response.status_code} - {response.text}", "red"))
            return []

    except requests.exceptions.RequestException as err:
        print("  -->", colored(err, "red"))
        return []

    except Exception as e:
        print("  -->", colored(f"Unexpected error: {e}", "red"))
        return []