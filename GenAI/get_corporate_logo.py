from selenium import webdriver
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import requests
import re
from urllib.parse import urlparse


def get_page_content(url):
    """
    Retrieve page content using Selenium for JavaScript-rendered pages.
    """
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")  # Run browser in headless mode
    driver = webdriver.Chrome(options=options)
    driver.get(url)
    page_source = driver.page_source
    driver.quit()
    return BeautifulSoup(page_source, "html.parser")


def is_logo_candidate(src, alt, class_name, id_name):
    """
    Check if an image is likely to be a logo based on attributes.
    """
    return (
        "logo" in (alt or "") or
        "logo" in (class_name or "") or
        "logo" in (id_name or "") or
        "logo" in (src or "") 
    )


def find_logo_url(soup, base_url):
    """
    Attempt to extract the logo URL from the page using multiple strategies.
    """
    # Strategy 1: Check common attributes in <img> tags
    logo_candidates = soup.find_all("img")
    print(f"Found {len(logo_candidates)} <img> tags")

    for img in logo_candidates:
        # Check various attributes for image source
        src = img.get("src") or img.get("data-src") or img.get("srcset") or img.get("data-lazy-src")
        alt = img.get("alt", "").lower()
        class_name = " ".join(img.get("class", [])).lower()
        id_name = img.get("id", "").lower()

        print(f"Checking image - src: {src}, alt: {alt}, class: {class_name}, id: {id_name}")

        if src and is_logo_candidate(src, alt, class_name, id_name):
            logo_url = urljoin(base_url, src)
            print(f"Logo found using <img> tag: {logo_url}")
            return logo_url

    # Strategy 2: Check <link rel="icon"> or <meta property="og:image">
    icon_link = soup.find("link", rel="icon")
    if icon_link and icon_link.get("href"):
        logo_url = urljoin(base_url, icon_link["href"])
        print(f"Logo found using <link rel='icon'>: {logo_url}")
        return logo_url

    og_image = soup.find("meta", property="og:image")
    if og_image and og_image.get("content"):
        logo_url = urljoin(base_url, og_image["content"])
        print(f"Logo found using <meta property='og:image'>: {logo_url}")
        return logo_url

    # Strategy 3: If there's only one large image on the page, use it
    large_images = [img for img in logo_candidates if img.get("src") and is_large_image(img)]
    if len(large_images) == 1:
        logo_url = urljoin(base_url, large_images[0].get("src"))
        print(f"Logo found using large image: {logo_url}")
        return logo_url

    print("No logo found.")
    return None


def is_large_image(img_tag):
    """
    Determine if the image is relatively large (likely to be the logo).
    """
    try:
        width = int(img_tag.get("width", 0))
        height = int(img_tag.get("height", 0))
        # Assume that a logo image is relatively large in width and height
        return width > 100 and height > 30
    except ValueError:
        return False

def get_facebook_profile_picture(url):
    """
    Get the profile picture of a Facebook page from the provided URL (for public profiles).
    """
    try:
        # Send a GET request to fetch the HTML content
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        response = requests.get(url, headers=headers)
        
        if response.status_code != 200:
            print(f"Error: Unable to fetch the webpage. Status code: {response.status_code}")
            return None

        # Parse the HTML content using BeautifulSoup
        soup = BeautifulSoup(response.text, "html.parser")

        # Find the og:image meta tag which usually contains the profile image URL
        og_image = soup.find("meta", property="og:image")
        if og_image:
            # Extract the URL from the content attribute of the og:image meta tag
            profile_picture_url = og_image["content"]
            print(f"Profile picture URL found: {profile_picture_url}")
            return profile_picture_url
        else:
            print("Error: No profile picture found in the meta tags.")
            return None

    except Exception as e:
        print(f"Error occurred: {e}")
        return None




def download_logo(logo_url, company_name):
    """
    Download the logo and save it locally.
    """
    if not logo_url:
        print("No logo URL to download.")
        return None

    response = requests.get(logo_url, stream=True,verify=False)
    try:
        headers = {"User-Agent": "Mozilla/5.0 (compatible; MyApp/1.0)"}
        response = requests.get(logo_url, headers=headers, stream=True, timeout=10)
        response.raise_for_status()  
        
        content_type = response.headers.get("Content-Type", "")
        if 'image/svg+xml' in content_type:
            file_extension = ".svg"
        elif 'image/png' in content_type:
            file_extension = ".png"
        elif 'image/jpeg' in content_type or 'image/jpg' in content_type:
            file_extension = ".jpg"
        else:
            print(f"Unsupported content type: {content_type}")
            return None

        # 根据公司名字生成文件名
        filename = f"{company_name}{file_extension}"

        # 保存文件
        with open(filename, "wb" if file_extension != ".svg" else "w", encoding="utf-8" if file_extension == ".svg" else None) as file:
            if file_extension == ".svg":
                file.write(response.text)  # SVG 文件是文本格式
            else:
                for chunk in response.iter_content(4096):
                    if chunk:
                        file.write(chunk)  # 写入二进制数据

        print(f"Logo saved as {filename}")
        return filename
    except requests.exceptions.RequestException as e:
        print(f"Error downloading logo: {e}")
        return None
    except IOError as e:
        print(f"File write error: {e}")
        return None




def get_logo(company_url):
    """
    Extract the logo from the company's homepage and save it locally.
    """
    try:
        soup = get_page_content(company_url)
        logo_url = find_logo_url(soup, company_url)
        if logo_url:
            logo_url = urljoin(company_url, logo_url)
            return logo_url
        else:
            print(f"No logo found for {company_url}.")
            return None
    except Exception as e:
        print(f"Error occurred: {e}")
        return None




def normalize_url(url):
    if not re.match(r'^[a-zA-Z0-9]+://', url):
        url = 'https://' + url  
    
    parsed_url = urlparse(url)
    if parsed_url.netloc and not parsed_url.netloc.startswith('www.'):
        url = url.replace(parsed_url.netloc, 'www.' + parsed_url.netloc)

    return url

get_logo('https://www.ccia.org.au/')
# if __name__ == "__main__":
#     # Test company homepage URL
#     company_url_list  = []
#     company_url = "https://www.facebook.com/charteredlifeinsurance/"
#     get_logo(company_url, "logo.=")
#     # url = "https://www.facebook.com/charteredlifeinsurance/"
#     # profile_picture_url = get_facebook_profile_picture(url)
#     # download_logo(profile_picture_url, 'sss')


#     # get_facebook_profile_picture("https://www.facebook.com/charteredlifeinsurance/")


#     # 需求：存储的格式应该是id + format
#     # 如果website crape logo结果为空，去找剩下的两个web，直到找到logo
#     # 存储结果应该为svg，png，wepg