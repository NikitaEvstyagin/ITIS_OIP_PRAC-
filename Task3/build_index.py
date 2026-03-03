import os
import re
import pymorphy3
import nltk
from collections import defaultdict

INPUT_DIR = "../Task1/pages"

morph = pymorphy3.MorphAnalyzer()
nltk.download("stopwords")
from nltk.corpus import stopwords
russian_stopwords = set(stopwords.words("russian"))

INDEX = defaultdict(set)
INDEX_TOKENS = defaultdict(list)
INDEX_LEMMAS = defaultdict(list)
DOCS = set()

print("Строим инвертированный индекс...")

for filename in os.listdir(INPUT_DIR):

    doc_id = int(filename.replace(".txt", ""))
    DOCS.add(doc_id)

    with open(os.path.join(INPUT_DIR, filename), "r", encoding="utf-8") as f:
        text = f.read().lower()
        words = re.findall(r"[а-яё]+", text)

        tokens_in_doc = set()
        lemmas_in_doc = set()            
                
        for word in words:
            if len(word) < 4:
                continue

            if word in russian_stopwords:
                continue
                
            tokens_in_doc.add(word)
            lemma = morph.parse(word)[0].normal_form
            lemmas_in_doc.add(lemma)

        for token in tokens_in_doc:
            INDEX_TOKENS[token].append(doc_id)

        for lemma in lemmas_in_doc:
            INDEX_LEMMAS[lemma].append(doc_id)

# сортировка списков документов
for term in INDEX_TOKENS:
    INDEX_TOKENS[term].sort()

for term in INDEX_LEMMAS:
    INDEX_LEMMAS[term].sort()

TERMS_TOKENS = sorted(INDEX_TOKENS.keys())
TERMS_LEMMAS = sorted(INDEX_LEMMAS.keys())


# сохраняем индекс в файл
with open("inverted_index_tokens.txt", "w", encoding="utf-8") as f:
    for term in sorted(INDEX_TOKENS.keys()):
        docs = INDEX_TOKENS[term]
        line = term + " " + " ".join(map(str, docs))
        f.write(line + "\n")

# сохраняем индекс лемм
with open("inverted_index_lemmas.txt", "w", encoding="utf-8") as f:
    for lemma in sorted(INDEX_LEMMAS.keys()):
        docs = INDEX_LEMMAS[lemma]
        line = lemma + " " + " ".join(map(str, docs))
        f.write(line + "\n")

print("Индексы сохранены") 