# python/ml/segment_llm.py
# Лёгкая zero-shot классификация ниш через эмбеддинги (без transformers pipeline)
# Модель: sentence-transformers (многоязычная), косинусная близость к названиям классов.

from typing import List, Dict
import numpy as np
from sentence_transformers import SentenceTransformer, util

# Ниши из ТЗ
CANDIDATES = [
    "люкс глэмпинги",
    "семейные гостевые дома",
    "эко-туризм",
    "этно-туризм (юрты)",
    "горные домики",
    "прочее"
]

# Один раз грузим модель (лёгкая и уже в requirements)
# Можно заменить на "intfloat/multilingual-e5-base", если хочешь унифицировать с дедупом.
_MODEL = SentenceTransformer("sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2")

# Кэш эмбеддингов классов
_LABEL_EMB = _MODEL.encode(CANDIDATES, normalize_embeddings=True, convert_to_numpy=True)

def _build_text(o: Dict) -> str:
    # Собираем короткий текст для классификации ниши
    fields = [
        o.get("name", ""),
        o.get("type", ""),
        o.get("address", ""),
        o.get("description", ""),
    ]
    text = " | ".join([str(x) for x in fields if x])
    # fallback
    if not text.strip():
        text = "туристический объект Казахстан"
    return text[:1200]

def classify_one(o: Dict) -> Dict:
    txt = _build_text(o)
    emb = _MODEL.encode([txt], normalize_embeddings=True, convert_to_numpy=True)  # shape (1, dim)
    # косинусная близость
    sims = util.cos_sim(emb, _LABEL_EMB).cpu().numpy()[0]  # shape (num_labels,)
    idx = int(np.argmax(sims))
    o["segment"] = CANDIDATES[idx]
    o["segment_score"] = float(sims[idx])
    return o

def classify_batch(items: List[Dict]) -> List[Dict]:
    # батч-энкодинг для ускорения
    texts = [_build_text(o) for o in items]
    embs = _MODEL.encode(texts, normalize_embeddings=True, convert_to_numpy=True)
    sims = util.cos_sim(embs, _LABEL_EMB).cpu().numpy()  # (N, L)
    for i, o in enumerate(items):
        row = sims[i]
        idx = int(np.argmax(row))
        o["segment"] = CANDIDATES[idx]
        o["segment_score"] = float(row[idx])
    return items
