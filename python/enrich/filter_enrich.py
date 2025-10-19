from ..utils.text import looks_relevant, clean_phone
from ..utils.io import hash_str

def normalize_obj(o: dict) -> dict:
    # телефоны
    if o.get("phones"):
        o["phones"] = sorted({clean_phone(p) for p in o["phones"] if clean_phone(p)})
    # id
    if not o.get("id"):
        o["id"] = hash_str((o.get("url") or o.get("name") or "") + (o.get("address") or ""))
    return o

def filter_relevant(objs):
    out=[]
    for o in objs:
        blob = " ".join([str(o.get(k,"")) for k in ("name","description","price","location","type")])
        if looks_relevant(blob):
            out.append(normalize_obj(o))
    return out
