import requests
from urllib.parse import quote
from termcolor import colored
from colorama import Fore, Style
import os

def init(domain, debug=False):
	HT = []

	print(Fore.CYAN + Style.BRIGHT + "[+]-Searching in HackerTarget..." + Style.RESET_ALL)

	url = "https://api.hackertarget.com/hostsearch/?q={0}".format(quote(domain))
	headers = {"user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:88.0) Gecko/20100101 Firefox/88.0"}

	try:
		response = requests.get(url, headers=headers).text
		hostnames = [result.split(",")[0] for result in response.split("\n")]

		for hostname in hostnames:
			if hostname:
				HT.append(hostname)

		HT = set(HT)

		for subdomain in HT:
			if debug:
				print(Fore.GREEN + f"  [DEBUG] {subdomain}" + Style.RESET_ALL)

		results_dir = f"Results/{domain}/Collectors"
		os.makedirs(results_dir, exist_ok=True)

		output_file = os.path.join(results_dir, "HackerTarget.txt")

		with open(output_file, "w") as file:
			for subdomain in HT:
				file.write(subdomain + "\n")

		print(Fore.CYAN + f"  --> Subdomains saved to: {output_file}" + Style.RESET_ALL)

		print("  --> {0}: {1}".format(colored("Subdomains found", "white"), colored(len(HT), "green")))
		return HT

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
