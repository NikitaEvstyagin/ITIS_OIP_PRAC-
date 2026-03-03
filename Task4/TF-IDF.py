import os
import re
import math
import pymorphy3
from collections import defaultdict

# -----------------------------
# Настройки путей
# -----------------------------
DOCS_DIR = "../Task1/pages"       # скачанные HTML/тексты
LEMMAS_DIR = "../Task2/lemmas"      # папка с леммами
OUTPUT_TF_DIR = "tf_idf_tokens"   # выходная папка для токенов
OUTPUT_LM_DIR = "tf_idf_lemmas"   # выходная папка для лемм

os.makedirs(OUTPUT_TF_DIR, exist_ok=True)
os.makedirs(OUTPUT_LM_DIR, exist_ok=True)

morph = pymorphy3.MorphAnalyzer()

LEMMA_FILES = [os.path.join(LEMMAS_DIR, f) for f in os.listdir(LEMMAS_DIR) if f.endswith(".txt")]

ALL_LEMMAS = set()
for file in LEMMA_FILES:
    with open(file, "r", encoding="utf-8") as f:
        for line in f:
            parts = line.strip().split()
            if parts:
                lemma = parts[0]
                ALL_LEMMAS.add(lemma)

print(f"Загружено {len(ALL_LEMMAS)} лемм из папки {LEMMAS_DIR}")

# -----------------------------
# Подсчет TF для каждого документа
# -----------------------------
doc_terms = {}   # {doc_id: {term: count}}
doc_lemmas = {}  # {doc_id: {lemma: count}}
doc_lengths = {} # общее число терминов в документе

for filename in os.listdir(DOCS_DIR):
    if not filename.endswith(".txt"):
        continue

    doc_id = filename
    filepath = os.path.join(DOCS_DIR, filename)

    with open(filepath, "r", encoding="utf-8") as f:
        text = f.read().lower()
        words = re.findall(r"[а-яё]+", text)

        term_count = defaultdict(int)
        lemma_count = defaultdict(int)

        for word in words:
            term_count[word] += 1
            lemma = morph.parse(word)[0].normal_form
            if lemma in ALL_LEMMAS:
                lemma_count[lemma] += 1

        doc_terms[doc_id] = term_count
        doc_lemmas[doc_id] = lemma_count
        doc_lengths[doc_id] = len(words)

print(f"Подсчитан TF для {len(doc_terms)} документов")

# -----------------------------
# Подсчет IDF
# -----------------------------
df_terms = defaultdict(int)
df_lemmas = defaultdict(int)

for doc_id, terms in doc_terms.items():
    for term in terms.keys():
        df_terms[term] += 1

for doc_id, lemmas in doc_lemmas.items():
    for lemma in lemmas.keys():
        df_lemmas[lemma] += 1

N = len(doc_terms)  # общее число документов

idf_terms = {term: math.log(N / df) for term, df in df_terms.items()}
idf_lemmas = {lemma: math.log(N / df) for lemma, df in df_lemmas.items()}

# -----------------------------
# Вычисление TF-IDF и запись
# -----------------------------
for doc_id in doc_terms:

    # TF-IDF для токенов
    with open(os.path.join(OUTPUT_TF_DIR, f"{doc_id}_tfidf.txt"), "w", encoding="utf-8") as f:
        for term, count in doc_terms[doc_id].items():
            tf = count / doc_lengths[doc_id]
            tf_idf = tf * idf_terms[term]
            f.write(f"{term} {idf_terms[term]:.6f} {tf_idf:.6f}\n")

    # TF-IDF для лемм
    with open(os.path.join(OUTPUT_LM_DIR, f"{doc_id}_tfidf.txt"), "w", encoding="utf-8") as f:
        total_lemmas = sum(doc_lemmas[doc_id].values())
        for lemma, count in doc_lemmas[doc_id].items():
            tf = count / total_lemmas if total_lemmas > 0 else 0
            tf_idf = tf * idf_lemmas[lemma]
            f.write(f"{lemma} {idf_lemmas[lemma]:.6f} {tf_idf:.6f}\n")

print("TF-IDF вычислен и сохранен для всех документов")