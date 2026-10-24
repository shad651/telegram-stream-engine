import sys
import requests
import re
import json

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
    
    # Ab hum wrapper ko chhod kar seedha official TeraBox domain use karenge
    base_domain = "www.terabox.com"
    
    session = requests.Session()
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
        "Connection": "keep-alive",
        "Referer": "https://www.terabox.com/"
    }
    
    api_url = f"https://{base_domain}/sharing/link?surl={surl}"
    
    try:
        print(f"[*] Official TeraBox server se data fetch ho raha hai...")
        response = session.get(api_url, headers=headers, timeout=15, allow_redirects=True)
        
        print(f"[+] Status Code Received: {response.status_code}")
        
        if response.status_code == 200:
            html_content = response.text
            
            # YunData ya script tags ke andar file ki details dhoondhna
            match_yundata = re.search(r'yunData\s*=\s*(\{.*?\});', html_content, re.DOTALL)
            
            if match_yundata:
                print("[+] Success! 'yunData' mil gaya.")
                raw_json = match_yundata.group(1)
                try:
                    data = json.loads(raw_json)
                    print("\n[!] File Details:")
                    print(json.dumps(data, indent=4))
                except:
                    print("[-] JSON decode karne me error aayi.")
            else:
                print("[-] yunData direct nahi mila. HTML me doosre patterns check ho rahe hain...")
                # File name ya dlink keywords check karna
                if "file_name" in html_content or "dlink" in html_content:
                    print("[+] Page par file data maujud hai!")
                else:
                    print("[-] Page par anti-bot ya login wall active hai.")
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
