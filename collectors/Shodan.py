import shodan
from re import findall
from json import dumps
from termcolor import colored
from configparser import RawConfigParser
from colorama import Fore, Style
import os

def init(domain, debug=False):

	tmp_dir = f"Results/{domain}/.tmp"
	os.makedirs(tmp_dir, exist_ok=True)
	tmp_file = os.path.join(tmp_dir, f"{__name__.split('.')[-1]}.done")

	if os.path.exists(tmp_file):
		if debug:
			print(f"[DEBUG] Skipping {__name__.split('.')[-1]}: already done.")
		return []

	SD = []

	print(Fore.CYAN + Style.BRIGHT + "[+]-Searching in Shodan..." + Style.RESET_ALL)

	parser = RawConfigParser()
	parser.read("config.ini")
	SHODAN_API_KEY = parser.get("Shodan", "SHODAN_API_KEY")
	api = shodan.Shodan(SHODAN_API_KEY)

	if SHODAN_API_KEY == "":
		print("  -->", colored("No Shodan API key configured", "red"))
		return []

	else:
		try:
			try:
				for res in api.search_cursor("hostname:.{0}".format(domain)):
					SD.extend([hostname for hostname in res["hostnames"] if ".{0}".format(domain) in hostname])

				for res in api.search_cursor("ssl:.{0}".format(domain)):
					SD.extend(findall(r"([\w\d][\w\d\-\.]*\.{0})".format(domain.replace(".", r"\.")), dumps(res)))

			except KeyError as errk:
				print("  --> ", colored(errk, "red"))
				return []

			SD = set(SD)

			for subdomain in SD:
				if debug:
					print(Fore.GREEN + f"  [DEBUG] {subdomain}" + Style.RESET_ALL)

			results_dir = f"Results/{domain}/Collectors"
			os.makedirs(results_dir, exist_ok=True)

			output_file = os.path.join(results_dir, "Shodan.txt")

			with open(output_file, "w") as file:
				for subdomain in SD:
					file.write(subdomain + "\n")

			print(Fore.CYAN + f"  --> Subdomains saved to: {output_file}" + Style.RESET_ALL)

			print("  --> {0}: {1}".format(colored("Subdomains found", "white"), colored(len(SD), "green")))

			with open(tmp_file, "w") as f:
				f.write("done\n")

			return SD

		except shodan.exception.APIError as err:
			print("  --> ", colored(err, "red"))
			return []

		except Exception:
			print("  --> ", colored("Something went wrong!", "red"))
			return []
