import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse

# Set of visited URLs to avoid revisiting
visited = set()

def get_all_links(url):
    """Fetches all links from a given URL."""
    try:
        response = requests.get(url)
        response.raise_for_status()  # Check if request was successful
        soup = BeautifulSoup(response.content, 'html.parser')

        # Find all links on the page
        links = []
        for a_tag in soup.find_all('a', href=True):
            link = a_tag['href']
            # Make the link absolute if it's relative
            full_link = urljoin(url, link)
            # Avoid links outside the website domain
            if urlparse(full_link).netloc == urlparse(url).netloc:
                links.append(full_link)
        return links
    except requests.exceptions.RequestException as e:
        print(f"Error fetching {url}: {e}")
        return []

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
        
        # Add new links to the queue
        for link in links:
            if link not in visited:
                to_visit.append(link)

# Start the crawling from the homepage
start_url = "https://cookbook.openai.com/"  # Replace with the target website URL
crawl_website(start_url)
s