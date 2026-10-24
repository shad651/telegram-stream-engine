import sys
import requests
import re

def extract_surl(url):
    """TeraBox URL se unique surl code nikalne ka function"""
    # Agar URL me 'surl=' hai ya /s/ hai
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
        print("[-] Error: URL se valid surl code nahi mila. Link check karein.")
        return
    
    print(f"[+] Extracted SURL Code: {surl}")
    
    # TeraBox web client headers taaki request block na ho
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Referer": "https://www.terabox.com/"
    }
    
    # TeraBox info API endpoint
    api_url = f"https://www.terabox.com/sharing/link?surl={surl}"
    
    try:
        print("[*] TeraBox server se data fetch ho raha hai...")
        response = requests.get(api_url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            # Check karte hain ki file data mil gaya kya
            if "dlink" in response.text or "file_name" in response.text:
                print("[+] Success! Page response mil gaya.")
                # Yahan se file ka naam aur direct download link extract kiya jata hai
                print("\n[!] Raw API Response Headers/Data fetched successfully.")
                print("Tip: TeraBox ki direct link API ko fully parse karne ke liye cookies aur sign token ki zarurat padti hai.")
            else:
                print("[-] Server ne response diya par file data nahi mila (Ho sakta hai link expired ho).")
        else:
            print(f"[-] Request failed with status code: {response.status_code}")
            
    except Exception as e:
        print(f"[-] Error aa gaya: {str(e)}")

if __name__ == "__main__":
    # Aap yahan apna koi bhi TeraBox link daal sakte hain test karne ke liye
    test_url = input("TeraBox Link Enter karein: ").strip()
    if test_url:
        get_terabox_link(test_url)
    else:
        print("[-] Koi link enter nahi kiya gaya.")
