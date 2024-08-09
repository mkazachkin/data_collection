import re
from decimal import Decimal

import requests
from lxml import html
import pandas as pd


# Функция для проверки наличия интернета
def check_internet_connection():
    try:
        # Проверяем соединение с интернетом, отправляя GET-запрос на известный сайт
        response = requests.get('https://www.google.com')
        return response.status_code == 200
    except Exception as e:
        print(f"Произошла ошибка при проверке интернет-соединения: {e}")
        return False


# Функция для проверки ответа от сервера
def check_server_response(response):
    if response.status_code != 200:
        print(f"Ошибка при получении данных: {response.status_code}")
        return False
    return True


# Функция для проверки данных
def check_data(df):
    # Проверяем, что все значения в столбце 'Digital code' соответствуют шаблону целого числа
    if not all(re.match(r'\d+', str(x)) for x in df['Digital code']):
        raise ValueError("Некоторые значения в столбце 'Digital code' не соответствуют шаблону целого числа")

    # Проверяем, что все значения в столбце 'Units' соответствуют шаблону целого числа
    if not all(re.match(r'\d+', str(x)) for x in df['Units']):
        raise ValueError("Некоторые значения в столбце 'Units' не соответствуют шаблону целого числа")

    # Проверяем, что все значения в столбце 'Exchange rate' соответствуют шаблону десятичной дроби
    if not all(re.match(r'^\d+(\.\d+)?$', str(x)) for x in df['Exchange rate']):
        raise ValueError("Некоторые значения в столбце 'Exchange rate' не соответствуют шаблону десятичной дроби")


# Получаем содержимое веб-страницы
if check_internet_connection():
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                      'AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/90.0.4430.93 Safari/537.36'}
    response = requests.get('https://cbr.ru/currency_base/daily/', headers=headers)
    if check_server_response(response):
        # Парсим HTML
        tree = html.fromstring(response.content)
        # Извлекаем таблицу с курсами валют
        base_path = '//div[@class="table-wrapper"]/div[@class="table"]/table[@class="data"]/tbody/tr'
        digital_code = tree.xpath(base_path + '/td[1]/text()')
        currency_code = tree.xpath(base_path + '/td[2]/text()')
        units = tree.xpath(base_path + '/td[3]/text()')
        currency_name = tree.xpath(base_path + '/td[4]/text()')
        exchange_rate = tree.xpath(base_path + '/td[5]/text()')

        # Создаем DataFrame из извлеченных данных
        df = pd.DataFrame({
            'Digital code': digital_code,
            'Currency code': currency_code,
            'Units': units,
            'Currency name': currency_name,
            'Exchange rate': exchange_rate
        })

        # Проверяем данные в DataFrame
        df['Exchange rate'] = df['Exchange rate'].map(lambda x: x.replace(',', '.'))
        try:
            check_data(df)
        except ValueError as e:
            print(f'{e}\nВозможно, получены некорректные данные. '
                  'Попробовать произвести преобразование типов данных?[Y/n]')
            answer = input()
            if answer.lower() != 'y':
                exit(1)

        # Преобразование типов
        df['Digital code'] = df['Digital code'].astype(int)
        df['Units'] = df['Units'].astype(int)
        df['Exchange rate'] = df['Exchange rate'].map(lambda x: Decimal(x))

        # Сохраняем DataFrame в CSV файл
        df.to_csv('currencies.csv', index=False)

        # Закрываем сессию
        response.close()
    else:
        print("Нет соединения с интернетом. Проверьте ваше подключение.")
