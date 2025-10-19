import time, random, re, requests
from bs4 import BeautifulSoup
from ..settings import CITY_SLUG, HEADERS
S = requests.Session()

def parse_2gis_page(firm_id: str) -> dict:
    url = f"https://2gis.kz/{CITY_SLUG}/firm/{firm_id}"
    time.sleep(random.uniform(1.0,2.0))
    r = S.get(url, headers=HEADERS, timeout=12)
    if r.status_code!=200: return {}
    soup = BeautifulSoup(r.text, "html.parser")
    out={}
    phones = [a.get("href","").replace("tel:","") for a in soup.find_all("a", href=True) if a["href"].startswith("tel:")]
    if phones: out["phones"] = phones
    mail = soup.find("a", href=re.compile(r"^mailto:", re.I))
    if mail: out["email"] = mail.get("href").split(":",1)[-1]
    insta = soup.find("a", href=re.compile(r"instagram\.com", re.I))
    if insta: out["instagram"] = insta.get("href")
    wa = soup.find("a", href=re.compile(r"(wa\.me|api\.whatsapp\.com)", re.I))
    if wa: out["whatsapp"] = wa.get("href")
    # краткий блок
    h = soup.find(["h1","h2"])
    if h:
        nxt = h.find_next("div")
        if nxt:
            desc = nxt.get_text(" ", strip=True)
            if desc and len(desc)>20: out["description"] = desc
    return out
