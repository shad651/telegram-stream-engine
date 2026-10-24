from pathlib import Path
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
    Path("response.html").write_text(
        html_content, encoding="utf-8"
    )

    print("[+] HTML saved: response.html")
    print(f"[+] Response length: {len(html_content)} characters")

    print("\n[DEBUG] HTML content indicators:")

    keywords = [
        "filelist",
        "shareid",
        "uk",
        "fs_id",
        "file_name",
        "video",
        "playurl",
        "dlink",
        "m3u8",
        ".mp4"
    ]

    for keyword in keywords:
        found = keyword.lower() in html_content.lower()
        print(f"{keyword}: {found}")

else:
    print("\n[-] Fetch function ne usable HTML return nahi kiya.")
    print("[!] Agar response.html maujood hai, usmein last response save ho sakta hai.")

if name == "main":
main()