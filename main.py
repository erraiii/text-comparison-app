from text_analysis import preprocess_text, cosine_measure, levenshtein_similarity
from text_analysis import select_split_words, split_texts_by_selected_word, normalize_old_russian
from text_diff import find_add_rem_words
from visualization import show_highlighted_text
from text_diff import diff_sentences, find_similar_sentences, find_diff_words


file1 = open("text1.txt", encoding="utf-8")
file2 = open("text2.txt", encoding="utf-8")
text_1 = file1.read()
text_2 = file2.read()
text1 = preprocess_text(text_1)
text2 = preprocess_text(text_2)

# Разбиваем тексты на предложения
selected_word = select_split_words(text1, text2)
text1_p, text2_p = split_texts_by_selected_word(text1, text2, selected_word)

# Находим различия между предложениями
added, removed, unmodif, replaced1, replaced2 = diff_sentences(text1_p, text2_p, 0, 0)

# Находим похожие предложения среди замененных
sim_sents = find_similar_sentences(replaced1, replaced2)

# Анализируем изменения в похожих предложениях
added_words_res, removed_words_res, replaced_pairs = find_add_rem_words(sim_sents)

print("\nРезультаты анализа:")
print("Добавленные слова:", added_words_res)
print("Удаленные слова:", removed_words_res)
print("Замененные пары слов:", replaced_pairs)

# Добавляем слова из полностью добавленных/удаленных предложений
final_added = set()
final_removed = set()

# Обрабатываем полностью добавленные предложения
for sent, idx in added:
    words = sent.split()
    for i, word in enumerate(words):
        # Вычисляем позицию слова в тексте
        position = idx + sum(len(w) + 1 for w in words[:i])
        final_added.add((word, position))

# Обрабатываем полностью удаленные предложения
for sent, idx in removed:
    words = sent.split()
    for i, word in enumerate(words):
        # Вычисляем позицию слова в тексте
        position = idx + sum(len(w) + 1 for w in words[:i])
        final_removed.add((word, position))

# Добавляем результаты анализа похожих предложений
final_added.update(added_words_res)
final_removed.update(removed_words_res)

# Убираем замененные слова из множеств добавленных и удаленных
if replaced_pairs:
    for (word1, idx1), (word2, idx2) in replaced_pairs:
        if (word1, idx1) in final_removed:
            final_removed.remove((word1, idx1))
        if (word2, idx2) in final_added:
            final_added.remove((word2, idx2))

# Вычисляем метрики схожести
lev_sim = levenshtein_similarity(text1, text2)
cos_sim = cosine_measure(normalize_old_russian(text_1), normalize_old_russian(text_2))

print("\nМетрики схожести:")
print("Левенштейн:", lev_sim)
print("Косинусная мера:", cos_sim)

show_highlighted_text(text_1, text_2, final_added, final_removed, lev_sim, cos_sim, replaced_pairs)

file1.close()
file2.close()