import os
import re
import nltk
import pymorphy3
from collections import defaultdict

# папка с html-файлами
INPUT_DIR = "../Task1/pages"

# выходные файлы
TOKENS_FILE = "tokens.txt"
LEMMAS_FILE = "lemmas.txt"

# загрузка стоп-слов
nltk.download("stopwords")
from nltk.corpus import stopwords
russian_stopwords = set(stopwords.words("russian"))

morph = pymorphy3.MorphAnalyzer()

tokens_set = set()

# =========================
# 1. Чтение и токенизация
# =========================
for filename in os.listdir(INPUT_DIR):
    filepath = os.path.join(INPUT_DIR, filename)

    with open(filepath, "r", encoding="utf-8") as f:
        text = f.read().lower()

        # токенизация — только русские слова
        words = re.findall(r"[а-яё]+", text)

        for word in words:
            # убрать короткие слова
            if len(word) < 4:
                continue

            # убрать стоп-слова
            if word in russian_stopwords:
                continue

            tokens_set.add(word)

# =========================
# 2. Сохранение токенов
# =========================
with open(TOKENS_FILE, "w", encoding="utf-8") as f:
    for token in sorted(tokens_set):
        f.write(token + "\n")

print("Tokens saved:", len(tokens_set))

# =========================
# 3. Лемматизация
# =========================
lemmas_dict = defaultdict(list)

for token in tokens_set:
    lemma = morph.parse(token)[0].normal_form
    lemmas_dict[lemma].append(token)

# =========================
# 4. Сохранение лемм
# =========================
with open(LEMMAS_FILE, "w", encoding="utf-8") as f:
    for lemma in sorted(lemmas_dict.keys()):
        line = lemma + " " + " ".join(sorted(lemmas_dict[lemma]))
        f.write(line + "\n")

print("Lemmas saved:", len(lemmas_dict))
