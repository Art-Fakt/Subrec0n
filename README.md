
# SubRec0n

**SubRec0n** is an advanced OSINT (Open Source Intelligence) tool designed for comprehensive subdomain reconnaissance. It combines passive and active techniques to identify subdomains, perform permutations, reverse lookups, port scans, and much more.
You have the possibility to launch scan directly without API key configured but if you want better results, it's advised to complete config.ini with your API key before scanning.
And yeeahh, **SubRec0n** is really **fast** & easily **configurable**, just test it to see !!!

For now, some collectors are missing and will be updated soon & pushed directly here.

## Features

- **Passive Collection**: Uses collectors to retrieve subdomains from various public sources.
- **Bruteforce**: Generates subdomains using wordlists and combinations.
- **Permutations**: Creates permutations based on existing subdomains.
- **Reverse Lookups**: Performs reverse DNS lookups on resolved IP ranges.
- **Port Scanning**: Identifies open ports on resolved IPs.
- **Takeover Detection**: Checks subdomains for potential takeovers.
- **Report Generation**: Exports results in CSV and HTML formats.
- **Result Management**: Cleans up temporary files and empty result files.
- **Extensible Collectors**: Easily add new collectors thanks to the modular structure.


## Installation

### Prerequisites

- Python 3.8 or higher
- Required Python modules (installed via `requirements.txt`)

### Installation Steps

1. Clone the repository:
```bash
git clone https://github.com/Art-Fakt/Subrec0n.git
cd SubRec0n
```

2. Install dependencies (optional with virtualenv):
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

3. Configure API keys in `config.ini` (if you want).

---

## Usage

### Basic Command

```bash
python3 subrecon.py <domain> [options]
```

### Available Options

| Option                          | Description                                                                                     | Default Value              |
|---------------------------------|-------------------------------------------------------------------------------------------------|----------------------------|
| `<domain>`                      | Target domain to analyze.                                                                      | Required                   |
| `-w, --wordlist`                | Wordlist containing subdomains to test.                                                        | `None`                     |
| `-hw, --hide-wildcards`         | Hides wildcard resolutions.                                                                    | `False`                    |
| `-t, --threads`                 | Number of threads to use.                                                                      | `100`                      |
| `-nc, --no-collectors`          | Skips passive subdomain enumeration.                                                           | `False`                    |
| `--permutate`                   | Performs permutations on resolved domains.                                                     | `False`                    |
| `-pw, --permutation-wordlist`   | Wordlist for permutations.                                                                     | `lists/words.txt`          |
| `--reverse`                     | Performs reverse DNS lookups on resolved public IP addresses.                                  | `False`                    |
| `-ripe, --ripe`                 | Queries the RIPE database for networks to use in reverse lookups.                              | `False`                    |
| `-r, --ranges`                  | Comma-separated IP ranges for reverse DNS lookups.                                             | `None`                     |
| `-or, --only-ranges`            | Uses only the provided ranges with `-r` or `--ripe`.                                           | `False`                    |
| `--portscan`                    | Scan resolved public IP addresses for open ports.                                             | `False`                    |
| `-p, --ports`                   | Ports to scan (`default`, `topports`, `top100`, `top1000`, or custom list).                    | `medium`                   |
| `--takeover`                    | Checks identified hosts for potential subdomain takeovers.                                     | `False`                    |
| `--markovify`                   | Uses Markov chains to identify additional subdomains.                                          | `False`                    |
| `-ms, --markov-state`           | Markov state size.                                                                             | `3`                        |
| `-ml, --markov-length`          | Maximum length of Markov substitutions.                                                        | `5`                        |
| `-mq, --markov-quantity`        | Maximum number of Markov results per candidate length.                                         | `5`                        |
| `-f, --flush`                   | Purges all records of the specified domain from the database.                                  | `False`                    |
| `--bruteforce`                  | Performs subdomain bruteforce for the target domain.                                           | `False`                    |
| `--maxdepth`                    | Maximum depth for bruteforce.                                                                  | `3`                        |
| `--output`                      | Output results to an HTML file.                                                               | `None`                     |
| `--silent`                      | Disable Banner print.                                                                         | `False`                    |
| `--debug`                       | Enable debug messages.                                                                        | `False`                    |
| `--commonn`                     | Checks subdomains with common prefixes.                                                        | `False`                    |
| `-zt, --zone-transfer`          | Attempts zone transfers from identified name servers.                                          | `False`                    |
| `--screenshot`                  | Take screenshots for all found resolved URLs                                                   | `False`                    |

---

## Examples

### Passive Collection (with or whithout API key configured in config.ini)

```bash
python3 subrecon.py example.com
```

### Complete scanning options exemple

```bash
python3 subrecon.py example.com --reverse --ripe --takeover --portscan -p top1000 --bruteforce --common --output Results.html --markovify
```

### Reverse Lookup with IP Ranges

```bash
python3 subrecon.py example.com --reverse -r 192.168.0.0/24,10.0.0.0/8
```

### Permutations and HTML Report Generation

```bash
python3 subrecon.py example.com --permutate --output results.html
```

### Port Scanning and Takeover Detection

```bash
python3 subrecon.py example.com --portscan --takeover
```

### Only Bruteforce (Need to improve rapidity for maxdepth > 3)

```bash
python3 subrecon.py example.com --no-collectors --bruteforce --maxdepth 3
```

---

## Results

Results are saved in the `Results/<domain>` directory and include:

- **`records.csv`**: Collected DNS records.
- **`resolved_public.csv`**: Resolved subdomains with public IPs.
- **`resolved_private.csv`**: Resolved subdomains with private IPs.
- **`unresolved.csv`**: Unresolved subdomains.
- **`wildcards.csv`**: Identified wildcard resolutions.
- **`open_ports.csv`**: Open ports identified.
- **`takeovers.csv`**: Subdomains vulnerable to takeovers.
- **`results.html`**: HTML report (if specified with `--output`).

You will also find all found subdomains by collector in corresponding .txt file in the folder 'Results/<domain>/Collectors' to see which subdomains are found by each collector.

---

## Extending SubRec0n

Adding new collectors is straightforward due to the modular structure of the tool. To add a new collector:

1. Create a new Python file in the `collectors` directory (e.g., `NewCollector.py`).
2. Implement an `init(domain, debug=False)` function that returns a list of subdomains.
3. Import and integrate the new collector in `subrecon.py`:
```python
import collectors.NewCollector
collector_subdomains += list(collectors.NewCollector.init(args.domain, args.debug))
```

## To-Do List

Some improvements are plannified like:

 - Adding option for custom resolvers
 - Adding Bruteforce results to the created Database
 - Improving HTML Page output
 - Adding the ability to select differents output like json, csv, txt, etc...
 - Adding more Collectors sources
 - Improving stability & rapidity
 - Improving Terminal Output & lisibility/colors
 - Adding & Configuring Telegram & Discord Notifications

---

## Contributions

Contributions are welcome! Feel free to submit a pull request or open an issue to report bugs or suggest improvements.

---

## License

This project is licensed under the NoFuckingLicense License. Don't try to See for the `LICENSE` file for details, there is no file...

---

## Author

**SubRec0n** is developed by **@4rt3f4kt**. For questions or suggestions, feel free to reach out.
