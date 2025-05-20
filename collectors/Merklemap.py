import requests
from bs4 import BeautifulSoup
from termcolor import colored
from colorama import Fore, Style
import os

def init(domain, debug=False):
	MKM = []

	print(Fore.CYAN + Style.BRIGHT + "[+]-Searching in Merklemap..." + Style.RESET_ALL)

	headers = {
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:88.0) Gecko/20100101 Firefox/88.0",
        "content-type": "application/json"
	}

	try:
		response = requests.get(f"https://www.merklemap.com/search?query=.{domain}", headers=headers)

		if debug:
			print(Fore.YELLOW + f"[DEBUG] HTTP Status Code: {response.status_code}" + Style.RESET_ALL)
			print(Fore.YELLOW + f"[DEBUG] Response Headers: {response.headers}" + Style.RESET_ALL)
			print(Fore.YELLOW + f"[DEBUG] Response Content: {response.text[:500]}" + Style.RESET_ALL)  # Limiter l'affichage pour éviter de surcharger

		if response.status_code == 200:
			try:
                # Analyse du contenu HTML avec BeautifulSoup
				soup = BeautifulSoup(response.text, 'html.parser')

                # Exemple : Supposons que les sous-domaines sont dans des balises <td> avec une classe spécifique
				for td in soup.find_all('td', class_='subdomain'):
					subdomain = td.text.strip()
					if subdomain:
						MKM.append(subdomain)
						if debug:
							print(Fore.GREEN + f"[DEBUG] Found subdomain: {subdomain}" + Style.RESET_ALL)

				MKM = set(MKM)

				results_dir = f"Results/{domain}/Collectors"
				os.makedirs(results_dir, exist_ok=True)

				output_file = os.path.join(results_dir, "Merklemap.txt")
				with open(output_file, "w") as file:
					for subdomain in MKM:
						file.write(subdomain + "\n")

				print(Fore.CYAN + f"  --> Subdomains saved to: {output_file}" + Style.RESET_ALL)
				print("  --> {0}: {1}".format(colored("Subdomains found", "white"), colored(len(MKM), "green")))
				return MKM

			except Exception as e:
				print(Fore.RED + "[ERROR] Failed to parse HTML response." + Style.RESET_ALL)
				print(Fore.RED + f"[ERROR] Exception: {e}" + Style.RESET_ALL)
				return []

		else:
			print(Fore.RED + f"[ERROR] HTTP Status Code: {response.status_code}" + Style.RESET_ALL)
			print(Fore.RED + f"[ERROR] Response Content: {response.text[:500]}" + Style.RESET_ALL)  # Limiter l'affichage
			print("  -->", colored("Something went wrong!", "red"))
			return []

	except requests.exceptions.RequestException as err:
		print("  -->", colored(err, "red"))
		return []

	except requests.exceptions.HTTPError as errh:
		print("  -->", colored(errh, "red"))
		return []

	except requests.exceptions.ConnectionError as errc:
		print("  -->", colored(errc, "red"))
		return []

	except requests.exceptions.Timeout as errt:
		print("  -->", colored(errt, "red"))
		return []

	except Exception:
		print("  -->", colored("Something went wrong!", "red"))
		return []