import time
from selenium import webdriver
from selenium.webdriver.common.by import By


class MeteoScraper:
    def __init__(self):
        self.base_url = "https://www.meteo.cat"
        self.list_url = self.base_url + "/observacions/llistat-xema"
        self.data = []

    def __get_station_list(self, driver) -> tuple[list[str], list[list]]:
        # Navigate to the list URL
        driver.get(self.list_url)
        # wait five seconds
        time.sleep(5)
        # Get station table
        table = driver.find_element(By.ID, "llistaEstacions")
        # Get table headings
        table_headings = [
            element.text for element in table.find_elements(By.XPATH, ".//th")
        ]
        # Get table data and filter out non-operational stations
        table_values = []
        for row in table.find_elements(By.XPATH, "./tbody/tr"):
            cells = [element for element in row.find_elements(By.XPATH, "./td")]
            if cells[-1].text != "Operativa":
                continue
            table_values.append(cells)
        return table_headings, table_values

    def scrape(self):
        # Implementation of the scrape method
        print("\tScraping data...")
        try:
            driver = webdriver.Chrome()
            # get the station list
            table_headings, table_values = self.__get_station_list(driver)
            print(f"\tFound {len(table_values)} operational stations.")
            # quit the driver
            driver.quit()
        except Exception as e:
            print(f"Error occurred while scraping: {e}")

    def data2csv(self, filename):
        # Implementation of the data2csv method
        print(f"Saving data to {filename}...")
        pass
