# Лёгкий заглушка-парсер Avito (если avi.kz недоступен — вернёт пусто)
import requests, time, random
from bs4 import BeautifulSoup
from ..settings import HEADERS
from ..utils.io import write_json

S = requests.Session()

SEARCH_URLS = [
    "https://www.avito.ru/kazakhstan?cd=1&q=%D0%B3%D0%BB%D1%8D%D0%BC%D0%BF%D0%B8%D0%BD%D0%B3",
]

def collect_avito():
    out=[]
    for url in SEARCH_URLS:
        try:
            time.sleep(random.uniform(1.2,2.0))
            r = S.get(url, headers=HEADERS, timeout=12)
            if r.status_code!=200: continue
            soup = BeautifulSoup(r.text, "html.parser")
            # для Avito структура часто меняется — оставим как best-effort
            for a in soup.select("a[href*='/kz/']"):
                href = a.get("href")
                title = a.get_text(strip=True)
                if href and title:
                    if href.startswith("/"): href = "https://www.avito.ru"+href
                    out.append({"name": title, "url": href, "source": "Avito"})
        except Exception: pass
    write_json("data/raw/avito_raw.json", out)
    print(f"[Avito] collected: {len(out)}")
    return out
