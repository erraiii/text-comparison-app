import re
from collections import Counter
from functools import lru_cache


def preprocess_text(text):
    """Приводит текст к нижнему регистру"""
    return text.lower()


def count_word_frequencies(text):
    """Считает частоту слов"""
    return Counter(text.split())


def find_common_words(counter1, counter2):
    """Находит общие слова в двух текстах"""
    return set(counter1.keys()) & set(counter2.keys())


def remove_punctuation(text):
    """
    Удаляет все знаки препинания из строки.
    Пример: "Привет, мир!" → "Привет мир"
    """
    return re.sub(r'[^\w\s]', '', text)


@lru_cache(maxsize=100_000)
def normalize_old_russian(text):
    """
    Нормализует дореволюционную русскую орфографию (до 1918 г.) к современной.
    Заменяет все устаревшие буквы на их современные аналоги.
    """
    replacements = {
        'ѣ': 'е', 'i': 'и', 'ѵ': 'и', 'ѳ': 'ф',
        'Ѣ': 'Е', 'I': 'И', 'Ѵ': 'И', 'Ѳ': 'Ф'
    }

    # Сначала заменяем все специальные символы
    for old_char, new_char in replacements.items():
        text = text.replace(old_char, new_char)

    # Удаляем твёрдый знак только в конце слов
    words = text.split()
    processed_words = []
    for word in words:
        if word.endswith('ъ') or word.endswith('Ъ'):
            word = word[:-1]
        processed_words.append(word)

    return ' '.join(processed_words)