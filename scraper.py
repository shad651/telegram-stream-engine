import random
from curl_cffi import requests
from config import DOMAINS, USER_AGENTS

def fetch_terabox_data(surl, original_domain):
# Original domain ko pehle try karna
domains_to_try = [original_domain] + [
d for d in DOMAINS if d != original_domain
]

for domain in domains_to_try:
    if not domain:
        continue

    # Session create karna
    session = requests.Session()

    # Random mobile User-Agent select karna
    ua = random.choice(USER_AGENTS)

    headers = {
        "User-Agent": ua,
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "Referer": f"https://{domain}/"
    }

    print(f"[*] Testing Domain (Mobile Mode): {domain}...")

    try:
        # Step 1: Sharing page request
        initial_url = f"https://{domain}/s/{surl}"

        res1 = session.get(
            initial_url,
            headers=headers,
            impersonate="chrome120",
            timeout=12
        )

        # Response status check karna
        if res1.status_code == 200:
            content = res1.text

            # Debug information
            print(f"[DEBUG] Status: {res1.status_code}")
            print(f"[DEBUG] Final URL: {res1.url}")
            print(
                f"[DEBUG] Content-Type: "
                f"{res1.headers.get('Content-Type')}"
            )
            print(f"[DEBUG] Response Length: {len(content)}")
            print(
                f"[DEBUG] First 300 characters: "
                f"{content[:300]!r}"
            )

            # Response check karna
            if (
                "BadJs" not in content
                and "juicyads" not in content.lower()
            ):
                print(
                    f"[+] Domain {domain} se response mil gaya."
                )
                return content

            else:
                # Step 2: Alternate endpoint check
                api_url = (
                    f"https://{domain}/sharing/link?surl={surl}"
                )

                res2 = session.get(
                    api_url,
                    headers=headers,
                    impersonate="chrome120",
                    timeout=12
                )

                print(
                    f"[DEBUG] API Status: {res2.status_code}"
                )
                print(
                    f"[DEBUG] API Content-Type: "
                    f"{res2.headers.get('Content-Type')}"
                )
                print(
                    f"[DEBUG] API Response Length: "
                    f"{len(res2.text)}"
                )
                print(
                    f"[DEBUG] API First 300 characters: "
                    f"{res2.text[:300]!r}"
                )

                if (
                    res2.status_code == 200
                    and "BadJs" not in res2.text
                ):
                    print(
                        f"[+] Response {domain} ke alternate "
                        f"endpoint se mila."
                    )
                    return res2.text

                else:
                    print(
                        f"[-] Domain {domain} se valid response "
                        f"confirm nahi hua."
                    )

        else:
            print(
                f"[-] Domain {domain} status: "
                f"{res1.status_code}"
            )

    except Exception as e:
        print(f"[-] Domain {domain} error: {e}")

    finally:
        session.close()

print("[-] Sabhi domains par request unsuccessful rahi.")
return None