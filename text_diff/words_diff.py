from difflib import SequenceMatcher


def find_diff_words(sent1, sent2):
    words1 = sent1[0].split(" ")
    words2 = sent2[0].split(" ")

    matcher = SequenceMatcher(None, words1, words2)
    opcodes = matcher.get_opcodes()

    add_diff_words = set()
    rm_diff_words = set()

    idx_offset1 = sent1[1]
    idx_offset2 = sent2[1]

    for tag, i1, i2, j1, j2 in opcodes:
        if tag == 'equal':
            idx_offset1 += sum(len(word) + 1 for word in words1[i1:i2])
            idx_offset2 += sum(len(word) + 1 for word in words2[j1:j2])
            continue
        elif tag == 'delete':
            for word in words1[i1:i2]:
                rm_diff_words.add((word, idx_offset1))
                idx_offset1 += len(word) + 1
        elif tag == 'insert':
            for word in words2[j1:j2]:
                add_diff_words.add((word, idx_offset2))
                idx_offset2 += len(word) + 1
        elif tag == 'replace':
            for word in words1[i1:i2]:
                rm_diff_words.add((word, idx_offset1))
                idx_offset1 += len(word) + 1
            for word in words2[j1:j2]:
                add_diff_words.add((word, idx_offset2))
                idx_offset2 += len(word) + 1

    return add_diff_words, rm_diff_words


def find_add_rem_words(similar_sentences):
    removed_words_res = set()  # полученные удаленные слова
    added_words_res = set()  # полученные добавленные слова
    intersection_dict = {}
    similar_sentences_count = {}

    for sentence1, sentence2, _, ind1, ind2 in similar_sentences:
        pair_key1 = (ind1, 1)  # Ключом будет кортеж из индексов предложений
        pair_key2 = (ind2, 2)
        if pair_key1 in similar_sentences_count:
            similar_sentences_count[pair_key1] += 1
        else:
            similar_sentences_count[pair_key1] = 1

        if pair_key2 in similar_sentences_count:
            similar_sentences_count[pair_key2] += 1
        else:
            similar_sentences_count[pair_key2] = 1

    print("Sim sent count: ", similar_sentences_count)

    for sentence1, sentence2, _, idx1, idx2 in similar_sentences:
        added, removed = find_diff_words((sentence1, idx1), (sentence2, idx2))
        pair_key1 = (idx1, 1)
        pair_key2 = (idx2, 2)
        print('\nРассматриваемые предложения:')
        print(sentence1)
        print(sentence2)
        if similar_sentences_count[pair_key1] != 1:
            if pair_key1 in intersection_dict:
                intersection_dict[pair_key1] = intersection_dict[pair_key1].intersection(removed)
                if pair_key2 in intersection_dict:
                    intersection_dict[pair_key2] = intersection_dict[pair_key2].union(
                        set([(sentence2.split()[0], idx2)]))
                else:
                    intersection_dict[pair_key2] = set([(sentence2.split()[0], idx2)])
            else:
                intersection_dict[pair_key1] = set(removed)
        else:
            removed_words_res = removed_words_res.union(removed)

        if similar_sentences_count[pair_key2] != 1:
            if pair_key2 in intersection_dict:
                intersection_dict[pair_key2] = intersection_dict[pair_key2].intersection(added)
                if pair_key1 in intersection_dict:
                    intersection_dict[pair_key1] = intersection_dict[pair_key1].union(
                        set([(sentence1.split()[0], idx1)]))
                else:
                    intersection_dict[pair_key1] = set([(sentence1.split()[0], idx1)])
            else:
                intersection_dict[pair_key2] = set(added)
        else:
            added_words_res = added_words_res.union(added)

        print('\nДобавленные слова: ')
        print(added)
        print('Удаленные слова:')
        print(removed)
        # Добавляем пересечения в итоговые результаты
    for key, words in intersection_dict.items():
        if key[1] == 1:  # Удаленные слова
            removed_words_res.update(words)
        else:  # Добавленные слова
            added_words_res.update(words)
    print("Intersection dict:", intersection_dict)
    return added_words_res, removed_words_res
