import requests
from bs4 import BeautifulSoup
import csv
import time
import re

# Base URL of the HobbyKing site
base_url = "https://hobbyking.com"

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
    "DNT": "1",  # Do Not Track Request Header
    "Connection": "keep-alive"
}

fieldnames=["Title", "Price", "Rating", "Review Count", 'Shipped from',"Specifications"]

def initialize_csv():
    with open('hobbyking_products.csv', 'w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        
def append_to_csv(products):
    with open('hobbyking_products.csv', 'a', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        for product in products:
            writer.writerow(product)
            
# Function to get soup object
def get_soup(url):
    response = requests.get(url, headers=headers)
    response.raise_for_status()  # Ensure we notice bad responses
    return BeautifulSoup(response.text, 'html.parser')

# Function to scrape a single product detail page
def scrape_product_page(product_url):
    soup = get_soup(product_url)
    product_details = {}

    # Extract title
    title_tag = soup.find("h1", class_="product-name")
    product_details['Title'] = title_tag.get_text(strip=True) if title_tag else 'N/A'
    product_details['Rating']=soup.find('div', class_="rating-wrap").find('meta', attrs={"itemprop":"ratingValue"})['content']
    product_details['Review Count']=soup.find('div', class_="rating-wrap").find('meta', attrs={"itemprop":"reviewCount"})['content']
    # Extract price
    price_tag = soup.find("div", class_="price-box").find('span', id=re.compile("product-price-\d+"))
    product_details['Price'] = price_tag.get_text(strip=True) if price_tag else 'N/A'

    product_details['Shipped from']=', '.join([li.text.strip() for li in soup.find('ul',class_='warehouse-stock-list').findAll('li')])
    # Extract specifications
    specs = {}
    specs_section = soup.find("table", class_="data-table")
    if specs_section:
        for row in specs_section.find_all("tr"):
            cells = row.find_all("td")
            if len(cells) == 2:
                key = cells[0].get_text(strip=True)
                value = cells[1].get_text(strip=True)
                specs[key] = value
    product_details['Specifications'] = specs

    return product_details

# Function to navigate through the product sitemap pages and scrape each product
def scrape_from_sitemap():
    page_number = 1
    all_products=[]
    initialize_csv()
    
    while True:
        page_products = []
        sitemap_url = f"https://hobbyking.com/en_us/catalog/seo_sitemap/product/?p={page_number}"
        soup = get_soup(sitemap_url)
        product_links = soup.find("ul", class_="sitemap")

        if not product_links:
            print(f"No more products found on page {page_number}. Stopping.")
            break
        
        product_links= product_links.find_all('a')

        if not product_links:
            print(f"No more products found on page {page_number}. Stopping.")
            break
        
        for link in product_links:
            product_url = link['href']
            print(f"Scraping {product_url}")
            try:
                product_details = scrape_product_page(product_url)
                page_products.append(product_details)
                all_products.append(product_details)
                time.sleep(0.2)
            except Exception as e:
                print(f"Failed to scrape {product_url}: {e}")

        append_to_csv(page_products)
        print(f"Page {page_number} scraped and data appended to CSV.")
        if page_number==155:
            break
        page_number+=1
        time.sleep(1)  # Respectful crawling by waiting a second

    return all_products

# Main function to orchestrate the scraping
def main():
    all_products = scrape_from_sitemap()
    
    # Writing to CSV
    if all_products:
        print("Data scraped successfully and written to hobbyking_products.csv")
    else:
        print("No products were scraped.")

if __name__ == "__main__":
    main()