class MeteoScraper:
    def __init__(self):
        self.base_url = "https://www.meteo.cat"
        self.list_url = self.base_url + "/observacions/llistat-xema"
        self.data = []

    def scrape(self):
        # Implementation of the scrape method
        print("Scraping data...")
        pass

    def data2csv(self, filename):
        # Implementation of the data2csv method
        print(f"Saving data to {filename}...")
        pass
