import time
from selenium import webdriver


class MeteoScraper:
    def __init__(self):
        self.base_url = "https://www.meteo.cat"
        self.list_url = self.base_url + "/observacions/llistat-xema"
        self.data = []

    def scrape(self):
        # Implementation of the scrape method
        print("\tScraping data...")
        try:
            driver = webdriver.Chrome()
            self.driver = webdriver.Chrome()
            # Get and print user agent
            agent = self.driver.execute_script("return navigator.userAgent")
            print(f"User agent: {agent}")
            # Navigate to the list URL
            self.driver.get(self.list_url)
            # wait five seconds
            time.sleep(5)
            # quit the driver
            self.driver.quit()
        except Exception as e:
            print(f"Error occurred while scraping: {e}")

    def data2csv(self, filename):
        # Implementation of the data2csv method
        print(f"Saving data to {filename}...")
        pass
