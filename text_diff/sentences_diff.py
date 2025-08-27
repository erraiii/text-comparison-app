from difflib import SequenceMatcher
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from text_analysis.text_utils import remove_punctuation, normalize_old_russian

def diff_sentences(sents1, sents2, offs1, offs2):
    added_sentences = []
    removed_sentences = []
    unmodified_sentences = []
    replaced_sentences_sents1 = []  # (text, offset, block_id)
    replaced_sentences_sents2 = []

    matcher = SequenceMatcher(None, sents1, sents2)
    block_id = 0

    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
        if tag == 'replace':
            for idx in range(i1, i2):
                offset = offs1 + sum(len(s) + 1 for s in sents1[:idx])
                replaced_sentences_sents1.append((sents1[idx], offset, block_id))
            for idx in range(j1, j2):
                offset = offs2 + sum(len(s) + 1 for s in sents2[:idx])
                replaced_sentences_sents2.append((sents2[idx], offset, block_id))
            block_id += 1
        elif tag == 'delete':
            for idx in range(i1, i2):
                removed_sentences.append((sents1[idx], offs1 + sum(len(s) + 1 for s in sents1[:idx])))
        elif tag == 'insert':
            for idx in range(j1, j2):
                added_sentences.append((sents2[idx], offs2 + sum(len(s) + 1 for s in sents2[:idx])))
        elif tag == 'equal':
            for idx in range(i1, i2):
                unmodified_sentences.append((sents1[idx], offs1 + sum(len(s) + 1 for s in sents1[:idx])))

    return added_sentences, removed_sentences, unmodified_sentences, replaced_sentences_sents1, replaced_sentences_sents2


def find_similar_sentences(sents1, sents2, threshold=0.5, seq_threshold=0.65): # при различном количестве разбиений
    print('\n===СРАВНИВАНИЕ ПРЕДЛОЖЕНИЙ===')

    similar_sentences = []

    blocks = set(bid for _, _, bid in sents1) & set(bid for _, _, bid in sents2)

    for block_id in blocks:
        block1 = [(text, offset) for text, offset, bid in sents1 if bid == block_id]
        block2 = [(text, offset) for text, offset, bid in sents2 if bid == block_id]

        if not block1 or not block2:
            continue

        texts1 = [normalize_old_russian(remove_punctuation(text)) for text, _ in block1]
        texts2 = [normalize_old_russian(remove_punctuation(text)) for text, _ in block2]
        print("ПРОВЕРКА ПУНКТУАЦИИ")
        print(texts1)
        print(texts2)


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

                print(f'\nПредложение 1: {sen1}')
                print(f'Предложение 2: {sen2}')
                print('Косинусное расстояние',similarity)
                print('SM: ', sequence_sim)
                if similarity >= threshold or (sequence_sim >= seq_threshold and similarity >= 0.35):
                    similar_sentences.append((sen1, sen2, similarity, sequence_sim, idx1, idx2,block_id))
                    print("Похожие")
                print()
    return similar_sentences


def get_offindexes_list(sentences_list):
    offindex = [0]
    for sent in sentences_list:
        offindex.append(offindex[-1] + len(sent) + 1)
    return offindex
