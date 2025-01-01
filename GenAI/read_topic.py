import pandas as pd
import asyncio
import os
from openai import OpenAI
import re

client = OpenAI()
api_key = os.getenv("OPENAI_API_KEY")
data1 = pd.read_csv('data1.csv')
data = pd.read_csv('data.csv')
# example = data.iloc[0]
# print(example["OpenAIPartnerResult"],example["url"])
# infor = example["OpenAIPartnerResult"]
# url = example["url"]
# print(data.columns)




def save_website_url(company_names,news_urls, websites_urls):
    results = []
    for company_name, news_url, website in zip(company_names, news_urls,websites_urls):

            # 假设 check_company_link 函数返回一个布尔值，表示是否找到匹配的链接
            if get_corporate_website( company_name, news_url):
                results.append({'Company Name': company_name, 'AURL': get_corporate_website( company_name, news_url)})
            else:
                # 如果没有找到匹配，添加 Company Name 和 None
                results.append({'Company Name': company_name, 'AURL': None}) 

    print(results)  # 输出匹配的结果
    df = pd.DataFrame(results)  # 创建一个 DataFrame
    df.to_csv('api_ma_result_summary.csv', mode='a', header=False, index=False)  


def get_corporate_website(company_name,news_url):
    try:
        completion = client.chat.completions.create(
            model="gpt-4", 
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a websites identification expert. You are responsible to provide accurate and reliable url for companies"
                    )
                },
                {
                    "role": "user",
                    "content": (
                        f"I want to get the official website of {company_name}\
                        the {news_url} writes about the company's recent investment. As the official website of the company could be included in {news_url}\
                        search the {company_name} and give me the official websites of the {company_name}\
                        You should return me the OFFICIAL website of the {company_name}.\
                        return me the url or none in json format."
                    )
                }
            ]
        )
        
        # Extract response content
        response_message = completion.choices[0].message.content
        print(response_message)
        url_match = re.search(r'(https?://[^\s]+)', response_message)
        if url_match:
            # If a URL is found, return it
            result = {"URL": url_match.group(0)}
            return result
        else:
            # If no URL found, return None
            result = {"URL": None}
            return None
        print("Result:", result)
        print("Token Consumed", completion.usage.completion_tokens)
    except Exception as e:
        print(f"Error fetching investor information: {e}")     
        

save_website_url(data1['OpenAIPartnerResult'],data['title'],data1['URL (News)'])