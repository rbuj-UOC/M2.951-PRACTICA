import time
from selenium import webdriver
from selenium.webdriver.common.by import By


class MeteoScraper:
    def __init__(self):
        self.base_url = "https://www.meteo.cat"
        self.list_url = self.base_url + "/observacions/llistat-xema"
        self.data = []

    def __get_station_list(self, driver) -> tuple[list[str], list[str]]:
        # Navigate to the list URL
        driver.get(self.list_url)
        # Wait five seconds
        time.sleep(5)
        # Get station table
        table = driver.find_element(By.ID, "llistaEstacions")
        # Get table headings, excluding the last one (status)
        table_headings = [
            element.text for element in table.find_elements(By.XPATH, ".//th")[:-1]
        ]
        # Add link heading
        table_headings.append("Enllaç")
        # Get table data and filter out non-operational stations
        table_values = []
        for row in table.find_elements(By.XPATH, "./tbody/tr"):
            # Get all cells in the row
            cells = [element for element in row.find_elements(By.XPATH, "./td")]
            # Filter out non-operational stations
            if cells[-1].text != "Operativa":
                continue
            # Get station data, excluding the last one (status)
            station_data = [cell.text for cell in cells[:-1]]
            # Get station link
            station_data.append(
                cells[2].find_element(By.TAG_NAME, "a").get_attribute("href")
            )
            table_values.append(station_data)
        return table_headings, table_values

    def scrape(self):
        # Implementation of the scrape method
        print("\tScraping data...")
        try:
            driver = webdriver.Chrome()
            # Get the station list
            station_headings, station_info = self.__get_station_list(driver)
            print(f"\tFound {len(station_info)} operational stations.")
            # Print the headings
            print("\tHeadings:", station_headings)
            # Print the first five stations
            for station in station_info[:5]:
                print(f"\tStation: {station}")
            # Quit the driver
            driver.quit()
        except Exception as e:
            print(f"Error occurred while scraping: {e}")

    def data2csv(self, filename):
        # Implementation of the data2csv method
        print(f"Saving data to {filename}...")
        pass
