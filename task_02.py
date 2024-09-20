
"""
Напишіть Python-скрипт, який завантажує текст із заданої URL-адреси,
аналізує частоту використання слів у тексті за допомогою парадигми
MapReduce і візуалізує топ-слова з найвищою частотою використання
у тексті.

Імпортуйте необхідні модулі (matplotlib та інші).
Візьміть код реалізації MapReduce з конспекту.
Створіть функцію visualize_top_words для візуалізації результатів.
У головному блоці коду отримайте текст за URL, застосуйте
MapReduce та візуалізуйте результати.
"""

import matplotlib.pyplot as plt
import string
from concurrent.futures import ThreadPoolExecutor
from collections import defaultdict
import requests


def get_text(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.text
    except requests.RequestException as e:
        print("error: ", e)


def remove_punctuation(text):
    return text.translate(str.maketrans("", "", string.punctuation))


def map_function(word):
    return word, 1


def shuffle_function(mapped_values):
    shuffled = defaultdict(list)
    for key, value in mapped_values:
        shuffled[key].append(value)
    return shuffled.items()


def reduce_function(key_values):
    key, values = key_values
    return key, sum(values)


def map_reduce(text, search_words=None):
    text = remove_punctuation(text)
    words = text.split()

    if search_words:
        words = [word for word in words if word in search_words]

    with ThreadPoolExecutor() as executor:
        mapped_values = list(executor.map(map_function, words))

    shuffled_values = shuffle_function(mapped_values)

    with ThreadPoolExecutor() as executor:
        reduced_values = list(executor.map(reduce_function, shuffled_values))

    return dict(reduced_values)


def sort_dict_by_value(d: dict, reverse=True, limit=None) -> dict:
    sorted_items = sorted(d.items(), key=lambda item: item[1], reverse=reverse)
    if limit:
        return dict(sorted_items[:limit])
    else:
        return sorted_items


def visualize_top_words(data: dict, title, xlabel, ylabel):
    plt.figure(figsize=(10, 6))
    plt.bar(data.keys(), data.values(), color='orange')
    plt.title(title)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()


if __name__ == "__main__":

    # url = "https://gutenberg.net.au/ebooks01/0100021.txt"
    
    url = input("Entry url: ")
    text = get_text(url)

    if text:
        result = map_reduce(text)
        most_recent = sort_dict_by_value(result, limit=10)
        visualize_top_words(most_recent, title="Most recent words in text",
                       xlabel="Words", ylabel="Frequency")
    else:
        print("Помилка: Не вдалося отримати вхідний текст.")
