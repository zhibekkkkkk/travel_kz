import re
def clean_phone(p):
    if not p: return ""
    p = re.sub(r"[^\d+]", "", p)
    if p.startswith("8") and len(p)==11: p = "+7"+p[1:]
    if p.startswith("7") and not p.startswith("+"): p = "+"+p
    return p

DROP_PATTERNS = [
    r"\bпродам\b", r"\bпрода[ёе]тс[я]\b", r"\bпродажа\b",
    r"домокомплект|каркас|шат[её]р|палатк|оборудовани|чан\b|баня[- ]чан",
    r"участок|земля под|готовый бизнес", r"склад|строймат",
]
KEEP_PATTERNS = [
    r"\bсдам\b|\bаренда\b|\bна\s*сутки\b|\bпосут(очно|)\b",
    r"гл[еэ]мпинг|юрта|кемпинг|база отдыха|эко[- ]отел|домик|guest\s*house"
]
def looks_relevant(text):
    t = (text or "").lower()
    if any(re.search(p, t) for p in DROP_PATTERNS): return False
    return any(re.search(p, t) for p in KEEP_PATTERNS)

def short_addr(a): 
    return (a or "").split(",")[0].strip() or "Алматы"
