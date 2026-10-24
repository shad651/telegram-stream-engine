import random
from curl_cffi import requests
from config import DOMAINS, USER_AGENTS

def fetch_terabox_data(surl, original_domain):
    # Working domains ki list
    domains_to_try = [original_domain] + [d for d in DOMAINS if d != original_domain]
    
    for domain in domains_to_try:
        if not domain:
            continue
            
        # Session use karte hain taaki cookies store rahein
        session = requests.Session()
        
        # Mobile User-Agent select karna
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
            # Step 1: Pehle link page hit karke cookie generate karna
            initial_url = f"https://{domain}/s/{surl}"
            res1 = session.get(initial_url, headers=headers, impersonate="chrome120", timeout=12)
            
            if res1.status_code == 200:
                content = res1.text

print(f"[DEBUG] Status: {res1.status_code}")
print(f"[DEBUG] Final URL: {res1.url}")
print(f"[DEBUG] Content-Type: {res1.headers.get('Content-Type')}")
print(f"[DEBUG] Response Length: {len(content)}")
print(f"[DEBUG] First 300 characters: {content[:300]!r}")
                
                # Check karna ki BadJs bypass hua ya nahi
                if "BadJs" not in content and "juicyads" not in content.lower():
                    print(f"[+] Success! Domain {domain} se data mil gaya.")
                    return content
                else:
                    # Step 2: Agar pehli baar me BadJs aaya, toh sharing link API endpoint par dobara hit karna usi session se
                    api_url = f"https://{domain}/sharing/link?surl={surl}"
                    res2 = session.get(api_url, headers=headers, impersonate="chrome120", timeout=12)
                    
                    if res2.status_code == 200 and "BadJs" not in res2.text:
                        print(f"[+] Success via API endpoint on {domain}!")
                        return res2.text
                    else:
                        print(f"[-] Domain {domain} par abhi bhi BadJs challenge active hai.")
            else:
                print(f"[-] Domain {domain} status: {res1.status_code}")
                
        except Exception as e:
            print(f"[-] Domain {domain} error: {str(e)}")
            
    print("[-] Sabhi domains par anti-bot challenge bypass nahi ho paya.")
    return None
