import sys
import requests
import re
from urllib.parse import urlparse

def extract_surl(url):
    match = re.search(r'surl=([a-zA-Z0-9_-]+)', url)
    if match:
        return match.group(1)
    
    match_short = re.search(r'/s/1([a-zA-Z0-9_-]+)', url)
    if match_short:
        return "1" + match_short.group(1)
        
    return None

def get_terabox_link(terabox_url):
    print(f"\n[*] Processing URL: {terabox_url}")
    
    surl = extract_surl(terabox_url)
    if not surl:
        print("[-] Error: URL se valid surl code nahi mila.")
        return
    
    print(f"[+] Extracted SURL Code: {surl}")
    
    # URL se exact domain nikalna (jaise terasharelink.com ya terabox.com)
    parsed_url = urlparse(terabox_url)
    base_domain = parsed_url.netloc
    if not base_domain:
        base_domain = "www.terabox.com"
        
    print(f"[+] Target Domain: {base_domain}")
    
    session = requests.Session()
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
        "Connection": "keep-alive",
        "Referer": f"https://{base_domain}/"
    }
    
    # Dynamic API URL based on input domain
    api_url = f"https://{base_domain}/sharing/link?surl={surl}"
    
    try:
        print(f"[*] {base_domain} se data fetch ho raha hai...")
        response = session.get(api_url, headers=headers, timeout=15, allow_redirects=True)
        
        print(f"[+] Status Code Received: {response.status_code}")
        
        if response.status_code == 200:
            print("[+] Success! Server ne response de diya.")
            print(f"[!] Response Preview: {response.text[:200]}...")
        else:
            print(f"[-] Request failed with status code: {response.status_code}")
            
    except requests.exceptions.Timeout:
        print("[-] Error: Connection Timeout! TeraBox ka ye domain aapke network par block ya unreachable ho sakta hai.")
    except Exception as e:
        print(f"[-] Error aa gaya: {str(e)}")

if __name__ == "__main__":
    test_url = input("TeraBox Link Enter karein: ").strip()
    if test_url:
        get_terabox_link(test_url)
    else:
        print("[-] Koi link enter nahi kiya gaya.")
