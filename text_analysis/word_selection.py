from text_analysis.text_utils import preprocess_text, count_word_frequencies, find_common_words


def select_split_word(text1, text2, target_length=100):
    """Выбирает слова для разделения текста"""
    words1 = preprocess_text(text1)
    words2 = preprocess_text(text2)
    print(words1, words2)

    counter1 = count_word_frequencies(words1)
    counter2 = count_word_frequencies(words2)

    common_words = find_common_words(counter1, counter2)

    differences = {word: abs(counter1[word] - counter2[word]) for word in common_words}
    sorted_diffs = sorted(differences.items(), key=lambda x: x[1])

    total_length = len(text1) + len(text2)
    target_word_freq = total_length // target_length
    selected_word = None

    for word, diff in sorted_diffs:
        word_freq_sum = counter1[word] + counter2[word]

        if (word_freq_sum >= target_word_freq * 0.8
                and word_freq_sum <= target_word_freq * 1.2):
            selected_word = word
            break
        elif word_freq_sum >= target_word_freq * 1.2:
            selected_word = word
            break
        else:
            selected_word = word

    return selected_word, differences
