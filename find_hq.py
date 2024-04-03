import requests
from bs4 import BeautifulSoup
from urllib.parse import parse_qsl, urljoin, urlparse

def get_headquarter_country(url):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            # Find the specific HTML tag or class that contains the relevant information indicating the headquarters location.
            # Search for keywords like "founded in", "manufactures in", etc.
            keywords = ["manufacturers in", "founded in"]
            for keyword in keywords:
                tag_containing_keyword = soup.find(lambda tag: keyword in tag.text.lower())
                if tag_containing_keyword:
                    # Extract the next word after the keyword
                    words_after_keyword = tag_containing_keyword.text.split(keyword)[-1].split()
                    if len(words_after_keyword) > 0:
                        country = words_after_keyword[0].strip().rstrip(',.')
                        return country
            print(f"Headquarters information not found on {url}")
            return None
        else:
            print(f"Failed to retrieve data from {url}. Status code: {response.status_code}")
            return None
    except Exception as e:
        print(f"An error occurred while scraping {url}: {str(e)}")
        return None

def read_countries_list():
    try:
        with open("countries_list.txt", "r") as file:
            countries_list = [line.strip() for line in file.readlines()]
            return countries_list
    except Exception as e:
        print(f"An error occurred while reading countries list: {str(e)}")
        return None

# List of drone company websites
company_websites = [
    "https://www.hqprop.com/art/about-us-a0040.html",
    "https://www.gemfanhobby.com/show.aspx?id=60&cid=30",
    # Add more company websites as needed
]


# Read countries list
countries_list = read_countries_list()
if countries_list:
    for website in company_websites:
        domain = urlparse(website).netloc.split('.')[1] # Parse the URL to get the domain name
        country = get_headquarter_country(website)
        if country:
            if country.lower() in [c.lower() for c in countries_list]:
                print(domain + " hq is in " + country)
            else:
                print(domain + " hq not listed or " + country + " not in list of countries")
                # print(f"Headquarters information not found on {domain}")
else:
    print("Failed to read countries list.")




# "https://www.hqprop.com/art/about-us-a0040.html",
# "https://www.gemfanhobby.com/show.aspx?id=60&cid=30"