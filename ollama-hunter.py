import requests
from bs4 import BeautifulSoup
import time
import json

# === USER INPUT ===
polito_cookie = input("Enter your Shodan 'polito' cookie value: ").strip()

# === SETTINGS ===
BASE_URL = "https://www.shodan.io/search"
QUERY = 'port:11434 product:"Ollama"'
START_PAGE = 1
DELAY = 2  # seconds between page fetches
DETAIL_TIMEOUT = 5  # timeout for each IP's /api/tags
OUTPUT_FILE = "ollama_hosts_with_models.txt"

# === HEADERS ===
HEADERS = {
    "Host": "www.shodan.io",
    "Cookie": f'polito="{polito_cookie}"',
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.6533.100 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
    "Referer": "https://www.shodan.io/",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
}

# === REST OF THE SCRIPT ===
def scrape_ips_from_page(page):
    params = {
        "query": QUERY,
        "page": page
    }

    print(f"[+] Fetching Shodan page {page}...")
    response = requests.get(BASE_URL, headers=HEADERS, params=params)

    if response.status_code != 200:
        print(f"[!] Error: Status code {response.status_code}")
        return []

    soup = BeautifulSoup(response.text, "html.parser")
    results = soup.find_all("div", class_="result")

    ips = []
    for result in results:
        a_tag = result.find("a", class_="title", href=True)
        if a_tag and "/host/" in a_tag["href"]:
            ip = a_tag["href"].split("/host/")[1]
            ips.append(ip)

    return ips

def fetch_models_from_ip(ip):
    url = f"http://{ip}:11434/api/tags"
    try:
        res = requests.get(url, timeout=DETAIL_TIMEOUT)
        res.raise_for_status()
        data = res.json()

        models = [m.get("name") for m in data.get("models", []) if "name" in m]
        return models
    except (requests.RequestException, json.JSONDecodeError) as e:
        return None

def main():
    all_ips = set()

    try:
        page = START_PAGE
        with open(OUTPUT_FILE, "a") as f:
            while True:
                ips = scrape_ips_from_page(page)
                if not ips:
                    print("[*] No more results found. Stopping.")
                    break

                for ip in ips:
                    if ip in all_ips:
                        continue

                    print(f"[+] Checking {ip}...")
                    models = fetch_models_from_ip(ip)
                    if models:
                        print(f" {ip}:")
                        f.write(f"{ip}:\n")
                        for model in models:
                            print(f"  - {model}")
                            f.write(f"  - {model}\n")
                        f.write("\n")
                    else:
                        print(f" [-] {ip} has no models or is unreachable.")

                    all_ips.add(ip)
                    time.sleep(1)

                page += 1
                time.sleep(DELAY)

    except KeyboardInterrupt:
        print("\n[!] Interrupted by user.")

    print(f"[✓] Done. Results saved to: {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
