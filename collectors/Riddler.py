import requests
from json import loads
from urllib.parse import quote
from termcolor import colored
from configparser import RawConfigParser
from colorama import Fore, Style


def init(domain):
	riddler = []

	print(Fore.CYAN + Style.BRIGHT + "[+]-Searching in Riddler..." + Style.RESET_ALL)

	parser = RawConfigParser()
	parser.read("config.ini")
	RIDDLER_USERNAME = parser.get("Riddler", "RIDDLER_USERNAME")
	RIDDLER_PASSWORD = parser.get("Riddler", "RIDDLER_PASSWORD")

	if RIDDLER_USERNAME == "" or RIDDLER_PASSWORD == "":
		print("  -->", colored("No Riddler API credentials configured", "red"))
		return []

	else:
		auth = {"email": RIDDLER_USERNAME, "password": RIDDLER_PASSWORD}
		auth_url = "https://riddler.io/auth/login"
		headers = {"user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:88.0) Gecko/20100101 Firefox/88.0", "content-type": "application/json"}

		try:
			auth_response = requests.post(auth_url, json=auth, headers=headers)
			auth_response_json = loads(auth_response.text)

			if auth_response_json["meta"]["code"] == 200:
				auth_token = auth_response_json["response"]["user"]["authentication_token"]
				search = {"query": "pld:{0}".format(quote(domain)), "output": "host"}
				search_url = "https://riddler.io/api/search"
				headers = {"user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:88.0) Gecko/20100101 Firefox/88.0", "content-type": "application/json", "authentication-token": auth_token}

				search_response = requests.post(search_url, json=search, headers=headers)

				if search_response.status_code == 500:
					print("  -->", colored("Internal Server Error.", "red"))
					return riddler

				else:
					search_response_json = loads(search_response.text)

				for item in search_response_json:
					riddler.append(item["host"])

				riddler = set(riddler)

				print("  --> {0}: {1}".format(colored("Subdomains found", "white"), colored(len(riddler), "green")))
				return riddler

			else:
				print("  -->", colored("Invalid Riddler API credentials.", "red"))
				return []

		except requests.exceptions.RequestException as err:
			print("  -->", colored(err, "red"))
			return []

		except requests.exceptions.HTTPError as errh:
			print("  -->", colored(errh, "red"))
			return []

		except requests.exceptions.ConnectionError as errc:
			print("  -->", colored(errc, "red"))
			return []

		except requests.exceptions.Timeout as errt:
			print("  -->", colored(errt, "red"))
			return []

		except ValueError as errv:
			print("  -->", colored(errv, "red"))
			return []

		except Exception:
			print("  -->", colored("Something went wrong!", "red"))
			return []
