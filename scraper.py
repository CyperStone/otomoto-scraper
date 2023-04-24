import os
import re
import httpx
import utils
import pandas as pd
from time import time
from datetime import datetime
from unidecode import unidecode
from selectolax.parser import HTMLParser
from playwright.sync_api import sync_playwright
from concurrent.futures import ThreadPoolExecutor


class OtomotoScraper:

    def __init__(self, website_cfg, scraper_cfg):
        self.website_cfg = website_cfg
        self.scraper_cfg = scraper_cfg

    def _get_car_brands(self, browser):
        url = f'{self.website_cfg.BASE_URL}/{self.website_cfg.PASSENGER_CARS_RESOURCE_PATH}'

        page = browser.new_page()
        page.goto(url)

        page.wait_for_load_state('networkidle', timeout=self.scraper_cfg.TIMEOUT_MS)
        page.get_by_text(self.website_cfg.COOKIE_POPUP_BTN_TEXT, exact=True).click()
        page.get_by_placeholder(self.website_cfg.CAR_BRANDS_BTN_TEXT, exact=True).click()

        html = page.content()
        page.close()

        tree = HTMLParser(html)
        nodes = tree.css(self.website_cfg.CSS_SELECTORS['CAR_BRANDS'])
        strings = [node.text() for node in nodes][1:]

        brands = []
        for s in strings:
            brand, counts = s.split('(')
            counts = int(counts.strip('()'))

            brand_original_name = brand.strip()

            if brand_original_name in self.website_cfg.UNTYPICAL_BRAND_SEARCH_STRINGS.keys():
                brand_search_string = self.website_cfg.UNTYPICAL_BRAND_SEARCH_STRINGS[brand_original_name]
            else:
                brand_search_string = unidecode(brand_original_name).lower().replace(' ', '-')

            brands.append((brand_original_name, brand_search_string, counts))

        return brands

    def _get_brand_models(self, brand_search_string, browser):
        url = f'{self.website_cfg.BASE_URL}/{self.website_cfg.PASSENGER_CARS_RESOURCE_PATH}/{brand_search_string}'

        page = browser.new_page()
        page.goto(url)

        page.wait_for_load_state('networkidle', timeout=self.scraper_cfg.TIMEOUT_MS)
        page.get_by_text(self.website_cfg.COOKIE_POPUP_BTN_TEXT, exact=True).click()
        page.get_by_placeholder(self.website_cfg.BRAND_MODELS_BTN_TEXT, exact=True).click()

        html = page.content()
        page.close()

        tree = HTMLParser(html)
        nodes = tree.css(self.website_cfg.CSS_SELECTORS['BRAND_MODELS'])
        strings = [node.text() for node in nodes][1:]

        models = []
        for s in strings:
            model, counts = s.split('(')
            counts = int(counts.strip('()'))

            model_original_name = model.strip()

            if model_original_name in self.website_cfg.UNTYPICAL_BRAND_MODELS_SEARCH_STRINGS.keys():
                model_search_string = self.website_cfg.UNTYPICAL_BRAND_MODELS_SEARCH_STRINGS[model_original_name]
            else:
                model_search_string = unidecode(model_original_name).lower()
                model_search_string = re.sub('[^A-Za-z0-9 ]+', '', model_search_string).replace(' ', '-')

            models.append((model_original_name, model_search_string, counts))

        return models

    def _concat_search_url(self, brand_search_string, model_search_string=None):
        if model_search_string is None:
            search_url = f'{self.website_cfg.BASE_URL}/{self.website_cfg.PASSENGER_CARS_RESOURCE_PATH}/{brand_search_string}'
        else:
            search_url = f'{self.website_cfg.BASE_URL}/{self.website_cfg.PASSENGER_CARS_RESOURCE_PATH}/{brand_search_string}/{model_search_string}'

        return search_url

    def _get_search_urls(self):
        playwright = sync_playwright().start()
        browser = playwright.chromium.launch(headless=True)

        brands = self._get_car_brands(browser)
        search_urls = []
        for _, brand_search_string, brand_counts in brands:
            if brand_counts == 0:
                continue

            if brand_counts > self.website_cfg.OFFERS_PER_PAGE * self.website_cfg.MAX_PAGE_NUMBER:
                brand_models = self._get_brand_models(brand_search_string, browser)

                for _, brand_model_search_string, brand_model_counts in brand_models:
                    if brand_model_counts == 0:
                        continue

                    search_urls.append(self._concat_search_url(brand_search_string, brand_model_search_string))

            else:
                search_urls.append(self._concat_search_url(brand_search_string, None))

        browser.close()
        playwright.stop()

        return search_urls

    def _send_get_request(self, url):
        try:
            response = httpx.get(url, headers=self.scraper_cfg.REQUEST_HEADERS, timeout=self.scraper_cfg.TIMEOUT_S)

        except Exception as e:
            print(f'Exception "{e}" (request: {url})')
            return None

        else:
            if response.status_code != 200:
                print(f'Status code "{response.status_code}" (request: {url})')
                return None

            else:
                return response

    def _get_search_offer_urls(self, search_url):
        def get_page_offer_urls(page_url):
            response = self._send_get_request(page_url)

            if response is None:
                return True, [], True

            tree = HTMLParser(response.text)
            page_offer_url_nodes = tree.css(self.website_cfg.CSS_SELECTORS['OFFER_URLS'])

            if len(page_offer_url_nodes) == 0:
                print(f'Found no offers on the page (request: {page_url})')
                return True, [], True

            page_offer_urls = [page_offer_url_node.attributes['href'] for page_offer_url_node in page_offer_url_nodes
                               if self.website_cfg.BASE_URL in page_offer_url_node.attributes['href']]

            next_page_btn_node = tree.css_first(self.website_cfg.CSS_SELECTORS['NEXT_PAGE_BTN'])
            is_next_page = False if next_page_btn_node is None else True

            return False, page_offer_urls, is_next_page

        url = f'{search_url}?{self.website_cfg.DATETIME_SORTING_QUERY_STRING}'
        failure_counts = 0
        page_number = 1
        is_next_page = True
        offer_urls = []

        while is_next_page:
            page_url = f'{url}&{self.website_cfg.PAGE_QUERY_STRING}{page_number}'
            failure, page_offer_urls, is_next_page = get_page_offer_urls(page_url)

            if failure:
                utils.go_to_sleep(self.scraper_cfg.RELOAD_OFFER_PAGE_TIME_INTERVAL)
                failure, page_offer_urls, is_next_page = get_page_offer_urls(page_url)

                if failure:
                    failure_counts += 1

            offer_urls.extend(page_offer_urls)

            page_number += 1
            if page_number > self.website_cfg.MAX_PAGE_NUMBER or \
                    failure_counts > self.scraper_cfg.GET_OFFER_URLS_MAX_FAILURE_COUNTS:
                break

            utils.go_to_sleep(self.scraper_cfg.REQUEST_TIME_DELAY_MIN,
                              self.scraper_cfg.REQUEST_TIME_DELAY_MAX)

        return offer_urls

    def _get_info_from_offer(self, offer_url):
        response = self._send_get_request(offer_url)

        if response is None:
            utils.go_to_sleep(self.scraper_cfg.RELOAD_OFFER_PAGE_TIME_INTERVAL)
            response = self._send_get_request(offer_url)

            if response is None:
                return None

        tree = HTMLParser(response.text)
        features_dict = {}

        try:
            offer_id = tree.css_first(self.website_cfg.CSS_SELECTORS['OFFER_ID']).text().strip()
            features_dict['ID'] = int(offer_id)

            features_dict['URL'] = offer_url

            datetime = [node.text() for node in tree.css(self.website_cfg.CSS_SELECTORS['OFFER_DATETIME'])
                        if 'id' not in node.attributes.keys()][0]
            features_dict['Data utworzenia oferty'] = utils.parse_datetime(datetime)

            title = tree.css_first(self.website_cfg.CSS_SELECTORS['OFFER_TITLE']).text(deep=False).strip()
            features_dict['Tytuł oferty'] = title

            price = tree.css_first(self.website_cfg.CSS_SELECTORS['OFFER_PRICE']).text(deep=False).strip()
            features_dict['Cena'] = int(price.replace(' ', '').split(',')[0])

            currency = tree.css_first(self.website_cfg.CSS_SELECTORS['OFFER_CURRENCY']).text().strip()
            features_dict['Waluta'] = currency

            seller_name = tree.css_first(self.website_cfg.CSS_SELECTORS['OFFER_SELLER_NAME']).text().strip()
            features_dict['Nazwa sprzedawcy'] = seller_name

            seller_details_nodes = tree.css(self.website_cfg.CSS_SELECTORS['OFFER_SELLER_DETAILS'])
            features_dict['Typ sprzedawcy'] = seller_details_nodes[0].text().strip()
            features_dict['Rok rejestracji sprzedawcy'] = int(seller_details_nodes[-1].text().strip().split(' ')[-1])

            location = tree.css_first(self.website_cfg.CSS_SELECTORS['OFFER_LOCATION']).text().strip()
            features_dict['Lokalizacja'] = location

            parameter_nodes = tree.css(self.website_cfg.CSS_SELECTORS['OFFER_PARAMETER_NODES'])
            for parameter_node in parameter_nodes:
                label = parameter_node.css_first(self.website_cfg.CSS_SELECTORS['OFFER_PARAMETER_LABEL']).text().strip()
                value = parameter_node.css_first(self.website_cfg.CSS_SELECTORS['OFFER_PARAMETER_VALUE']).text().strip()
                features_dict[label] = value

            car_feature_nodes = tree.css(self.website_cfg.CSS_SELECTORS['OFFER_CAR_FEATURES'])
            for car_feature_node in car_feature_nodes:
                car_feature = car_feature_node.text().strip()
                features_dict[car_feature] = True

            description = tree.css_first(self.website_cfg.CSS_SELECTORS['OFFER_DESCRIPTION']).text(deep=False).strip()
            features_dict['Opis oferty'] = description

        except Exception as e:
            print(f'Exception "{e}" (request: {offer_url})')
            return None

        utils.go_to_sleep(self.scraper_cfg.REQUEST_TIME_DELAY_MIN,
                          self.scraper_cfg.REQUEST_TIME_DELAY_MAX)

        return features_dict

    def scrape_all_offers(self, results_dir=None):
        time_start = time()
        search_urls = self._get_search_urls()
        print(f'Found {len(search_urls)} different searches.')

        n_threads = min(len(search_urls), self.scraper_cfg.MAX_THREADS)
        print(f'Started scraping offers URLs using {n_threads} threads.')
        with ThreadPoolExecutor(max_workers=n_threads) as executor:
            offer_urls = [search_offer_urls for search_offer_urls in executor.map(self._get_search_offer_urls, search_urls)]

        offer_urls = list(set([url for urls_list in offer_urls for url in urls_list]))
        print(f'Found {len(offer_urls)} car offers.')

        n_threads = min(len(offer_urls), self.scraper_cfg.MAX_THREADS)
        print(f'Started scraping car offers using {n_threads} threads.')
        with ThreadPoolExecutor(max_workers=n_threads) as executor:
            features_dicts = [features_dict for features_dict in executor.map(self._get_info_from_offer, offer_urls)]

        features_dicts = [features_dict for features_dict in features_dicts if isinstance(features_dict, dict)]
        offers = pd.DataFrame(features_dicts)

        time_stop = time()
        time_elapsed_str = utils.format_time(time_stop - time_start)
        print(f'Scraped {len(offers)} car offers in {time_elapsed_str}.')

        if results_dir is None:
            results_dir = self.scraper_cfg.DEFAULT_RESULTS_DIR

            if not os.path.isdir(results_dir):
                os.mkdir(results_dir)

        timestamp = datetime.now().strftime("%d-%m-%Y_%H-%M-%S")
        full_path = f'{results_dir}/{self.scraper_cfg.RESULTS_FILE_NAME}_{timestamp}.csv'
        offers.to_csv(full_path, sep=';', index=False)
        print(f'Saved offers to {full_path}.')

        return offers
