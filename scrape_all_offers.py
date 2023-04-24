import config
from scraper import OtomotoScraper


if __name__ == '__main__':
    results_dir = './data'
    scraper = OtomotoScraper(config.website, config.scraper)

    _ = scraper.scrape_all_offers(results_dir)
