import os
import json
import glob
import csv

import requests

class DownloadImages:
    def __init__(self, brand):
        self.brand = brand
        self.images = []

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
                    for variant in product.get("variants", []):
                        image_url = variant.get("image")
                        variant_id = variant.get("variant_id")
                        product_info = (image_id, product_id, variant_id, category, price, currency, image_url, product_url, self.brand)
                        self.images.append(product_info)
                        image_id += 1
        
        os.makedirs(f'data/images/{self.brand}', exist_ok=True)
        self._write_to_csv(f'data/images/{self.brand}/image_data.csv')

    def _write_to_csv(self, output_path):
        print("\nWriting image data to CSV file...")
        with open(output_path, 'w', newline='', encoding='utf-8') as csvfile:
            csvwriter = csv.writer(csvfile)
            csvwriter.writerow(['image_id', 'product_id', 'variant_id', 'category', 'price', 'image_url', 'brand', 'product_url', 'currency'])
            csvwriter.writerows(self.images)

        print(f"\nSaved {len(self.images)} rows to {output_path}")

    def download_images(self):
        print("\nStarting image download...")
        for image in self.images:
            image_id, product_id, variant_id, category, price, currency, image_url, product_url, brand = image
            image_extension = os.path.splitext(image_url)[1]
            image_filename = f"{image_id}_{product_id}_{variant_id}{image_extension}"
            image_path = os.path.join(f'data/images/{self.brand}/product-images', image_filename)

            try:
                response = requests.get(image_url, stream=True)
                if response.status_code == 200:
                    with open(image_path, 'wb') as img_file:
                        for chunk in response.iter_content(1024):
                            img_file.write(chunk)
                    print(f"Downloaded image: {image_filename}")
                else:
                    print(f"Failed to download image {image_filename}: Status code {response.status_code}")
            except Exception as e:
                print(f"Exception occurred while downloading image {image_filename}: {e}")

        print("\nImage download completed.")

if __name__ == '__main__':
    product_brands = glob.glob('data/products/*')
    for brand_path in product_brands:
        print(f"\nProcessing brand directory: {brand_path}")
        brand = os.path.basename(brand_path)
        downloader = DownloadImages(brand)
        downloader.save_image_data()