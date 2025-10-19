import time, random, re, requests
from bs4 import BeautifulSoup
from ..settings import HEADERS
from ..utils.io import write_json
from ..utils.text import looks_relevant

S = requests.Session()

SEARCH_URLS = [
    "https://www.olx.kz/d/ru/list/q-%D0%B3%D0%BB%D1%8D%D0%BC%D0%BF%D0%B8%D0%BD%D0%B3/",
    "https://www.olx.kz/d/ru/list/q-%D0%B1%D0%B0%D0%B7%D0%B0%20%D0%BE%D1%82%D0%B4%D1%8B%D1%85%D0%B0/",
    "https://www.olx.kz/d/ru/list/q-%D0%BA%D0%B5%D0%BC%D0%BF%D0%B8%D0%BD%D0%B3/",
    "https://www.olx.kz/d/ru/list/q-%D1%8D%D0%BA%D0%BE-%D0%BE%D1%82%D0%B5%D0%BB%D1%8C/",
]

def safe_text(tag, sep=" ", strip=True):
    if not tag:
        return ""
    try:
        return tag.get_text(sep, strip=strip)
    except Exception:
        return ""

def parse_card(card):
    # ссылка
    a = card.find("a", href=True)
    if not a:
        return None
    href = a["href"]
    if href.startswith("/"):
        href = "https://www.olx.kz" + href

    # заголовок (olx может рендерить h6, h4, h3, span)
    title = None
    for sel in [
        ("h6", {}), ("h4", {}), ("h3", {}), ("div", {"data-cy": "ad-card-title"}),
        ("p", {"data-testid": "ad-card-title"}), ("span", {"data-testid": "ad-card-title"}),
    ]:
        t = card.find(sel[0], sel[1]) if sel[1] else card.find(sel[0])
        if t:
            title = safe_text(t)
            if title:
                break

    # цена
    price = ""
    for sel in [
        ("p", {"data-testid": "ad-price"}),
        ("h6", {"data-testid": "ad-price"}),
        ("span", {"data-testid": "ad-price"}),
        ("div", {"data-testid": "ad-price"}),
    ]:
        p = card.find(sel[0], sel[1])
        if p:
            price = safe_text(p)
            if price:
                break

    # локация/дата (поле часто меняет селектор)
    loc = ""
    for sel in [
        ("p", {"data-testid": "location-date"}),
        ("span", {"data-testid": "location-date"}),
        ("div", {"data-testid": "location-date"}),
    ]:
        l = card.find(sel[0], sel[1])
        if l:
            loc = safe_text(l)
            if loc:
                break

    obj = {"name": title, "price": price, "location": loc, "url": href, "source": "OLX"}
    # предварительная релевантность по карточке
    blob = " ".join([obj.get("name") or "", obj.get("price") or "", obj.get("location") or ""])
    if not looks_relevant(blob):
        return None
    return obj

def parse_listing(url):
    time.sleep(random.uniform(1.2, 2.0))
    r = S.get(url, headers=HEADERS, timeout=15)
    if r.status_code != 200:
        return []
    soup = BeautifulSoup(r.text, "html.parser")

    # основной контейнер карточек
    cards = soup.find_all("div", {"data-cy": "l-card"})
    if not cards:
        # запасной вариант: некоторые страницы могут иметь другие контейнеры
        cards = soup.select("div[data-testid='l-card'], div.css-1sw7q4x")  # запасной селектор

    out = []
    for c in cards:
        try:
            obj = parse_card(c)
            if obj:
                out.append(obj)
        except Exception:
            continue
    return out

def parse_item(url):
    time.sleep(random.uniform(1.0, 2.0))
    r = S.get(url, headers=HEADERS, timeout=15)
    if r.status_code != 200:
        return {}
    soup = BeautifulSoup(r.text, "html.parser")

    # описание
    desc = None
    for sel in [
        ("div", {"data-cy": "ad_description"}),
        ("div", {"data-testid": "ad-description"}),
        ("div", {"id": "textContent"}),
    ]:
        d = soup.find(sel[0], sel[1]) if sel[1] else soup.find(sel[0])
        if d:
            desc = safe_text(d, "\n")
            if desc and len(desc) > 10:
                break
    if not desc:
        desc = ""

    # фото
    photos = []
    for img in soup.find_all("img"):
        src = img.get("src") or img.get("data-src")
        if src and "olx" in src and src.startswith("http"):
            photos.append(src)
    photos = list(dict.fromkeys(photos))[:12]

    # телефоны (в тексте описания)
    phones = []
    for m in re.findall(r"(\+?7[\d\-\s\(\)]{9,})", desc):
        p = re.sub(r"[^\d+]", "", m)
        if p and p not in phones:
            phones.append(p)

    # instagram / whatsapp (в тексте)
    insta = None
    im = re.search(r"(https?://(?:www\.)?instagram\.com/[^\s]+)", desc, re.I)
    if im:
        insta = im.group(1)

    wa = None
    wm = re.search(r"(https?://(?:api\.)?wa\.me/[^\s]+)", desc, re.I)
    if wm:
        wa = wm.group(1)

    return {"description": desc, "photos": photos, "phones": phones, "instagram": insta, "whatsapp": wa}

def collect_olx():
    seen = {}
    for url in SEARCH_URLS:
        try:
            for it in parse_listing(url):
                # детали карточки
                details = parse_item(it["url"])
                it.update(details)
                seen[it["url"]] = it
        except Exception:
            continue
    out = list(seen.values())
    write_json("data/raw/olx_raw.json", out)
    print(f"[OLX] collected: {len(out)}")
    return out
