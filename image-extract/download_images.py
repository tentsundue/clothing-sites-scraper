import os
import json
import glob
import csv
import time, random
from PIL import Image

import requests

class DownloadImages:
    def __init__(self, brand):
        self.brand = brand
        self.images = []
        self.variants_count = {"tops": 0, "bottoms": 0, "outerwear": 0, "innerwear": 0}

    def save_image_data(self):
        input_files = glob.glob(f'data/products/{self.brand}/*.json')
        image_id = 1
        for file_path in input_files:
            print(f"\nProcessing file: {file_path}")
            with open(file_path, 'r', encoding='utf-8') as f:
                products = json.load(f)
                print(f"Found {len(products)} products in {file_path}")
                for product in products:
                    price = product.get("price")
                    product_id = product.get("id")
                    category = product.get("category")
                    product_url = product.get("product_url")
                    currency = product.get("currency")
                    gender = product.get("gender")
                    rating = product.get("rating_avg")
                    rating_count = product.get("rating_count")
                    for variant in product.get("variants", []):
                        image_url = variant.get("image")
                        variant_id = variant.get("variant_id")
                        product_info = (image_id, product_id, variant_id, gender, category, price, currency, image_url, product_url, self.brand, rating, rating_count)
                        self.images.append(product_info)
                        self.variants_count[category] += 1
                        image_id += 1
        
        os.makedirs(f'data/images/{self.brand}', exist_ok=True)
        self._write_to_csv(f'data/images/{self.brand}/image_data.csv')

    def _write_to_csv(self, output_path):
        print("\nWriting image data to CSV file...")
        with open(output_path, 'w', newline='', encoding='utf-8') as csvfile:
            csvwriter = csv.writer(csvfile)
            csvwriter.writerow(['image_id', 'product_id', 'variant_id', 'gender', 'category', 'price', 'currency', 'image_url', 'product_url', 'brand', 'rating', 'rating_count'])
            csvwriter.writerows(self.images)

        print(f"\nSaved {len(self.images)} rows to {output_path}")

    def download_images(self):
        print("\nStarting image downloads...")
        failures = []
        for image in self.images:
            image_id, product_id, variant_id, gender, category, price, currency, image_url, product_url, brand, rating, rating_count = image
            image_extension = os.path.splitext(image_url)[1] or '.jpg'  # Default to .jpg if no extension found
            image_filename = f"{image_id}_{product_id}_{variant_id}{image_extension}"
            os.makedirs(f'data/images/{brand}/product-images', exist_ok=True)
            image_path = os.path.join(f'data/images/{brand}/product-images', image_filename)

            # Skip if already downloaded
            if os.path.exists(image_path):
                continue

            try:
                response = requests.get(image_url, stream=True, timeout=10)

                if response.status_code != 200:
                    failures.append((image_url, response.status_code))
                    continue
                
                with open(image_path, 'wb') as img_file:
                    for chunk in response.iter_content(1024):
                        img_file.write(chunk)
                
                # Validate AFTER saving, re-open for conversion
                try:
                    with Image.open(image_path) as img:
                        img.verify()

                    with Image.open(image_path) as img:
                        img = img.convert("RGB")
                        img.save(image_path)

                except Exception as verify_error:
                    print(f"Invalid image removed: {image_filename} -> {verify_error}")
                    os.remove(image_path)
                    failures.append((image_url, "Invalid image"))

                print(f"== Downloaded image: {image_filename} ==")

                time.sleep(random.uniform(0.5, 1.5)) # Don't overwhelm the server with requests and get locked out

            except Exception as e:
                failures.append((image_url, str(e)))

        print("\nImage downloads completed.")

        if failures:
            print(f"\nFailed to download {len(failures)} images.")
            for failure in failures:
                print(f"Failed URL: {failure[0]}, With Failure: {failure[1]}")

    def check_variant_counts(self):
        with open(f'data/images/{self.brand}/sanity_check.txt', 'w', encoding='utf-8') as f:
            f.write("Category, Variant Count\n")
            for category, count in self.variants_count.items():
                f.write(f"{category}, {count}\n")
            
            unique_products = set()
            for image in self.images:
                product_id = image[1]
                unique_products.add(product_id)

            f.write("-----------------------------------------\n")
            f.write(f"Total Unique Products: {len(unique_products)}\n")
            f.write(f"Total Variants across all categories: {sum(self.variants_count.values())}\n")
            f.write(f"Total Images to Download: {len(self.images)}\n")
        
if __name__ == '__main__':
    product_brands = glob.glob('data/products/*')
    for brand_path in product_brands:
        print(f"\nProcessing brand directory: {brand_path}")
        brand = os.path.basename(brand_path)
        downloader = DownloadImages(brand)
        downloader.save_image_data()
        # downloader.download_images()
        downloader.check_variant_counts()