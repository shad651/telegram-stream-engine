import random
from curl_cffi import requests
from config import DOMAINS, USER_AGENTS

def fetch_terabox_data(surl, original_domain):
    """
    Automatic Domain Fallback Loop: 
    Pehle user ke diye gaye domain ko try karega, 
    agar fail hua toh baaki backup domains par switch ho jayega.
    """
    # Sabse pehle input domain ko rakhenge, fir baaki domains ko
    domains_to_try = [original_domain] + [d for d in DOMAINS if d != original_domain]
    
    for domain in domains_to_try:
        if not domain:
            continue
            
        api_url = f"https://{domain}/sharing/link?surl={surl}"
        headers = {
            "User-Agent": random.choice(USER_AGENTS),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9",
            "Connection": "keep-alive",
            "Referer": f"https://{domain}/"
        }
        
        print(f"[*] Testing Domain: {domain}...")
        try:
            # curl_cffi TLS impersonation ke sath request bhej raha hai
            response = requests.get(api_url, headers=headers, impersonate="chrome120", timeout=10)
            
            if response.status_code == 200:
                content = response.text
                # Check karte hain ki anti-bot challenge page toh nahi aaya
                if "BadJs" not in content and "juicyads" not in content.lower():
                    print(f"[+] Success! Domain {domain} se data mil gaya.")
                    return content
                else:
                    print(f"[-] Domain {domain} par Anti-Bot challenge detect hua. Agla domain try kar rahe hain...")
            else:
                print(f"[-] Domain {domain} returned status: {response.status_code}")
                
        except Exception as e:
            print(f"[-] Domain {domain} connection failed: {str(e)}")
            
    print("[-] Sabhi backup domains fail ho gaye.")
    return None
