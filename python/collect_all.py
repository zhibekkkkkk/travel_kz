from .settings import DATA_RAW, DATA_OUT
from .utils.io import write_json, read_json
from .sources.two_gis import collect_2gis
from .sources.olx import collect_olx
from .sources.avito import collect_avito
from .enrich.parse_2gis_page import parse_2gis_page
from .enrich.instagram_fetch import fetch_profile
from .enrich.filter_enrich import filter_relevant, normalize_obj
from .ml.segment_llm import classify_batch
from .ml.embed_dedupe import dedupe
from .ml.gen_descriptions import add_descriptions
from .ml.score_ml import add_scores
import os

def main():
    os.makedirs(DATA_RAW, exist_ok=True); os.makedirs(DATA_OUT, exist_ok=True)

    # 1) источники
    d2 = collect_2gis()
    d_olx = collect_olx()
    d_avito = collect_avito()

    # 2) enrich 2GIS карточки
    for it in d2:
        if it.get("id"):
            it.update(parse_2gis_page(str(it["id"])))

    # 3) normalize/filter all
    raw_all = [normalize_obj(x) for x in (d2 + d_olx + d_avito)]
    filtered = filter_relevant(raw_all)

    # 4) instagram best-effort
    for it in filtered:
        if it.get("instagram"):
            it.update(fetch_profile(it["instagram"]))

    write_json(f"{DATA_RAW}/merged_filtered.json", filtered)

    # 5) сегментация
    segmented = classify_batch(filtered)

    # 6) дедупликация
    deduped = dedupe(segmented)

    # 7) описания
    with_desc = add_descriptions(deduped)

    # 8) скоринг
    scored = add_scores(with_desc)

    write_json(f"{DATA_OUT}/places_final.json", scored)

    # CSV
    try:
        import pandas as pd
        # выкинем тяжёлые поля
        slim=[]
        for o in scored:
            d=o.copy()
            for k in ("photos","photos_instagram","generated_description"):
                d.pop(k, None)
            slim.append(d)
        pd.DataFrame(slim).to_csv(f"{DATA_OUT}/places_final.csv", index=False)
    except Exception as e:
        print("[CSV] skip:", e)

    print(f"[OK] total objects: {len(scored)} -> data/out/places_final.*")

if __name__ == "__main__":
    main()
