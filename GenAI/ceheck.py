import pandas as pd
import requests
from bs4 import BeautifulSoup

def save_website_url(company_names, news_urls):
    results = []
    for company_name, news_url in zip(company_names, news_urls):
        # Call the function to check if the company name is within a hyperlink
        found_url = check_company_link(news_url, company_name)
        if found_url:
            results.append({'Company Name': company_name, 'URL': found_url})
        else:
            # If no match is found, append None for the URL
            results.append({'Company Name': company_name, 'URL': None})
    
    # Output results
    print(results)
    
    # Create a DataFrame and save to a CSV file
    df = pd.DataFrame(results)
    df.to_csv('matched_links_updated1.csv', mode='a', header=False, index=False)

def check_company_link(url, company_name):
    try:
        # Send the HTTP request to get the page content
        response = requests.get(url, verify=False)
        response.raise_for_status()  # Check if the request was successful
        html_content = response.text

        # Parse the HTML content with BeautifulSoup
        soup = BeautifulSoup(html_content, 'html.parser')

        # Find all <a> tags with an href attribute
        links = soup.find_all('a', href=True)

        # Check if the company name is part of any link's text and if the link is present
        company_name_lower = company_name.lower()

        for link in links:
            link_text = link.get_text().strip().lower()  # Get the link's text and convert to lowercase
            
            # Check if the company name is present in the text of the <a> tag
            if company_name_lower in link_text:
                # If found, return the href attribute (the URL)
                print(f"Found company name '{company_name}' in link: {link['href']}")
                return link['href']

        print(f"No matching link found for company: {company_name}")
        return None

    except requests.RequestException as e:
        print(f"An error occurred: {e}")
        return None

# Load the data
data = pd.read_csv('data.csv')

# Call the save_website_url function with the columns from your DataFrame
save_website_url(data['OpenAIPartnerResult'], data['url'])
