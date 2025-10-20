from scrapper import MeteoScraper


def main() -> None:
    output_file = "dataset.csv"
    scraper = MeteoScraper()
    scraper.scrape()
    scraper.data2csv(output_file)


if __name__ == "__main__":
    main()
