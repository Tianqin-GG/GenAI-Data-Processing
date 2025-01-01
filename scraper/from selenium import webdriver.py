import requests
from bs4 import BeautifulSoup

def search_linkedin_google(domain):
    """
    Search LinkedIn URL for a domain using Google Search.
    """
    # Construct Google search query
    search_query = f"{domain} site:linkedin.com"
    google_search_url = f"https://www.google.com/search?q={search_query}"

    # Send a GET request with User-Agent to avoid bot detection
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.5615.50 Safari/537.36"}
    response = requests.get(google_search_url, headers=headers)

    if response.status_code == 200:
        # Parse the search results
        soup = BeautifulSoup(response.content, "html.parser")

        # Extract search results and look for LinkedIn links
        for link in soup.find_all("a", href=True):
            href = link["href"]
            if "linkedin.com/company/" in href:  # Check if it's a LinkedIn company link
                # Clean the Google redirect link
                clean_link = href.split("/url?q=")[-1].split("&")[0]
                return clean_link  # Return the first valid LinkedIn URL

    print("No LinkedIn link found.")
    return None

# Example usage
if __name__ == "__main__":
    email = "example@galengrowth.com"  # Example email
    domain = email.split("@")[-1]  # Extract domain from the email
    linkedin_url = search_linkedin_google(domain)
    if linkedin_url:
        print(f"LinkedIn URL found: {linkedin_url}")
    else:
        print("No LinkedIn URL found.")
