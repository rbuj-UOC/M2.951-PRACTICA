import time
import pandas as pd
from os import makedirs, path
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
        # Dataset folder path: ../dataset
        self.dataset_folder = path.join(path.dirname(path.dirname(__file__)), "dataset")
        self.data = []

    def __dataframe_to_csv(self, df: pd.DataFrame, output_file: str) -> None:
        """
        Save a DataFrame to a CSV file in dataset folder.
        Args:
            df: The DataFrame to save.
            output_file: The output CSV file name.
        """
        try:
            # Create the dataset folder if not exists
            makedirs(self.dataset_folder, exist_ok=True)
            # Build the full file path
            file_path = path.join(self.dataset_folder, output_file)
            # Save the DataFrame to CSV in dataset folder, overwriting if it exists
            df.to_csv(file_path, index=False, mode="w")
            # Print success message
            print(f"\tDataFrame saved to {file_path}")
        except Exception as e:
            raise Exception(f"Error occurred while saving DataFrame to CSV: {e}")

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

    def __get_station_data(
        self, driver: webdriver.Chrome, station_list: pd.DataFrame, num_days: int
    ) -> None:
        """
        Get the meteorological data for each station.
        Args:
            driver: The selenium webdriver instance.
            station_list: The list of stations as a DataFrame.
            num_days: The number of days to scrape data for.
        """
        try:
            # Get tomorrow's date
            tomorrow = datetime.now() + timedelta(days=1)
            # Navigate to station data page
            self.__navigate_to_station_data_page(driver, timeout=10, delay=2)
            # Get station data for each station
            for i, station in station_list.iterrows():
                # Get station name, code, start date, and end date
                station_full_name = station["Estació [Codi]"]
                station_code = station_full_name[-3:-1]
                station_name = station_full_name[0:-5]
                station_status = station["Estat actual"]
                if station_status == "Operativa":
                    end_date = tomorrow
                elif station_status == "Desmantellada":
                    end_date = datetime.strptime(station["Data baixa"], "%d.%m.%Y")
                else:
                    raise Exception(f"Unknown station status: {station_status}")
                start_date = datetime.strptime(station["Data alta"], "%d.%m.%Y")
                # Print station name and code
                print(f'\tScraping data for station: "{station_name}" [{station_code}]')
                # Get station data for each day
                for day in self.__get_day_list(num_days):
                    # if day is greater than end_date or less than start_date, skip
                    if day > end_date or day < start_date:
                        continue
                    print(f"\t\tDate: {day.strftime('%d.%m.%Y')}")
                    pass  # Implement data scraping for each station and day
        except Exception as e:
            raise Exception(f"Error occurred while getting station data: {e}")

    def __get_station_list(self, driver: webdriver.Chrome) -> pd.DataFrame:
        """
        Get the list of meteorological stations from the website.
        Args:
            driver: The selenium webdriver instance.
        Returns:
            A DataFrame containing the station list.
        """
        # Navigate to the list URL
        self.__navigate_to_station_list_page(driver, timeout=10, delay=2)
        # Reject cookies
        self.__reject_cookies(driver, delay=2)
        # Get station list table from the page
        try:
            table = driver.find_element(By.ID, "llistaEstacions")
            # Get df columns
            headings = [
                element.text for element in table.find_elements(By.XPATH, ".//th")
            ]
            # Get df data
            data = []
            for row in table.find_elements(By.XPATH, "./tbody/tr"):
                # Get all cells in the row
                cells = [cell.text for cell in row.find_elements(By.XPATH, "./td")]
                # Append station data to table data
                data.append(cells)
            # Create DataFrame
            station_list = pd.DataFrame(data, columns=headings)
            # Print number of stations found
            print(f"\tFound {len(station_list)} stations.")
            # save station list to csv
            self.__dataframe_to_csv(station_list, "station_list.csv")
            # Return as DataFrame
            return station_list
        except Exception as e:
            raise Exception(f"Error occurred while getting station list: {e}")

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

    def data2csv(self, output_file: str) -> None:
        """
        Save the scraped data to a CSV file.
        """
        print(f"Saving data to {output_file}...")
        pass  # Implementation of the data2csv method

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
            station_list = self.__get_station_list(driver)
            # Get the station data
            self.__get_station_data(driver, station_list, num_days)
            # Quit the driver
            driver.quit()
        except Exception as e:
            raise Exception(f"Error occurred while scraping: {e}")
