from datasets import load_dataset
from sklearn.feature_extraction.text import CountVectorizer
from app.normalizer import normalize

ds = load_dataset("deepset/prompt-injections")["train"]
inj    = [normalize(t) for t, l in zip(ds["text"], ds["label"]) if l == 1]
benign = [normalize(t) for t, l in zip(ds["text"], ds["label"]) if l == 0]

cv = CountVectorizer(ngram_range=(3, 5), min_df=3)
X = cv.fit_transform(inj)
counts = X.sum(axis=0).A1
top = sorted(zip(cv.get_feature_names_out(), counts), key=lambda x: -x[1])[:50]

for phrase, n in top:
    in_benign = sum(phrase in b for b in benign)
    print(f"{n:4d} inj | {in_benign:3d} benign | {phrase}")