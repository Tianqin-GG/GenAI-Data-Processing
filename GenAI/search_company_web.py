import requests
from bs4 import BeautifulSoup
import pandas as pd
import random
import time
df = pd.read_csv('web.csv')

def get_company_website(company_name):
    search_url = "https://www.google.com/search"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36"
    }
    params = {
        "q": company_name + " official website",
        "hl": "en",
    }

    retries = 3
    while retries > 0:
        try:
            response = requests.get(search_url, headers=headers, params=params, timeout=10)
            response.raise_for_status()

            # Parse HTML and extract the first search result link
            soup = BeautifulSoup(response.text, "html.parser")
            search_results = soup.find_all("div", class_="tF2Cxc")

            if search_results:
                first_result = search_results[0].find("a")
                if first_result:
                    return first_result["href"]

            return "No website found"
        except requests.exceptions.Timeout:
            print(f"Timeout occurred for {company_name}. Retrying...")
            retries -= 1
            time.sleep(random.randint(5, 10))
        except requests.exceptions.RequestException as e:
            if response.status_code == 429:
                print(f"Rate-limited (429) for {company_name}. Retrying after a longer delay...")
                retries -= 1
                time.sleep(random.randint(30, 60))  # Wait longer for 429 errors
            else:
                print(f"Error occurred for {company_name}: {e}. Skipping.")
                break

    return "No website found"

results = []
if __name__ == "__main__":
    for name, ids in zip(df['NAME'], df['corporate_id']):
        print(f"Processing {name} ({ids})")
        website = get_company_website(name)

        result = {
            'corporate_id': ids,
            'NAME': name,
            'website': website
        }

        print(f"Website for {name}: {website}")
        results.append(result)

    # Save results to a CSV
    data = pd.DataFrame(results)
    data.to_csv("results.csv", mode="a", header=False, index=False)
