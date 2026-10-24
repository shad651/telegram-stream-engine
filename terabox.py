import sys
import requests
import re

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
    
    # Session use karte hain taaki cookies maintain rahein
    session = requests.Session()
    
    # Real browser jaise headers
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9,hi;q=0.8",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
        "Referer": "https://www.terabox.com/"
    }
    
    api_url = f"https://www.terabox.com/sharing/link?surl={surl}"
    
    try:
        print("[*] TeraBox server se data fetch ho raha hai...")
        # Headers aur timeout ke sath request bhej rahe hain
        response = session.get(api_url, headers=headers, timeout=15, allow_redirects=True)
        
        print(f"[+] Status Code Received: {response.status_code}")
        
        if response.status_code == 200:
            if "dlink" in response.text or "file_name" in response.text or "surl" in response.text:
                print("[+] Success! Server ne data de diya.")
                print(f"[!] Response Length: {len(response.text)} characters")
            else:
                print("[-] Server ne response diya, par anti-bot page ya login page aa gaya hai.")
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
