import re
import logging


def split_texts_by_selected_word(t1, t2, sel_words):
    """
    Разбивает тексты по заданному списку слов без их удаления.
    
    Возвращает списки частей текстов после разбиения.
    """
    #pattern = r"\s(?=" + "|".join(map(re.escape, sel_words)) + r")"
    #pattern = r"(?<=\s|^)(?=" + "|".join(map(re.escape, sel_words)) + r")(?!\w)"
    pattern = r"\s(?=(?:" + "|".join(map(re.escape, sel_words)) + r")(?!\w))"

    text1_parts = re.split(pattern, t1)
    text2_parts = re.split(pattern, t2)

    logging.debug("text1_parts: %s", text1_parts)
    logging.debug("text2_parts: %s", text2_parts)

    return text1_parts, text2_parts