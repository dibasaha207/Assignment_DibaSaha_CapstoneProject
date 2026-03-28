"""
Download UCI SMS Spam Collection, train Multinomial Naive Bayes (stdlib),
write app/spam_model.json for the API.
"""
from __future__ import annotations

import io
import json
import math
import random
import zipfile
from collections import Counter
from pathlib import Path
from urllib.request import urlopen

UCI_ZIP = "https://archive.ics.uci.edu/static/public/228/sms+spam+collection.zip"
OUT = Path(__file__).resolve().parent / "app" / "spam_model.json"

MIN_DF = 2
MAX_FEATURES = 12_000
ALPHA = 1.0


def load_sms_data():
    raw = urlopen(UCI_ZIP, timeout=120).read()
    with zipfile.ZipFile(io.BytesIO(raw)) as zf:
        inner = [n for n in zf.namelist() if n.endswith("SMSSpamCollection")]
        if not inner:
            raise RuntimeError("SMSSpamCollection not found in zip")
        with zf.open(inner[0]) as f:
            lines = f.read().decode("utf-8", errors="replace").splitlines()
    texts, labels = [], []
    for line in lines:
        if "\t" not in line:
            continue
        label, text = line.split("\t", 1)
        label = label.strip().lower()
        if label not in ("ham", "spam"):
            continue
        labels.append(label)
        texts.append(text.strip())
    return texts, labels


def tokenize(text: str) -> list[str]:
    import re

    return re.findall(r"[a-z0-9']+", text.lower())


def build_vocab(texts: list[str], min_df: int, max_features: int) -> list[str]:
    df = Counter()
    for t in texts:
        df.update(set(tokenize(t)))
    total = Counter()
    for t in texts:
        total.update(tokenize(t))
    cand = [w for w, c in df.items() if c >= min_df]
    cand.sort(key=lambda w: (-total[w], w))
    return cand[:max_features]


def train(texts: list[str], labels: list[str], vocab: list[str]) -> dict:
    V = len(vocab)
    w_index = {w: i for i, w in enumerate(vocab)}
    n_docs = len(texts)
    class_n = Counter(labels)
    tc: dict[str, Counter] = {c: Counter() for c in ("ham", "spam")}
    for t, y in zip(texts, labels):
        for w in tokenize(t):
            if w in w_index:
                tc[y][w] += 1

    log_prior = {c: math.log(class_n[c] / n_docs) for c in ("ham", "spam")}
    log_prob: dict[str, list[float]] = {"ham": [], "spam": []}
    for c in ("ham", "spam"):
        denom = sum(tc[c].values()) + ALPHA * V
        row = []
        for w in vocab:
            num = tc[c].get(w, 0) + ALPHA
            row.append(math.log(num / denom))
        log_prob[c] = row

    return {
        "classes": ["ham", "spam"],
        "vocab": vocab,
        "log_prior": log_prior,
        "log_prob": log_prob,
    }


def metrics_on_holdout(texts: list[str], labels: list[str]) -> None:
    from app.nb_model import NBSpamModel

    idx = list(range(len(texts)))
    random.seed(42)
    random.shuffle(idx)
    cut = int(len(idx) * 0.8)
    train_i, test_i = idx[:cut], idx[cut:]
    tr_t = [texts[i] for i in train_i]
    tr_y = [labels[i] for i in train_i]
    te_t = [texts[i] for i in test_i]
    te_y = [labels[i] for i in test_i]
    vocab = build_vocab(tr_t, MIN_DF, MAX_FEATURES)
    m = train(tr_t, tr_y, vocab)
    nb = NBSpamModel(m)
    tp = fp = tn = fn = 0
    for t, y in zip(te_t, te_y):
        p = nb.predict_proba(t)
        pred = "spam" if p["spam"] >= 0.5 else "ham"
        if y == "spam" and pred == "spam":
            tp += 1
        elif y == "ham" and pred == "spam":
            fp += 1
        elif y == "ham" and pred == "ham":
            tn += 1
        else:
            fn += 1
    n = len(te_t)
    acc = (tp + tn) / n
    prec = tp / (tp + fp) if (tp + fp) else 0.0
    rec = tp / (tp + fn) if (tp + fn) else 0.0
    print(f"Hold-out (seed=42): accuracy={acc:.4f} precision(spam)={prec:.4f} recall(spam)={rec:.4f}")


def main():
    texts, labels = load_sms_data()
    metrics_on_holdout(texts, labels)
    vocab = build_vocab(texts, MIN_DF, MAX_FEATURES)
    model = train(texts, labels, vocab)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(model, f)
    print(f"Saved production model to {OUT} (vocab size={len(vocab)})")


if __name__ == "__main__":
    main()
