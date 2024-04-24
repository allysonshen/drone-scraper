import requests
from bs4 import BeautifulSoup, Tag
import csv
import time
import re
import os

# Base URL of the HobbyKing site
base_url = "https://hobbyking.com"

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
    "DNT": "1",  # Do Not Track Request Header
    "Connection": "keep-alive"
}

fieldnames=["Title","SKU","Price", "Rating", "Review Count", 'Shipped from',"Specifications", "URL"]
all_products=[]
ingested=set()

def add_product_features(prev_products,new_product, csv=False):
    # Update the global list of all features discovered so far
    prev=list(prev_products)
    for key in new_product.keys():
        if key not in fieldnames:
            fieldnames.append(key)

    # Ensure all products have all features (existing ones are filled with None if missing)
    min_count=100000
    for product in prev:
        count=0
        for feature in fieldnames:
            if feature not in product:
                count+=1
                product[feature] = None  # Set None if feature key is not present
        if count<min_count:
            min_count=count

    if csv:
        if min_count>0:
            print(min_count, "new features discovered and recorded into the CSV.")
        else:
            print("No new features discovered")
    # Prepare new product with all features
    full_product = {feature: new_product.get(feature, None) for feature in fieldnames}
    prev.append(full_product)
    return prev.copy()
        
def append_page_to_csv(products, page_number, existing):
    if len(products)==0:
        return
    if page_number==1 and not existing:
        with open('hobbyking_products.csv', 'w', newline='', encoding='utf-8') as file:
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()
            for product in products:
                writer.writerow(product)
    else:
        past_prod=[]
        with open('hobbyking_products.csv', 'r',newline='',encoding='utf-8') as file:
            reader=csv.DictReader(file)
            past_prod=add_product_features(reader,products[-1],csv=True)[:-1]
        past_prod.extend(products)
        with open('hobbyking_products.csv', 'w', newline='', encoding='utf-8') as file:
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()
            for product in past_prod:
                writer.writerow(product)
            
            
            
# Function to get soup object
def get_soup(url):
    for num_try in range(5):
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()  # Ensure we notice bad responses
            break
        except Exception as e:
            print("Try",num_try+1,"failed",e)
            time.sleep(0.15*(num_try+2))
    return BeautifulSoup(response.text, 'html.parser')

