# text_diff/__init__.py
from text_diff.sentences_diff import (diff_sentences, find_similar_sentences, get_offindexes_list) #,
                                      #find_add_rem_sim_sents, find_unique_diff_sents)
from text_diff.words_diff import find_diff_words, find_add_rem_words

__all__ = ["diff_sentences", "find_similar_sentences", "get_offindexes_list",
           #"find_add_rem_sim_sents", "find_unique_diff_sents",
           "find_diff_words", "find_add_rem_words"]