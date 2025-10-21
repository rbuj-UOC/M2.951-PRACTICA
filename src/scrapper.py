import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException, NoSuchElementException


class MeteoScraper:
    def __init__(self):
        """
        Initialize the MeteoScraper with base URL and data storage.
        """
        self.base_url = "https://www.meteo.cat"
        self.list_url = self.base_url + "/observacions/llistat-xema"
        self.data = []

    def __reject_cookies(self, driver: webdriver.Chrome) -> None:
        """
        Reject cookies on the website.
        Args:
            driver: The selenium webdriver instance.
        """
        try:
            # Find and click the reject cookies button
            reject_button = driver.find_element(
                By.XPATH,
                "//div[@id='missatge_cookie']//button[@id='rebutjar']",
            )
            reject_button.click()
            # Wait for two seconds
            time.sleep(2)
        except NoSuchElementException:
            raise Exception("Could not reject cookies. Element not found.")

    def __get_station_list(self, driver) -> tuple[list[str], list[str]]:
        """
        Get the list of meteorological stations from the website.
        Args:
            driver: The selenium webdriver instance.
        Returns:
            A tuple containing the table headings and the station data.
        """
        # Navigate to the list URL
        driver.set_page_load_timeout(10)
        try:
            driver.get(self.list_url)
        except TimeoutException:
            raise Exception("Station list page did not load in time")
        # Reject cookies
        self.__reject_cookies(driver)
        # Get station table
        try:
            table = driver.find_element(By.ID, "llistaEstacions")
        except NoSuchElementException:
            raise Exception("Station list table not found")
        # Get table headings, excluding the last one (status)
        try:
            table_headings = [
                element.text for element in table.find_elements(By.XPATH, ".//th")[:-1]
            ]
        except Exception:
            raise Exception("Error occurred while getting table headings")
        # Add link heading
        table_headings.append("Enllaç")
        # Get table data and filter out non-operational stations
        table_data = []
        try:
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
                # Append station data to table data
                table_data.append(station_data)
        except Exception as e:
            raise Exception(f"Error occurred while getting table row: {e}")
        return table_headings, table_data

    def scrape(self) -> None:
        """
        Scrape meteorological data from the website.
        """
        # Implementation of the scrape method
        print("\tScraping data...")
        try:
            # Initialize the webdriver
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
            raise Exception(f"Error occurred while scraping: {e}")

    def data2csv(self, filename: str) -> None:
        """
        Save the scraped data to a CSV file.
        """
        # Implementation of the data2csv method
        print(f"Saving data to {filename}...")
        pass
