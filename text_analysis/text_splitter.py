import re


def split_texts_by_selected_word(t1, t2, sel_word):
    pattern = r"\s(?=" + re.escape(sel_word) + r")"  # Выражение для совпадения с пробелом перед selected_word
    text1_parts = re.split(pattern, t1)
    text2_parts = re.split(pattern, t2)
    return text1_parts, text2_parts