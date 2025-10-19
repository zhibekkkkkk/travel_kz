import time, random, re, requests
from bs4 import BeautifulSoup
from ..settings import DGIS_API_KEY, REGION_NAME, CITY_SLUG, SEARCH_TERMS, HEADERS
from ..utils.io import write_json

S = requests.Session()

def get_region_id():
    try:
        r = S.get("https://catalog.api.2gis.com/2.0/region/search",
                  params={"q": REGION_NAME, "key": DGIS_API_KEY}, timeout=10)
        items = (r.json().get("result") or {}).get("items") or []
        for it in items:
            if it.get("id"): return it["id"]
    except Exception: pass
    return None

def api_items(region_id, q, page=1):
    r = S.get("https://catalog.api.2gis.com/3.0/items", headers=HEADERS, timeout=12,
              params={"q": q, "region_id": region_id, "key": DGIS_API_KEY,
                      "fields": "items.point,items.address,items.rubrics,items.reviews",
                      "page": page,"page_size": 10, "type":"branch","locale":"ru_RU"})
    r.raise_for_status()
    return (r.json().get("result") or {}).get("items") or []

def scrape_search(q):
    url = f"https://2gis.kz/{CITY_SLUG}/search/{q}"
    time.sleep(random.uniform(1.0,2.0))
    h = S.get(url, headers=HEADERS, timeout=12).text
    ids = set(re.findall(r"/firm/(\d+)", h))
    out=[]
    for fid in ids:
        try:
            r = S.get("https://catalog.api.2gis.com/3.0/items/byid", headers=HEADERS, timeout=10,
                      params={"id": fid,"key":DGIS_API_KEY,"fields":"items.point,items.address,items.rubrics,items.reviews"})
            items = (r.json().get("result") or {}).get("items") or []
            if items:
                it = items[0]
                out.append({
                    "id": str(fid),
                    "name": it.get("name"),
                    "address": (it.get("address") or {}).get("value"),
                    "lat": (it.get("point") or {}).get("lat"),
                    "lon": (it.get("point") or {}).get("lon"),
                    "type": (it.get("rubrics") or [{}])[0].get("name") if it.get("rubrics") else None,
                    "rating": (it.get("reviews") or {}).get("rating"),
                    "reviews_count": (it.get("reviews") or {}).get("review_count"),
                    "source": "2GIS"
                })
        except Exception: pass
    return out

def collect_2gis():
    region_id = get_region_id()
    seen={}
    if region_id:
        for term in SEARCH_TERMS:
            empty=0
            for page in range(1,7):
                time.sleep(random.uniform(0.5,1.1))
                try:
                    for it in api_items(region_id, term, page):
                        seen[it["id"]] = {
                            "id": str(it["id"]),
                            "name": it.get("name"),
                            "address": (it.get("address") or {}).get("value"),
                            "lat": (it.get("point") or {}).get("lat"),
                            "lon": (it.get("point") or {}).get("lon"),
                            "type": (it.get("rubrics") or [{}])[0].get("name") if it.get("rubrics") else None,
                            "rating": (it.get("reviews") or {}).get("rating"),
                            "reviews_count": (it.get("reviews") or {}).get("review_count"),
                            "source": "2GIS"
                        }
                    if not it: empty+=1
                    if empty>=2: break
                except Exception: break
    if not seen:
        for term in SEARCH_TERMS:
            for it in scrape_search(term):
                seen[it["id"]] = it
    out = list(seen.values())
    write_json("data/raw/2gis_raw.json", out)
    print(f"[2GIS] collected: {len(out)}")
    return out
