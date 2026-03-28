# Project Proposal — SpamGuard (AI Capstone)

**Author:** [Your name]  
**Date:** March 2026  

## 1. Problem statement

Unsolicited SMS and chat messages remain a major channel for scams, phishing, and malware delivery. Many users—especially older adults and busy professionals—lack time to assess whether a short text is legitimate. A wrong click or reply can lead to financial loss or account compromise. The problem is **timely triage**: users need a fast, understandable signal that a message resembles known spam patterns, without replacing human judgment or official verification.

## 2. Proposed solution

**SpamGuard** is a small web application that lets users paste a message and receive:

- A **binary label** (likely spam vs likely legitimate) with **calibrated probabilities**.
- Short **actionable guidance** (e.g. avoid clicking unknown links, verify via official channels).

The system is designed as an **educational safety assistant**, not a legal or security guarantee, with clear disclaimers in the UI.

## 3. AI / ML approach

- **Task:** Supervised binary text classification (spam vs ham).
- **Dataset:** [UCI SMS Spam Collection](https://archive.ics.uci.edu/dataset/228/sms+spam+collection) (public, widely used for teaching).
- **Model:** **Multinomial Naive Bayes** with **Laplace smoothing** (α = 1). Tokenization uses lowercase alphanumeric tokens (regex). The vocabulary is built from training data with **minimum document frequency** 2 and capped at **12,000** terms by global frequency.
- **Artifact:** Model parameters (log priors and per-class log probabilities per vocabulary term) are serialized to **JSON** (`spam_model.json`) for fast, dependency-light inference—no scikit-learn required at runtime, which improves portability (including Python 3.14+ environments without prebuilt sklearn wheels).
- **Evaluation:** A reproducible **80/20 shuffle split** (seed 42) reports approximate accuracy and spam precision/recall in `train_model.py` when retraining.

## 4. Technology stack

| Layer      | Choice                                      |
|-----------|----------------------------------------------|
| Frontend  | React 18, Vite 6, static deploy (e.g. Vercel) |
| Backend   | Starlette, Uvicorn                          |
| AI        | Custom Multinomial NB (training + inference) |
| Version control | Git / GitHub                             |
| Deployment | Frontend: Vercel; Backend: Render (free tier) |

## 5. Scope and ethics

- **In scope:** English-like SMS text; probability and advice display; REST API.
- **Out of scope:** Guaranteed blocking of messages, multilingual support, and attachment/image analysis.
- **Ethics:** The UI states the tool is a prototype; users must not treat outputs as definitive proof of legitimacy or malice.

---

*Length: ~1.5 pages when exported to PDF from Markdown.*
