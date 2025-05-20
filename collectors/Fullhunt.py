import requests
from json import loads
from termcolor import colored
from configparser import RawConfigParser
from colorama import Fore, Style
import os

def init(domain):
    FullHunt = []

    print(Fore.CYAN + Style.BRIGHT + "[+]-Searching in FullHunt..." + Style.RESET_ALL)

    parser = RawConfigParser()
    parser.read("config.ini")
    FULLHUNT_KEY = parser.get("FullHunt", "FULLHUNT_KEY")

    if FULLHUNT_KEY == "":
        print("  -->", colored("No FullHunt API key configured", "red"))
        return []

    url = f"https://fullhunt.io/api/v1/domain/{domain}/subdomains"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:88.0) Gecko/20100101 Firefox/88.0",
        "X-API-KEY": FULLHUNT_KEY
    }

    try:
        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            data = loads(response.text)

            if "hosts" in data:
                FullHunt.extend(data["hosts"])
                FullHunt = set(FullHunt)

                results_dir = f"Results/{domain}/Collectors"
                os.makedirs(results_dir, exist_ok=True)

                output_file = os.path.join(results_dir, "FullHunt.txt")

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