from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm
from colorama import Fore, Style
import socket
import os

def brute_force_subdomains(domain, threads, maxdepth=3):

    charset = 'abcdefghijklmnopqrstuvwxyz0123456789'
    entries = []

    for letter1 in charset:
        entries.append(letter1)
        for letter2 in charset:
            entries.append(letter1 + letter2)
            for letter3 in charset:
                entries.append(letter1 + letter2 + letter3)
                if maxdepth == 4:
                    for letter4 in charset:
                        entries.append(letter1 + letter2 + letter3 + letter4)

    print(Fore.CYAN + Style.BRIGHT + f"\n[+] Testing Bruteforce with " + Fore.GREEN + f"{len(entries)} " + Fore.CYAN + Style.BRIGHT + f"combinations for " + Fore.GREEN + f"{domain}" + Fore.CYAN + Style.BRIGHT + "..." + Style.RESET_ALL)

    chunk_size = len(entries) // threads + 1
    chunks = [entries[i:i + chunk_size] for i in range(0, len(entries), chunk_size)]

    results_dir = f"Results/{domain}/Collectors"
    os.makedirs(results_dir, exist_ok=True)

    output_file = os.path.join(results_dir, "Bruteforce.txt")

    all_results = []

    def check_subdomains(chunk):
        results = []
        for sub in chunk:
            subdomain = f"{sub}.{domain}"
            try:
                socket.gethostbyname(subdomain)
                results.append(subdomain)
            except socket.gaierror:
                pass
        return results

    with ThreadPoolExecutor(max_workers=threads) as executor:
        futures = [executor.submit(check_subdomains, chunk) for chunk in chunks]
        with tqdm(total=len(entries), desc="Bruteforce Progress", dynamic_ncols=True) as progress_bar:
            for future in as_completed(futures):
                results = future.result()
                if results:
                    all_results.extend(results)
                progress_bar.update(len(chunks[0]))

    with open(output_file, "w") as file:
        for subdomain in all_results:
            file.write(subdomain + "\n")

    if all_results:
        print(Fore.WHITE + f"\n[+] Bruteforce completed! Found " + Fore.GREEN + f"{len(all_results)}" + Fore.WHITE + f" subdomains:" + Style.RESET_ALL)
        for subdomain in all_results:
            print(Fore.CYAN + f"  - {subdomain}" + Style.RESET_ALL)
        print(Fore.YELLOW + Style.BRIGHT + f"\n[!]-Check if Bruteforced subdomains are already found before or not! Results are not yet added to DB..." + Style.RESET_ALL)
        print(Fore.WHITE + f"[+] Results saved to: " + Fore.GREEN + f"{output_file}" + Style.RESET_ALL)

    else:
        print(Fore.YELLOW + "\n[!] No subdomains found during bruteforce." + Style.RESET_ALL)
