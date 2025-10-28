"""
Main script to run the Meteo.cat scraper and merge data files.
"""

from datetime import datetime
from os import listdir
from os.path import dirname, isfile, join
import argparse
from scrapper import MeteoScraper


# Helper function to get the current list of files in the dataset folder.
# Only for demonstration purposes; in a real scenario, this would be handled by the scraper.
def get_current_file_list(output_file: str) -> list[str]:
    """
    Get the current list of files in the dataset folder, excluding the station list CSV.
    Args:
        output_file: The output CSV file name.
    Returns:
        A list of file names.
    """
    # Placeholder function to get the current list of files
    dataset_folder = join(dirname(dirname(__file__)), "dataset")
    # Get all csv files in dataset_folder
    csv_files = [
        file_name
        for file_name in listdir(dataset_folder)
        if isfile(join(dataset_folder, file_name)) and file_name.endswith(".csv")
    ]
    csv_files.remove("station_list.csv")
    # Remove output_file from the list
    if output_file in csv_files:
        csv_files.remove(output_file)
    return csv_files


def main() -> None:
    """
    Main function to run the Meteo.cat scraper and merge data files.
    """
    parser = argparse.ArgumentParser(description="Meteo.cat scraper")
    parser.add_argument(
        "-d", "--days", help="Number of days to scrape", type=int, default=7
    )
    parser.add_argument(
        "-o", "--output", help="Output CSV file", type=str, default="dataset.csv"
    )
    parser.add_argument(
        "-w",
        "--skip-download",
        help="Skip the downloading of data files",
        action="store_true",
    )
    parser.add_argument(
        "-m",
        "--skip-merge",
        help="Do not merge the data files into a single CSV",
        action="store_true",
    )
    parser.add_argument(
        "-b",
        "--begin-date",
        help="The start date for data scraping (format: DD.MM.YYYY)",
        type=str,
        default=datetime.now().strftime("%d.%m.%Y"),
    )
    args = parser.parse_args()
    if args.days <= 0:
        print("Error: Number of days must be greater than 0.")
        parser.print_help()
        return
    scraper = MeteoScraper()
    try:
        file_list = []
        if args.skip_download:
            print("Skipping download of data files.")
            file_list = get_current_file_list(output_file=args.output)
        else:
            file_list = scraper.scrape(num_days=args.days, begin_date=args.begin_date)
        if args.skip_merge:
            print("Skipping merging of data files.")
            return
        scraper.final_csv(file_list=file_list, output_file=args.output)
    except Exception as e:
        print(f"Error occurred: {e}")


if __name__ == "__main__":
    main()
