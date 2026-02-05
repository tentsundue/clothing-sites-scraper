import json
import os
import requests
from bs4 import BeautifulSoup, Comment
from collections import defaultdict
from utils.robotCheck import RobotCheck


BRAND = "UNIQLO"
URLS = {"tops": ["https://www.uniqlo.com/us/en/men/tops"],
        "bottoms": ["https://www.uniqlo.com/us/en/women/bottoms"]
       }
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Safari/537.36"
HEADERS = {
            "User-Agent": USER_AGENT
          }
ROBOT_CACHE = {}


'''
Helper Function that checks if the given URL path is allowed based on the disallowed paths from robots.txt
'''
def is_allowed(parsed_url, disallowed):
    for path in disallowed:
        if parsed_url.path.startswith(path):
            return False
    
    return True


'''
Checks all URLs in the URLS dictionary against their robots.txt files
and returns a dictionary of valid URLs categorized by their category.
All valid URLs are those that are not disallowed by the robots.txt rules.
'''
def find_valid_urls():
    valid_urls = defaultdict(list)
    for category, urls in URLS.items():
        for url in urls:
            robotChecker = RobotCheck(url)
            parsed_url = robotChecker.get_parsed_url()
            domain = robotChecker.get_domain_url()

            disallowed_paths = []
            if domain in ROBOT_CACHE:
                disallowed_paths = ROBOT_CACHE[domain]
            else:
                disallowed_paths, _ = robotChecker.retrieveRobotsContent()
                ROBOT_CACHE[domain] = disallowed_paths
            
            if is_allowed(parsed_url, disallowed_paths):
                    valid_urls[category].append(url)
    
    return valid_urls


'''
Scrapes product data from the valid URLs and saves them into JSON files categorized by product type.
'''
def scraper(urls: defaultdict(list)): # type: ignore
    print("=" * 30)
    print("STARTING SCRAPE...")
    print("=" * 30)

    for category, url_list in urls.items():
        print("=" * 50)
        print("NOW SCRAPING CATEGORY:", category)
        print("=" * 50)

        for url in url_list:
            response = requests.get(url, headers=HEADERS)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, "html.parser")

            print(f"\nRETRIEVED SOUP OBJECT FOR URL: {url}")
     

            # removes all comment from the html file
            for comment in soup.find_all(string = lambda string: isinstance(string, Comment)):
                comment.extract()
            
            script = soup.find(
                "script",
                string=lambda t: t and "__PRELOADED_STATE__" in t
            )
            if not script:
                raise RuntimeError("PRELOADED_STATE script not found")
            
            raw = script.string

            start = raw.find("window.__PRELOADED_STATE__")
            start = raw.find("=", start) + 1
            end = raw.rfind("}")

            json_text = raw[start:end+1].strip()

            data = json.loads(json_text)
            products_raw = data["entity"]["searchEntity"]

            parse_products(products_raw, category)


'''
Helper Function to parse raw product data into structured format (SEE README for structure) and save to JSON.
USED IN: scraper()
'''
def parse_products(products_raw, category):
        products_parsed = []

        for productContainer in products_raw.values():
            product_info = productContainer["product"]
            product_base = {}

            product_id = product_info['productId']
            product_priceGroup = product_info['priceGroup']
            product_main_images = product_info['images']['main']

            product_base["id"] = f"uniqlo_{product_id}"
            product_base["brand"] = BRAND
            product_base["name"] = product_info["name"]
            product_base["category"] = category
            product_base["gender"] = product_info["genderCategory"]
            product_base["price"] = product_info["prices"]["base"]["value"]
            product_base["currency"] = product_info["prices"]["base"]["currency"]["code"]
            product_base["product_url"] = f"https://www.uniqlo.com/us/en/products/{product_id}/{product_priceGroup}"
            product_base["rating_avg"] = product_info["rating"]["average"]
            product_base["rating_count"] = product_info["rating"]["count"]

            variants = []
            for color in product_info.get("colors", []):
                displayCode = color["displayCode"]
                variant = {
                    "variant_id": color["code"],
                    "color": color["name"],
                    "sizes": [size["name"] for size in color.get("sizes", [])],
                    "image": product_main_images[displayCode]["image"]
                }
                variants.append(variant)
            
            product_base["variants"] = variants
            products_parsed.append(product_base)
        
        write_to_json(products_parsed, category)


'''
Helper Function to write parsed product data to a JSON file. 
Each set of files is stored in a directory named after the brand. (eg. products/UNIQLO/tops.json)
USED IN: parse_products()
'''
def write_to_json(products_parsed, category):
        os.makedirs(f'data/products/{BRAND}', exist_ok=True)
        print("\nSaving data to JSON file...")

        with open(f'data/products/{BRAND}/{category}.json', 'w', encoding='utf-8') as f:
            json.dump(products_parsed, f, indent=4)

        print(f"\nData saved to data/products/{BRAND}/{category}.json")
        print("=" * 30)



if __name__ == '__main__':
    products = scraper(find_valid_urls())

