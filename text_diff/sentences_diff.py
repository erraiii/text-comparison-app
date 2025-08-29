from difflib import SequenceMatcher
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from text_analysis.text_utils import remove_punctuation, normalize_old_russian
import logging


def _prefix_offsets(items):
    """Вычисляет префиксные суммы длин элементов для быстрого получения смещений."""
    offsets = [0]
    for s in items:
        offsets.append(offsets[-1] + len(s) + 1)
    return offsets


def diff_sentences(sents1, sents2, offs1, offs2):
    """
    Находит различия между двумя последовательностями предложений.
    
    Возвращает списки добавленных, удаленных, неизмененных и замененных предложений.
    """
    added_sentences = []
    removed_sentences = []
    unmodified_sentences = []
    replaced_sentences_sents1 = []  # (text, offset, block_id)
    replaced_sentences_sents2 = []

    matcher = SequenceMatcher(None, sents1, sents2)
    block_id = 0

    # Префиксные суммы для O(1) получения смещения
    pref1 = _prefix_offsets(sents1)
    pref2 = _prefix_offsets(sents2)

    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
        if tag == 'replace':
            for idx in range(i1, i2):
                offset = offs1 + pref1[idx]
                replaced_sentences_sents1.append((sents1[idx], offset, block_id))
            for idx in range(j1, j2):
                offset = offs2 + pref2[idx]
                replaced_sentences_sents2.append((sents2[idx], offset, block_id))
            block_id += 1
        elif tag == 'delete':
            for idx in range(i1, i2):
                removed_sentences.append((sents1[idx], offs1 + pref1[idx]))
        elif tag == 'insert':
            for idx in range(j1, j2):
                added_sentences.append((sents2[idx], offs2 + pref2[idx]))
        elif tag == 'equal':
            for idx in range(i1, i2):
                unmodified_sentences.append((sents1[idx], offs1 + pref1[idx]))

    return added_sentences, removed_sentences, unmodified_sentences, replaced_sentences_sents1, replaced_sentences_sents2


def find_similar_sentences(sents1, sents2, threshold=0.5, seq_threshold=0.65):
    """
    Находит похожие предложения между двумя наборами предложений.
    
    Использует TF-IDF и SequenceMatcher для определения схожести.
    """
    logging.debug('=== СРАВНИВАНИЕ ПРЕДЛОЖЕНИЙ ===')

    similar_sentences = []

    blocks = set(bid for _, _, bid in sents1) & set(bid for _, _, bid in sents2)

    for block_id in blocks:
        block1 = [(text, offset) for text, offset, bid in sents1 if bid == block_id]
        block2 = [(text, offset) for text, offset, bid in sents2 if bid == block_id]

        if not block1 or not block2:
            continue

        texts1 = [normalize_old_russian(remove_punctuation(text)) for text, _ in block1]
        texts2 = [normalize_old_russian(remove_punctuation(text)) for text, _ in block2]
        logging.debug("ПРОВЕРКА ПУНКТУАЦИИ")
        logging.debug("texts1: %s", texts1)
        logging.debug("texts2: %s", texts2)


        all_texts = texts1 + texts2
        vectorizer = TfidfVectorizer().fit(all_texts)
        tfidf_matrix = vectorizer.transform(all_texts)
        tfidf_sents1 = tfidf_matrix[:len(texts1)]
        tfidf_sents2 = tfidf_matrix[len(texts1):]

        sim_matrix = cosine_similarity(tfidf_sents1, tfidf_sents2)

        for i, (sen1, idx1) in enumerate(block1):
            for j, (sen2, idx2) in enumerate(block2):
                similarity = sim_matrix[i, j]
                sent1 = normalize_old_russian(remove_punctuation(sen1))
                sent2 = normalize_old_russian(remove_punctuation(sen2))
                sequence_sim = SequenceMatcher(None, sent1, sent2).ratio()

                logging.debug('Предложение 1: %s', sen1)
                logging.debug('Предложение 2: %s', sen2)
                logging.debug('Косинусная схожесть: %s', similarity)
                logging.debug('SM: %s', sequence_sim)
                if similarity >= threshold or (sequence_sim >= seq_threshold and similarity >= 0.35):
                    similar_sentences.append((sen1, sen2, similarity, sequence_sim, idx1, idx2,block_id))
                    logging.debug("Похожие")
    return similar_sentences


def get_offindexes_list(sentences_list):
    """Вычисляет список смещений для последовательности предложений."""
    offindex = [0]
    for sent in sentences_list:
        offindex.append(offindex[-1] + len(sent) + 1)
    return offindex
