import requests
from re import findall
from termcolor import colored
from colorama import Fore, Style
import os

def parseResponse(response, domain):
	hostnameRegex = r"([\w\d][\w\d\-\.]*\.{0})".format(domain.replace(".", r"\."))
	hosts = findall(hostnameRegex, response)

	return [host.lstrip(".") for host in hosts]


def init(domain, debug=False):
	CS = []

	print(Fore.CYAN + Style.BRIGHT + "[+]-Searching in CertSpotter..." + Style.RESET_ALL)

	base_url = "https://api.certspotter.com"
	next_link = "/v1/issuances?domain={0}&include_subdomains=true&expand=dns_names".format(domain)
	headers = {"user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:88.0) Gecko/20100101 Firefox/88.0"}

	while next_link:
		try:
			response = requests.get(base_url + next_link, headers=headers)

			if response.status_code == 429 and len(CS) == 0:
				print("  --> ", colored("Search rate limit exceeded.", "red"))
				return []

			elif response.status_code == 429 and len(CS) > 0:
				break

			CS += parseResponse(response.text, domain)

			try:
				next_link = response.headers["Link"].split(";")[0][1:-1]

			except KeyError:
				break

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

	CS = set(CS)

	for subdomain in CS:
		if debug:
			print(Fore.GREEN + f"  [DEBUG] {subdomain}" + Style.RESET_ALL)

	results_dir = f"Results/{domain}/Collectors"
	os.makedirs(results_dir, exist_ok=True)

	output_file = os.path.join(results_dir, "CertSpotter.txt")

	with open(output_file, "w") as file:
		for subdomain in CS:
			file.write(subdomain + "\n")

	print(Fore.CYAN + f"  --> Subdomains saved to: {output_file}" + Style.RESET_ALL)
	
	print("  --> {0}: {1}".format(colored("Subdomains found", "white"), colored(len(CS), "green")))
	return CS
