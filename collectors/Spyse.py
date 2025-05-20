import requests
from json import loads
from termcolor import colored
from configparser import RawConfigParser
from colorama import Fore, Style
import os

def init(domain, debug=False):
	SP = []

	print(Fore.CYAN + Style.BRIGHT + "[+]-Searching in Spyse..." + Style.RESET_ALL)

	parser = RawConfigParser()
	parser.read("config.ini")
	SPYSE_API_TOKEN = parser.get("Spyse", "SPYSE_API_TOKEN")

	if SPYSE_API_TOKEN == "":
		print("  -->", colored("No Spyse API token configured", "red"))
		return []

	headers = {
		"user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:88.0) Gecko/20100101 Firefox/88.0",
		"Authorization": "Bearer {0}".format(SPYSE_API_TOKEN),
		"accept": "application/json"
	}

	limit = 100
	offset = 0
	url = "https://api.spyse.com/v3/data/domain/subdomain?limit={0}&offset={1}&domain={2}".format(limit, offset, domain)

	try:
		response = requests.get(url, headers=headers)

		if response.status_code == 200:
			response_json = loads(response.text)

			for item in response_json["data"]["items"]:
				SP.append(item["name"])

			total_count = response_json["data"]["total_count"]

			if total_count > limit:
				offset += limit

				while offset < total_count:
					url = "https://api.spyse.com/v3/data/domain/subdomain?limit={0}&offset={1}&domain={2}".format(limit, offset, domain)

					response = requests.get(url, headers=headers)

					if response.status_code == 200:
						response_json = loads(response.text)

						for item in response_json["data"]["items"]:
							SP.append(item["name"])

						offset += limit

					elif response.status_code == 402:
						break;

			SP = set(SP)

			for subdomain in SP:
				if debug:
					print(Fore.GREEN + f"  [DEBUG] {subdomain}" + Style.RESET_ALL)

			results_dir = f"Results/{domain}"
			os.makedirs(results_dir, exist_ok=True)

			output_file = os.path.join(results_dir, "HackerTarget.txt")

			with open(output_file, "w") as file:
				for subdomain in SP:
					file.write(subdomain + "\n")

			print(Fore.CYAN + f"  --> Subdomains saved to: {output_file}" + Style.RESET_ALL)

			print("  -->  {0}: {1}".format(colored("Subdomains found", "white"), colored(len(SP), "green")))
			return SP

		elif response.status_code == 401:
			print("  --> ", colored("Authentication error.", "red"))
			return []

		elif response.status_code == 402:
			print("  --> ", colored("Request quota exceeded.", "red"))
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
