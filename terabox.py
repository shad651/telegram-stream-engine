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
    
    parsed_url = urlparse(terabox_url)
    base_domain = parsed_url.netloc
    if not base_domain:
        base_domain = "www.terabox.com"
        
    session = requests.Session()
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
        "Connection": "keep-alive",
        "Referer": f"https://{base_domain}/"
    }
    
    api_url = f"https://{base_domain}/sharing/link?surl={surl}"
    
    try:
        print(f"[*] Data fetch ho raha hai...")
        response = session.get(api_url, headers=headers, timeout=15, allow_redirects=True)
        
        print(f"[+] Status Code Received: {response.status_code}")
        
        if response.status_code == 200:
            html_content = response.text
            print("[+] Success! HTML page mil gaya.")
            
            # TeraBox page ke andar JavaScript variables (yunData / sign / token) dhoondhna
            # Yeh data file ki info contain karta hai
            sign_match = re.search(r'sign\s*[:=]\s*["\']([a-zA-Z0-9_-]+)["\']', html_content)
            timestamp_match = re.search(r'timestamp\s*[:=]\s*([0-9]+)', html_content)
            
            if sign_match:
                print(f"[+] Extracted Sign Token: {sign_match.group(1)}")
            else:
                print("[-] Sign token HTML me direct nahi mila (Ho sakta hai JS render ho raha ho).")
                
            # Response me file name ya keywords check karna
            if "filename" in html_content or "file_name" in html_content:
                print("[+] File metadata is page ke andar maujud hai!")
            else:
                print("[-] Page standard login/captcha wall ho sakta hai.")
                
        else:
            print(f"[-] Request failed with status code: {response.status_code}")
            
    except Exception as e:
        print(f"[-] Error aa gaya: {str(e)}")

if __name__ == "__main__":
    test_url = input("TeraBox Link Enter karein: ").strip()
    if test_url:
        get_terabox_link(test_url)
    else:
        print("[-] Koi link enter nahi kiya gaya.")
