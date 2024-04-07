from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import csv
import os
import time
from utils import inputfolder, outputfolder
from concurrent.futures import ThreadPoolExecutor
import threading

class ProductScraper:
    def __init__(self, input_file, output_folder):
        self.input_file = input_file
        self.output_folder = output_folder
        self.lock = threading.Lock()
        self.header = ['Product Name', 'Product ID', 'Product Description', 'Product Brand', 'Product URL', 'Product Size', 'Product Price', 'Product Availability', 'Grade', 'API Family', 'Agency', 'Manufacturer/Tradename', 'Application', 'Format', 'Storage Temp', 'Smiles String']
        self.scraped_urls = set()

    def scrape(self):
        with open(self.input_file, 'r') as file:
            urls = file.read().splitlines()

        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(self.scrape_product, url) for url in urls]

            all_data = []
            for future in futures:
                data = future.result()
                if data:
                    all_data.append(data)
                    with self.lock:
                        self.scraped_urls.add(data[4]) # Assuming URL is at index 4
                # if len(self.scraped_urls) >= 2000:
                #     break

        # Remove scraped URLs from the input file
        remaining_urls = [url for url in urls if url not in self.scraped_urls]
        with open(self.input_file, 'w') as file:
            file.write('\n'.join(remaining_urls))

        csv_name = os.path.splitext(os.path.basename(self.input_file))[0] + '.csv'
        csv_file_path = os.path.join(self.output_folder, csv_name)

        with open(csv_file_path, 'w', newline='', encoding='utf-8-sig') as csv_file:
            writer = csv.writer(csv_file)
            writer.writerow(self.header)
            writer.writerows(all_data)

    def scrape_product(self, url):
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--disable-extensions")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-browser-side-navigation")
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_argument("--disable-features=VizDisplayCompositor")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--mute-audio")
        chrome_options.add_argument("--disable-setuid-sandbox")
        chrome_options.add_argument("--disable-logging")
        chrome_options.add_argument("--log-level=3")
        chrome_options.add_argument("--disable-software-rasterizer")
        chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
        chrome_options.add_argument("--disable-web-security")
        chrome_options.add_argument("--allow-running-insecure-content")

        driver = webdriver.Chrome(options=chrome_options)
        driver.get(url)
        time.sleep(2)
        html_content = driver.page_source
        soup = BeautifulSoup(html_content, 'lxml')

        data = []

        # Scraping logic goes here
        try:
            product_name = soup.find('span', id="product-name").text
            data.append(product_name)
        except:
            data.append("")
        try:
            product_id = soup.find('p', id="product-number").text
            data.append(product_id)
        except:
            data.append("")
        try:
            product_description = soup.find('span', id="product-description").text
            data.append(product_description)
        except:
            data.append("")
        try:
            product_brand = url.split("/")[-2]
            data.append(product_brand)
        except:
            data.append("")
        try:
            product_url = url
            data.append(product_url)
        except:
            data.append("")

        try:
            size_price_info = soup.find(lambda tag: tag.name == 'h3' and 'Select a Size' in tag.text.strip())
            size_price = size_price_info.find_next('span', class_="MuiChip-label")
            size_value = size_price.find('span').text.strip()
            price_value = size_price.find('div').text.strip()
            data.append(size_value)
        except:
            data.append("")
        try:
            size_price_info = soup.find(lambda tag: tag.name == 'h3' and 'Select a Size' in tag.text.strip())
            size_price = size_price_info.find_next('span', class_="MuiChip-label")
            size_value = size_price.find('span').text.strip()
            price_value = size_price.find('div').text.strip()
            data.append(price_value)
        except:
            data.append("")
        try:
            availability_info = soup.find(lambda tag: tag.name == 'h6' and 'Availability' in tag.text.strip())
            availab_infos = availability_info.find_next('p')
            availab_info = ' '.join([text for text in availab_infos.stripped_strings if text != 'Details']) # The stripped_strings attribute in BeautifulSoup is a generator that provides an iterator over the strings inside a tag,
            data.append(availab_info)
        except:
            data.append("")
        try:
            divs = soup.find('h3', string='grade')
            if divs:
                value_div = divs.find_next('p')
                value = value_div.text.strip()
                data.append(value)
            else:
                data.append("")
        except:
            value = ""
            data.append(value)
        try:
            divs1 = soup.find('h3', string='API family')
            if divs1:
                value_div1 = divs1.find_next('p')
                value1 = value_div1.text.strip()
                data.append(value1)
            else:
                data.append("")
        except:
            value1 = ""
            data.append(value1)
        try:
            divs2 = soup.find('h3', string="Agency")
            if divs2:
                value_div2 = divs2.find_next('p')
                value2 = value_div2.text.strip()
                data.append(value2)
            else:
                data.append("")
        except:
            value2 = ""
            data.append(value2)
        try:
            divs3 = soup.find('h3', string='manufacturer/tradename')
            if divs3:
                value_div3 = divs3.find_next('p')
                value3 = value_div3.text.strip()
                data.append(value3)
            else:
                data.append("")
        except:
            value3 = ""
            data.append(value3)
        try:
            divs4 = soup.find('h3', string='application(s)')
            if divs4:
                value_div4 = divs4.find_next('p')
                value4 = value_div4.text.strip()
                data.append(value4)
            else:
                data.append("")
        except:
            value4 = ""
            data.append(value4)
        try:
            divs5 = soup.find('h3', string='format')
            if divs5:
                value_div5 = divs5.find_next('p')
                value5 = value_div5.text.strip()
                data.append(value5)
            else:
                data.append("")
        except:
            value5 = ""
            data.append(value5)
        try:
            divs6 = soup.find('h3', string='storage temp.')
            if divs6:
                value_div6 = divs6.find_next('p')
                value6 = value_div6.text.strip()
                data.append(value6)
            else:
                data.append("")
        except:
            value6 = ""
            data.append(value6)

        try:
            divs7 = soup.find('h3', string='SMILES string')
            if divs7:
                value_div7 = divs7.find_next('p')
                value7 = value_div7.text.strip()
                data.append(value7)
            else:
                data.append("")
        except:
            value7 = ""
            data.append(value7)
        #driver.quit()

        return data

if __name__ == "__main__":
    file_name = "pharmacopeia-and-metrological-institutes-standards.txt"
    input_file_path = os.path.join(inputfolder, file_name)

    output_folder_path = outputfolder

    scraper = ProductScraper(input_file_path, output_folder_path)
    scraper.scrape()
