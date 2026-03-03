import os
import math
import pymorphy3
from collections import defaultdict


class VectorSearchEngine:

    def __init__(self, tfidf_dir):
        self.tfidf_dir = tfidf_dir
        self.morph = pymorphy3.MorphAnalyzer()

        self.documents = {}      # {doc_id: {term: tfidf}}
        self.idf_values = {}     # {term: idf}
        self.doc_norms = {}      # {doc_id: norm}

        self._load_documents()

    # ===============================
    # ЗАГРУЗКА ДОКУМЕНТОВ
    # ===============================

    def _load_documents(self):

        for filename in os.listdir(self.tfidf_dir):

            if not filename.endswith(".txt"):
                continue

            doc_id = filename.replace("_tfidf.txt", "")
            self.documents[doc_id] = {}

            norm = 0

            with open(os.path.join(self.tfidf_dir, filename),
                      "r", encoding="utf-8") as f:

                for line in f:
                    term, idf, tfidf = line.strip().split()

                    idf = float(idf)
                    tfidf = float(tfidf)

                    self.documents[doc_id][term] = tfidf
                    self.idf_values[term] = idf
                    norm += tfidf ** 2

            self.doc_norms[doc_id] = math.sqrt(norm)

        print("Документов загружено:", len(self.documents))

    # ===============================
    # ПОСТРОЕНИЕ ВЕКТОРА ЗАПРОСА
    # ===============================

    def _build_query_vector(self, query):

        words = query.lower().split()
        lemmas = [self.morph.parse(w)[0].normal_form for w in words]

        term_count = defaultdict(int)

        for lemma in lemmas:
            term_count[lemma] += 1

        query_vector = {}
        total_terms = len(lemmas)

        for lemma, count in term_count.items():

            if lemma not in self.idf_values:
                continue

            tf = count / total_terms
            idf = self.idf_values[lemma]
            query_vector[lemma] = tf * idf

        norm = math.sqrt(sum(v ** 2 for v in query_vector.values()))

        return query_vector, norm

    # ===============================
    # COSINE SIMILARITY
    # ===============================

    def _cosine_similarity(self, query_vector, query_norm,
                           doc_vector, doc_norm):

        if query_norm == 0 or doc_norm == 0:
            return 0

        dot_product = 0

        for term in query_vector:
            if term in doc_vector:
                dot_product += query_vector[term] * doc_vector[term]

        return dot_product / (query_norm * doc_norm)

    # ===============================
    # ПОИСК TOP-K
    # ===============================

    def search(self, query, top_k=10):

        query_vector, query_norm = self._build_query_vector(query)

        scores = []

        for doc_id in self.documents:

            score = self._cosine_similarity(
                query_vector,
                query_norm,
                self.documents[doc_id],
                self.doc_norms[doc_id]
            )

            if score > 0:
                scores.append((doc_id, score))

        scores.sort(key=lambda x: x[1], reverse=True)

        return scores[:top_k]


# ===============================
# КОНСОЛЬНЫЙ ЗАПУСК (опционально)
# ===============================

if __name__ == "__main__":

    engine = VectorSearchEngine("../Task4/tf_idf_lemmas")

    print("\nВекторная поисковая система (TF-IDF + cosine)")
    print("Введите 'exit' для выхода")

    while True:

        query = input("\nЗапрос: ")

        if query.lower() == "exit":
            break

        results = engine.search(query)

        print("\nРезультаты:")

        for doc_id, score in results:
            print(f"Документ {doc_id} | similarity = {score:.4f}")