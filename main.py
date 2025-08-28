import argparse
import logging
from text_analysis import preprocess_text, cosine_measure, levenshtein_similarity
from text_analysis import select_split_words, split_texts_by_selected_word, normalize_old_russian
from text_diff import find_add_rem_words
from visualization import show_highlighted_text
from text_diff import diff_sentences, find_similar_sentences


def setup_logging(verbose: bool) -> None:
    logging.basicConfig(
        level=logging.DEBUG if verbose else logging.INFO,
        format='%(asctime)s %(levelname)s %(message)s'
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Сравнение двух текстов и визуализация различий")
    parser.add_argument("text1", nargs="?", default="text1.txt", help="Путь к первому текстовому файлу")
    parser.add_argument("text2", nargs="?", default="text2.txt", help="Путь ко второму текстовому файлу")
    parser.add_argument("--no-gui", action="store_true", help="Не показывать GUI, только метрики")
    parser.add_argument("--verbose", action="store_true", help="Подробные логи")
    return parser.parse_args()


def read_text(path: str) -> str:
    with open(path, encoding="utf-8") as f:
        return f.read()


def compute_diffs(raw_text1: str, raw_text2: str):
    text1 = preprocess_text(raw_text1)
    text2 = preprocess_text(raw_text2)

    selected_word = select_split_words(text1, text2)
    text1_p, text2_p = split_texts_by_selected_word(text1, text2, selected_word)

    added, removed, unmodif, replaced1, replaced2 = diff_sentences(text1_p, text2_p, 0, 0)
    sim_sents = find_similar_sentences(replaced1, replaced2)
    added_words_res, removed_words_res, replaced_pairs = find_add_rem_words(sim_sents)

    final_added = set()
    final_removed = set()

    for sent, idx in added:
        words = sent.split()
        offset = idx
        for word in words:
            final_added.add((word, offset))
            offset += len(word) + 1

    for sent, idx in removed:
        words = sent.split()
        offset = idx
        for word in words:
            final_removed.add((word, offset))
            offset += len(word) + 1

    final_added.update(added_words_res)
    final_removed.update(removed_words_res)

    if replaced_pairs:
        for (word1, idx1), (word2, idx2) in replaced_pairs:
            if (word1, idx1) in final_removed:
                final_removed.remove((word1, idx1))
            if (word2, idx2) in final_added:
                final_added.remove((word2, idx2))

    return final_added, final_removed, replaced_pairs, text1, text2


def compute_metrics(text1: str, text2: str, raw1: str, raw2: str):
    lev_sim = levenshtein_similarity(text1, text2)
    cos_sim = cosine_measure(normalize_old_russian(raw1), normalize_old_russian(raw2))
    return lev_sim, cos_sim


def main() -> None:
    args = parse_args()
    setup_logging(args.verbose)

    logging.info("Чтение файлов")
    raw1 = read_text(args.text1)
    raw2 = read_text(args.text2)

    logging.info("Вычисление различий")
    final_added, final_removed, replaced_pairs, text1, text2 = compute_diffs(raw1, raw2)

    logging.info("Метрики")
    lev_sim, cos_sim = compute_metrics(text1, text2, raw1, raw2)
    logging.info("Левенштейн: %s", lev_sim)
    logging.info("Косинусная мера: %s", cos_sim)

    if not args.no_gui:
        show_highlighted_text(raw1, raw2, final_added, final_removed, lev_sim, cos_sim, replaced_pairs)


if __name__ == "__main__":
    main()