from types import SimpleNamespace


website = SimpleNamespace(
    BASE_URL='https://www.otomoto.pl',
    PASSENGER_CARS_RESOURCE_PATH='osobowe',
    PAGE_QUERY_STRING='page=',
    DATETIME_SORTING_QUERY_STRING='search[order]=created_at_first%3Adesc',
    OFFERS_PER_PAGE=32,
    MAX_PAGE_NUMBER=500,
    COOKIE_POPUP_BTN_TEXT='Akceptuję',
    CAR_BRANDS_BTN_TEXT='Marka pojazdu',
    BRAND_MODELS_BTN_TEXT='Model pojazdu',
    UNTYPICAL_BRAND_SEARCH_STRINGS={
        'BMW-ALPINA': 'alpina',
        'Warszawa': 'marka_warszawa',
        'Zastava': 'zastawa'
    },
    UNTYPICAL_BRAND_MODELS_SEARCH_STRINGS={
        'Inny': 'other',
        'ID.5': 'id-6',
        'ID.Buzz': 'id-buzz',
        'T-Cross': 't-cross',
        'T-Roc': 't-roc',
        'X6M': 'x6-m',
        'e-tron': 'e-tron',
        'e-tron GT': 'e-tron-gt'
    },
    CSS_SELECTORS={
        'CAR_BRANDS': 'div[data-testid="filter_enum_make"] > div > ul > li > div > label > p',
        'BRAND_MODELS': 'div[data-testid="filter_enum_model"] > div > ul > li > div > label > p',
        'OFFER_URLS': 'article[data-testid=listing-ad] > div > h2 > a[href]',
        'NEXT_PAGE_BTN': 'li[data-testid="pagination-step-forwards"][aria-disabled="false"]',
        'OFFER_ID': 'span#ad_id',
        'OFFER_DATETIME': 'span.offer-meta__value',
        'OFFER_TITLE': 'span[class="offer-title big-text fake-title "]',
        'OFFER_PRICE': 'span[class="offer-price__number"]',
        'OFFER_CURRENCY': 'span[class="offer-price__currency"]',
        'OFFER_SELLER_NAME': 'h2[class="seller-heading__seller-name"]',
        'OFFER_SELLER_DETAILS': 'section[class="seller-card"] > section[class="seller-features"] > article > span',
        'OFFER_LOCATION': 'section[class="seller-card__links"] > article > a',
        'OFFER_PARAMETER_NODES': 'div#parameters > ul.offer-params__list > li.offer-params__item',
        'OFFER_PARAMETER_LABEL': 'span.offer-params__label',
        'OFFER_PARAMETER_VALUE': 'div.offer-params__value',
        'OFFER_CAR_FEATURES': 'div.offer-features > div.offer-features__row > ul.parameter-feature-group > li.parameter-feature-item',
        'OFFER_DESCRIPTION': 'div#description > div.offer-description__description'
    }
)

scraper = SimpleNamespace(
    TIMEOUT_S=10,
    TIMEOUT_MS=20000,
    MAX_THREADS=20,
    REQUEST_HEADERS={
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'pl-PL,pl;q=0.9,en-US;q=0.8,en;q=0.7',
        'Referer': 'https://www.google.com/',
        'Sec-Ch-Ua': '\"Chromium\";v=\"112\", \"Google Chrome\";v=\"112\", \"Not:A-Brand\";v=\"99\"',
        'Sec-Ch-Ua-Mobile': '?0',
        'Sec-Ch-Ua-Platform': '\"Windows\"',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'none',
        'Sec-Fetch-User': '?1',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36'
    },
    RELOAD_OFFER_PAGE_TIME_INTERVAL=10,
    GET_OFFER_URLS_MAX_FAILURE_COUNTS=5,
    REQUEST_TIME_DELAY_MIN=1,
    REQUEST_TIME_DELAY_MAX=4,
    DEFAULT_RESULTS_DIR='./data',
    RESULTS_FILE_NAME='otomoto_all_offers'
)
