from collections import Counter


def preprocess_text(text):
    """Приводит текст к нижнему регистру"""
    return text.lower()


def count_word_frequencies(text):
    """Считает частоту слов"""
    return Counter(text.split())


def find_common_words(counter1, counter2):
    """Находит общие слова в двух текстах"""
    return set(counter1.keys()) & set(counter2.keys())