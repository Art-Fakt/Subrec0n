import requests
from termcolor import colored
from configparser import RawConfigParser
from colorama import Fore, Style
import os

def init(domain, debug=False):

	tmp_dir = f"Results/{domain}.tmp"
	os.makedirs(tmp_dir, exist_ok=True)
	tmp_file = os.path.join(tmp_dir, f"{__name__.split('.')[-1]}.done")

	if os.path.exists(tmp_file):
		if debug:
			print(f"[DEBUG] Skipping {__name__.split('.')[-1]}: already done.")
		return []

	PT = []

	print(Fore.CYAN + Style.BRIGHT + "[+]-Searching PassiveTotal..." + Style.RESET_ALL)

	parser = RawConfigParser()
	parser.read("config.ini")
	PT_KEY = parser.get("PassiveTotal", "PT_KEY")
	PT_SECRET = parser.get("PassiveTotal", "PT_SECRET")

	if PT_KEY == "" or PT_SECRET == "":
		print("  -->", colored("No PassiveTotal API credentials configured", "red"))
		return []

	else:
		auth = (PT_KEY, PT_SECRET)
		url = "https://api.passivetotal.org/v2/enrichment/subdomains"
		data = {"query": domain}
		headers = {"user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:88.0) Gecko/20100101 Firefox/88.0"}

		try:
			response = requests.get(url, auth=auth, json=data, headers=headers)

			if response.status_code == 402:
				print("  --> ", colored("Quota exceeded.", "red"))
				return []

			try:
				for subdomain in response.json()["subdomains"]:
					PT.append("%s.%s" % (subdomain, domain))

				PT = set(PT)

				for subdomain in PT:
					print(Fore.GREEN + f"  [DEBUG] {subdomain}" + Style.RESET_ALL)

				results_dir = f"Results/{domain}/Collectors"
				os.makedirs(results_dir, exist_ok=True)

				output_file = os.path.join(results_dir, "PassiveTotal.txt")

				with open(output_file, "w") as file:
					for subdomain in PT:
						file.write(subdomain + "\n")

				print(Fore.CYAN + f"  --> Subdomains saved to: {output_file}" + Style.RESET_ALL)

				print("  --> {0}: {1}".format(colored("Subdomains found", "white"), colored(len(PT), "green")))

				with open(tmp_file, "w") as f:
					f.write("done\n")

				return PT

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
