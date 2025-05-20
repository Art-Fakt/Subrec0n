import requests
from re import findall
from json import loads
from base64 import b64encode
from termcolor import colored
from configparser import RawConfigParser
from colorama import Fore, Style
import os

def init(domain, debug=False):
	FOFA = []

	print(Fore.CYAN + Style.BRIGHT + "[+]-Searching in FOFA..." + Style.RESET_ALL)

	parser = RawConfigParser()
	parser.read("config.ini")
	FOFA_EMAIL = parser.get("FOFA", "FOFA_EMAIL")
	FOFA_KEY = parser.get("FOFA", "FOFA_KEY")

	if FOFA_EMAIL == "" or FOFA_KEY == "":
		print("  -->", colored("No FOFA API credentials configured", "red"))
		return []

	size = 10000
	page = 1
	encodedDomain = b64encode(domain.encode("utf8")).decode("utf8")
	parameters = {"email": FOFA_EMAIL, "key": FOFA_KEY, "qbase64": encodedDomain, "page": page, "size": size, "full": "true", "fields": "host,title,domain,header,banner,cert"}
	headers = {"user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:88.0) Gecko/20100101 Firefox/88.0"}

	try:
		response = requests.get("https://fofa.so/api/v1/search/all", params=parameters, headers=headers)

		if response.status_code == 200 and loads(response.text)["error"] is False:
			data = loads(response.text)

			resultNumber = data["size"]

			if resultNumber % size == 0:
				pagesToRequest = resultNumber // size
			else:
				pagesToRequest = (resultNumber // size) +1

			while page <= pagesToRequest:

				if page != 1:
					parameters = {"email": FOFA_EMAIL, "key": FOFA_KEY, "qbase64": encodedDomain, "page": page, "size": size, "full": "true", "fields": "host,title,domain,header,banner,cert"}
					response = requests.get("https://fofa.so/api/v1/search/all", params=parameters, headers=headers)

				if loads(response.text)["error"] is False:
					FOFA.extend([item.lower() for item in findall(r"([\w\d][\w\d\-\.]*\.{0})".format(domain.replace(".", r"\.")), response.text)])
					page += 1
				else:
					break

			FOFA = set(FOFA)

			for subdomain in FOFA:
				if debug:
					print(Fore.GREEN + f"  [DEBUG] {subdomain}" + Style.RESET_ALL)

			results_dir = f"Results/{domain}/Collectors"
			os.makedirs(results_dir, exist_ok=True)

			output_file = os.path.join(results_dir, "FOFA.txt")

			with open(output_file, "w") as file:
				for subdomain in FOFA:
					file.write(subdomain + "\n")

			print(Fore.CYAN + f"  --> Subdomains saved to: {output_file}" + Style.RESET_ALL)

			print("  --> {0}: {1}".format(colored("Subdomains found", "white"), colored(len(FOFA), "green")))
			return FOFA

		else:
			print("  --> ", colored("Something went wrong!", "red"))
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
