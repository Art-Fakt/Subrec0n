import requests
from re import findall
from json import loads
from termcolor import colored
from configparser import RawConfigParser
from colorama import Fore, Style
import os

def init(domain, debug=False):

	tmp_dir = f"Results/{domain}/.tmp"
	os.makedirs(tmp_dir, exist_ok=True)
	tmp_file = os.path.join(tmp_dir, f"{__name__.split('.')[-1]}.done")

	if os.path.exists(tmp_file):
		print(f"[WARN] Skipping {__name__.split('.')[-1]}: already done.")
		return []
	
	C = []

	print(Fore.CYAN + Style.BRIGHT + "[+]-Searching Censys..." + Style.RESET_ALL)

	parser = RawConfigParser()
	parser.read("config.ini")
	API_URL = "https://search.censys.io/api/v1"
	UID = parser.get("Censys", "CENSYS_UID")
	SECRET = parser.get("Censys", "CENSYS_SECRET")

	if UID == "" or SECRET == "":
		print("  -->", colored("No Censys API credentials configured", "red"))
		return []

	else:
		payload = {"query": domain}

		try:
			res = requests.post(API_URL + "/search/certificates", json=payload, auth=(UID, SECRET))

			if res.status_code == 429:
				print("  --> ", colored("Rate limit exceeded. See https://www.censys.io/account for rate limit details.", "red"))
				return C

			C = findall(r"CN=([\w\d][\w\d\-\.]*\.{0})".format(domain.replace(".", r"\.")), str(res.content))
			numberOfPages = findall(r"pages\":\s(\d+)?}", str(res.content))

			for page in range(2, int(numberOfPages[0]) + 1):
				payload = {"query": domain, "page": page}
				res = requests.post(API_URL + "/search/certificates", json=payload, auth=(UID, SECRET))

				if res.status_code != 200:
					if loads(res.text)["error_type"] == "max_results":
						print("  --> ", colored("Search result limit reached. See https://www.censys.io/account for search results limit details.", "red"))
						break
					
					else:
						print("  --> {0} {1} {2}".format(colored("An error occured on page", "red"), colored("{0}:".format(page), "red"), colored(loads(res.text)["error_type"], "red")))

				else:
					tempC = findall(r"CN=([\w\d][\w\d\-\.]*\.{0})".format(domain.replace(".", r"\.")), str(res.content))
					C = C + tempC

			C = set(C)

			for subdomain in C:
				if debug:
					print(Fore.GREEN + f"  [DEBUG] {subdomain}" + Style.RESET_ALL)

			results_dir = f"Results/{domain}/Collectors"
			os.makedirs(results_dir, exist_ok=True)

			output_file = os.path.join(results_dir, "Censys.txt")

			with open(output_file, "w") as file:
				for subdomain in C:
					file.write(subdomain + "\n")

			print(Fore.CYAN + f"  --> Subdomains saved to: {output_file}" + Style.RESET_ALL)

			print("  --> {0}: {1}".format(colored("Subdomains found", "white"), colored(len(C), "yellow")))

			with open(tmp_file, "w") as f:
				f.write("done\n")

			return C

		except KeyError as errk:
			print("  --> ", colored(errk, "red"))
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
