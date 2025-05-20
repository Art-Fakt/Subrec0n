import requests
from json import loads
from termcolor import colored
from colorama import Fore, Style

def init(domain):
	TM = []

	print(Fore.CYAN + Style.BRIGHT + "[+]-Searching in Threatminer..." + Style.RESET_ALL)

	parameters = {"q": "{0}".format(domain), "rt": "5"}
	headers = {"user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:88.0) Gecko/20100101 Firefox/88.0"}

	try:
		response = requests.get("https://api.threatminer.org/v2/domain.php", params=parameters, headers=headers)

		if response.status_code == 200:
			data = loads(response.text)

			if data["status_message"] == "Results found.":
				for item in data["results"]:
					TM.append(item)

			TM = set(TM)

			print("  --> {0}: {1}".format(colored("Subdomains found", "white"), colored(len(TM), "green")))
			return TM

		else:
			print("  -->", colored("Something went wrong!", "red"))
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

	except Exception:
		print("  -->", colored("Something went wrong!", "red"))
		return []
