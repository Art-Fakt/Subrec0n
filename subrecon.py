#!/usr/bin/env python3

from argparse import ArgumentParser, FileType
from warnings import simplefilter
from termcolor import colored
from time import sleep
from gc import collect
from colorama import Fore, Style

from dns import resolver
res = resolver.Resolver()

import collectors.AnubisDB
import collectors.AlienVault
import collectors.Analytics
import collectors.SecurityTrails
import collectors.c99nl
import collectors.Censys
import collectors.CertSpotter
import collectors.CRT
import collectors.DNSDumpster
import collectors.DNSRepo
import collectors.DNSTrails
import collectors.Dorki
import collectors.FOFA
import collectors.Fullhunt
import collectors.GoogleTransparency
import collectors.HackerTarget
import collectors.Hudson_Rock
import collectors.HunterHow
import collectors.Merklemap
import collectors.NoError
import collectors.Odin
import collectors.PassiveTotal
import collectors.pkey
import collectors.PDChaos
import collectors.ProjectCrobat
import collectors.ProjectSonar
import collectors.Netcraft
import collectors.RapidApi
import collectors.RapidDNS
import collectors.Riddler
import collectors.Rsecloud
import collectors.Shodan
import collectors.Shrewdeye
import collectors.SiteDossier
import collectors.Spyse
import collectors.ThreatCrowd
import collectors.ThreatMiner
import collectors.TLSX
import collectors.UrlScan
import collectors.Vedbex
import collectors.ViewDns
import collectors.VirusTotal
import collectors.WaybackMachine
import collectors.ZoomEye
import submodules.Permutations
import submodules.PortScan
import submodules.ReverseLookups
import submodules.TakeOver
import submodules.Markov
import submodules.Bruteforce
import utilities.DatabaseHelpers
import utilities.MiscHelpers
import utilities.ScanHelpers


simplefilter("ignore")
version = "1.0"

def printBanner():
	banner = """
    █████╗ ████████╗███████╗    ██████╗ ███████╗ ██████╗ ██████╗ ███╗   ██╗
    ██╔══██╗╚══██╔══╝██╔════╝    ██╔══██╗██╔════╝██╔════╝██╔═████╗████╗  ██║
    ███████║   ██║   █████╗█████╗██████╔╝█████╗  ██║     ██║██╔██║██╔██╗ ██║
    ██╔══██║   ██║   ██╔══╝╚════╝██╔══██╗██╔══╝  ██║     ████╔╝██║██║╚██╗██║
    ██║  ██║   ██║   ██║         ██║  ██║███████╗╚██████╗╚██████╔╝██║ ╚████║
    ╚═╝  ╚═╝   ╚═╝   ╚═╝         ╚═╝  ╚═╝╚══════╝ ╚═════╝ ╚═════╝ ╚═╝  ╚═══╝
	"""
	print(Fore.GREEN + banner + Style.RESET_ALL) 
	print(Fore.CYAN + "                                        Subdomains Edition v{0}".format(version) + Fore.CYAN + " By @rt3f4kt" + Style.RESET_ALL)
	sleep(1)

