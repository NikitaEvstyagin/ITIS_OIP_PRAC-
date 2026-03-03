import pymorphy3

INDEX_FILE_lemma = "inverted_index_lemmas.txt"
INDEX_FILE_token = "inverted_index_tokens.txt"
morph = pymorphy3.MorphAnalyzer()

INDEX = {}
DOCS = set()

# =========================
# ЗАГРУЗКА ИНДЕКСА
# =========================

with open(INDEX_FILE_lemma, "r", encoding="utf-8") as f:
    for line in f:
        parts = line.strip().split()
        term = parts[0]
        docs = list(map(int, parts[1:]))

        INDEX[term] = docs
        DOCS.update(docs)

TERMS = sorted(INDEX.keys())

print("Индекс загружен.")
print("Терминов:", len(TERMS))
print("Документов:", len(DOCS))


# =========================
# ДВОИЧНЫЙ ПОИСК
# =========================

def binary_search(arr, target):
    left = 0
    right = len(arr) - 1

    while left <= right:
        mid = (left + right) // 2

        if arr[mid] == target:
            return mid
        elif arr[mid] < target:
            left = mid + 1
        else:
            right = mid - 1

    return -1


# =========================
# ПОЛУЧЕНИЕ ДОКУМЕНТОВ
# =========================

def get_docs_general(term):

    result_docs = set()

    # поиск как токен
    index_token = binary_search(TERMS, term)
    if index_token != -1:
        result_docs.update(INDEX[TERMS[index_token]])

    # поиск как лемма
    lemma = morph.parse(term)[0].normal_form
    index_lemma = binary_search(TERMS, lemma)
    if index_lemma != -1:
        result_docs.update(INDEX[TERMS[index_lemma]])

    return sorted(result_docs)


# =========================
# БУЛЕВЫ ОПЕРАЦИИ
# =========================

def AND(list1, list2):
    i = j = 0
    result = []

    while i < len(list1) and j < len(list2):
        if list1[i] == list2[j]:
            result.append(list1[i])
            i += 1
            j += 1
        elif list1[i] < list2[j]:
            i += 1
        else:
            j += 1

    return result


def OR(list1, list2):
    return sorted(set(list1) | set(list2))


def NOT(list1):
    return sorted(DOCS - set(list1))


# =========================
# ВЫЧИСЛЕНИЕ ВЫРАЖЕНИЯ
# =========================

def evaluate_simple(tokens):

    # NOT
    i = 0
    while i < len(tokens):
        if tokens[i] == "NOT":
            result = NOT(tokens[i + 1])
            tokens[i:i + 2] = [result]
        else:
            i += 1

    # AND
    i = 0
    while i < len(tokens):
        if tokens[i] == "AND":
            result = AND(tokens[i - 1], tokens[i + 1])
            tokens[i - 1:i + 2] = [result]
            i = 0
        else:
            i += 1

    # OR
    i = 0
    while i < len(tokens):
        if tokens[i] == "OR":
            result = OR(tokens[i - 1], tokens[i + 1])
            tokens[i - 1:i + 2] = [result]
            i = 0
        else:
            i += 1

    return tokens[0]


# =========================
# ОСНОВНОЙ ЦИКЛ
# =========================

while True:

    query = input("\nВведите запрос (или exit): ").lower()

    if query == "exit":
        break

    tokens = query.replace("(", " ( ").replace(")", " ) ").split()
    stack = []

    for token in tokens:

        if token == "and":
            stack.append("AND")

        elif token == "or":
            stack.append("OR")

        elif token == "not":
            stack.append("NOT")

        elif token == "(":
            stack.append(token)

        elif token == ")":
            temp = []
            while stack[-1] != "(":
                temp.append(stack.pop())
            stack.pop()
            stack.append(evaluate_simple(temp[::-1]))

        else:
            stack.append(get_docs_general(token))

    result = evaluate_simple(stack)

    print("Документы:", result)


"""
Примеры:

автор AND автомобиль
август OR августейший
автор AND NOT авторство
(август AND августейший) OR (автомобиль AND автомобилист)
(автобиография OR автобиографический) AND NOT авторство
"""