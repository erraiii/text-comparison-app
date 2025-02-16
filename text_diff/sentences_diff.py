from difflib import SequenceMatcher


def diff_sentences(sents1, sents2, offs1, offs2):
    added_sentences = []
    removed_sentences = []
    unmodified_sentences = []

    matcher = SequenceMatcher(None, sents1, sents2)

    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
        if tag == 'replace':
            for idx in range(i1, i2):
                removed_sentences.append((sents1[idx], offs1 + sum(len(s) + 1 for s in sents1[:idx])))
            for idx in range(j1, j2):
                added_sentences.append((sents2[idx], offs2 + sum(len(s) + 1 for s in sents2[:idx])))
        elif tag == 'delete':
            for idx in range(i1, i2):
                removed_sentences.append((sents1[idx], offs1 + sum(len(s) + 1 for s in sents1[:idx])))
        elif tag == 'insert':
            for idx in range(j1, j2):
                added_sentences.append((sents2[idx], offs2 + sum(len(s) + 1 for s in sents2[:idx])))
        elif tag == 'equal':
            for idx in range(i1, i2):
                unmodified_sentences.append((sents1[idx], offs1 + sum(len(s) + 1 for s in sents1[:idx])))

    return added_sentences, removed_sentences, unmodified_sentences


def find_similar_sentences(sents1, sents2, threshold=0.5):
    sim_sentences = []

    for sen1, sen1_index in sents1:
        for sen2, sen2_index in sents2:
            similarity_ratio = SequenceMatcher(None, sen1, sen2).ratio()

            # Проверяем степень сходства предложений по пороговому значению
            if similarity_ratio > threshold:
                sim_sentences.append((sen1, sen2, similarity_ratio, sen1_index, sen2_index))

    return sim_sentences


def get_offindexes_list(sentences_list):
    offindex = [0]
    for sent in sentences_list:
        offindex.append(offindex[-1] + len(sent) + 1)
    return offindex


def find_add_rem_sim_sents(text1_parts, text2_parts, differences, selected_word):
    offsets_text1 = get_offindexes_list(text1_parts)
    offsets_text2 = get_offindexes_list(text2_parts)

    removed_sentences_set = set()
    added_sentences_set = set()

    similar_sentences = []

    n = differences[selected_word] * 2 + 1

    for i, sentence1 in enumerate(text1_parts):
        start_index = max(0, i - n)
        end_index = min(len(text2_parts) - 1, i + n)

        sentences1 = [text1_parts[i]]
        sentences2 = text2_parts[start_index:end_index + 1]

        # Используем заранее вычисленные индексы
        offset1 = offsets_text1[i]
        offset2 = offsets_text2[start_index]

        added, removed, unmodified = diff_sentences(sentences1, sentences2, offset1, offset2)

        for sentence, position in added:
            added_sentences_set.add((sentence, position))

        for sentence, position in removed:
            removed_sentences_set.add((sentence, position))

        new_data = find_similar_sentences(removed, added)
        similar_sentences.extend(new_data)

    print('\nРезультат:')
    print("Добавленные предложения:")
    for sentence, position in added_sentences_set:
        print(f"+ {sentence} - Индекс: {position}")
    print("Удаленные предложения:")
    for sentence, position in removed_sentences_set:
        print(f"- {sentence} - Индекс: {position}")

    return added_sentences_set, removed_sentences_set, similar_sentences


def find_unique_diff_sents(add_sent_set, rem_sent_set, similar_sentences):
    matched_removed = set()
    matched_added = set()

    for s1, s2, similarity, ind1, ind2 in similar_sentences:
        matched_removed.add(s1)  # Удаленные предложения с похожими
        matched_added.add(s2)

        print(f"\nSimilarity: {similarity:.3f}\nText 1: {s1} Index: {ind1}\nText 2: {s2} Index: {ind2}")

    final_removed = {(s, p) for (s, p) in rem_sent_set if s not in matched_removed}
    final_added = {(s, p) for (s, p) in add_sent_set if s not in matched_added}

    print("Уникальные удаленные предложения (без похожих):")
    for s, p in final_removed:
        print(f"- {s} (Position: {p})")

    print("\nУникальные добавленные предложения (без похожих):")
    for s, p in final_added:
        print(f"+ {s} (Position: {p})")

    return final_added, final_removed
