import requests
from json import loads
from termcolor import colored
from configparser import RawConfigParser
from colorama import Fore, Style
import os
import re

def init(domain, debug=False):
	NETC = []

	print(Fore.CYAN + Style.BRIGHT + "[+]-Searching in Netcraft..." + Style.RESET_ALL)

	url = "https://searchdns.netcraft.com/"
	headers = {'Pragma': 'no-cache', 'DNT': '1',
				'Accept-Encoding': 'gzip, deflate, br',
				'Accept-Language': 'en-US,en;q=0.9,it;q=0.8',
				'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.94 Safari/537.36',
				'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
				'Cache-Control': 'no-cache',
				'Referer': 'https://searchdns.netcraft.com/?restriction=site+ends+with&host=',
				'Connection': 'keep-alive', }
	try:
		response = requests.get(url, headers=headers).text
		subdomains = loads(response)["subdomains"]

		scraped = response.text
		trimmed = scraped[scraped.find('<div class="blogtitle">'):scraped.rfind(f'<div id="copyright">')]
		subdomain_finder = re.compile(r'<a href="http://toolbar.netcraft.com/site_report\?url=(.*)">')
		subdomain = subdomain_finder.findall(trimmed)
		
		for domain in subdomain:
			if subdomain:
				NETC.append("{0}.{1}".format(subdomain, domain))

		NETC = set(NETC)

		for subdomain in NETC:
			if debug:
				print(Fore.GREEN + f"  [DEBUG] {subdomain}" + Style.RESET_ALL)

		results_dir = f"Results/{domain}"
		os.makedirs(results_dir, exist_ok=True)

		output_file = os.path.join(results_dir, "NetCraft.txt")

		with open(output_file, "w") as file:
			for subdomain in NETC:
				file.write(subdomain + "\n")
		
		print(Fore.CYAN + f"  --> Subdomains saved to: {output_file}" + Style.RESET_ALL)

		print("  --> {0}: {1}".format(colored("Subdomains found", "white"), colored(len(NETC), "green")))
		return NETC

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
