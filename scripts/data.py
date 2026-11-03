import os
import csv
from datasets import load_dataset
from app.normalizer import normalize

# Verify column names on huggingface.co if a source fails; names sometimes change.
SOURCES = [
    {"name": "deepset/prompt-injections",          "text": "text",   "label": "label"},
    {"name": "xTRam1/safe-guard-prompt-injection", "text": "text",   "label": "label"},
    {"name": "jackhhao/jailbreak-classification",  "text": "prompt", "label": "type",
     "map": {"jailbreak": 1, "benign": 0}},
    {"name": "Lakera/gandalf_ignore_instructions", "text": "text",   "label": None, "const": 1},
]

def _rows(split, cfg):
    out = []
    for ex in split:
        t = ex.get(cfg["text"])
        if cfg.get("const") is not None:
            l = cfg["const"]
        else:
            l = ex.get(cfg["label"])
            if "map" in cfg:
                l = cfg["map"].get(str(l).lower())
        if not t or l is None:
            continue
        out.append((normalize(str(t)), int(l)))
    return out

# --- HELPER FUNCTION TO LOAD HARD NEGATIVES ---
def _load_custom():
    rows, path = [], os.path.join("data", "custom.csv")
    if os.path.exists(path):
        with open(path, encoding="utf-8") as f:
            for r in csv.DictReader(f):
                if r.get("text") and r.get("label") in ("0", "1"):
                    rows.append((normalize(r["text"]), int(r["label"])))
    return rows

def load_splits():
    train, tests = [], {}
    for cfg in SOURCES:
        try:
            ds = load_dataset(cfg["name"])
            train += _rows(ds["train"], cfg)
            if "test" in ds:
                tests[cfg["name"]] = _rows(ds["test"], cfg)
        except Exception as e:
            print(f"[skip] {cfg['name']}: {e}")

    # remove duplicates and anything that also appears in a test set (leakage)
    test_texts = {t for rows in tests.values() for t, _ in rows}
    seen, clean = set(), []
    for t, l in train:
        if not t or t in test_texts or t in seen:
            continue
        seen.add(t)
        clean.append((t, l))

    # Add weighted custom hard negatives at the end (repeated 5 times so the model learns them)
    clean += _load_custom() * 5

    return clean, tests