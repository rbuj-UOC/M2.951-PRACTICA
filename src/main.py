from scrapper import MeteoScraper


def main() -> None:
    output_file = "dataset.csv"
    scraper = MeteoScraper()
    try:
        scraper.scrape()
        scraper.data2csv(output_file)
    except Exception as e:
        print(f"Error occurred: {e}")


if __name__ == "__main__":
    main()
