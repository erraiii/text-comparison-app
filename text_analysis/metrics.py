from Levenshtein import ratio
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


def levenshtein_similarity(text1, text2):
    """Вычисляет схожесть по алгоритму Левенштейна (0..1)."""
    return round(ratio(text1, text2), 2)


def cosine_measure(text1, text2):
    """Вычисляет косинусную схожесть на основе TF-IDF векторов (0..1)."""
    vectorizer = TfidfVectorizer()
    tfidf_matrix = vectorizer.fit_transform([text1, text2])

    # Вычисление косинусной схожести
    similarity = cosine_similarity(tfidf_matrix[0], tfidf_matrix[1])[0][0]

    return round(similarity, 2)