import subprocess, shlex
from ..settings import OLLAMA_MODEL, DESC_MAX_WORDS

PROMPT = """Ты — редактор туристического каталога. Напиши описание {words} слов на русском.
Учитывай сегмент: {segment}. Выдели уникальные преимущества и локацию (Казахстан).
Не выдумывай цены. 
ДАНО:
Название: {name}
Адрес: {address}
Инфраструктура: {infra}
Короткое описание: {desc}
"""

def ollama_generate(prompt):
    cmd = f"ollama run {OLLAMA_MODEL}"
    res = subprocess.run(shlex.split(cmd), input=prompt.encode("utf-8"),
                         stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return res.stdout.decode("utf-8").strip()

def add_descriptions(objects):
    for o in objects:
        if o.get("generated_description"): continue
        infra = ", ".join(o.get("infrastructure", [])[:12])
        desc = (o.get("description") or "")[:600]
        prompt = PROMPT.format(words=DESC_MAX_WORDS, segment=o.get("segment","прочее"),
                               name=o.get("name","—"), address=o.get("address","—"),
                               infra=infra, desc=desc)
        o["generated_description"] = ollama_generate(prompt)
    return objects
