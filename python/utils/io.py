import json, os, hashlib
def read_json(path, default=None):
    if not os.path.exists(path): return default
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def write_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def hash_str(s: str) -> str:
    return hashlib.sha1((s or "").encode("utf-8")).hexdigest()[:16]
