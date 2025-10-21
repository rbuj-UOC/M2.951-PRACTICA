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
        self.data_url = self.base_url + "/observacions/xema/dades"
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

    def __navigate_to_station_data_page(
        self, driver: webdriver.Chrome, timeout: int, delay: int
    ) -> None:
        """
        Navigate to the station data page.
        Args:
            driver: The selenium webdriver instance.
            timeout: The maximum time to wait for the page to load.
            delay: The time to wait after page load.
        """
        driver.set_page_load_timeout(timeout)
        try:
            driver.get(self.data_url)
        except TimeoutException:
            raise Exception("Station data page did not load in time")
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
        """
        Get the station list table from the page.
        Args:
            driver: The selenium webdriver instance.
        Returns:
            The selenium web element representing the station table.
        """
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
            table_headings.append("Estació")
            table_headings.append("Codi")
        except Exception:
            raise Exception("Error occurred while getting table headings")
        # Get table data
        table_data = []
        try:
            for row in table.find_elements(By.XPATH, "./tbody/tr"):
                # Get all cells in the row
                cells = [cell.text for cell in row.find_elements(By.XPATH, "./td")]
                # Get station name and code from third cell
                station_full_name = cells[2].strip()
                station_name = station_full_name[0:-5]
                station_code = station_full_name[-3:-1]
                cells.append(station_name)
                cells.append(station_code)
                # Append station data to table data
                table_data.append(cells)
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

    def __get_day_list(self, num_days: int) -> list[datetime]:
        """
        Get the list of days for which to scrape data.
        Args:
            num_days: The number of days to scrape.
        Returns:
            A list of dates as strings.
        """
        today = datetime.now()
        return [today - timedelta(days=i) for i in range(num_days)]

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
            print(f"\tFound {len(station_info)} stations.")
            # Get tomorrow's date
            tomorrow = datetime.now() + timedelta(days=1)
            # Navigate to station data page
            self.__navigate_to_station_data_page(driver, timeout=10, delay=2)
            # Get station data for each station
            for station in station_info:
                # Get station name, code, start date, and end date
                station_code = station[-1]
                station_name = station[-2]
                station_status = station[-3]
                if station_status == "Operativa":
                    end_date = tomorrow
                elif station_status == "Desmantellada":
                    end_date = datetime.strptime(station[-4], "%d.%m.%Y")
                else:
                    raise Exception(f"Unknown station status: {station_status}")
                start_date = datetime.strptime(station[-5], "%d.%m.%Y")
                # Print station name and code
                print(f'\tScraping data for station: "{station_name}" [{station_code}]')
                # Get station data for each day
                for day in self.__get_day_list(num_days):
                    # if day is greater than end_date or less than start_date, skip
                    if day > end_date or day < start_date:
                        continue
                    print(f"\t\tDate: {day.strftime('%d.%m.%Y')}")
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
