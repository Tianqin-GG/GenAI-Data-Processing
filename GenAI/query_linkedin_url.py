import requests
from bs4 import BeautifulSoup
import openai
import os
import asyncio
import re

openai.api_key = os.getenv("OPENAI_API_KEY")


async def search_google_for_linkedin(person_name, company_name, description=None):
    """
    Google search for url based on name, company and description
    """
    query = f'site:linkedin.com/in "{person_name}" "{company_name}"'
    if description:
        query += f' "{description}"'

    search_url = f"https://www.google.com/search?q={query}"

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }


    loop = asyncio.get_event_loop()
    try:
        response = await loop.run_in_executor(
            None, lambda: requests.get(search_url, headers=headers, verify=False)
        )
        response.raise_for_status()  
    except requests.RequestException as e:
        print(f"Google Search Request failed: {e}")
        return []


    soup = BeautifulSoup(response.text, "html.parser")
    linkedin_urls = []
    for a_tag in soup.find_all("a", href=True):
        href = a_tag["href"]
        if "linkedin.com/in" in href:
            clean_url = href.split("/url?q=")[-1].split("&")[0]
            linkedin_urls.append(clean_url)

    return linkedin_urls
def extract_urls(text):
    url_pattern = r'https?://(?:www\.)?[\w-]+(?:\.[\w-]+)+(?:/[\w\-/]*)?'
    urls = re.findall(url_pattern, text)
    
    return urls

async def filter_linkedin_via_api_bulk(linkedin_urls, target_name, target_company, target_company_description):
    """
    OpenAI to filter out the url
    """

    prompt = (
        f"I want to get the URL of {target_name} who works in {target_company}. "
        f"The company is described as {target_company_description}. "
        f"Look through the following LinkedIn URLs and find the most accurate match: {linkedin_urls}."
        f"If you find no match, search the information and suggest me the person's linkedin url"
        f"return the url, or None"
    )

    try:

        response = await asyncio.get_event_loop().run_in_executor(
            None,
            lambda: openai.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are an expert at analyzing LinkedIn URLs."},
                    {"role": "user", "content": prompt},
                ],
            ),
        )


        result = response.choices[0].message.content.strip()
        print(response.usage.completion_tokens)
        # print("Raw API Response:", result)  


        return extract_urls(result)

    except Exception as e:
        print(f"Error when calling API: {e}")
        return None


async def main():
    person_name = "Dario"
    company_name = "Galen Growth"
    description = "Singapore"

    linkedin_urls = await search_google_for_linkedin(person_name, company_name, description)

    if linkedin_urls:
        print("Searched URLs:")
        print(linkedin_urls)
        result = await filter_linkedin_via_api_bulk(linkedin_urls, person_name, company_name, description)

        print("\nAPI filter result:")
        
        print(result)
    else:
        print("No LinkedIn URLs")



asyncio.run(main())
