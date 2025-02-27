from text_analysis import preprocess_text, cosine_measure, levenshtein_similarity
from text_analysis import select_split_word, split_texts_by_selected_word
from text_diff import (find_add_rem_sim_sents, find_unique_diff_sents,
                       find_add_rem_words)
from visualization import show_highlighted_text


file1 = open("text1.txt", encoding="utf-8")
file2 = open("text2.txt", encoding="utf-8")
text_1 = file1.read()
text_2 = file2.read()
text1 = preprocess_text(text_1)
text2 = preprocess_text(text_2)
#print(text1, 'text 1')
#print(text2, 'text 2')

selected_word, differences = select_split_word(text1, text2)
text1_p, text2_p = split_texts_by_selected_word(text1, text2, selected_word)
# print(text1_p, 'text 1')
# print(text2_p, 'text 2')

added_sentences_set, removed_sentences_set, similar_sentences = (
    find_add_rem_sim_sents(text1_p, text2_p))

final_added, final_removed = find_unique_diff_sents(added_sentences_set, removed_sentences_set, similar_sentences)
added_words_res, removed_words_res = find_add_rem_words(similar_sentences)

print('Все добавленные слова:', added_words_res)
print('Все удаленные слова:', removed_words_res)
final_removed = final_removed.union(removed_words_res)
final_added = final_added.union(added_words_res)
lev_sim = levenshtein_similarity(text1, text2)
cos_sim = cosine_measure(text_1, text_2)
print("Lev:", lev_sim)
print("Cos:", cos_sim)
show_highlighted_text(text_1, text_2, final_added, final_removed, lev_sim, cos_sim)