# Function to scrape a single product detail page
def scrape_product_page(product_url):
    soup = get_soup(product_url)
    product_details = {}
    product_details['URL']=product_url
   
    # Extract title    
    title_tag = soup.find("h1", class_="product-name")
    product_details['Title'] = title_tag.get_text(strip=True) if title_tag else 'N/A'
    product_details['Rating']=soup.find('div', class_="rating-wrap").find('meta', attrs={"itemprop":"ratingValue"})['content']
    product_details['Review Count']=soup.find('div', class_="rating-wrap").find('meta', attrs={"itemprop":"reviewCount"})['content']
    # Extract price
    price_tag = soup.find("div", class_="price-box").find('span', id=re.compile("product-price-\d+"))
    product_details['Price'] = price_tag.get_text(strip=True) if price_tag else 'N/A'
    product_details['SKU']=soup.find('div', class_="row-column sku").find('div', class_='value').get_text(strip=True)
    try:
        product_details['Shipped from']=', '.join([li.text.strip() for li in soup.find('ul',class_='warehouse-stock-list').findAll('li')])
    except Exception as e:
        product_details['Shipped from']=None
    # Extract specifications
    description=soup.find('div', class_='product-view main-product-view').find('div', class_='product-additional-info', recursive=False).find('div', id='tab-description').find('div', class_='std')
    text=''
    p_count=0
    for p in description.find_all('p'):
        p_count+=1
        if p.contents and isinstance(p.contents[0], Tag) and p.contents[0].name == 'br':
            p.contents=p.contents[1:]
        if p.get_text(strip=True)=='&nbsp;' :
            continue
        elif p.contents and isinstance(p.contents[0], Tag) and p.contents[0].name == 'strong':
            spec_lines = p.decode_contents().split('<br/>')
            specs=[]
            if p.contents[0].get_text(strip=True)==product_details['Title']:
                continue
            try:
                spec_name,_=p.contents[0].get_text(strip=True).split(':',1)
            except Exception as e:
                print(e, p.contents[0].get_text(strip=True))
                if p.contents[0].get_text(strip=True)=='':
                    spec_lines=spec_lines[1:]
                    spec_name='*note'
                elif p_count==1:
                    product_details['Alt Title']=p.contents[0].get_text(strip=True)
                    continue
                elif p.contents[0].get_text(strip=True) in ['Spec.','Specs.','Sp.','Spec;','Specs;','Sp;', 'SPEC.', 'SPEC;','Specs','Spec']:
                    spec_lines=spec_lines[1:]
                    spec_name='Specs'
                elif p.contents[0].get_text(strip=True) in ['Feat.','Feat;','Feats.','Feats;','Ft.','Fts.','Ft;','Fts;','Features.','Features;','Feat','Features','Feats','Feature','Feature.','Feature;','Key Feats.','Key Features.','Key Features;','Key Features']:
                    spec_lines=spec_lines[1:]
                    spec_name='Features'
                elif p.contents[0].get_text(strip=True) in ['Included','Includes','Including', 'Included.','Includes.','Including.','Included;','Includes;','Including;']:
                    spec_lines=spec_lines[1:]
                    spec_name='Included'
                elif p.contents[0].get_text(strip=True) in ['Advantages over traditional Lipoly batteries;', 'Advantages over traditional Lipoly batteries.', 'Advantages over traditional Lipoly batteries']:
                    spec_lines=spec_lines[1:]
                    spec_name='Advantages'
                else:
                    product_details['*note']=[p.contents[0].get_text(strip=True)]
                    continue
            
            for line in spec_lines:
    # Using BeautifulSoup again to parse each line and extract text cleanly
                line_soup = BeautifulSoup(line, 'html.parser')
    # Extract text which should be in the format "key: value"
                line_text = line_soup.get_text(strip=True)
                if line_text=='':
                    continue
                if ':' in line_text:  # Check if the line contains a spec
                    key, value = line_text.split(':', 1)  # Split only on the first colon
                    if not value=='':
                        if product_details.get(key.strip().lower()):
                            product_details[key.strip().lower()] += value.strip()
                        else:
                            product_details[key.strip().lower()] = value.strip()
                else:
                    specs.append(line_text)
            if spec_name=='Specifications' or spec_name=='SPECS':
                spec_name='Specs'
            elif spec_name=='Key Features' or spec_name=='Feature' or spec_name=='Feats':
                spec_name='Features'
            
            if len(specs)>0:
                if product_details.get(spec_name.lower()):
                    list_form=list(product_details[spec_name.lower()])
                    list_form.extend(specs)
                    product_details[spec_name.lower()]=list_form
                else:
                    product_details[spec_name.lower()]=specs
                    
        else:
            text=text+p.get_text(strip=True)
    
    if not text=='':
        product_details['Description']=text
    else:
        product_details['Description']=None
    
     
        
    specs = {}
    specs_section = soup.find('div', class_='product-additional-info').find('div', id='tab-additional')
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
def scrape_from_sitemap(existing):
    page_number = 1
    
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
        
        start_time=time.perf_counter()
        for link in product_links:
            if link.text.strip() in ingested:
                print("-----DUPLICATE FOUND. Skipping (",link.text.strip(),")-----")
                continue
            product_url = link['href']
            if len(existing)>0 and product_url in existing:
                print('-----ALREADY IN PREVIOUS CSV. Skipping (',link.text.strip(),')-----')
                continue
            print(f"Scraping {product_url}")
            #try:
            product_details = scrape_product_page(product_url)
            page_products=add_product_features(page_products,product_details)
            all_products.append(product_details)
            time.sleep(0.15)
            #except Exception as e:
             #   print(f"Failed to scrape {product_url}: {e}")
        if len(existing)>0:
            append_page_to_csv(page_products, page_number, True)
        else:
            append_page_to_csv(page_products, page_number, False)
        end_time=time.perf_counter()
        print()
        print(f"------- Page {page_number} scraped and data appended to CSV. ------ (", int(end_time-start_time), "seconds to scrape)")
        print()
        if page_number==155:
            break
        page_number+=1
        time.sleep(1)  # Respectful crawling by waiting a second

    return all_products

# Main function to orchestrate the scraping
def main():
    global fieldnames
    existing=set()
    if os.path.exists('hobbyking_products.csv'):
        print("CSV exists! Getting list of known products...")
        with open('hobbyking_products.csv', mode='r',newline='',encoding='utf-8') as file:
            reader=csv.DictReader(file)
            fieldnames=list(reader.fieldnames)
            for product in reader:
                existing.add(product['URL'])
                
    all_products = scrape_from_sitemap(existing)
    
    # Writing to CSV
    if all_products:
        print("Data scraped successfully and written to hobbyking_products.csv")
    else:
        print("No products were scraped.")

if __name__ == "__main__":
    main()