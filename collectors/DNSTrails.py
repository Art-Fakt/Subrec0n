import requests
from json import loads
from termcolor import colored
from configparser import RawConfigParser
from colorama import Fore, Style
import os

def init(domain):
	DT = []

	print(Fore.CYAN + Style.BRIGHT + "[+]-Searching in DNSTrails..." + Style.RESET_ALL)

	parser = RawConfigParser()
	parser.read("config.ini")
	DNSTrails_API_KEY = parser.get("DNSTrails", "DNSTRAILS_API_KEY")

	if DNSTrails_API_KEY == "":
		print("  -->", colored("No DNSTrails API key configured", "red"))
		return []

	else:
		headers = {"user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:88.0) Gecko/20100101 Firefox/88.0", "content-type": "application/json", "APIKEY": DNSTrails_API_KEY}
		url = "https://api.securitytrails.com/v1/domain/{}/subdomains".format(domain)

		try:
			response = requests.get(url, headers=headers)

			if response.status_code == 429:
				print("  --> ", colored("You've exceeded the usage limits for your account.", "red"))
				return []

			else:
				payload = loads(response.text)

			for item in payload["subdomains"]:
				DT.append(".".join([item, domain]))

			DT = set(DT)

			results_dir = f"Results/{domain}/Collectors"
			os.makedirs(results_dir, exist_ok=True)

			output_file = os.path.join(results_dir, "DNSTrails.txt")

			with open(output_file, "w") as file:
				for subdomain in DT:
					file.write(subdomain + "\n")

			print("  --> {0}: {1}".format(colored("Subdomains found", "white"), colored(len(DT), "green")))
			return DT

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
