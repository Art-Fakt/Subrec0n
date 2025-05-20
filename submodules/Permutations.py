from re import findall
from gc import collect
from termcolor import colored
from utilities.DatabaseHelpers import Resolution, Unresolved
from utilities.ScanHelpers import identifyWildcards, massResolve
import utilities.MiscHelpers
from colorama import Fore, Style

def permuteDash(subdomain, wordlist):
	for word in wordlist:
		yield "-".join([word, subdomain])
		yield "-".join([subdomain, word])

	if "." in subdomain:
		subParts = subdomain.split(".")

		for part in subParts:
			for word in wordlist:
				yield subdomain.replace(part, "-".join([word, part]))
				yield subdomain.replace(part, "-".join([part, word]))


def permuteDot(subdomain, wordlist):
	for word in wordlist:
		yield ".".join([word, subdomain])
		yield ".".join([subdomain, word])

	if "." in subdomain:
		subParts = subdomain.split(".")

		for part in subParts:
			for word in wordlist:
				yield subdomain.replace(part, ".".join([word, part]))


def permuteWords(subdomain, wordlist):
	for word in wordlist:
		yield "".join([word, subdomain])
		yield "".join([subdomain, word])

	if "." in subdomain:
		subParts = subdomain.split(".")

		for part in subParts:
			for word in wordlist:
				yield subdomain.replace(part, "".join([word, part]))
				yield subdomain.replace(part, "".join([part, word]))


def permuteNumbers(subdomain):
	for number in range(10):
		yield "-".join([subdomain, str(number)])
		yield "".join([subdomain, str(number)])

	if "." in subdomain:
		subParts = subdomain.split(".")

		for part in subParts:
			for number in range(10):
				yield subdomain.replace(part, "-".join([part, str(number)]))
				yield subdomain.replace(part, "".join([part, str(number)]))


def permuteIterations(subdomain):
	instancesOfNumbers = findall(r"\d+", subdomain)	
	for instance in instancesOfNumbers:
		instancelength = len(instance)
		
		if instancelength == 1:				
			for newinstance in range(0,10):
				yield subdomain.replace(instance, str(newinstance))		
		
		elif instancelength == 2:				
			for newinstance in range(0,100):
				yield subdomain.replace(instance, str(newinstance))
		
		elif instancelength == 3:				
			for newinstance in range(0,1000):
				yield subdomain.replace(instance, str(newinstance))


def init(db, domain, wordlist, hideWildcards, threads):
	base = set()

	for row in db.query(Resolution).filter(Resolution.domain == domain, Resolution.isWildcard == False):
		if row.subdomain:
			base.add(row.subdomain)

	for row in db.query(Unresolved).filter(Unresolved.domain == domain):
		if row.subdomain:
			base.add(row.subdomain)

	numberOfChunks = 50

	if len(base) <= 100:
		print(Fore.CYAN + Style.BRIGHT + f"\n[+]-Performing permutations on " + Fore.GREEN + colored(str(len(base))) + Fore.CYAN + Style.BRIGHT + " hostnames..." + Style.RESET_ALL)
	else:
		print(Fore.CYAN + Style.BRIGHT + f"\n[+]-Performing permutations on " + Fore.GREEN + colored(str(len(base))) + Fore.CYAN + Style.BRIGHT + " hostnames in chunks of 100..." + Style.RESET_ALL)
		numberOfChunks = len(base) // 100 + 1

	baseChunks = utilities.MiscHelpers.chunkify(list(base), 100)
	iteration = 1

	words = [line.strip() for line in wordlist.readlines()]
	wordlist.close()

	for chunk in baseChunks:
		generators = []
		permutations = set()

		for subdomain in chunk:
			generators.append(permuteDash(subdomain, words))
			generators.append(permuteDot(subdomain, words))
			generators.append(permuteWords(subdomain, words))
			generators.append(permuteNumbers(subdomain))
			generators.append(permuteIterations(subdomain))

		for generator in generators:
			for subdomain in generator:
				permutations.add((subdomain, "Permutations"))

		permutations = list(permutations)
		print(Fore.CYAN + Style.BRIGHT + f"\n[+]-Generated " + Fore.GREEN + str(len(permutations)) + Fore.CYAN + Style.BRIGHT + f" permutated subdomains for chunk " + Fore.GREEN + str(iteration) + "/" + str(numberOfChunks) + Style.RESET_ALL)
		iteration += 1

		identifyWildcards(db, permutations, domain, threads)
		massResolve(db, permutations, domain, hideWildcards, threads)
