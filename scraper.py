import random
from pathlib import Path
from curl_cffi import requests
from config import DOMAINS, USER_AGENTS

def fetch_terabox_data(surl, original_domain):
domains_to_try = [original_domain] + [
d for d in DOMAINS if d != original_domain
]

for domain in domains_to_try:
    if not domain:
        continue

    session = requests.Session()
    ua = random.choice(USER_AGENTS)

    headers = {
        "User-Agent": ua,
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
        "Referer": f"https://{domain}/"
    }

    print(f"[*] Testing Domain: {domain}...")

    try:
        initial_url = f"https://{domain}/s/{surl}"

        res1 = session.get(
            initial_url,
            headers=headers,
            impersonate="chrome120",
            timeout=12
        )

        print(f"[DEBUG] Status: {res1.status_code}")
        print(f"[DEBUG] Final URL: {res1.url}")
        print(f"[DEBUG] Content-Type: {res1.headers.get('Content-Type')}")
        print(f"[DEBUG] Response Length: {len(res1.text)}")
        print(f"[DEBUG] First 300 characters: {res1.text[:300]!r}")

        # Save the received HTML, even if later checks fail.
        Path("response.html").write_text(
            res1.text, encoding="utf-8"
        )
        print("[+] HTML saved to response.html")

        if res1.status_code == 200:
            content = res1.text

            if "BadJs" not in content and "juicyads" not in content.lower():
                print(f"[+] HTML received from {domain}.")
                return content

            api_url = f"https://{domain}/sharing/link?surl={surl}"

            res2 = session.get(
                api_url,
                headers=headers,
                impersonate="chrome120",
                timeout=12
            )

            print(f"[DEBUG] API Status: {res2.status_code}")
            print(f"[DEBUG] API Content-Type: {res2.headers.get('Content-Type')}")
            print(f"[DEBUG] API Response Length: {len(res2.text)}")
            print(f"[DEBUG] API First 300 characters: {res2.text[:300]!r}")

            Path("response.html").write_text(
                res2.text, encoding="utf-8"
            )
            print("[+] Alternate response saved to response.html")

            if res2.status_code == 200 and "BadJs" not in res2.text:
                print(f"[+] HTML received from alternate endpoint: {domain}")
                return res2.text

            print(f"[-] Expected response not confirmed for {domain}.")

        else:
            print(f"[-] Domain {domain} status: {res1.status_code}")

    except Exception as e:
        print(f"[-] Domain {domain} error: {e}")

    finally:
        session.close()

print("[-] All domain requests failed.")
return None