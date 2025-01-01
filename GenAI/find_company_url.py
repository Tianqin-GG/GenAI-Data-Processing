import pandas as pd
import requests
from bs4 import BeautifulSoup
data = pd.read_csv('data.csv')
# data = data[:3]
# example = data.iloc[5]
# print(example["OpenAIPartnerResult"],example["url"])
# infor = example["OpenAIPartnerResult"]
# url = example["url"]
import requests
from bs4 import BeautifulSoup
from rapidfuzz.fuzz import partial_ratio


import requests
from bs4 import BeautifulSoup

def save_website_url(company_names,news_urls):
    results = []
    for company_name, news_url in zip(company_names, news_urls):
        # 假设 check_company_link 函数返回一个布尔值，表示是否找到匹配的链接
        if check_company_link(news_url, company_name):
            results.append({'Company Name': company_name, 'URL': news_url})
        else:
            # 如果没有找到匹配，添加 Company Name 和 None
            results.append({'Company Name': company_name, 'URL': None}) 
    print(results)  # 输出匹配的结果
    df = pd.DataFrame(results)  # 创建一个 DataFrame
    df.to_csv('matched_links_updated.csv', mode='a', header=False, index=False)  

def check_company_link(url, company_name):
    try:
        # 发送 HTTP 请求获取页面内容
        response = requests.get(url,verify=False)
        response.raise_for_status()  # 检查请求是否成功
        html_content = response.text

        soup = BeautifulSoup(html_content, 'html.parser')

        links = soup.find_all('a', href=True)

        for link in links:
            href = link['href'].lower()  # 将链接转换为小写，忽略大小写

            company_name_parts = str(company_name).lower().split(" ")
            if company_name.lower() in href:
                print(f"Full match found: {href} for {company_name}")
                return href
            if any(part in href for part in company_name_parts):
                print(href, company_name)
                return href
        
        print("No matching link found.")
        return None


    except requests.RequestException as e:
        print(f"An error occurred: {e}")
        return False

# 示例用法
# url_to_check = url
# company_name = infor
# print([i for i in infor.split(" ")])
# check_company_link(url_to_check, company_name)
save_website_url(data['OpenAIPartnerResult'],data['url'])
