# python/ml/embed_dedupe.py
# Дедуп через cosine similarity без FAISS/OMP (устойчиво на macOS ARM + Py3.13)

from sentence_transformers import SentenceTransformer, util
from typing import List, Dict

def build_text(o: Dict) -> str:
    return " | ".join([str(o.get(k, "")) for k in ("name", "address", "description")])

def dedupe(objects: List[Dict], thr: float = 0.92) -> List[Dict]:
    if not objects:
        return []

    # одна модель на всё (можно ту же, что и раньше)
    model = SentenceTransformer("intfloat/multilingual-e5-base")

    texts = [build_text(o) for o in objects]
    # берём torch.Tensor, чтобы сразу использовать util.cos_sim
    embs = model.encode(texts, normalize_embeddings=True, convert_to_tensor=True)

    # косинусная матрица сходства [N x N]
    sim = util.cos_sim(embs, embs).cpu().numpy()
    n = len(objects)

    # DSU (union-find) для склейки кластеров
    parent = list(range(n))
    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x
    def union(a, b):
        ra, rb = find(a), find(b)
        if ra != rb:
            parent[rb] = ra

    # попарно объединяем близкие объекты
    for i in range(n):
        # можно слегка ограничить j диапазон, но при сотнях N это ок
        for j in range(i + 1, n):
            if sim[i, j] >= thr:
                union(i, j)

    # собираем кластеры
    clusters = {}
    for i in range(n):
        r = find(i)
        clusters.setdefault(r, []).append(i)

    # объединяем поля внутри кластера
    def merge_list(idxs: List[int]) -> Dict:
        base = {}
        for i in idxs:
            o = objects[i]
            for k, v in o.items():
                if v in (None, ""):
                    continue
                if isinstance(v, list):
                    base.setdefault(k, [])
                    for x in v:
                        if x not in base[k]:
                            base[k].append(x)
                else:
                    if not base.get(k):
                        base[k] = v
        return base

    return [merge_list(v) for v in clusters.values()]
