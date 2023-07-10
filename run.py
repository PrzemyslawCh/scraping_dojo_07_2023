import os
import json
import time
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.proxy import Proxy, ProxyType
from dotenv import load_dotenv
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

# Load .env file
load_dotenv()

PROXY = os.getenv("PROXY")
INPUT_URL = os.getenv("INPUT_URL")
OUTPUT_FILE = os.getenv("OUTPUT_FILE")

# Create Firefox options
options = Options()
options.headless = True

# Set up proxy
proxy_argument = Proxy({
    'proxyType': ProxyType.MANUAL,
    'httpProxy': PROXY,
    'ftpProxy': PROXY,
    'sslProxy': PROXY,
})

class Scraper:
    def __init__(self, url, proxy):
        self.driver = webdriver.Firefox(options=options, proxy=proxy)
        self.driver.get(url)
        self.seen_quotes = set()

    def get_quotes(self):
        WebDriverWait(self.driver, 20).until(
            EC.presence_of_element_located((By.CLASS_NAME, "quote"))
        )
        quote_elements = self.driver.find_elements_by_class_name('quote')
        quotes = []
        for quote in quote_elements:
            text = quote.find_element_by_class_name('text').text
            author = quote.find_element_by_class_name('author').text
            tag_elements = quote.find_elements_by_class_name('tag')
            tags = [tag.text for tag in tag_elements]
            quote_dict = {'text': text, 'by': author, 'tags': tags}

            # Convert the quote dictionary to a JSON string to be able to add it to a set
            quote_json = json.dumps(quote_dict, sort_keys=True)
            if quote_json not in self.seen_quotes:
                self.seen_quotes.add(quote_json)
                quotes.append(quote_dict)
        return quotes

    def go_to_next_page(self):
        try:
            next_button = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, '.next a')))
            self.driver.execute_script("arguments[0].scrollIntoView();", next_button)
            next_button.click()
            return True
        except Exception as e:
            print(str(e))
            return False

    def close_browser(self):
        self.driver.quit()
    
def main():
    url = os.getenv('INPUT_URL')
    proxy = os.getenv('PROXY')
    output_file = os.getenv('OUTPUT_FILE')

    scraper = Scraper(url, proxy)

    while True:  # keep repeating the process until the 'next' button is not found
        quotes = scraper.get_quotes()

        with open(output_file, 'a') as f:
            for quote in quotes:
                f.write(json.dumps(quote) + '\n')

        if not scraper.go_to_next_page():  # try to go to the next page
            break  # if there's no 'next' button, exit the loop

    scraper.close_browser()


if __name__ == "__main__":
    main()
