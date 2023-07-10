# Python built-in modules for OS interactions, JSON handling, normalizing text and logging
import os
import json
import logging
import unicodedata

# Selenium is a web driver used to automate browser actions
from selenium import webdriver

# Importing Firefox specific options and Proxy handling from Selenium
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.common.proxy import Proxy, ProxyType

# dotenv is used for environment variable management
from dotenv import load_dotenv

# Additional Selenium utilities for waiting for page to load and expected conditions
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

# tqdm is used for progress bar
from tqdm import tqdm

# Setting the logging level to INFO
logging.basicConfig(level=logging.INFO)

# Loading environment variables from the .env file
load_dotenv()

# Fetching environment variables
PROXY = os.getenv("PROXY")
INPUT_URL = os.getenv("INPUT_URL")
OUTPUT_FILE = os.getenv("OUTPUT_FILE")

# Setting Firefox options for headless browsing
options = FirefoxOptions()
options.add_argument('-headless')

# Setting up proxy configurations for browsing
proxy = Proxy()
proxy.proxy_type = ProxyType.MANUAL
proxy.http_proxy = PROXY
proxy.ssl_proxy = PROXY

# Define normalize_text function
# def normalize_text(text):
#         text = unicodedata.normalize('NFKD', text)  # normalize text
#         text = text.encode('ascii', 'ignore')  # encode to ascii and ignore errors
#         text = text.decode('utf-8', 'ignore')  # decode to utf-8
#         return text
def normalize_text(text):
    text = unicodedata.normalize('NFKD', text)  # normalize text
    text = text.encode('ascii', 'ignore')  # encode to ascii and ignore errors
    text = text.decode('utf-8', 'ignore')  # decode to utf-8
    return text



# Scraper class encapsulates all the scraping operations
class Scraper:
    def __init__(self, url, proxy):
        # Initializing webdriver with given options and proxy, and navigating to the url
        self.driver = webdriver.Firefox(options=options, proxy=proxy)
        self.driver.get(url)
        
        # Set of seen quotes to avoid duplicate scraping
        self.seen_quotes = set()

    # Method to get quotes from the page
    def get_quotes(self):
        # Wait until the page has fully loaded the 'quote' class elements
        WebDriverWait(self.driver, 20).until(
            EC.presence_of_element_located((By.CLASS_NAME, "quote"))
        )
        # Get all 'quote' class elements
        quote_elements = self.driver.find_elements_by_class_name('quote')
        quotes = []
        # Iterate through each quote element
        for quote in quote_elements:
            # Get the text and author elements
            text = quote.find_element_by_class_name('text').text
            text = normalize_text(text)
            text = text.replace('“', '').replace('”', '')
            author = quote.find_element_by_class_name('author').text
            author = normalize_text(author)
            # Get the tags associated with the quote
            tag_elements = quote.find_elements_by_class_name('tag')
            tags = [tag.text for tag in tag_elements]
            # Create a dictionary of the quote information
            quote_dict = {'text': text, 'by': author, 'tags': tags}
            # Convert to JSON string for easy set checking
            quote_json = json.dumps(quote_dict, sort_keys=True)
            # If the quote is not in the seen_quotes set, add it and append to list
            if quote_json not in self.seen_quotes:
                self.seen_quotes.add(quote_json)
                quotes.append(quote_dict)
        return quotes

    # Method to navigate to the next page
    def go_to_next_page(self):
        try:
            # Try to find the 'next' button
            next_button = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, '.next a')))
        except Exception as e:
            # If there's no 'next' button, print a message and return False
            print("Reached the last page.")
            return False
        # If there is a 'next' button, scroll to it, click it, and return True
        self.driver.execute_script("arguments[0].scrollIntoView();", next_button)
        next_button.click()
        return True

    # Method to close the browser once scraping is done
    def close_browser(self):
        self.driver.quit()

   
    

# Main function where the program execution begins
def main():
    # Getting environment variables
    url = os.getenv('INPUT_URL')
    proxy = os.getenv('PROXY')
    output_file = os.getenv('OUTPUT_FILE')

    # Creating scraper instance
    scraper = Scraper(url, proxy)

    # Initialize tqdm for progress bar
    with tqdm(total=None, unit='page') as pbar:
        while True:  # Keep repeating the process until the 'next' button is not found
            quotes = scraper.get_quotes()
            # Write scraped quotes to file
            with open(output_file, 'a') as f:
                for quote in quotes:
                    f.write(json.dumps(quote) + '\n')
            # If there's no 'next' button, break the loop
            if not scraper.go_to_next_page():
                break
            # Update the progress bar
            pbar.update()
    # Close the browser
    scraper.close_browser()

# Ensuring main function is called when script is run directly
if __name__ == "__main__":
    main()