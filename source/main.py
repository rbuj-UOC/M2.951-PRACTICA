"""
Main script to run the Meteo.cat scraper and merge data files.
"""

from datetime import datetime
import argparse
from scrapper import MeteoScraper, MeteoScraperError


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
            file_list = scraper.get_file_list(args.output)
        else:
            file_list = scraper.scrape(num_days=args.days, begin_date=args.begin_date)
        if args.skip_merge:
            print("Skipping merging of data files.")
            return
        scraper.final_csv(file_list=file_list, output_file=args.output)
    except MeteoScraperError as e:
        print(f"Error occurred: {e}")


if __name__ == "__main__":
    main()
