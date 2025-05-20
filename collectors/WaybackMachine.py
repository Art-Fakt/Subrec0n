import requests
from urllib.parse import quote
from termcolor import colored
from urllib.parse import urlparse
from colorama import Fore, Style
import os

def init(domain, debug=False):
	WB = []

	print(Fore.CYAN + Style.BRIGHT + "[+]-Searching in WaybackMachine..." + Style.RESET_ALL)

	url = "http://web.archive.org/cdx/search/cdx?url=*.{0}&output=json&fl=original&collapse=urlkey".format(quote(domain))
	headers = {"user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:88.0) Gecko/20100101 Firefox/88.0"}

	try:
		response = requests.get(url, headers=headers)
		urls = response.json()

		for url in urls:
			urlString = url[0]

			if domain in urlString:
				parsed_uri = urlparse(urlString)
				onlyDomain = "{uri.netloc}".format(uri=parsed_uri).split(":")[0]
				WB.append(onlyDomain)

			else:
				pass

		WB = set(WB)

		for subdomain in WB:
			if debug:
				print(Fore.GREEN + f"  [DEBUG] {subdomain}" + Style.RESET_ALL)

		results_dir = f"Results/{domain}/Collectors"
		os.makedirs(results_dir, exist_ok=True)

		output_file = os.path.join(results_dir, "Wayback.txt")

		with open(output_file, "w") as file:
			for subdomain in WB:
				file.write(subdomain + "\n")

		print(Fore.CYAN + f"  --> Subdomains saved to: {output_file}" + Style.RESET_ALL)

		print("  --> {0}: {1}".format(colored("Subdomains found", "white"), colored(len(WB), "green")))
		return WB

	except ValueError as errv:
		print("  --> ", colored(errv, "red"))
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
