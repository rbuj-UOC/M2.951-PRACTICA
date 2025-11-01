"""
Meteo.cat scraper module.
"""

from os import listdir, makedirs, path
import re
import time
from datetime import datetime, timedelta
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException


# define a custom exception for scraper errors
class MeteoScraperError(Exception):
    """Custom exception for scraper errors.
    Attributes:
        message -- explanation of the error
    """

    def __init__(self, message):
        self.message = message
        super().__init__(self.message)


class MeteoScraper:
    """
    A class to scrape weather data from Meteo.cat.
    """

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
        Args:
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
            raise MeteoScraperError(
                "Error occurred while loading CSV to DataFrame"
            ) from e

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
            raise MeteoScraperError(
                "Error occurred while saving DataFrame to CSV."
            ) from e

    def __enter_date(
        self,
        form_element,
        day: datetime,
        delay: float = 0.1,
        timeout: float = 10.0,
    ) -> None:
        """
        Enter the date in the datepicker input field.
        Args:
            form_element: The form element containing the datepicker.
            day: The date to enter.
            delay: The time to wait after each action.
            timeout: The maximum time to wait for each action.
        """
        date_element = form_element.find_element(By.ID, "datepicker")
        date_element.clear()
        date_element.send_keys(day.strftime("%d.%m.%Y"))
        time.sleep(delay)

    def __exists_dataset(self, file_name: str) -> bool:
        """
        Check if a dataset file exists in the dataset folder.
        Args:
            file_name: The file name to check.
        Returns:
            True if the file exists, False otherwise.
        """
        # Create the dataset folder if not exists
        makedirs(self.dataset_folder, exist_ok=True)
        # Get the full file path
        file_path = self.__get_file_path(file_name)
        # Check if the file exists
        return path.exists(file_path)

    def __get_all_stations_data(
        self,
        driver: webdriver.Chrome,
        station_list: pd.DataFrame,
        num_days: int,
        begin_date: str,
        delay: float = 0.1,
        timeout: float = 10.0,
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
            timeout: The maximum time to wait for each action.
            max_retries: The maximum number of retries for each station/day.
        Returns:
            A list of file names where the data is saved.
        """
        try:
            file_list = []
            self.__navigate_to_station_data_page(driver)
            # Get station data for each day
            for day in self.__get_day_list(num_days, begin_date):
                for i, station in station_list.iterrows():
                    try:
                        # Get station name, code, start date, and end date
                        station_full_name = station["Estació [Codi]"]
                        station_code = station_full_name[-3:-1]
                        station_name = station_full_name[0:-5]
                        station_status = station["Estat actual"]
                        # Determine end_date based on station status
                        if station_status == "Operativa":
                            end_date = datetime.strptime(
                                begin_date, "%d.%m.%Y"
                            ) + timedelta(
                                days=1
                            )  # tomorrow
                        elif station_status == "Desmantellada":
                            continue  # skip dismantled stations
                        else:
                            raise MeteoScraperError(
                                f"Unknown station status: {station_status}"
                            )
                        # Determine start_date
                        start_date = datetime.strptime(station["Data alta"], "%d.%m.%Y")
                        # If day is greater than end_date or less than start_date, skip
                        if day > end_date or day < start_date:
                            continue
                        # Check if the dataset already exists for the given station and date
                        file_name = f"{station_code}_{day.strftime('%Y-%m-%d')}.csv"
                        if self.__exists_dataset(file_name):
                            print(
                                f"Dataset for {station_name} on {day.strftime('%d.%m.%Y')} "
                                + "already exists. Skipping..."
                            )
                            continue
                        # Get station data for the given day and station
                        self.__get_station_data(
                            driver,
                            station_name,
                            station_code,
                            day,
                            file_name,
                            delay,
                            timeout,
                            max_retries,
                        )
                        file_list.append(file_name)
                    except Exception as e:
                        print(
                            f"Error occurred while scraping station {station_name}: {e}"
                        )
            return file_list
        except Exception as e:
            print(f"Error occurred while getting station data: {e}")

    def __get_station_data(
        self,
        driver: webdriver.Chrome,
        station_name: str,
        station_code: str,
        day: datetime,
        file_name: str,
        delay: float = 0.1,
        timeout: float = 10.0,
        max_retries: int = 5,
    ) -> None:
        """
        Get the meteorological data for each station.
        Args:
            driver: The selenium webdriver instance.
            station_name: The name of the station.
            station_code: The code of the station.
            day: The date to scrape data for.
            file_name: The file name to save the data.
            delay: The time to wait after each action.
            timeout: The maximum time to wait for each action.
            max_retries: The maximum number of retries for each station/day.
        """
        # Print station name and code
        print(
            f'Scraping data for station: "{station_name}" [{station_code}] '
            + f'on {day.strftime("%d.%m.%Y")}'
        )
        # Retry logic for each day
        retries = 0
        while retries < max_retries:
            try:
                # Get form element
                form_element = driver.find_element(By.ID, "seleccio-estacions")
                # Select station the station from the autocomplete dropdown
                self.__select_station(driver, form_element, station_name)
                # Enter date in the input field
                self.__enter_date(form_element, day, delay, timeout)
                # Submit the form
                submit_button = form_element.find_element(By.ID, "cercaEstacioButton")
                submit_button.click()
                time.sleep(delay)
                # Wait until the station data appears in the breadcrumbs
                WebDriverWait(driver, timeout=timeout).until(
                    EC.text_to_be_present_in_element(
                        (
                            By.XPATH,
                            "//nav[@class='breadcrumbs']/ul/li[last()]",
                        ),
                        station_name,
                    )
                )
                # click on tab "Dades per període"
                tabs_element = driver.find_element(By.ID, "tabs")
                tab_element = tabs_element.find_element(By.ID, "ui-id-6")
                tab_element.click()
                # Get station data table from the page
                WebDriverWait(driver, timeout=timeout).until(
                    EC.presence_of_element_located(
                        (By.XPATH, "//table[@class='tblperiode']")
                    )
                )
                # Delay to ensure table is fully loaded
                time.sleep(1.0)
                # Get table element
                table_element = driver.find_element(
                    By.XPATH, "//table[@class='tblperiode']"
                )
                # Get table data
                table_data = []
                for row in table_element.find_elements(By.XPATH, "./tbody/tr"):
                    # Get all cells in the row
                    cells = [
                        cell.text for cell in row.find_elements(By.XPATH, "./td | ./th")
                    ]
                    # Append station data to table data
                    table_data.append(cells)
                # Replace new lines with spaces in first row of table_data
                table_data[0] = [cell.replace("\n", " ") for cell in table_data[0]]
                # Create DataFrame
                df = pd.DataFrame(table_data[1:], columns=table_data[0])
                # save station list to csv
                self.__dataframe_to_csv(df, file_name)
            except Exception as e:
                print(
                    f"Error occurred while scraping data for {station_name}: "
                    f"{day.strftime('%d.%m.%Y')}: {e}"
                )
                print(f"Retrying {retries + 1}/{max_retries}...")
                try:
                    # Navigate to station data page
                    self.__navigate_to_station_data_page(driver)
                except Exception as ex:
                    print(f"Error occurred while navigating to station data page: {ex}")
            else:
                break
            retries += 1

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

    def __get_station_list(
        self, driver: webdriver.Chrome, timeout: float = 10.0
    ) -> pd.DataFrame:
        """
        Get the list of meteorological stations from the website.
        Args:
            driver: The selenium webdriver instance.
            timeout: The maximum time to wait for each action.
        Returns:
            A DataFrame containing the station list.
        """
        try:
            # Navigate to the list URL
            self.__navigate_to_station_list_page(driver)
            # Reject cookies
            self.__reject_cookies(driver)
            # wait until the station list table is present
            WebDriverWait(driver, timeout=timeout).until(
                EC.presence_of_element_located((By.ID, "llistaEstacions"))
            )
            # Get station list table from the page
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
            raise MeteoScraperError("Error occurred while getting station list.") from e

    def __navigate_to_station_data_page(
        self,
        driver: webdriver.Chrome,
        timeout: float = 10.0,
        delay: float = 0.1,
        max_retries: int = 5,
    ) -> None:
        """
        Navigate to the station data page.
        Args:
            driver: The selenium webdriver instance.
            timeout: The maximum time to wait for each action.
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
            raise MeteoScraperError(
                "Failed to load station data page after multiple retries"
            )
        # Wait for a short delay
        time.sleep(delay)

    def __navigate_to_station_list_page(
        self, driver: webdriver.Chrome, timeout: float = 10.0, delay: float = 0.1
    ) -> None:
        """
        Navigate to the station list page.
        Args:
            driver: The selenium webdriver instance.
            timeout: The maximum time to wait for each action.
            delay: The time to wait after page load.
        """
        driver.set_page_load_timeout(timeout)
        try:
            driver.get(self.list_url)
        except TimeoutException as e:
            raise MeteoScraperError("Station list page did not load in time") from e
        # Wait for a short delay
        time.sleep(delay)

    def __reject_cookies(
        self, driver: webdriver.Chrome, timeout: float = 10.0, delay: float = 0.1
    ) -> None:
        """
        Reject cookies on the website.
        Args:
            driver: The selenium webdriver instance.
            timeout: The maximum time to wait for the element to be present.
            delay: The time to wait after rejecting cookies.
        """
        try:
            # Wait for the reject cookies button to be present
            WebDriverWait(driver, timeout=timeout).until(
                EC.presence_of_element_located(
                    (By.XPATH, "//div[@id='missatge_cookie']//button[@id='rebutjar']")
                )
            )
            # Find and click the reject cookies button
            reject_button = driver.find_element(
                By.XPATH,
                "//div[@id='missatge_cookie']//button[@id='rebutjar']",
            )
            reject_button.click()
            # Wait for a short delay
            time.sleep(delay)
        except NoSuchElementException:
            print("Could not reject cookies. Element not found.")

    def __select_station(
        self,
        driver: webdriver.Chrome,
        form_element,
        station_name: str,
        timeout: float = 10.0,
        delay: float = 0.1,
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
            name_element = form_element.find_element(By.ID, "nom")
            name_element.clear()
            name_element.send_keys(station_name)
            # Wait until the 1st autocomplete suggestions contains the station name
            WebDriverWait(driver, timeout=timeout).until(
                EC.text_to_be_present_in_element(
                    (By.XPATH, "//ul[@id='ui-id-1']/li[1]"), station_name
                )
            )
            # Select the station from the autocomplete dropdown
            name_element.send_keys(Keys.DOWN)
            name_element.send_keys(Keys.RETURN)
            # Wait for a short delay
            time.sleep(delay)
        except Exception as e:
            raise MeteoScraperError(f"Could not select station {station_name}.") from e

    def final_csv(self, file_list: list[str], output_file: str) -> None:
        """
        Save the scraped data to a CSV file.
        Args:
            file_list: The list of file names where the data is saved.
            output_file: The output CSV file name.
        """
        print(f"Saving data to {output_file}...")
        frames = []
        # Get all station codes from file names and load data into DataFrames
        station_codes = set([file_name.split("_")[0] for file_name in file_list])
        # Build dataset for each station, append to frames list, and save to csv
        for station_code in station_codes:
            print(f"\tProcessing station: {station_code}")
            station_files = [
                file_name
                for file_name in file_list
                if file_name.startswith(station_code)
            ]
            station_frames = []
            for file_name in station_files:
                try:
                    df = self.__csv_to_dataframe(file_name)
                    # Get date from file name
                    date_str = file_name.split("_")[1].replace(".csv", "")
                    date_datetime = datetime.strptime(date_str, "%Y-%m-%d")
                    # Add date column to dataframe
                    df["date"] = date_datetime.strftime("%d.%m.%Y")
                    # Move date column to first position
                    cols = df.columns.tolist()
                    cols = [cols[-1]] + cols[:-1]
                    df = df[cols]
                    # Append to station frames list
                    station_frames.append(df)
                except Exception as e:
                    print(f"Error occurred while loading {file_name}: {e}")
                    continue
            # Concatenate all DataFrames
            station_df = pd.concat(station_frames, ignore_index=True, sort=False)
            # Convert "date" column to datetime
            station_df["date"] = pd.to_datetime(station_df["date"], format="%d.%m.%Y")
            # Sort by date and time
            station_df = station_df.sort_values(by=["date", "Període TU"])
            # Convert "date" column back to string
            station_df["date"] = station_df["date"].dt.strftime("%d.%m.%Y")
            # Save station data to csv
            self.__dataframe_to_csv(station_df, f"{station_code}_merged.csv")
            # Set station code column
            station_df["code"] = station_code
            # Append to frames list
            frames.append(station_df)
        # Concatenate all merged dataframes
        measurements_df = pd.concat(frames, ignore_index=True, sort=False)
        # Get all stations
        stations_df = self.__csv_to_dataframe("station_list.csv")
        # Add "code" column to stations_df
        stations_df["code"] = stations_df["Estació [Codi]"].apply(lambda x: x[-3:-1])
        # Merge measurements with stations on "code"
        final_df = pd.merge(stations_df, measurements_df, on="code", how="inner")
        # Save to CSV
        self.__dataframe_to_csv(final_df, output_file)

    def get_file_list(self, output_file: str = "dataset.csv") -> list[str]:
        """
        Get the list of CSV files in the dataset folder witch should be merged.
        Args:
            output_file: The output CSV file name.
        Returns:
            A list of file names.
        """
        # Check if dataset folder exists
        if not path.exists(self.dataset_folder):
            raise MeteoScraperError("dataset folder does not exist.")
        # Get all csv files in dataset_folder
        pattern = r"^[A-Z|0-9]{2}_\d{4}-\d{2}-\d{2}\.csv$"
        csv_files = [
            file_name
            for file_name in listdir(self.dataset_folder)
            if path.isfile(self.__get_file_path(file_name))
            and file_name.endswith(".csv")
            and re.match(pattern, file_name)
        ]
        # Remove station_list.csv from the list
        if "station_list.csv" in csv_files:
            csv_files.remove("station_list.csv")
        # Remove output_file from the list
        if output_file in csv_files:
            csv_files.remove(output_file)
        return csv_files

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
            file_list = self.__get_all_stations_data(
                driver, station_list, num_days, begin_date
            )
            # Quit the driver
            driver.quit()
            # return the list of files
            return file_list
        except Exception as e:
            raise MeteoScraperError("Error occurred while scraping.") from e
