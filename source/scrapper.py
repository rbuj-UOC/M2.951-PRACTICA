"""
Meteo.cat scraper module.
"""

from os import makedirs, path
import time
from datetime import datetime, timedelta
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
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

    def __csv_to_dataframe(self, input_file: str) -> pd.DataFrame:
        """
        Load a CSV file into a DataFrame.
        Args:            input_file: The input CSV file name.
            input_file: The input CSV file name.
        Returns:
            A DataFrame containing the CSV data.
        """
        try:
            # Get file path
            file_path = self.__get_file_path(input_file)
            # Load the CSV into a DataFrame
            df = pd.read_csv(file_path)
            # Print success message
            print(f"\tCSV loaded from {file_path}")
            # Return the DataFrame
            return df
        except Exception as e:
            raise Exception(f"Error occurred while loading CSV to DataFrame: {e}")

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
            # Get the file path for the output file
            file_path = self.__get_file_path(output_file)
            # Save the DataFrame to CSV in dataset folder, overwriting if it exists
            df.to_csv(file_path, index=False, mode="w")
            # Print success message
            print(f"\tDataFrame saved to {file_path}")
        except Exception as e:
            raise Exception(f"Error occurred while saving DataFrame to CSV: {e}")

    def __exists_dataset(self, file_name: str) -> bool:
        """
        Check if a dataset file exists in the dataset folder.
        Args:
            file_name: The file name to check.
        Returns:
            True if the file exists, False otherwise.
        """
        file_path = self.__get_file_path(file_name)
        return path.exists(file_path)

    def __get_day_list(self, num_days: int, begin_date: str) -> list[datetime]:
        """
        Get the list of days for which to scrape data.
        Args:
            num_days: The number of days to scrape.
            begin_date: The start date for data scraping (format: DD.MM.YYYY).
        Returns:
            A list of dates as strings.
        """
        begin_date_dt = datetime.strptime(begin_date, "%d.%m.%Y")
        return [begin_date_dt - timedelta(days=i) for i in range(num_days)]

    def __get_file_path(self, file_name: str) -> str:
        """
        Get the full file path for a dataset file.
        Args:
            file_name: The file name.
        Returns:
            The full file path.
        """
        return path.join(self.dataset_folder, file_name)

    def __get_station_data(
        self,
        driver: webdriver.Chrome,
        station_list: pd.DataFrame,
        num_days: int,
        begin_date: str,
        delay: float = 2.0,
        max_retries: int = 5,
    ) -> list[str]:
        """
        Get the meteorological data for each station.
        Args:
            driver: The selenium webdriver instance.
            station_list: The list of stations as a DataFrame.
            num_days: The number of days to scrape data for.
            begin_date: The start date for data scraping (format: DD.MM.YYYY).
            delay: The time to wait after each action.
            max_retries: The maximum number of retries for each station/day.
        Returns:
            A list of file names where the data is saved.
        """
        try:
            file_list = []
            # Navigate to station data page
            self.__navigate_to_station_data_page(driver)
            for i, station in station_list.iterrows():
                try:
                    # Get station data for each station
                    # Get station name, code, start date, and end date
                    station_full_name = station["Estació [Codi]"]
                    station_code = station_full_name[-3:-1]
                    station_name = station_full_name[0:-5]
                    station_status = station["Estat actual"]
                    if station_status == "Operativa":
                        end_date = datetime.strptime(
                            begin_date, "%d.%m.%Y"
                        ) + timedelta(
                            days=1
                        )  # tomorrow
                    elif station_status == "Desmantellada":
                        continue  # skip dismantled stations
                    else:
                        raise Exception(f"Unknown station status: {station_status}")
                    start_date = datetime.strptime(station["Data alta"], "%d.%m.%Y")
                    # Select station the station from the autocomplete dropdown
                    self.__select_station(driver, station_name)
                    # Print station name and code
                    print(
                        f'\tScraping data for station: "{station_name}" [{station_code}]'
                    )
                    # Get station data for each day
                    for day in self.__get_day_list(num_days, begin_date):
                        # Check if the dataset already exists for the given station and date
                        file_name = f"{station_code}_{day.strftime('%Y-%m-%d')}.csv"
                        if self.__exists_dataset(file_name):
                            print(
                                f"Dataset for {station_name} on {day.strftime('%d.%m.%Y')} already exists. Skipping..."
                            )
                            continue
                        # If day is greater than end_date or less than start_date, skip
                        if day > end_date or day < start_date:
                            continue
                        # Retry logic for each day
                        retries = 0
                        while retries < max_retries:
                            try:
                                # Select date in form input field
                                form_element = driver.find_element(
                                    By.ID, "seleccio-estacions"
                                )
                                date_element = form_element.find_element(
                                    By.ID, "datepicker"
                                )
                                date_element.clear()
                                date_element.send_keys(day.strftime("%d.%m.%Y"))
                                time.sleep(delay)
                                # Submit the form
                                submit_button = form_element.find_element(
                                    By.ID, "cercaEstacioButton"
                                )
                                submit_button.click()
                                time.sleep(delay)
                                # click on tab "Dades per període"
                                tabs_element = driver.find_element(By.ID, "tabs")
                                tab_element = tabs_element.find_element(
                                    By.ID, "ui-id-6"
                                )
                                tab_element.click()
                                time.sleep(delay)
                                # Get station data table from the page
                                table_element = driver.find_element(
                                    By.XPATH, "//table[@class='tblperiode']"
                                )
                                # Get table data
                                table_data = []
                                for row in table_element.find_elements(
                                    By.XPATH, "./tbody/tr"
                                ):
                                    # Get all cells in the row
                                    cells = [
                                        cell.text
                                        for cell in row.find_elements(
                                            By.XPATH, "./td | ./th"
                                        )
                                    ]
                                    # Append station data to table data
                                    table_data.append(cells)
                                # Replace new lines with spaces in first row of table_data
                                table_data[0] = [
                                    cell.replace("\n", " ") for cell in table_data[0]
                                ]
                                # Create DataFrame
                                df = pd.DataFrame(table_data[1:], columns=table_data[0])
                                # save station list to csv
                                self.__dataframe_to_csv(df, file_name)
                                file_list.append(file_name)
                            except Exception as e:
                                print(
                                    f"Error occurred while scraping data for {station_name}: {day.strftime('%d.%m.%Y')}: {e}"
                                )
                                print(f"Retrying {retries + 1}/{max_retries}...")
                                try:
                                    # Navigate to station data page
                                    self.__navigate_to_station_data_page(driver)
                                    # Select station the station from the autocomplete dropdown
                                    self.__select_station(driver, station_name)
                                except Exception as e:
                                    print(
                                        f"Error occurred while re-navigating to station data page for {station_name}: {e}"
                                    )
                            else:
                                break
                            retries += 1
                except Exception as e:
                    print(f"Error occurred while scraping station {station_name}: {e}")
            return file_list
        except Exception as e:
            print(f"Error occurred while getting station data: {e}")

    def __get_station_list(self, driver: webdriver.Chrome) -> pd.DataFrame:
        """
        Get the list of meteorological stations from the website.
        Args:
            driver: The selenium webdriver instance.
        Returns:
            A DataFrame containing the station list.
        """
        # Navigate to the list URL
        self.__navigate_to_station_list_page(driver, timeout=10)
        # Reject cookies
        self.__reject_cookies(driver)
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
        self,
        driver: webdriver.Chrome,
        timeout: int = 10,
        delay: float = 0.1,
        max_retries: int = 5,
    ) -> None:
        """
        Navigate to the station data page.
        Args:
            driver: The selenium webdriver instance.
            timeout: The maximum time to wait for the page to load.
            delay: The time to wait after page load.
            max_retries: The maximum number of retries for loading the page.
        """
        driver.set_page_load_timeout(timeout)
        retries = 0
        while retries < max_retries:
            try:
                driver.get(self.data_url)
            except TimeoutException:
                print(f"Retrying... ({retries + 1}/{max_retries})")
            else:
                break
            retries += 1
        if retries == max_retries:
            raise Exception("Failed to load station data page after multiple retries")
        # Wait for a short delay
        time.sleep(delay)

    def __navigate_to_station_list_page(
        self, driver: webdriver.Chrome, timeout: int, delay: float = 0.1
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

    def __reject_cookies(self, driver: webdriver.Chrome, delay: float = 0.1) -> None:
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

    def __select_station(
        self, driver: webdriver.Chrome, station_name: str, delay: float = 2.0
    ) -> None:
        """
        Select a station from the autocomplete dropdown.
        Args:
            driver: The selenium webdriver instance.
            station_name: The name of the station to select.
            delay: The time to wait after selecting the station.
        """
        try:
            # Enter station name in form input field
            form_element = driver.find_element(By.ID, "seleccio-estacions")
            name_element = form_element.find_element(By.ID, "nom")
            name_element.clear()
            name_element.send_keys(station_name)
            time.sleep(delay)
            # Select the station from the autocomplete dropdown
            name_element.send_keys(Keys.DOWN)
            name_element.send_keys(Keys.RETURN)
            time.sleep(delay)
        except:
            raise Exception(f"Could not select station {station_name}.")

    def final_csv(self, file_list: list[str], output_file: str) -> None:
        """
        Save the scraped data to a CSV file.
        Args:
            file_list: The list of file names where the data is saved.
            output_file: The output CSV file name.
        """
        print(f"Saving data to {output_file}...")
        frames = []
        for file_name in file_list:
            try:
                df = self.__csv_to_dataframe(file_name)
                # Get station code from file name
                df["code"] = file_name.split("_")[0]
                # Get date from file name
                date_str = file_name.split("_")[1].replace(".csv", "")
                date_datetime = datetime.strptime(date_str, "%Y-%m-%d")
                df["date"] = date_datetime.strftime("%d.%m.%Y")
                # Append to frames list
                frames.append(df)
            except Exception as e:
                print(f"Error occurred while loading {file_name}: {e}")
        # Concatenate all DataFrames
        measurements_df = pd.concat(frames, ignore_index=True, sort=False)
        # Get all stations
        stations_df = self.__csv_to_dataframe("station_list.csv")
        stations_df["code"] = stations_df["Estació [Codi]"].apply(lambda x: x[-3:-1])
        # Merge measurements with stations on "code"
        final_df = pd.merge(stations_df, measurements_df, on="code", how="inner")
        # Save to CSV
        self.__dataframe_to_csv(final_df, output_file)

    def scrape(self, num_days: int, begin_date: str) -> list[str]:
        """
        Scrape meteorological data from the website.
        Args:
            num_days: The number of days to scrape data for.
            begin_date: The start date for data scraping (format: DD.MM.YYYY).
        Returns:
            A list of file names where the data is saved.
        """
        # Implementation of the scrape method
        print("\tScraping data...")
        try:
            # Initialize the webdriver
            driver = webdriver.Chrome()
            # Check user agent
            agent = driver.execute_script("return navigator.userAgent")
            print(f"User agent: {agent}")
            # Get the station list
            station_list = self.__get_station_list(driver)
            # Get the station data
            file_list = self.__get_station_data(
                driver, station_list, num_days, begin_date
            )
            # Quit the driver
            driver.quit()
            # return the list of files
            return file_list
        except Exception as e:
            raise Exception(f"Error occurred while scraping: {e}")
