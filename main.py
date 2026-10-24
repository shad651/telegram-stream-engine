import json
from extractor import extract_surl, get_domain
from scraper import fetch_terabox_data

def main():
    print("========================================")
    print("   TeraBox Multi-Domain Stream Engine   ")
    print("========================================")
    
    test_url = input("TeraBox Link Enter karein: ").strip()
    if not test_url:
        print("[-] Koi link enter nahi kiya gaya.")
        return
        
    surl = extract_surl(test_url)
    if not surl:
        print("[-] Error: URL se valid surl code nahi mila.")
        return
        
    print(f"[+] Extracted SURL Code: {surl}")
    
    original_domain = get_domain(test_url)
    
    # Scraper module ko call karna jo automatic fallback handle karega
    html_content = fetch_terabox_data(surl, original_domain)
    
    if html_content:
        print("\n[+] Data successfully fetch ho gaya hai!")
        print(f"[!] Total Content Length: {len(html_content)} characters")
        
        # Yahan aap apna file name ya streaming link parse karne ka logic laga sakte hain
    else:
        print("\n[-] Data fetch nahi ho paya. Link check karein ya thodi der baad try karein.")

if __name__ == "__main__":
    main()
