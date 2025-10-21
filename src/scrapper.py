import time
from datetime import datetime, timedelta
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

    def __navigate_to_station_list_page(
        self, driver: webdriver.Chrome, timeout: int, delay: int
    ) -> None:
        """
        Navigate to the station list page.
        Args:
            driver: The selenium webdriver instance.
            timeout: The maximum time to wait for the page to load.
            delay: The time to wait after page load.
        """
        driver.set_page_load_timeout(timeout)
        try:
            driver.get(self.list_url)
        except TimeoutException:
            raise Exception("Station list page did not load in time")
        # Wait for a short delay
        time.sleep(delay)

    def __reject_cookies(self, driver: webdriver.Chrome, delay: int) -> None:
        """
        Reject cookies on the website.
        Args:
            driver: The selenium webdriver instance.
            delay: The time to wait after rejecting cookies.
        """
        try:
            # Find and click the reject cookies button
            reject_button = driver.find_element(
                By.XPATH,
                "//div[@id='missatge_cookie']//button[@id='rebutjar']",
            )
            reject_button.click()
            time.sleep(delay)
        except NoSuchElementException:
            raise Exception("Could not reject cookies. Element not found.")

    def __get_station_list_table(self, driver: webdriver.Chrome):
        try:
            return driver.find_element(By.ID, "llistaEstacions")
        except NoSuchElementException:
            raise Exception("Station list table not found")

    def __get_headings_and_data_from_station_list_table(
        self, table
    ) -> tuple[list[str], list[str]]:
        """
        Get the headings and data from the station table.
        Args:
            table: The selenium web element representing the station table.
        Returns:
            A tuple containing the table headings and the station data.
        """
        # Get table headings, excluding the last heading (status)
        try:
            table_headings = [
                element.text for element in table.find_elements(By.XPATH, ".//th")[:-1]
            ]
            # Add link heading
            table_headings.append("Enllaç")
        except Exception:
            raise Exception("Error occurred while getting table headings")
        # Get table data
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

    def __get_station_lists(self, driver) -> tuple[list[str], list[str]]:
        """
        Get the list of meteorological stations from the website.
        Args:
            driver: The selenium webdriver instance.
        Returns:
            A tuple containing the table headings and the station data.
        """
        # Navigate to the list URL
        self.__navigate_to_station_list_page(driver, timeout=10, delay=2)
        # Reject cookies
        self.__reject_cookies(driver, delay=2)
        # Get station list table
        table = self.__get_station_list_table(driver)
        # Return headings and data from station list table
        return self.__get_headings_and_data_from_station_list_table(table)

    def __get_day_list(self, num_days: int) -> list[str]:
        """
        Get the list of days for which to scrape data.
        Args:
            num_days: The number of days to scrape.
        Returns:
            A list of dates as strings.
        """
        today = datetime.now()
        return [
            (today - timedelta(days=i)).strftime("%d.%m.%Y") for i in range(num_days)
        ]

    def scrape(self, num_days: int) -> None:
        """
        Scrape meteorological data from the website.
        """
        # Implementation of the scrape method
        print("\tScraping data...")
        try:
            # Initialize the webdriver
            driver = webdriver.Chrome()
            # Get the station list
            station_headings, station_info = self.__get_station_lists(driver)
            print(f"\tFound {len(station_info)} operational stations.")
            # Get station data for each station
            for station in station_info:
                station_link = station[-1].strip()
                station_full_name = station[2].strip()
                station_name = station_full_name[0:-5]
                station_code = station_link[-2:]
                print(
                    f'\tScraping data for station: "{station_name}" [{station_code}] ({station_link})'
                )
                for day in self.__get_day_list(num_days):
                    print(f"\t\tDate: {day}")
                    # ToDo: Implement data scraping for each station and day
            # Quit the driver
            driver.quit()
        except Exception as e:
            raise Exception(f"Error occurred while scraping: {e}")

    def data2csv(self, output_file: str) -> None:
        """
        Save the scraped data to a CSV file.
        """
        # Implementation of the data2csv method
        print(f"Saving data to {output_file}...")
        pass
