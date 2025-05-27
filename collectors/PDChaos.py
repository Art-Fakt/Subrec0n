import requests
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

	PDCH = []

	print(Fore.CYAN + Style.BRIGHT + "[+]-Searching in Project Discovery Chaos..." + Style.RESET_ALL)

	parser = RawConfigParser()
	parser.read("config.ini")
	CHAOS_KEY = parser.get("PDChaos", "CHAOS_API_KEY")

	if CHAOS_KEY == "":
		print("  -->", colored("No Project Discovery Chaos API key configured", "red"))
		return []

	headers = {"user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:88.0) Gecko/20100101 Firefox/88.0", "Authorization": CHAOS_KEY}
	url = "https://dns.projectdiscovery.io/dns/{0}/subdomains".format(domain)

	try:
		response = requests.get(url, headers=headers).text
		subdomains = loads(response)["subdomains"]

		for subdomain in subdomains:
			if subdomain:
				PDCH.append("{0}.{1}".format(subdomain, domain))

		PDCH = set(PDCH)

		for subdomain in PDCH:
			if debug:
				print(Fore.GREEN + f"  [DEBUG] {subdomain}" + Style.RESET_ALL)

		results_dir = f"Results/{domain}/Collectors"
		os.makedirs(results_dir, exist_ok=True)

		output_file = os.path.join(results_dir, "PDChaos.txt")

		with open(output_file, "w") as file:
			for subdomain in PDCH:
				file.write(subdomain + "\n")
		
		print(Fore.CYAN + f"  --> Subdomains saved to: {output_file}" + Style.RESET_ALL)

		print("  --> {0}: {1}".format(colored("Subdomains found", "white"), colored(len(PDCH), "green")))

		with open(tmp_file, "w") as f:
			f.write("done\n")

		return PDCH

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
