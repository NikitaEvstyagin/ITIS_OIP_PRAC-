import os
import time
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse, parse_qs
from collections import deque

START_URL = "https://www.100bestbooks.ru/"
MAX_PAGES = 100
OUTPUT_DIR = "pages"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; SimpleLitresCrawler/1.0)"
}

visited = set()
queue = deque([START_URL])
domain = urlparse(START_URL).netloc

os.makedirs(OUTPUT_DIR, exist_ok=True)

def is_valid_link(url):
    parsed = urlparse(url)

    # должен быть тот же домен
    if parsed.netloc != domain:
        return False

    # пропустить расширения медиа/скриптов/стилей
    skip_ext = (
        ".jpg", ".jpeg", ".png", ".svg",
        ".css", ".js", ".pdf", ".zip",
        ".mp3", ".mp4", ".gif", ".exe"
    )
    
    if "item_info.php" not in parsed.path:
        return False


    # относительные пути лучше пропустить
    bad_paths = [
        "/search", "/cart", "/login",
        "/register", "/favorites",
        "/profile", "/order", "/checkout"
    ]
    for bad in bad_paths:
        if parsed.path.lower().startswith(bad):
            return False

    # базовый HTML должен быть длиной
    return True

def crawl():
    count = 0
    index_lines = []

    while queue and count < MAX_PAGES:
        url = queue.popleft()

        if url in visited:
            continue

        try:
            response = requests.get(url, headers=HEADERS, timeout=10)
            if "text/html" not in response.headers.get("Content-Type", ""):
                continue

            visited.add(url)
            count += 1

            filename = f"{count}.txt"
            filepath = os.path.join(OUTPUT_DIR, filename)

            with open(filepath, "w", encoding="utf-8") as f:
                f.write(response.text)

            index_lines.append(f"{count} {url}")
            print(f"[{count}] Saved: {url}")

            soup = BeautifulSoup(response.text, "html.parser")

            for td in soup.find_all("td", class_="vline"):

                book_link = td.find("a", href=lambda x: x and "item_info.php" in x)

                if book_link:
                    full_url = urljoin(url, book_link["href"])

                    if is_valid_link(full_url) and full_url not in visited:
                        queue.append(full_url)

            time.sleep(1)  # небольшая задержка

        except Exception as e:
            print(f"Error crawling {url}: {e}")

    with open("index.txt", "w", encoding="utf-8") as idx:
        idx.write("\n".join(index_lines))

    print("Finished.")

if __name__ == "__main__":
    crawl()
