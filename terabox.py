import sys
import requests
import re
import json
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
        print(f"[*] Page fetch kiya ja raha hai...")
        response = session.get(api_url, headers=headers, timeout=15, allow_redirects=True)
        
        if response.status_code == 200:
            html_content = response.text
            print("[+] Success! HTML data mil gaya.")
            
            # TeraBox ke page me 'yunData' variable ko dhoondhna
            match_yundata = re.search(r'yunData\s*=\s*(\{.*?\});', html_content, re.DOTALL)
            
            if match_yundata:
                print("[+] Target 'yunData' object mil gaya!")
                raw_json = match_yundata.group(1)
                try:
                    data = json.loads(raw_json)
                    print("\n[!] File Details Found:")
                    print(json.dumps(data, indent=4))
                except json.JSONDecodeError:
                    print("[-] yunData JSON format me decode nahi ho paya.")
            else:
                print("[-] HTML me 'yunData' nahi mila. Ho sakta hai page structure badal gaya ho.")
                
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
