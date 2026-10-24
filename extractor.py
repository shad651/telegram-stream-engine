import re
from urllib.parse import urlparse

def extract_surl(url):
    """TeraBox URL se unique surl code nikalne ka function"""
    match = re.search(r'surl=([a-zA-Z0-9_-]+)', url)
    if match:
        return match.group(1)
    
    match_short = re.search(r'/s/1([a-zA-Z0-9_-]+)', url)
    if match_short:
        return "1" + match_short.group(1)
        
    return None

def get_domain(url):
    """URL se base domain nikalne ka function"""
    parsed = urlparse(url)
    return parsed.netloc
