import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from get_additional_info import get_investor_information

# Set of visited URLs to avoid revisiting
visited = set()

# Keywords for categorization
founder_keywords = ["partners", "team", "founders", "leadership", "management"]
news_investment_keywords = ["news", "investment", "press", "funding", "stories"]

# Save results in separate lists
founder_related_texts = []
news_investment_texts = []
headers = {
"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}

def get_all_links(url):
    """Fetches all links from a given URL."""
    
    try:
        response = requests.get(url,headers=headers)
        response.raise_for_status()  
        soup = BeautifulSoup(response.content, 'html.parser')

        # Find all links on the page
        links = []
        for a_tag in soup.find_all('a', href=True):
            link = a_tag['href']
            full_link = urljoin(url, link)
            # Only include internal links
            if urlparse(full_link).netloc == urlparse(url).netloc:
                links.append(full_link)
        return links
    except requests.exceptions.RequestException as e:
        print(f"Error fetching {url}: {e}")
        return []

def is_keyword_related(url, text_content, keywords):
    """Check if a URL or text content contains any of the specified keywords."""
    url_lower = url.lower()
    text_lower = text_content.lower()
    for keyword in keywords:
        if keyword in url_lower or keyword in text_lower:
            return True
    return False

def extract_text_content(url):
    """Extract text content from a URL."""

    try:
        response = requests.get(url,headers=headers)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Extract all visible text from the page
        text = soup.get_text(separator=' ', strip=True)
        return text
    except requests.exceptions.RequestException as e:
        print(f"Error fetching {url}: {e}")
        return ""

def save_to_file(filename, data):
    """Save extracted text data to a file."""
    with open(filename, "w", encoding="utf-8") as file:
        for item in data:
            file.write(item + "\n\n")

def crawl_website(start_url):
    """Crawl the website starting from the start URL."""
    to_visit = [start_url]  # Queue of pages to visit
    
    while to_visit:
        current_url = to_visit.pop()
        
        # Skip if already visited
        if current_url in visited:
            continue
        
        print(f"Visiting: {current_url}")
        visited.add(current_url)
        
        # Fetch all links from the current page
        links = get_all_links(current_url)
        
        # Extract text content from the current URL
        text_content = extract_text_content(current_url)
        
        # Check if the content is related to founders or news/investment
        if is_keyword_related(current_url, text_content, founder_keywords):
            print(f"Found founder-related content at: {current_url}")
            founder_related_texts.append(f"URL: {current_url}\n{text_content}")
        
        if is_keyword_related(current_url, text_content, news_investment_keywords):
            print(f"Found news/investment-related content at: {current_url}")
            news_investment_texts.append(f"URL: {current_url}\n{text_content}")
        
        # Add new links to the queue
        for link in links:
            if link not in visited:
                to_visit.append(link)

# Start the crawling from the homepage
start_url = "https://www.lavfund.com/"  # Replace with the target website URL
crawl_website(start_url)

# Save results to files
print(founder_related_texts)
print(news_investment_texts)
result = get_investor_information(news_investment_texts)
print(result)
# save_to_file("founder_related_content.txt", founder_related_texts)
# save_to_file("news_investment_content.txt", news_investment_texts)

print("Crawling completed. Results saved to files.")
