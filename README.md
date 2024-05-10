# drone-scraper
# CARTER at USC Web Scraper for Drone Parts' Manufacturers and Manufacturing Origins

This repository contains a web scraper for team CARTER at USC (University of Southern California) to collect data on the manufacturers of the drone components and their origins. It scrapes some of the known websites that drone designers frequent to look for COTS parts. We provide 2 scrapers: one for getfpv.com and the other for hobbyking.com. Additionally, we have already exhaustively ran the HobbyKing scraper and populated a CSV-formatted database of all parts available on the marketplace, `hobbyking_products.csv`. After cloning, future runs of the scraper will simply append newly discovered parts to the database.

## Purpose
The data can be useful for
1. gathering the list of drone part manufacturers
2. discovering compliance based on the country of origin.

## How to Use GetFPV scraper (Allyson Shen)
1. Clone this repository to your local machine.
2. Run the `find_hq.py` script to start scraping data.
3. Specify the parameters such as sources, key words, etc., as necessary.
4. The result will be outputted in the terminal.

## How to Use HobbyKing scraper (Lavrenti Mikaelyan)
1. Clone this repository to your local machine.
2. Run the `hobbyking-scrape.py` script to begin scraping through all products on the website
3. You will see updates in the terminal as each part is scraped and recorded
4. Stop the script at any time with Ctrl+C
5. After termination, check out the `hobbyking_products.csv` file for the most current database.

## Note
Components within these scrapers and the populated database can be repurposed to scrape other relevant websites as well.

## Contributors
- Lavrenti Mikaelyan (mikaelya@usc.edu)
- Allyson Shen (asshen@usc.edu)
- Abhi Singh (asingh17@usc.edu)

