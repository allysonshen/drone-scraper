from bs4 import BeautifulSoup
from selenium import webdriver
import re

url = "https://www.getfpv.com/motors/mini-quad-motors.html"
browser = webdriver.Firefox()
browser.get(url)
html = browser.page_source
soup = BeautifulSoup(html)

checkbox_labels = []

# Find all anchor tags with "manufacturer=" in the href attribute
manufacturer_links = soup.find_all('a', href=lambda href: href and 'manufacturer=' in href)

# Print the contents of the anchor tags
for link in manufacturer_links:
    link_content = link.text
    end_idx = link_content.find('(')
    if end_idx != -1:
        link_content = link_content[:end_idx].strip()
    else:
        link_content = link_content.strip()
    print(link_content)

browser.close()
