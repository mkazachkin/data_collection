import re
import sys
import datetime
import time
import random
import urllib
from typing import Optional

import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.common import SessionNotCreatedException, NoSuchDriverException
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.webdriver import WebDriver

WEBDRIVER = '/usr/bin/chromedriver'
DEFAULT_PAGE_LIMIT = 3


def get_webdriver(use_gui: bool = True) -> WebDriver:
    """Инициализация сессии Chrome с возможностью запуска в графическом интерфейсе или без него."""
    chrome_service = Service(WEBDRIVER)
    chrome_options = Options()
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--ignore-certificate-errors')
    chrome_options.add_argument('--ignore-certificate-errors-spki-list')
    chrome_options.add_argument('--disable-extensions')
    if use_gui:
        chrome_options.add_argument('--start-maximized')
        chrome_options.add_argument('--start-fullscreen')
    else:
        chrome_options.add_argument('--headless=new')
        chrome_options.add_argument('--window-size=1920,1080')
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_driver = webdriver.Chrome(
        service=chrome_service,
        options=chrome_options,
    )
    chrome_driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
        'source': '''
        delete window.cdc_adoQpoasnfa76pfcZLmcfl_Array;
        delete window.cdc_adoQpoasnfa76pfcZLmcfl_Promise;
        delete window.cdc_adoQpoasnfa76pfcZLmcfl_Symbol;
        '''
    })
    return chrome_driver


def get_soup(html: str) -> BeautifulSoup:
    """Преобразование HTML в объект BeautifulSoup."""
    return BeautifulSoup(html, 'lxml')


def get_next_page(soup) -> Optional[str]:
    """Получение ссылки на следующую страницу и её преобразование в абсолютную."""
    next_page = soup.find('a', {'class': 'paginator__item _active'})
    if next_page:
        next_page = next_page.find_next_sibling('a')
        if next_page:
            relative_url = next_page['href']
            absolute_url = urllib.parse.urljoin('http://167000.ru/komi/prodam/dom/', relative_url)
            return absolute_url
    return None


def sleep_randomly(min_seconds, max_seconds):
    """Приостановка выполнения скрипта на случайное время."""
    sleep_time = random.randint(min_seconds, max_seconds)
    time.sleep(sleep_time)


def collect_data(soup):
    """Сбор данных из таблицы offer-table"""
    columns_header = ['Тип', 'Адрес', 'Цена', 'Этаж', 'Площадь', 'Отделка', 'Дата', 'Фото']
    rows = soup.find_all('tr', class_='offer-table__row')
    data = [tuple(td.text.strip() for td in row.find_all('td')) for row in rows]
    df = pd.DataFrame(data, columns=columns_header)
    # Удаление последней колонки
    df.drop(['Фото'], axis=1, inplace=True)
    # Преобразование цены в целое число
    df['Цена'] = df['Цена'].apply(lambda x: int(re.sub(r'[^0-9]', '', x)) if x else 0)
    # Обработка поля "Дата"
    today = datetime.date.today().strftime('%d.%m')
    yesterday = (datetime.date.today() - datetime.timedelta(days=1)).strftime('%d.%m')
    df['Дата'] = df['Дата'].replace({'сегодня': today, 'вчера': yesterday}, regex=True)
    return df


def accumulate_dataframes(dfs):
    """Слияние датафреймов в один большой датафрейм."""
    combined_df = pd.concat(dfs, ignore_index=True)
    combined_df.to_csv('data.csv', index=False, sep='\t')


try:
    driver = get_webdriver()
except (SessionNotCreatedException, NoSuchDriverException) as err:
    print(err)
    sys.exit(1)

dfs = []
end_flag = False
current_page = 'http://167000.ru/komi/prodam/dom/?sort=uptime'
counter = 0
while not end_flag or counter < DEFAULT_PAGE_LIMIT:
    counter += 1
    driver.get(current_page)
    page_soup = get_soup(driver.page_source)
    df = collect_data(page_soup)
    dfs.append(df)
    current_page = get_next_page(page_soup)
    if not current_page:
        end_flag = True
    else:
        sleep_randomly(0, 2)

accumulate_dataframes(dfs)
driver.close()
