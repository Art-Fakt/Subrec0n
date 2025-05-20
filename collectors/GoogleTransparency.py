import requests
from re import findall
from termcolor import colored
from colorama import Fore, Style
import os

def parseResponse(response, domain):
	try:
		try:
			token = findall(r"(\w+)\",[\w\"]+,\d+,\d+\]\]\]$", response)[0]
		except Exception:
			token = "null"

		hostnameRegex = r"([\w\d][\w\d\-\.]*\.{0})".format(domain.replace(".", r"\."))
		hosts = findall(hostnameRegex, response)

		return token, [host.lstrip(".") for host in hosts]

	except Exception:
		return "null", []


def init(domain, debug=False):
	GTR = []

	print(Fore.CYAN + Style.BRIGHT + "[+]-Searching in Google Transparency..." + Style.RESET_ALL)

	baseURL = "https://www.google.com/transparencyreport/api/v3/httpsreport/ct/certsearch"
	headers = {"user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:88.0) Gecko/20100101 Firefox/88.0", "referrer": "https://transparencyreport.google.com/https/certificates"}
	token = ""

	try:
		while True:
			if not token:
				url = "".join([baseURL, "?domain=", domain, "&include_expired=true&include_subdomains=true"])

			else:
				url = "".join([baseURL, "/page?domain=", domain, "&include_expired=true&include_subdomains=true&p=", token])

			response = requests.get(url, headers=headers)
			token, hostnames = parseResponse(response.text, domain)

			for hostname in hostnames:
				GTR.append(hostname)

			if token == "null":
				break

		GTR = set(GTR)

		for subdomain in GTR:
			if debug:
				print(Fore.GREEN + f"  [DEBUG] {subdomain}" + Style.RESET_ALL)

			results_dir = f"Results/{domain}/Collectors"
			os.makedirs(results_dir, exist_ok=True)

			output_file = os.path.join(results_dir, "GoogleTransparency.txt")

			with open(output_file, "w") as file:
				for subdomain in GTR:
					file.write(subdomain + "\n")

			print(Fore.CYAN + f"  --> Subdomains saved to: {output_file}" + Style.RESET_ALL)

		print("  --> {0}: {1}".format(colored("Subdomains found", "white"), colored(len(GTR), "green")))
		return GTR

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
