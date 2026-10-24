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

html_content = fetch_terabox_data(surl, original_domain)

if html_content:

        with open("response.html", "w", encoding="utf-8") as f:
            f.write(html_content)

        print("[+] HTML saved: response.html")

        with open("response.html", "w", encoding="utf-8") as f:
            f.write(html_content)

        print("[+] HTML response response.html mein save ho gaya.")
    print("\n[+] Response successfully receive hua!")
    print(f"[!] Total Content Length: {len(html_content)} characters")

    print("\n[DEBUG] HTML content indicators:")

    keywords = [
        "filelist",
        "shareid",
        "uk",
        "fs_id",
        "file_name",
        "video",
        "sign",
        "list",
        "BadJs"
    ]

    for keyword in keywords:
        found = keyword.lower() in html_content.lower()
        print(f"{keyword}: {found}")

else:
    print("\n[-] Data fetch nahi ho paya. Link check karein ya thodi der baad try karein.")

if name == "main":
main()