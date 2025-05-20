import requests
import base64
from termcolor import colored
from configparser import RawConfigParser
from colorama import Fore, Style
import os

def init(domain, debug=False):
    HunterHowResults = []

    print(Fore.CYAN + Style.BRIGHT + "[+]-Searching in Hunter.how..." + Style.RESET_ALL)

    parser = RawConfigParser()
    parser.read("config.ini")
    HUNTERHOW_KEY = parser.get("HunterHow", "HUNTERHOW_KEY")

    if HUNTERHOW_KEY == "":
        print("  -->", colored("No HunterHow API key configured", "red"))
        return []

    query = f'domain="{domain}"'
    encoded_query = base64.urlsafe_b64encode(query.encode("utf-8")).decode('ascii')
    page = 1
    page_size = 100
    start_time = '2022-01-01'
    end_time = '2022-12-01'
    fields = 'product,transport_protocol,protocol,banner,country,province,city,asn,org,web,updated_at'

    url = f"https://api.hunter.how/search?api-key={HUNTERHOW_KEY}&query={encoded_query}&page={page}&page_size={page_size}&start_time={start_time}&end_time={end_time}&fields={fields}"

    try:
        response = requests.get(url)

        if response.status_code == 200:
            data = response.json()

            if "results" in data:
                for result in data["results"]:
                    subdomain = result.get("web")
                    if subdomain:
                        HunterHowResults.append(subdomain)
                        if debug:
                            print(Fore.GREEN + f"  [DEBUG] Found subdomain: {subdomain}" + Style.RESET_ALL)

                HunterHowResults = set(HunterHowResults)

                results_dir = f"Results/{domain}/Collectors"
                os.makedirs(results_dir, exist_ok=True)

                output_file = os.path.join(results_dir, "HunterHow.txt")

                with open(output_file, "w") as file:
                    for subdomain in HunterHowResults:
                        file.write(subdomain + "\n")

                print(Fore.CYAN + f"  --> Subdomains saved to: {output_file}" + Style.RESET_ALL)
                print("  --> {0}: {1}".format(colored("Subdomains found", "white"), colored(len(HunterHowResults), "green")))
                return HunterHowResults
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

    except Exception as e:
        print("  --> ", colored(f"Unexpected error: {e}", "red"))
        return []