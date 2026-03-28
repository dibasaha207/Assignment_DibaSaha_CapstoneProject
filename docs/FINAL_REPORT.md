# Final Report — SpamGuard AI Capstone

**Project:** SpamGuard — SMS-like spam triage with Naive Bayes  
**Date:** March 2026  

## 1. Problem solved

Digital fraud often starts with a short, plausible message: a fake prize, a “bank alert,” or a parcel delivery link. Victims benefit from **quick, interpretable feedback** before they act. SpamGuard addresses this by classifying pasted text and surfacing **probabilities** plus **non-technical safety advice**, reducing reliance on gut feeling alone while keeping the user in control.

## 2. System design

### 2.1 Architecture

The app follows a classic **three-tier pattern**:

1. **Client (React + Vite):** Text area, submit action, loading and error states, visualization of spam vs ham probabilities, and disclaimer copy.
2. **API (Starlette):** `/health` for monitoring and `/predict` accepting JSON `{ "text": "..." }`, returning label, probabilities, and advice.
3. **Model:** Loaded at startup from `spam_model.json`; inference is O(document length × hit vocabulary) with a hash map from tokens to indices.

CORS is restricted via the `CORS_ORIGINS` environment variable in production (comma-separated origins), defaulting to local Vite URLs for development.

### 2.2 Key design decisions

- **Naive Bayes over deep learning:** The dataset is small tabular text; NB is fast, interpretable, and easy to explain in coursework. It meets the “AI/ML component” requirement without GPU cost.
- **JSON weights instead of sklearn at inference:** Training and inference use the Python standard library plus a minimal ASGI stack (Starlette/Uvicorn). This avoids build failures on newer Python versions and keeps the Render slug small.
- **Separate frontend and backend hosting:** Static frontends deploy cheaply on Vercel; the API on Render exposes a public URL consumed via `VITE_API_URL`.

## 3. AI workflow

1. **Data acquisition:** `train_model.py` downloads the official UCI zip over HTTPS and parses `SMSSpamCollection` (tab-separated label and body).
2. **Preprocessing:** Tokenize with `[a-z0-9']+`; build vocabulary with `min_df=2`, `max_features=12000`.
3. **Training:** For each class, accumulate token counts (multinomial). Apply Laplace smoothing:  
   \(P(w|c) = \frac{\text{count}(w,c) + \alpha}{\sum_w \text{count}(w,c) + \alpha |V|}\).  
   Store \(\log P(c)\) and \(\log P(w|c)\) for numerical stability.
4. **Inference:** For an input message, sum log probabilities weighted by token counts in the message (restricted to known vocabulary), normalize with a log-sum-exp trick to obtain posterior probabilities for `spam` and `ham`.
5. **Threshold:** Default decision rule is 0.5 on spam probability (configurable in future work).

**Hold-out metrics** (one run, seed 42, 80/20 split): accuracy ≈ **0.98**, spam precision ≈ **0.97**, spam recall ≈ **0.90**—strong on this corpus but **not** indicative of performance on all domains or languages.

## 4. Results and limitations

**What works well**

- Clear separation of UI, API, and model; easy local run (`README`).
- Fast predictions suitable for interactive use.
- Honest UX: shows uncertainty (probabilities) and disclaimers.

**Limitations**

- **Domain shift:** Marketing SMS in the training set may not match email, WhatsApp scams, or other locales.
- **Adversarial inputs:** Attackers can paraphrase to evade bag-of-words models.
- **No personalization:** No user feedback loop or active learning in v1.

## 5. Deployment notes

- **Backend (Render):** Set `CORS_ORIGINS` to the Vercel site origin (e.g. `https://your-app.vercel.app`). Cold starts may delay the first request on the free tier.
- **Frontend (Vercel):** Set build root or use repo-level `vercel.json`; define `VITE_API_URL` to the Render API base (no trailing slash required).

## 6. Conclusion

SpamGuard delivers a **complete capstone pipeline**: real problem framing, a trained probabilistic classifier, REST backend, React frontend, version control, and documented deployment. Future work could add multilingual embeddings, user-reported false positives/negatives, or a lightweight explainability view (top contributing tokens).

---

*Length: ~4 pages when exported to PDF.*
