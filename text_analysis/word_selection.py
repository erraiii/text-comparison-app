import re
import math
import random
from math import log
from text_analysis.text_utils import preprocess_text, count_word_frequencies, find_common_words
import logging


def max_allowed_diff(avg_freq, c=0.5):
    """Вычисляет максимально допустимое относительное отклонение частот."""
    return min(1.0, c / math.sqrt(avg_freq))


def estimate_sample_size(p, confidence=0.98):
    """
    Вычисляет необходимое число случайных выборок, чтобы хотя бы одна из них
    с вероятностью confidence попала в "хорошую" (по p) комбинацию.
    Формула: n ≥ log(1 - confidence) / log(1 - p)
    """
    if p <= 0.0:
        return 1  # минимально 1
    return math.ceil(log(1 - confidence) / log(1 - p))


def sample_combinations(items, k, max_samples):
    """
    Генерирует случайные уникальные комбинации из items длины k.
    """
    if len(items) < k:
        return []

    seen = set()
    samples = []
    attempts = 0
    max_attempts = max_samples * 10

    while len(samples) < max_samples and attempts < max_attempts:
        combo = tuple(sorted(random.sample(items, k)))
        if combo not in seen:
            seen.add(combo)
            samples.append(combo)
        attempts += 1

    return samples


def estimate_p(candidate_words, desired_splits, text1, text2, sample_size=100, threshold=10000):
    """
    Оценивает вероятность p (что случайная комбинация даст хорошее разбиение).
    threshold - порог дисперсии, при котором считаем разбиение удачным.
    """
    good = 0
    for _ in range(sample_size):
        combo = random.sample(candidate_words, desired_splits)
        score1 = evaluate_split_quality_for_words(combo, text1)
        score2 = evaluate_split_quality_for_words(combo, text2)
        if (score1 + score2) < threshold:
            good += 1
    return good / sample_size


def evaluate_split_quality_for_words(words, text, total_len=None):
    """
    Оценивает равномерность разбиения текста по вхождениям заданного набора слов.
    Чем меньше возвращаемое значение — тем лучше разбиение. Использует дисперсию.
    """
    if total_len is None:
        total_len = len(text)

    # Получаем позиции всех вхождений каждого слова
    positions = []
    for word in words:
        positions.extend(m.start() for m in re.finditer(r'\b' + re.escape(word) + r'\b', text))

    if not positions:
        return float("inf")  # нет вхождений — плохое разбиение

    all_positions = [0] + sorted(positions) + [total_len]
    fragment_lengths = [all_positions[i + 1] - all_positions[i] for i in range(len(all_positions) - 1)]

    avg_len = total_len / len(fragment_lengths)
    variance = sum((l - avg_len) ** 2 for l in fragment_lengths) / len(fragment_lengths)
    return variance


def select_split_words(text1, text2, target_length=50, max_global_limit=100):
    """
    Выбирает набор слов, оптимально разбивающих тексты на фрагменты.
    Использует качество разбиения (по дисперсии) для оценки.
    """

    words1 = preprocess_text(text1)
    words2 = preprocess_text(text2)

    counter1 = count_word_frequencies(words1)
    counter2 = count_word_frequencies(words2)
    total_words = len(words1.split()) + len(words2.split())
    desired_splits = max(3, total_words // (2 * target_length))

    common_words = find_common_words(counter1, counter2)

    candidates = []
    for word in common_words:
        f1 = counter1[word]
        f2 = counter2[word]
        avg_f = (f1 + f2) / 2
        if avg_f == 0:
            continue

        rel_diff = abs(f1 - f2) / avg_f
        if rel_diff <= max_allowed_diff(avg_f):
            total_f = f1 + f2
            candidates.append((word, total_f, avg_f))

    # Отсортировать по редкости и общему количеству
    candidates.sort(key=lambda x: (x[2], x[1]))  # avg_freq, total_freq
    candidate_words = [word for word, _, _ in candidates]

    if len(candidate_words) < desired_splits:
        return sorted(common_words, key=lambda w: counter1[w] + counter2[w])

    est_p = 0.05 # Эмпирическая вероятность успеха одной комбинации
    max_tries = min(estimate_sample_size(est_p, confidence=0.95), max_global_limit)
    logging.debug('Max tries: %s', max_tries)

    combos = sample_combinations(candidate_words, desired_splits, max_tries)

    best_score = float("inf")
    best_set = []
    logging.debug('combos: %s', combos)
    for combo in combos:
        score1 = evaluate_split_quality_for_words(combo, text1)
        score2 = evaluate_split_quality_for_words(combo, text2)
        total_score = score1 + score2
        if total_score < best_score:
            best_score = total_score
            best_set = combo

    # est_p = estimate_p(candidate_words, desired_splits, text1, text2)
    # print("ОЦЕНКА ДЛЯ P", est_p)

    logging.debug("Лучший набор: %s", best_set)
    score1 = evaluate_split_quality_for_words(best_set, text1)
    score2 = evaluate_split_quality_for_words(best_set, text2)
    logging.debug("score1: %s", score1)
    logging.debug("score2: %s", score2)
    if not best_set:
        if len(common_words) < desired_splits:
            return sorted(common_words, key=lambda w: counter1[w] + counter2[w])
        else:
            return sorted(common_words, key=lambda w: counter1[w] + counter2[w])[:desired_splits]

    return list(best_set)
