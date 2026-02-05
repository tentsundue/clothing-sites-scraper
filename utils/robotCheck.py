import re
import requests
import time
from urllib.parse import urlparse

USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Safari/537.36"

class RobotCheck:
    def __init__(self, url):
        self.parsed_url = urlparse(url)
        self.domain_url = self.retrieveRootDomain()
        self.robot_url = self.domain_url + "/robots.txt"


    def retrieveRootDomain(self):
        return self.parsed_url.scheme + "://" + self.parsed_url.netloc


    def retrieveRobotsContent(self):
        print("=" * 30)
        print("Starting robots analysis for:", self.domain_url)
        start = time.time()

        try:
            response = requests.get(self.robot_url, 
                                    timeout=(3,5),
                                    headers={"User-Agent": USER_AGENT}
                                    )
        except Exception as e:
            print(f"Exception: \n\t{e}")
            # Note to self: Most likely SSLError, we aren't allowed/couldn't access robots.txt of url
            return [], []
        
        print("\nResponse retrieved...")
        main_robot_txt = response.text
        disallowed_paths = re.findall(r"Disallow:\s*(.*)", main_robot_txt)
        sitemaps = re.findall(r"Sitemap:\s*(.*)", main_robot_txt)

        # clean up whitespace
        disallowed_paths = [path.strip() for path in disallowed_paths]
        sitemaps = [url.strip() for url in sitemaps]

        end = time.time()
        print(f"\nFinshed analyzing robots.txt in {end - start:.2f}s")

        return disallowed_paths, sitemaps


    def get_robot_url(self):
        return self.robot_url


    def get_domain_url(self):
        return self.domain_url
    
    
    def get_parsed_url(self):
        return self.parsed_url

r = RobotCheck("https://www.uniqlo.com")
print(r.get_domain_url())
