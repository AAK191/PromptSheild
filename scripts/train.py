import os
import joblib
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.pipeline import make_pipeline, make_union

from scripts.data import load_splits

OUT = os.path.join("app", "models", "clf.joblib")
THR_MIN, THR_MAX = 0.45, 0.95        # allowed range for the tuned threshold
TARGET_FPR = 0.01                   # flag at most ~1% of benign validation prompts


def metrics(y, pred):
    y, pred = np.array(y), np.array(pred).astype(int)
    tp = int(((pred == 1) & (y == 1)).sum())
    fp = int(((pred == 1) & (y == 0)).sum())
    fn = int(((pred == 0) & (y == 1)).sum())
    tn = int(((pred == 0) & (y == 0)).sum())
    p = tp / max(tp + fp, 1)
    r = tp / max(tp + fn, 1)
    return {
        "precision": round(p, 3),
        "recall": round(r, 3),
        "f1": round(2 * p * r / max(p + r, 1e-9), 3),
        "fpr": round(fp / max(fp + tn, 1), 3),
        "n": int(len(y)),
    }


def build_model():
    return make_pipeline(
        make_union(
            TfidfVectorizer(ngram_range=(1, 3), min_df=2, sublinear_tf=True,
                            max_features=150_000),
            TfidfVectorizer(analyzer="char_wb", ngram_range=(3, 5), min_df=3,
                            sublinear_tf=True, max_features=150_000),  # German/typos
        ),
        LogisticRegression(C=5, max_iter=2000, class_weight="balanced"),
    )


def main():
    train, tests = load_splits()
    X = [t for t, _ in train]
    y = [l for _, l in train]
    print(f"train rows: {len(X)}  (injection share: {np.mean(y):.2f})")

    # Hold out 15% of TRAIN to choose the threshold, so test sets stay untouched.
    Xtr, Xval, ytr, yval = train_test_split(
        X, y, test_size=0.15, stratify=y, random_state=42)

    model = build_model()
    model.fit(Xtr, ytr)

    pv = model.predict_proba(Xval)[:, 1]
    benign = pv[np.array(yval) == 0]
    raw_thr = float(np.quantile(benign, 1 - TARGET_FPR))
    thr = float(np.clip(raw_thr, THR_MIN, THR_MAX))
    print(f"threshold: raw={raw_thr:.3f} -> used={thr:.3f}")

    for name, rows in tests.items():
        xt = [t for t, _ in rows]
        yt = [l for _, l in rows]
        pr = model.predict_proba(xt)[:, 1]
        print(f"\n{name}")
        print("  @0.50   ", metrics(yt, pr >= 0.5))
        if abs(thr - 0.5) > 1e-6:
            print(f"  @{thr:.2f}   ", metrics(yt, pr >= thr))

    # Error analysis on the realistic test set
    dname = "deepset/prompt-injections"
    if dname in tests:
        xt = [t for t, _ in tests[dname]]
        yt = [l for _, l in tests[dname]]
        pr = model.predict_proba(xt)[:, 1]
        print(f"\n--- missed attacks on {dname} (p < {thr:.2f}) ---")
        for t, l, p in zip(xt, yt, pr):
            if l == 1 and p < thr:
                print(f"{p:.2f} | {t[:120]}")
        print(f"\n--- false positives on {dname} (p >= {thr:.2f}) ---")
        for t, l, p in zip(xt, yt, pr):
            if l == 0 and p >= thr:
                print(f"{p:.2f} | {t[:120]}")

    # Final model: refit on ALL training data (the 15% was only for the threshold)
    final = build_model()
    final.fit(X, y)
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    joblib.dump({"model": final, "threshold": thr}, OUT)
    print("\nsaved", OUT)


if __name__ == "__main__":
    main()