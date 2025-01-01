import re
from urllib.parse import urlparse

def normalize_url(url):
    # 确保网址是合法的
    if not re.match(r'^[a-zA-Z0-9]+://', url):
        url = 'https://' + url  # 默认为 https
    
    # 确保网址包含 www
    parsed_url = urlparse(url)
    if parsed_url.netloc and not parsed_url.netloc.startswith('www.'):
        url = url.replace(parsed_url.netloc, 'www.' + parsed_url.netloc)

    return url

# 测试
urls = [
    "assam.gov.in", 
    "example.com", 
    "http://testsite.org", 
    "https://othersite.net"
]

normalized_urls = [normalize_url(url) for url in urls]
print(normalized_urls)
