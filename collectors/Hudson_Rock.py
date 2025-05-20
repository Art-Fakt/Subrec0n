import requests
from json import loads
from termcolor import colored
from colorama import Fore, Style
import os

def init(domain, debug=False):
	HR = []

	print(Fore.CYAN + Style.BRIGHT + "[+]-Searching in Hudson Rock..." + Style.RESET_ALL)

	#parameters = {"q": "%.{0}".format(domain), "output": "json"}
	headers = {"user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:88.0) Gecko/20100101 Firefox/88.0", "content-type": "application/json"}

	try:
		response = requests.get("https://cavalier.hudsonrock.com/api/json/v2/osint-tools/search-by-domain?domain=" + domain, headers=headers)
		data = response.json()
		if response.status_code == 200:
			data = loads(response.text)

			for d in data:
				if "\n" in d["name_value"]:
					values = d["name_value"].split("\n")

					for value in values:
						if not value.startswith("*"):
							HR.append(value)

				else:
					if not d["name_value"].startswith("*"):
						HR.append(d["name_value"])

			HR = set(HR)

			for subdomain in HR:
				if debug:
					print(Fore.GREEN + f"  [DEBUG] {subdomain}" + Style.RESET_ALL)

			results_dir = f"Results/{domain}"
			os.makedirs(results_dir, exist_ok=True)

			output_file = os.path.join(results_dir, "HudsonRock.txt")

			with open(output_file, "w") as file:
				for subdomain in HR:
					file.write(subdomain + "\n")

			print(Fore.CYAN + f"  --> Subdomains saved to: {output_file}" + Style.RESET_ALL)

			print("  --> {0}: {1}".format(colored("Subdomains found", "white"), colored(len(HR), "green")))
			return HR

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
