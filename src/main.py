import argparse
from scrapper import MeteoScraper


def main() -> None:
    parser = argparse.ArgumentParser(description="Meteo.cat scraper")
    parser.add_argument(
        "-d", "--days", help="Number of days to scrape", type=int, default=7
    )
    parser.add_argument(
        "-o", "--output", help="Output CSV file", type=str, default="dataset.csv"
    )
    args = parser.parse_args()
    scraper = MeteoScraper()
    try:
        scraper.scrape(num_days=args.days)
        scraper.data2csv(output_file=args.output)
    except Exception as e:
        print(f"Error occurred: {e}")


if __name__ == "__main__":
    main()
