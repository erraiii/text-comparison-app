from difflib import SequenceMatcher
import logging


def find_diff_words(sent1, sent2):
    """
    Находит различия между словами в двух предложениях.
    
    Возвращает множества добавленных, удаленных слов и пары замен.
    """
    words1 = sent1[0].replace('\n', ' ').split(" ")
    words2 = sent2[0].replace('\n', ' ').split(" ")
    logging.debug("words1: %s", words1)
    logging.debug("words2: %s", words2)

    matcher = SequenceMatcher(None, words1, words2)
    opcodes = matcher.get_opcodes()

    add_diff_words = set()
    rm_diff_words = set()
    replaced_pairs = set()  # Новое множество для хранения пар замен

    idx_offset1 = sent1[1]
    idx_offset2 = sent2[1]

    for tag, i1, i2, j1, j2 in opcodes:
        if tag == 'equal':
            # Пропускаем одинаковые части
            phrase_len = sum(len(word) + 1 for word in words1[i1:i2])
            idx_offset1 += phrase_len
            idx_offset2 += phrase_len
            continue
        elif tag == 'delete':
            # Собираем удаленную фразу целиком
            phrase = " ".join(words1[i1:i2])
            rm_diff_words.add((phrase, idx_offset1))
            idx_offset1 += sum(len(word) + 1 for word in words1[i1:i2])
        elif tag == 'insert':
            # Собираем добавленную фразу целиком
            phrase = " ".join(words2[j1:j2])
            add_diff_words.add((phrase, idx_offset2))
            idx_offset2 += sum(len(word) + 1 for word in words2[j1:j2])
        elif tag == 'replace':
            # Собираем замененные фразы целиком и добавляем их как пару замены
            phrase1 = " ".join(words1[i1:i2])
            phrase2 = " ".join(words2[j1:j2])
            replaced_pairs.add(((phrase1, idx_offset1), (phrase2, idx_offset2)))
            idx_offset1 += sum(len(word) + 1 for word in words1[i1:i2])
            idx_offset2 += sum(len(word) + 1 for word in words2[j1:j2])
            logging.debug("replace: '%s' -> '%s'", phrase1, phrase2)

    return add_diff_words, rm_diff_words, replaced_pairs


def find_add_rem_words(similar_sentences):
    """
    Обрабатывает похожие предложения и извлекает различия на уровне слов.
    
    Возвращает множества добавленных, удаленных слов и пары замен.
    """
    removed_words_res = set()  # полученные удаленные слова
    added_words_res = set()  # полученные добавленные слова
    replaced_pairs_res = set()  # полученные пары замен

    # Группируем предложения по block_id
    blocks = {}
    for sentence1, sentence2, _, _, idx1, idx2, block_id in similar_sentences:
        if block_id not in blocks:
            blocks[block_id] = []
        blocks[block_id].append((sentence1, sentence2, idx1, idx2))

    # Обрабатываем каждый блок замен
    for block_sentences in blocks.values():
        for sentence1, sentence2, idx1, idx2 in block_sentences:
            # Находим изменения в паре предложений
            added, removed, replacements = find_diff_words((sentence1, idx1), (sentence2, idx2))
            logging.debug('Добавленные: %s', added)
            logging.debug('Удаленные: %s', removed)
            logging.debug('Замены: %s', replacements)

            # Добавляем замены
            for rm, add in replacements:
                replaced_pairs_res.add((rm, add))
            # Добавляем чистые удаления и добавления
            removed_words_res.update(removed)
            added_words_res.update(added)

    return added_words_res, removed_words_res, replaced_pairs_res
