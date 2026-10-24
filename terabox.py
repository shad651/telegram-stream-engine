import sys
import re
import json
from urllib.parse import urlparse
from curl_cffi import requests

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
    base_domain = parsed_url.netloc if parsed_url.netloc else "terasharelink.com"
    print(f"[+] Using Domain: {base_domain}")
    
    # Target API endpoint jahan file ka actual data hota hai
    api_url = f"https://{base_domain}/sharing/link?surl={surl}"
    
    try:
        print(f"[*] Bypass request bhej rahe hain (curl_cffi)...")
        
        # impersonate='chrome120' server ko yakeen dilata hai ki ye real Chrome browser hai
        response = requests.get(api_url, impersonate="chrome120", timeout=15)
        
        print(f"[+] Status Code: {response.status_code}")
        
        if response.status_code == 200:
            html_content = response.text
            
            # Check karte hain ki file data mila ya nahi
            if "file_name" in html_content or "dlink" in html_content:
                print("[+] Success! File data mil gaya!")
                
                # JSON ya script data extract karne ki koshish
                match_data = re.search(r'data\s*=\s*(\{.*?\});', html_content, re.DOTALL)
                if match_data:
                    print("\n[!] Extracted Data Payload:")
                    print(match_data.group(1)[:600])
                else:
                    print("\n[!] Response text (First 500 characters):")
                    print(html_content[:500])
            else:
                print("[-] Anti-bot challenge abhi bhi active hai. Response preview:")
                print(html_content[:300])
        else:
            print(f"[-] Request failed with status: {response.status_code}")
            
    except Exception as e:
        print(f"[-] Error aa gaya: {str(e)}")

if __name__ == "__main__":
    test_url = input("TeraBox Link Enter karein: ").strip()
    if test_url:
        get_terabox_link(test_url)
    else:
        print("[-] Koi link enter nahi kiya gaya.")
