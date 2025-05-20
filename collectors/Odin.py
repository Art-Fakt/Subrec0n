import requests
from json import loads
from termcolor import colored
from configparser import RawConfigParser
from colorama import Fore, Style
import os

def init(domain, keyword="", limit=100, published_after="", published_before=""):
    FullHunt = []

    print(Fore.CYAN + Style.BRIGHT + "[+]-Searching in Odin..." + Style.RESET_ALL)

    # Lecture des clés API depuis config.ini
    parser = RawConfigParser()
    parser.read("config.ini")
    ODIN_KEY = parser.get("Odin", "ODIN_KEY")

    if ODIN_KEY == "":
        print("  -->", colored("No Odin API key configured", "red"))
        return []

    # Configuration de l'URL, des en-têtes et du payload
    url = "https://api.odin.io/v1/domain/subdomain/search"
    payload = {
        "domain": domain,
        "keyword": keyword,
        "limit": limit,
        "publishedAfter": published_after,
        "publishedBefore": published_before,
        "start": [{}]
    }
    headers = {
        "X-API-Key": ODIN_KEY,
        "Content-Type": "application/json"
    }

    try:
        response = requests.post(url, json=payload, headers=headers)

        if response.status_code == 200:
            data = response.json()

            if "hosts" in data:
                FullHunt.extend(data["hosts"])
                FullHunt = set(FullHunt)

                results_dir = f"Results/{domain}/Collectors"
                os.makedirs(results_dir, exist_ok=True)

                output_file = os.path.join(results_dir, "Odin.txt")

                with open(output_file, "w") as file:
                    for subdomain in FullHunt:
                        file.write(subdomain + "\n")

                print("  --> {0}: {1}".format(colored("Subdomains found", "white"), colored(len(FullHunt), "green")))
                return FullHunt
            else:
                print("  --> ", colored("No subdomains found.", "yellow"))
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

    except requests.exceptions.HTTPError as errh:
        print("  --> ", colored(errh, "red"))
        return []

    except requests.exceptions.ConnectionError as errc:
        print("  --> ", colored(errc, "red"))
        return []

    except requests.exceptions.Timeout as errt:
        print("  --> ", colored(errt, "red"))
        return []

    except Exception:
        print("  --> ", colored("Something went wrong!", "red"))
        return []