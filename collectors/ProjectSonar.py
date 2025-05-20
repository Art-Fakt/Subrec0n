import requests
from json import loads
from termcolor import colored
from colorama import Fore, Style


def init(domain):
	Sonar = []

	print(Fore.CYAN + Style.BRIGHT + "[+]-Searching in Rapid7 Open Data..." + Style.RESET_ALL)


	url = "http://dns.bufferover.run/dns?q=.{0}".format(domain)
	headers = {"user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:88.0) Gecko/20100101 Firefox/88.0"}

	try:
		response = requests.get(url, headers=headers)
		response_json = loads(response.text)

		if response_json["FDNS_A"]:
			for record in response_json["FDNS_A"]:
				Sonar += record.split(",")

		if response_json["RDNS"]:
			for record in response_json["RDNS"]:
				Sonar.append(record.split(",")[1])

		print("  --> {0}: {1}".format(colored("subdomains found", "white"), colored(len(Sonar), "green")))
		return Sonar

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
