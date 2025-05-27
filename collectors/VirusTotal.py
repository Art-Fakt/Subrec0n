import requests
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

	VT = []

	print(Fore.CYAN + Style.BRIGHT + "[+]-Searching in VirusTotal..." + Style.RESET_ALL)

	parser = RawConfigParser()
	parser.read("config.ini")
	VT_API_KEY = parser.get("VirusTotal", "VT_API_KEY")

	if VT_API_KEY == "":
		print("  -->", colored("No VirusTotal API key configured", "red"))
		return []

	else:
		parameters = {"domain": domain, "apikey": VT_API_KEY}
		headers = {"user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:88.0) Gecko/20100101 Firefox/88.0"}

		try:
			response = requests.get("https://www.virustotal.com/vtapi/v2/domain/report", params=parameters, headers=headers)
			response_dict = response.json()

			if "subdomains" in response_dict:
				for sd in response_dict["subdomains"]:
					VT.append(sd)

			VT = set(VT)

			for subdomain in VT:
				if debug:
					print(Fore.GREEN + f"  [DEBUG] {subdomain}" + Style.RESET_ALL)

			results_dir = f"Results/{domain}/Collectors"
			os.makedirs(results_dir, exist_ok=True)

			output_file = os.path.join(results_dir, "VirusTotal.txt")

			with open(output_file, "w") as file:
				for subdomain in VT:
					file.write(subdomain + "\n")

			print(Fore.CYAN + f"  --> Subdomains saved to: {output_file}" + Style.RESET_ALL)

			print("  --> {0}: {1}".format(colored("Subdomains found", "white"), colored(len(VT), "green")))

			with open(tmp_file, "w") as f:
				f.write("done\n")

			return VT

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
