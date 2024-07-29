# Напишите сценарий на языке Python, который предложит пользователю ввести интересующую
# его категорию (например, кофейни, музеи, парки и т.д.).
# Используйте API Foursquare для поиска заведений в указанной категории.
# Получите название заведения, его адрес и рейтинг для каждого из них.
# Скрипт должен вывести название и адрес и рейтинг каждого заведения в консоль.


import requests


CITIES = {
    'Moscow': 'Москва',
    'Saint Petersburg, RU': 'Санкт-Петербург (Россия)',
    'Saint Petersburg, US': 'Санкт-Петербург (США)',
    'Syktyvkar': 'Сыктывкар',
}

# https://docs.foursquare.com/data-products/docs/categories
CATEGORIES = {
    '': 'Кафе',
    'Factory': 'Производства',
    'Barbershop': 'Барбершопы',
    'Cafe': 'Кафе',
}


def get_choice(title, menu_dict):
    """
    Принимает словарь с ключами пунктов меню и их названием,
    выводит меню на экран, принимает ответ пользователя
    и возвращает ключ выбранного пункта
    Аргументы:
        menu_dict - словарь пунктов меню вида ключ: название
    Возвращает:
        ключ выбранного пункта меню
    """
    counter = 1
    chooses = []
    print(f'\n {title}')
    for key, value in menu_dict.items():
        print(f'{counter} - {value}')
        chooses.append(key)
        counter += 1
    while True:
        try:
            return chooses[int(input('Выберите пункт меню >>')) - 1]
        except Exception as err:
            print(f'Не могу обработать ваш выбор: {err}')


def get_foursquare_data(city, category, limit=10):
    """
    Запрашивает данные в API FourSquare в заданном городе по заведениям
    в выбранной категории и возвращает их в виде списка словарей
    Аргументы:
        city - название города
        category - название категории
        limit - максимальное количество возвращаемых объектов (по-умолчанию 10)
    Возвращает:
        ответ API в случае успеха или None
    """
    api_url = 'https://api.foursquare.com/v3/places/search'
    headers = {
        'Accept': 'application/json',
        'Authorization': 'secret',
    }
    params = {
        'near': city,
        'limit': limit,
        'query': category,
        'fields': 'name,location,rating'
    }
    response = requests.get(api_url, params=params, headers=headers)

    if response.status_code == 200:
        return response.json()['results']
    return None


user_city = get_choice('Выберите город', CITIES)
user_category = get_choice('Выберите категорию', CATEGORIES)
data = get_foursquare_data(user_city, user_category)
if data is not None:
    for record in data:
        location_name = record.get('name')
        location_address = record.get('location').get('formatted_address')
        location_rating = record.get('rating', 'Нет данных')
        print(f'Объект: {location_name}\n\tАдрес: {location_address}\n\tРейтинг: {location_rating}\n')
else:
    print('Ошибка в получении данных из API')
