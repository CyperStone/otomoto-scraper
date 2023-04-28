import argparse
import config
from scraper import OtomotoScraper


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Run scraping all car offers from Otomoto.pl')
    parser.add_argument('--results_dir', dest='results_dir', type=str, nargs='?', default=None,
                        help='Path to directory where results have to be saved')
    parser.add_argument('--to_eng', dest='to_eng', type=str, action=argparse.BooleanOptionalAction, default=False,
                        help='Type of camera the videos were recorded')
    args = parser.parse_args()

    scraper = OtomotoScraper(config.website, config.scraper)
    _ = scraper.scrape_all_offers(results_dir=args.results_dir, to_eng=args.to_eng)