if __name__ == "__main__":
	parser = ArgumentParser(prog="subrecon.py", description="Infrastructure OSINT")
	parser.add_argument("domain", help="domain to search")
	parser.add_argument("-w", "--wordlist", action="store", dest="wordlist", help="wordlist with subdomains", type=FileType("r"))
	parser.add_argument("-hw", "--hide-wildcards", action="store_true", dest="hideWildcards", help="hide wildcard resolutions", default=False)
	parser.add_argument("-t", "--threads", action="store", dest="threads", help="number of threads [default is 100]", type=int, default=100)
	parser.add_argument("-nc", "--no-collectors", action="store_true", dest="noCollectors", help="skip passive subdomain enumeration", default=False)
	parser.add_argument("--permutate", action="store_true", dest="permutate", help="perform permutations on resolved domains", default=False)
	parser.add_argument("-pw", "--permutation-wordlist", dest="permutation_wordlist", help="wordlist to perform permutations with [default is lists/words.txt]", type=FileType("r"), default="lists/words.txt")
	parser.add_argument("--reverse", action="store_true", dest="reverse", help="perform reverse dns lookups on resolved public IP addresses", default=False)
	parser.add_argument("-ripe", "--ripe", action="store_true", dest="ripe", help="query ripe database with the 2nd level domain for networks to be used for reverse lookups", default=False)
	parser.add_argument("-r", "--ranges", action="store", dest="ranges", help="comma seperated ip ranges to perform reverse dns lookups on", type=str, default=None)
	parser.add_argument("-or", "--only-ranges", action="store_true", dest="only_ranges", help="use only ranges provided with -r or -ripe and not all previously identified IPs", default=False)
	parser.add_argument("--portscan", action="store_true", dest="portscan", help="scan resolved public IP addresses for open ports", default=False)
	parser.add_argument("-p", "--ports", action="store", dest="ports", help="set of ports to be used by the portscan module [default is medium]", type=str)
	parser.add_argument("--takeover", action="store_true", dest="takeover", help="check identified hosts for potential subdomain take-overs", default=False)
	parser.add_argument("--markovify", action="store_true", dest="markovify", help="use markov chains to identify more subdomains", default=False)
	parser.add_argument("-ms", "--markov-state", action="store", dest="markov_state", help="markov state size [default is 3]", type=int, default=3)
	parser.add_argument("-ml", "--markov-length", action="store", dest="markov_length", help="max length of markov substitutions [default is 5]", type=int, default=5)
	parser.add_argument("-mq", "--markov-quantity", action="store", dest="markov_quantity", help="max quantity of markov results per candidate length [default is 5]", type=int, default=5)
	parser.add_argument("-f", "--flush", action="store_true", dest="doFlush", help="purge all records of the specified domain from the database", default=False)
	parser.add_argument("-v", "--version", action="version", version="SubRecon v{0}".format(version))
	#parser.add_argument("-r", "--resolvers", help="File with DNS resolvers to use", type=FileType("r"))
	parser.add_argument("--bruteforce", action="store_true", dest="bruteforce", help="Bruteforce subdomains for the target domain", default=False)
	parser.add_argument("--maxdepth", action="store", dest="maxdepth", help="Maximum depth for bruteforce [default is 3]", type=int, default=3)
	parser.add_argument("--output", action="store", dest="output", help="Output results to an HTML file", type=str, default=None)
	parser.add_argument("--debug", action="store_true", dest="debug", help="Enable debug messages", default=False)
	parser.add_argument("--commonn", action="store_true", dest="commonn", help="check subdomains with common prefixes", default=False)
	parser.add_argument("-zt", "--zone-transfer", action="store_true", dest="zoneTransfer", help="attempt to zone transfer from identified name servers", default=False)	
	parser.add_argument("--silent", action="store_true", dest="silent", help="don't print banner", default=False)
	parser.add_argument("--screenshot", action="store_true", dest="screenshot", help="Take screenshots of all found URLs after portscan (Need Nuclei installed)", default=False)
	args = parser.parse_args()

	# if args.resolvers:
	# 	res.nameservers = [line.strip() for line in args.resolvers if line.strip()]
	# else:
	# 	res.nameservers = ['1.1.1.1', '8.8.8.8'] 

		# if not utilities.MiscHelpers.checkArgumentValidity(parser, args):
		# 	exit(1)

	if args.silent:
		print(Fore.CYAN + Style.BRIGHT + f"\nCoded with ❤️  By 4rt3f4kt" + Style.RESET_ALL)
	else:
		printBanner()

	db = utilities.DatabaseHelpers.init()

	if args.doFlush:
		utilities.MiscHelpers.purgeOldFindings(db, args.domain)
		print("{0} {1} {2}".format(colored("\n[!]-Flushed", "white"), colored(args.domain, "cyan"), colored("from the database", "yellow")))
		exit(0)

	#print("{0} {1}".format(colored("\n[+]-Running SubAtfOr against:", "yellow"), colored(args.domain, "cyan")))
	print(Fore.CYAN + Style.BRIGHT + "\n[+]-" + Fore.WHITE + f"Running Atf-SubRec0n against:" + Style.RESET_ALL + " " + Fore.YELLOW + Style.BRIGHT + args.domain + Style.RESET_ALL)

	old_resolved, old_unresolved, old_takeovers = utilities.MiscHelpers.loadOldFindings(db, args.domain)
	utilities.MiscHelpers.purgeOldFindings(db, args.domain)

	try:
		utilities.ScanHelpers.retrieveDNSRecords(db, args.domain)

		if args.zoneTransfer:
			zt_subdomains = utilities.ScanHelpers.zoneTransfer(db, args.domain)

		else:
			zt_subdomains = None

		if args.noCollectors:
			collector_subdomains = None

		else:
			print()
			collector_subdomains = []
			#collector_subdomains += list(collectors.AnubisDB.init(args.domain))
			collector_subdomains += list(collectors.AlienVault.init(args.domain))
			#collector_subdomains += list(collectors.Analytics.init(args.domain))
			#collector_subdomains += list(collectors.BinaryEdge.init(args.domain, args.debug)) # no more accessible
			#collector_subdomains += list(collectors.c99nl.init(args.domain, args.debug))
			collector_subdomains += list(collectors.Censys.init(args.domain, args.debug))
			collector_subdomains += list(collectors.CertSpotter.init(args.domain))
			collector_subdomains += list(collectors.CRT.init(args.domain, args.debug))
			collector_subdomains += list(collectors.DNSDumpster.init(args.domain, args.debug))
			collector_subdomains += list(collectors.DNSRepo.init(args.domain))
			collector_subdomains += list(collectors.DNSTrails.init(args.domain))
			collector_subdomains += list(collectors.FOFA.init(args.domain, args.debug))
			collector_subdomains += list(collectors.Fullhunt.init(args.domain))
			collector_subdomains += list(collectors.GoogleTransparency.init(args.domain))
			collector_subdomains += list(collectors.HackerTarget.init(args.domain, args.debug))
			collector_subdomains += list(collectors.HunterHow.init(args.domain, args.debug))
			collector_subdomains += list(collectors.Merklemap.init(args.domain, args.debug))
			collector_subdomains += list(collectors.NoError.init(args.domain))
			collector_subdomains += list(collectors.Odin.init(args.domain))
			collector_subdomains += list(collectors.PassiveTotal.init(args.domain))
			#collector_subdomains += list(collectors.pkey.init(args.domain))
			collector_subdomains += list(collectors.PDChaos.init(args.domain, args.debug))
			collector_subdomains += list(collectors.ProjectCrobat.init(args.domain, args.ranges))
			#collector_subdomains += list(collectors.Netcraft.init(args.domain, args.ranges))
			#collector_subdomains += list(collectors.ProjectSonar.init(args.domain))
			collector_subdomains += list(collectors.RapidApi.init(args.domain, args.debug))
			collector_subdomains += list(collectors.RapidDNS.init(args.domain, args.debug))
			collector_subdomains += list(collectors.Riddler.init(args.domain))
			collector_subdomains += list(collectors.Rsecloud.init(args.domain, args.debug))
			collector_subdomains += list(collectors.SecurityTrails.init(args.domain, args.debug))
			#collector_subdomains += list(collectors.SiteDossier.init(args.domain))
			collector_subdomains += list(collectors.Shodan.init(args.domain, args.debug))
			#collector_subdomains += list(collectors.Shrewdeye.init(args.domain, args.debug))
			collector_subdomains += list(collectors.Spyse.init(args.domain, args.debug))
			#collector_subdomains += list(collectors.ThreatCrowd.init(args.domain)) # error 503 for now !!!!
			collector_subdomains += list(collectors.ThreatMiner.init(args.domain))
			#collector_subdomains += list(collectors.TLSX.init(args.domain))
			collector_subdomains += list(collectors.Vedbex.init(args.domain, args.debug))
			#collector_subdomains += list(collectors.ViewDns.init(args.domain, args.debug))
			collector_subdomains += list(collectors.VirusTotal.init(args.domain))
			collector_subdomains += list(collectors.WaybackMachine.init(args.domain, args.debug))
			collector_subdomains += list(collectors.ZoomEye.init(args.domain))
			collector_subdomains += list(collectors.UrlScan.init(args.domain, args.debug))
			#collector_subdomains += list(collectors.Hudson_Rock.init(args.domain, args.debug))
			collector_subdomains += list(collectors.Dorki.init(args.domain, args.debug))

		if args.wordlist:
			wordlist_subdomains = utilities.MiscHelpers.loadWordlist(args.domain, args.wordlist)

		else:
			wordlist_subdomains = None

		findings = utilities.MiscHelpers.cleanupFindings(
			args.domain,
			old_resolved,
			old_unresolved,
			zt_subdomains,
			list(collector_subdomains) if collector_subdomains else [],
			wordlist_subdomains
		)

		del old_unresolved
		del zt_subdomains
		del collector_subdomains
		del wordlist_subdomains
		collect()

		if findings:
			utilities.ScanHelpers.identifyWildcards(db, findings, args.domain, args.threads)
			utilities.ScanHelpers.massResolve(db, findings, args.domain, args.hideWildcards, args.threads)
		
			if args.debug:
				print(Fore.YELLOW + f"\n[DEBUG] " + Fore.WHITE + f"Findings: " + Fore.CYAN + f"{findings}" + Style.RESET_ALL)
			
			structured_findings = utilities.MiscHelpers.structure_findings(findings)

			if args.bruteforce:
				submodules.Bruteforce.brute_force_subdomains(args.domain, args.threads, args.maxdepth)

			if args.commonn:
				print(Fore.CYAN + Style.BRIGHT + "\n[+]-Checking subdomains with common prefixes..." + Style.RESET_ALL)
				utilities.ScanHelpers.checkCommonPrefix(db, args.domain, findings, args.threads)

			if args.permutate:
				submodules.Permutations.init(db, args.domain, args.permutation_wordlist, args.hideWildcards, args.threads)

			if args.reverse:
				submodules.ReverseLookups.init(db, args.domain, args.ripe, args.ranges, args.only_ranges, args.threads)
			
			if args.markovify:
				submodules.Markov.init(db, args.domain, args.markov_state, args.markov_length, args.markov_quantity, args.hideWildcards, args.threads)

			if args.output:
				print(Fore.CYAN + Style.BRIGHT + f"\n[+]-Generating HTML output..." + Style.RESET_ALL)
				structured_findings = utilities.MiscHelpers.structure_findings(findings)  # Structure les données
				utilities.MiscHelpers.generate_html_output(db, args.domain, args.output)

			del findings
			collect()

			utilities.ScanHelpers.massRDAP(db, args.domain, args.threads)

			if args.portscan:
				submodules.PortScan.init(db, args.domain, args.ports, args.threads)

			if args.portscan and args.screenshot:
				utilities.ScanHelpers.take_screenshots_with_nuclei(args.domain)

			if args.takeover:
				submodules.TakeOver.init(db, args.domain, old_takeovers, args.threads)

		
		utilities.MiscHelpers.exportFindings(db, args.domain, old_resolved, False)
		utilities.MiscHelpers.delete_empty_txt_files(args.domain)
		utilities.MiscHelpers.delete_tmp_files()

	except KeyboardInterrupt:
		print(colored("\n[!]-Received keyboard interrupt! Shutting down...", "red"))
		utilities.MiscHelpers.exportFindings(db, args.domain, old_resolved, True)
		
		exit(-1)
