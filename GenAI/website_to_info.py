from urllib.request import urlopen
from bs4 import BeautifulSoup
import re
import requests
import json
from fuzzywuzzy import fuzz
from get_information_basic import get_information_basic
from get_additional_info import get_investor_information
import pandas as pd
import asyncio
cate = pd.read_csv('./data/part.csv')
# print(category.head())
category = []
for i in cate['name']:
    if i not in category:
        category.append(i)


testdata = pd.read_csv('add.csv')


headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3538.102 Safari/537.36 Edge/18.19582"
}
debug = False

def startsWithHttp(url):
    """
    Check if Url starts with 'HTTP/s' else append it before and return.

    """
    
    match = re.match(r'^(?:http)s?://', url, re.I | re.M)  # ignore case
    if match:
        return url
    else:
        return "https://" + url


def get_text_from_soup(page_soup: BeautifulSoup):
    """Given the beautiful soup object of the page, extract all text

    Args:
            page_soup (BeautifulSoup): Soup object of the page.

    Returns:
            list: List of text of the page.
    """
    try:
        # get text
        text = page_soup.get_text()
        # break into lines and remove leading and trailing space on each
        lines = (line.strip() for line in text.splitlines())
        # break multi-headlines into a line each
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        # drop blank lines
        return [chunk for chunk in chunks if chunk]
    except Exception as e:
        print('Unable to get text of the page.')
        return []
    
def get_meta(page_soup):
    """Gets the meta data of the page given the BeautifulSoup object.

    Args:
            page_soup (BeautifulSoup): page content

    Returns:
            dict: A dictionary of the meta keys and their values. 
    """
    return {each['property']: each['content'] for each in page_soup.find_all('meta') if 'property' in each.attrs and 'content' in each.attrs}

def get_soup(website):
    """Gets the BeautifulSoup object of the page content if website is responsive.

    Args:
            website (string): webpage link

    Returns:
            BeautifulSoup: page content. 
            None: if page does not load.
    """
    try:
        html = requests.get(website, headers=headers, timeout=5)
        return BeautifulSoup(html.text, features="html.parser")
    except Exception as e:
        if debug:
            print('NO RESULT')
        return None

def get_soup_and_meta(page_url):
    """Gets the meta data of the page given the url.

    Args:
            page_url (string): webpage link

    Returns:
            dict: A dictionary of the meta keys and their values. 
                        if page is irresponsive, returns None.
    """
    soup = get_soup(page_url)
    if soup:
        return get_meta(soup)
    return None


class WebsiteSocials:
    """Given the BeautifulSoup object of the page content, extracts the social links.
    """
    def __init__(self, soup):
        self.soup = soup
        self.all_links, self.wix_image = self.get_all_links()
        self.twitter = self.process_link('twitter.com')
        self.linkedin = self.process_link('linkedin.com')
        self.facebook = self.process_link('facebook.com')
        self.instagram = self.process_link('instagram.com')

    def get_all_links(self):
        soup = self.soup
        hrefs = [l['href'] for l in soup.find_all('a') if 'href' in l.attrs]
        wix_image = None
        for e in soup.find_all('a'):
            img = e.find('img')
            if img and 'src' in img.attrs:
                wix_image = img['src']
                for x in ['.png', '.webp']:
                    if wix_image.count('.png') > 1:
                        wix_image = wix_image[:wix_image.find(x) + len(x)]
                break
        return hrefs, wix_image

    def process_link(self, search_string):
        for each in self.all_links:
            if search_string in each:
                return each
        return

def save_basic_information(company_urls, company_names):
    if len(company_urls) != len(company_names):
        raise ValueError("The lengths of company_urls and company_names must match!")

    results = []

    for i, (url, name) in enumerate(zip(company_urls, company_names)):
        # 每次循环都初始化一个默认字典
        result = {
            "Company Name": None,
            "Industry": None,
            "Specialties": None,
            "Description": None,
            "Founded": None,
            "URL": url,  # 保留原始 URL 信息
            "Company_AI_name": name,  # 当前循环的公司名
        }
        
        if not pd.isna(url):  # 检查 URL 是否为空
            print(f"Processing {i + 1}/{len(company_urls)}: {name} -> {url}")
            soup = get_soup(startsWithHttp(url))
            if soup:
                try:
                    text_data = get_text_from_soup(soup)
                    if text_data:
                        structured_result = get_information_basic(text_data, category)
                        if structured_result:
                            # 更新结果字典
                            result.update({
                                "Company Name": structured_result.get("Company Name"),
                                "Industry": structured_result.get("Industry"),
                                "Specialties": structured_result.get("Specialties"),
                                "Description": structured_result.get("Description"),
                                "Founded": structured_result.get("Founded"),
                            })
                        else:
                            print(f"No structured result for {name}.")
                    else:
                        print(f"Failed to fetch text data for {name}.")
                except Exception as e:
                    print(f"Error fetching company information for {name}: {e}")
        else:
            print(f"Skipping invalid URL at row {i + 1}: {name}.")

        # 将结果加入列表，即使失败或为空也加入默认结果
        results.append(result)

    # 将结果保存为 DataFrame
    df = pd.DataFrame(results)
    print("Final DataFrame:")
    print(df)

    # 保存到 CSV 文件
    df.to_csv("resultsssss.csv", mode="a", header=False, index=False)



save_basic_information(testdata['website'],testdata['name'])




