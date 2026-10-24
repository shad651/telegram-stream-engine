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
    base_domain = parsed_url.netloc if parsed_url.netloc else "terasharelink.com"
    print(f"[+] Using Working Domain: {base_domain}")
    
    # Session object automatically cookies store karta hai
    session = requests.Session()
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
        "Connection": "keep-alive",
        "Referer": f"https://{base_domain}/"
    }
    
    try:
        # Step 1: Pehle main page hit karke cookies/session establish karna
        initial_url = f"https://{base_domain}/s/{surl}"
        print(f"[*] Step 1: Session establish ho raha hai ({base_domain})...")
        res1 = session.get(initial_url, headers=headers, timeout=15)
        
        print(f"[+] Step 1 Status: {res1.status_code}")
        
        if res1.status_code == 200:
            html_content = res1.text
            
            # Check karte hain ki file data direct mila ya nahi
            if "file_name" in html_content or "dlink" in html_content or "download" in html_content:
                print("[+] Success! Page ke andar file data mil gaya.")
                # Yahan hum script tags ya JSON dhoond sakte hain
                match_data = re.search(r'data\s*=\s*(\{.*?\});', html_content, re.DOTALL)
                if match_data:
                    print("[+] Extracted Payload JSON:")
                    print(match_data.group(1)[:500])
                else:
                    print("[!] Data raw HTML me maujud hai. (Response length:", len(html_content), "chars)")
            else:
                print("[-] Page par abhi bhi anti-bot challenge ya redirect hai. Cookies update ho rahi hain...")
                
                # Step 2: Agar cookies set hui hain toh same session se dobara hit karna
                print(f"[*] Step 2: Data endpoint par request bhej rahe hain...")
                api_url = f"https://{base_domain}/sharing/link?surl={surl}"
                res2 = session.get(api_url, headers=headers, timeout=15)
                print(f"[+] Step 2 Status: {res2.status_code}")
                if "file_name" in res2.text or "dlink" in res2.text:
                    print("[+] Step 2 me file data successfully mil gaya!")
                else:
                    print("[-] Anti-bot challenge bypass nahi ho paya. Response preview:")
                    print(res2.text[:300])
        else:
            print(f"[-] Initial request failed with status: {res1.status_code}")
            
    except Exception as e:
        print(f"[-] Error aa gaya: {str(e)}")

if __name__ == "__main__":
    test_url = input("TeraBox Link Enter karein: ").strip()
    if test_url:
        get_terabox_link(test_url)
    else:
        print("[-] Koi link enter nahi kiya gaya.")
