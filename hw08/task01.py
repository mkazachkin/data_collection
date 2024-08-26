import inspect
import os
import pandas as pd


def load_data_from_csv(relative_file_path):
    """Загружает данные из CSV файла и возвращает датафрейм."""
    script_dir = os.path.dirname(inspect.getfile(inspect.currentframe()))
    abs_file_path = os.path.join(script_dir, relative_file_path)
    df = pd.read_csv(abs_file_path)
    return df


def calculate_empty_percentages(df):
    """Рассчитывает и выводит процент пустых значений для каждого столбца."""
    empty_percentages = df.isnull().mean() * 100
    empty_columns = empty_percentages[empty_percentages > 0].index
    print(f"Столбцы с пустыми значениями:")
    for column in empty_columns:
        print(f"{column}: {empty_percentages[column]:.2f}%")


df = load_data_from_csv('data/train.csv')
calculate_empty_percentages(df)