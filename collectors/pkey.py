import requests
from json import loads
from termcolor import colored
from colorama import Fore, Style
import os

def init(domain, debug=False):
	PKEY = []

	print(Fore.CYAN + Style.BRIGHT + "[+]-Searching in Pkey.in..." + Style.RESET_ALL)

	parameters = {"q": "%.{0}".format(domain), "output": "json"}
	headers = {'Pragma': 'no-cache', 'Origin': 'https://www.pkey.in', "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:88.0) Gecko/20100101 Firefox/88.0", "content-type": "application/json"}

	data = [('zone', domain), ('submit', ''), ]

	try:
		response = requests.post('https://www.pkey.in/tools-i/search-subdomains',
							headers=headers, data=data, verify=False, timeout=10.0)
		scraped = response.text
		trimmed = scraped[scraped.find('<table class="clearborder">'):scraped.rfind(
		'</tbody>')].split('\n')
		
		if response.status_code == 200:
			data = loads(response.text)

			for d in data:
				if "\n" in d["name_value"]:
					values = d["name_value"].split("\n")

					for value in values:
						if not value.startswith("*"):
							PKEY.append(value)

				else:
					if not d["name_value"].startswith("*"):
						PKEY.append(d["name_value"])

			PKEY = set(PKEY)

			for subdomain in PKEY:
				if debug:
					print(Fore.GREEN + f"  [DEBUG] {subdomain}" + Style.RESET_ALL)

			results_dir = f"Results/{domain}"
			os.makedirs(results_dir, exist_ok=True)

			output_file = os.path.join(results_dir, "CRT.txt")

			with open(output_file, "w") as file:
				for subdomain in PKEY:
					file.write(subdomain + "\n")

			print(Fore.CYAN + f"  --> Subdomains saved to: {output_file}" + Style.RESET_ALL)

			print("  --> {0}: {1}".format(colored("Subdomains found", "white"), colored(len(PKEY), "green")))
			return PKEY

		else:
			print(Fore.RED + f"  --> Something went wrong! HTTP Status Code: {response.status_code}" + Style.RESET_ALL)
			# print(Fore.RED + f"  --> Response Content: {response.text}" + Style.RESET_ALL)
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
