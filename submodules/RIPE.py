import requests
import ipaddress
from re import findall
from termcolor import colored
from colorama import Fore, Style

def init(domain):
	R = []
	print(Fore.CYAN + Style.BRIGHT + f"\n[+]-Searching RIPE database for networks..." + Style.RESET_ALL)

	headers = {"user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:88.0) Gecko/20100101 Firefox/88.0"}
	searchUrl = "https://rest.db.ripe.net/search.json?query-string={0}&flags=no-referenced&flags=no-irt&source=RIPE".format(domain.split(".")[-2])

	try:
		response = requests.get(searchUrl, headers=headers)
		IPranges = findall(r"value\"\s:\s\"(\d+\.\d+\.\d+\.\d+\s-\s\d+\.\d+\.\d+\.\d+)\"", response.text)

		for arange in IPranges:
			startip = ipaddress.IPv4Address(arange.split(" - ")[0])
			endip = ipaddress.IPv4Address(arange.split(" - ")[1])
			cidr = str([ipaddr for ipaddr in ipaddress.summarize_address_range(startip, endip)][0])
			R.append(cidr)
		
		R = list(set(R))

		print("  --> {0}: {1}".format(colored("Networks found", "white"), colored(len(R), "green")))
		return R

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
