import pymongo
import json
from pymongo import errors

# Подключение к MongoDB
client = pymongo.MongoClient("mongodb://localhost:27017/")

# Получаем базу данных
db_name = "books"
db = client[db_name]

# Получаем коллекцию
collection_name = "books_collection"
collection = db[collection_name]

def load_data():
    """Загружает данные из JSON файла в коллекцию"""
    try:
        with open("books.json", encoding='utf-8') as file:
            data = json.load(file)
        collection.insert_many(data, ordered=False, upsert=True)
    except FileNotFoundError as e:
        print("Ошибка при чтении файла: ", e)
    except json.decoder.JSONDecodeError as e:
        print("Некорректный JSON: ", e)
    else:
        print(f"Добавлено {len(result.inserted_ids)} документов.")

def search_by_title(title):
    """Поиск книги по названию"""
    result = collection.find_one({"name": title})
    if result:
        print(f"Книга '{title}' найдена.")
        # Здесь можно вывести информацию о книге
        print(result)
    else:
        print(f"Книга с названием '{title}' не найдена в базе данных.")

def search_by_price(min_price, max_price):
    """Поиск книг по диапазону цен"""
    if min_price <= max_price:
        results = list(collection.find({"price": {"$gte": min_price, "$lte": max_price}}))
        print(f"Найдено {len(results)} книг в диапазоне цен от {min_price} до {max_price}.")
    else:
        print("Минимальная цена должна быть меньше максимальной.")

def search_by_description(search_term):
    """Поиск книг по части описания"""
    results = list(collection.find({"description": {"$regex": search_term}}))
    if len(results) > 0:
        print(f"Найдено {len(results)} книг, содержащих '{search_term}' в описании.")
    else:
        print("Ни одна книга не содержит строку '{}' в описании.".format(search_term))

def main_menu():
    """Текстовое меню для выбора операции"""
    while True:
        print("Меню:")
        print("1. Загрузить данные из JSON")
        print("2. Поиск книги по названию")
        print("3. Поиск книг по диапазону цен")
        print("4. Поиск книг по части описания")
        print("5. Выход из программы")
        choice = int(input("Выберите операцию: "))
        if choice == 1:
            load_data()
        elif choice == 2:
            title = input("Введите название книги: ")
            search_by_title(title)
        elif choice == 3:
            min_price = float(input("Введите минимальную цену: "))
            max_price = float(input("Введите максимальную цену: "))
            search_by_price(min_price, max_price)
        elif choice == 4:
            search_term = input("Введите часть описания книги для поиска: ")
            search_by_description(search_term)
        elif choice == 5:
            break
        else:
            print("Неверный выбор. Попробуйте снова.")

# Запуск программы
main_menu()

# Закрываем подключение к базе данных
client.close()
