import os, numpy as np, torch
from datasets import Dataset
from sklearn.model_selection import train_test_split
from transformers import (AutoTokenizer, AutoModelForSequenceClassification,
                          Trainer, TrainingArguments,
    DataCollatorWithPadding)

from scripts.data import load_splits
from scripts.train import metrics

MODEL = "distilbert-base-uncased"
OUT = os.path.join("app", "models", "bert")
MAXLEN = 128

def main():
    train, tests = load_splits()
    X = [t for t, _ in train]; y = [l for _, l in train]
    Xtr, Xval, ytr, yval = train_test_split(X, y, test_size=0.1, stratify=y, random_state=42)

    tok = AutoTokenizer.from_pretrained(MODEL)
    def enc(texts, labels):
        e = tok(texts, truncation=True, max_length=MAXLEN)
        e["labels"] = labels
        return Dataset.from_dict(e)

    model = AutoModelForSequenceClassification.from_pretrained(MODEL, num_labels=2)
    args = TrainingArguments(
        output_dir="bert_tmp", num_train_epochs=3, per_device_train_batch_size=16,
        per_device_eval_batch_size=64, learning_rate=3e-5, weight_decay=0.01,
        eval_strategy="epoch", save_strategy="no", logging_steps=100,
        fp16=torch.cuda.is_available(), report_to="none")
    trainer = Trainer(
    model=model,
    args=args,
    train_dataset=enc(Xtr, ytr),
    eval_dataset=enc(Xval, yval),
    data_collator=DataCollatorWithPadding(tok)  # <--- Add this argument
    )
    
    trainer.train()

    model.eval()
    def probs(texts):
        out = []
        for i in range(0, len(texts), 64):
            b = tok(texts[i:i+64], truncation=True, max_length=MAXLEN,
                    padding=True, return_tensors="pt").to(model.device)
            with torch.no_grad():
                out += torch.softmax(model(**b).logits, -1)[:, 1].cpu().tolist()
        return np.array(out)

    for name, rows in tests.items():
        xt = [t for t, _ in rows]; yt = [l for _, l in rows]
        print(f"\n{name}\n  @0.5", metrics(yt, probs(xt) >= 0.5))

    os.makedirs(OUT, exist_ok=True)
    model.save_pretrained(OUT); tok.save_pretrained(OUT)
    print("saved", OUT)

if __name__ == "__main__":
    main()