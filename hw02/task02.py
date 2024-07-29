# Выполнить скрейпинг данных в веб-сайта http://books.toscrape.com/
# и извлечь информацию о всех книгах на сайте во всех категориях: название, цену,
# количество товара в наличии (In stock (19 available)) в формате integer, описание.
#
# Затем сохранить эту информацию в JSON-файле.


import json
import re

import requests
from bs4 import BeautifulSoup


class Book:
    """
    Класс (модель) книги.
    """
    __slots__ = ['upc', 'name', 'price', 'quantity', 'description']

    def __init__(self, **kwargs):
        self.upc = kwargs.get('upc')
        self.name = kwargs.get('name')
        self.price = kwargs.get('price')
        self.quantity = kwargs.get('quantity')
        self.description = kwargs.get('description')

    def __str__(self):
        return f'Книга: {self.name}. Цена {self.price}. Остаток: {self.quantity}. Код: {self.upc}'

    def get_data(self):
        return {
            'upc': self.upc,
            'name': self.name,
            'price': self.price,
            'quantity': self.quantity,
            'description': self.description,
        }

    @property
    def uid(self):
        return self.upc


class BooksDB:
    """
    Класс для хранения данных по книгам
    """
    __slots__ = ['data']

    def __init__(self):
        self.data = {}

    def add_book(self, book: Book):
        self.data[book.uid] = book

    def get_book(self, uid):
        return self.data.get(uid, None)

    def del_book(self, uid):
        try:
            del self.data[uid]
        except KeyError:
            pass

    def get_data(self):
        return [book.get_data() for book in self.data.values()]


class BookScrapper:
    """
    Класс скраппера
    """
    base_url = 'https://books.toscrape.com/'
    catalogue_url = base_url + 'catalogue/'
    user_agent = 'Web Scrapper Demo'

    def __init__(self):
        self.urls = set()
        self.session = requests.session()
        self.books = BooksDB()

    def __del__(self):
        self.session.close()

    def get_page_soup(self, url):
        response = self.session.get(url, headers={'User-Agent': self.user_agent})
        return BeautifulSoup(response.text, 'lxml')

    def explore_catalogue(self):
        current_url = self.catalogue_url + 'page-1.html'
        while current_url is not None:
            print(f'Обработка страницы {current_url}')
            page_soup = self.get_page_soup(current_url)
            self.get_book_urls(page_soup)
            try:
                current_url = self.catalogue_url + \
                              page_soup.find('li', {'class': 'next'}).find('a')['href']
            except AttributeError:
                current_url = None

    def get_book_urls(self, page_soup: BeautifulSoup):
        titles = page_soup.find('section').find_all('h3')
        for title in titles:
            self.urls.add(self.catalogue_url + title.find('a')['href'])

    def get_book_data(self, book_url):
        print(f'Обработка страницы {book_url}')
        book_soup = self.get_page_soup(book_url)
        book_name = book_soup. \
            find('div', {'class': 'col-sm-6 product_main'}). \
            find('h1').text.strip().strip('"')
        book_description = None
        try:
            book_description = book_soup. \
                find('div', {'id': 'product_description'}). \
                find_next_sibling().text.strip().strip('"')
        except AttributeError:
            pass
        book_price_tmp = book_soup.\
            find('p', {'class': 'price_color'}).text
        book_quantity_tmp = book_soup. \
            find('p', {'class': 'instock availability'}).text.strip()

        book_price = None
        try:
            book_price = float(re.sub(r'[^0-9.]+', '', book_price_tmp))
        except Exception as err:
            print(f'Не могу обработать цену книги: {err}')

        book_quantity = 0
        try:
            book_quantity = int(re.sub(r'[^0-9]+', '', book_quantity_tmp))
        except Exception as err:
            pass

        book_upc = book_soup.find('table', {'class': 'table table-striped'}).find('td').text.strip()
        self.books.add_book(
            Book(
                upc=book_upc,
                name=book_name,
                price=book_price,
                quantity=book_quantity,
                description=book_description
            )
        )

    def save_json(self, path):
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(self.books.get_data(), f, ensure_ascii=False, indent=2)

    def run(self):
        self.explore_catalogue()
        for book_page in self.urls:
            self.get_book_data(book_page)


app = BookScrapper()
app.run()
app.save_json('books.json')
