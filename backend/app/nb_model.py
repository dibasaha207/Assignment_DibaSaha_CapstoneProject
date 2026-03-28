"""
Multinomial Naive Bayes for spam/ham — pure Python inference from a JSON artifact.
Training lives in train_model.py (also stdlib-only).
"""

from __future__ import annotations

import json
import math
import re
from pathlib import Path

_TOKEN_RE = re.compile(r"[a-z0-9']+", re.I)


def tokenize(text: str) -> list[str]:
    return _TOKEN_RE.findall(text.lower())


class NBSpamModel:
    def __init__(self, data: dict):
        self.classes: list[str] = data["classes"]
        self.vocab: list[str] = data["vocab"]
        self.word_to_i: dict[str, int] = {w: i for i, w in enumerate(self.vocab)}
        self.log_prior: dict[str, float] = data["log_prior"]
        # log_prob[c][i] = log P(vocab[i] | c)
        self.log_prob: dict[str, list[float]] = data["log_prob"]

    def predict_proba(self, text: str) -> dict[str, float]:
        tokens = tokenize(text)
        counts: dict[str, int] = {}
        for t in tokens:
            if t in self.word_to_i:
                counts[t] = counts.get(t, 0) + 1
        log_scores: dict[str, float] = {}
        for c in self.classes:
            s = self.log_prior[c]
            lp = self.log_prob[c]
            for word, n in counts.items():
                idx = self.word_to_i[word]
                s += n * lp[idx]
            log_scores[c] = s
        m = max(log_scores.values())
        exp_sum = sum(math.exp(log_scores[c] - m) for c in self.classes)
        return {c: math.exp(log_scores[c] - m) / exp_sum for c in self.classes}

    @staticmethod
    def load(path: Path) -> "NBSpamModel":
        with open(path, encoding="utf-8") as f:
            return NBSpamModel(json.load(f))


_MODEL_PATH = Path(__file__).resolve().parent / "spam_model.json"
_model: NBSpamModel | None = None


def get_model() -> NBSpamModel:
    global _model
    if _model is None:
        if not _MODEL_PATH.exists():
            raise FileNotFoundError(
                f"Model missing: {_MODEL_PATH}. Run: python train_model.py (from backend/)"
            )
        _model = NBSpamModel.load(_MODEL_PATH)
    return _model
