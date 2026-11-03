import numpy as np
import app.main as m
from app.ml import ml_score
from scripts.data import load_splits
from scripts.train import metrics   # reruns training; if slow, copy metrics() here instead

_, tests = load_splits()
for name, rows in tests.items():
    xt = [t for t, _ in rows]; yt = [l for _, l in rows]
    res = {}

    m.ml_score = lambda t, use_bert=True: 0.0   
    res["rules only"] = [int(not m.scan_text(t)["safe"]) for t in xt]
    m.ml_score = ml_score                            # rules + ML
    res["rules + ML"] = [int(not m.scan_text(t)["safe"]) for t in xt]

    print(f"\n{name}")
    for k, pred in res.items():
        print(f"  {k:12s}", metrics(yt, pred))