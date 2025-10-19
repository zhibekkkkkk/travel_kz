import numpy as np

SEG_WEIGHT = {"люкс глэмпинги":1.0,"эко-туризм":0.9,"горные домики":0.8,"семейные гостевые дома":0.7,"этно-туризм (юрты)":0.7,"прочее":0.4}

def _completeness(o):
    keys = ["name","address","lat","lon","phones","instagram","whatsapp"]
    got = sum(bool(o.get(k)) for k in keys)
    return got/len(keys)

def _activity(o):
    sc = 0.0 + (0.6 if o.get("instagram") else 0) + (0.3 if o.get("whatsapp") else 0) + (0.1 if o.get("website") else 0)
    return min(sc,1.0)

def _popularity(o):
    r = 0.0
    try: r += min(float(o.get("rating",0))/5.0,1.0)*0.6
    except: pass
    try: r += min(float(o.get("reviews_count",0))/100.0,1.0)*0.4
    except: pass
    return min(r,1.0)

def _segment(o):
    return SEG_WEIGHT.get(o.get("segment","прочее"),0.4)

def score(o):
    s = (_completeness(o)*0.35 + _activity(o)*0.25 + _popularity(o)*0.20 + _segment(o)*0.20)*10.0
    return round(s,1)

def bucket(v):
    if v>=8.0: return "горячий лид"
    if v>=5.5: return "тёплый"
    return "холодный"

def add_scores(objects):
    for o in objects:
        s = score(o); o["priority_score"]=s; o["priority_bucket"]=bucket(s)
    objects.sort(key=lambda x: x.get("priority_score",0), reverse=True)
    return objects
