import requests
from json import loads
from termcolor import colored
from colorama import Fore, Style
import os

def init(domain, debug=False):
	CRT = []

	print(Fore.CYAN + Style.BRIGHT + "[+]-Searching in Crt.sh..." + Style.RESET_ALL)

	parameters = {"q": "%.{0}".format(domain), "output": "json"}
	headers = {"user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:88.0) Gecko/20100101 Firefox/88.0", "content-type": "application/json"}

	try:
		response = requests.get("https://crt.sh/?", params=parameters, headers=headers)

		if response.status_code == 200:
			data = loads(response.text)

			for d in data:
				if "\n" in d["name_value"]:
					values = d["name_value"].split("\n")

					for value in values:
						if not value.startswith("*"):
							CRT.append(value)

				else:
					if not d["name_value"].startswith("*"):
						CRT.append(d["name_value"])

			CRT = set(CRT)

			for subdomain in CRT:
				if debug:
					print(Fore.GREEN + f"  [DEBUG] {subdomain}" + Style.RESET_ALL)

			results_dir = f"Results/{domain}/Collectors"
			os.makedirs(results_dir, exist_ok=True)

			output_file = os.path.join(results_dir, "CRT.txt")

			with open(output_file, "w") as file:
				for subdomain in CRT:
					file.write(subdomain + "\n")

			print(Fore.CYAN + f"  --> Subdomains saved to: {output_file}" + Style.RESET_ALL)

			print("  --> {0}: {1}".format(colored("Subdomains found", "white"), colored(len(CRT), "green")))
			return CRT

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
