<<<<<<< HEAD
# SpamGuard — AI Capstone (Frontend + Backend + ML)

SpamGuard helps users **triage suspicious SMS-style messages** before they reply or click links. Paste text, get **spam vs legitimate probabilities** from a **Multinomial Naive Bayes** model trained on the [UCI SMS Spam Collection](https://archive.ics.uci.edu/dataset/228/sms+spam+collection), plus short safety guidance.

## Repository layout

```
backend/           Starlette API + trained model JSON
  app/
    main.py        Routes: /health, /predict
    nb_model.py    NB inference
    spam_model.json Trained parameters (committed for reliable deploys)
  train_model.py   Retrain from UCI zip (requires network)
frontend/          React (Vite) UI
docs/              Proposal + final report (Markdown → PDF)
```

## AI model and methodology

- **Algorithm:** Multinomial Naive Bayes with Laplace smoothing (α = 1).
- **Features:** Word tokens from lowercase alphanumeric regex; vocabulary filtered by `min_df = 2`, max 12,000 terms by frequency.
- **Training data:** UCI “SMS Spam Collection” (labels `spam` / `ham`).
- **Artifact:** `backend/app/spam_model.json` — class log-priors and per-class log-probabilities per vocabulary term. Inference uses log-space sums and a log-sum-exp normalization for stable probabilities.
- **Retraining:** From repo root or `backend/`: `cd backend && python train_model.py` (downloads the dataset; prints hold-out metrics). Overwrites `spam_model.json`.

## Local setup

### Backend

```bash
cd backend
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

- Health: `GET /health`  
- Predict: `POST /predict` with JSON body `{ "text": "your message" }`

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Open http://127.0.0.1:5173 — Vite proxies `/api/*` to the backend, so the UI works without setting `VITE_API_URL` locally.

### Production build (frontend)

```bash
cd frontend
npm run build
npm run preview   # optional local check of dist/
```

Set `VITE_API_URL` to your deployed API origin (e.g. `https://spamguard-api.onrender.com`) when building for production if you are **not** using a same-origin proxy.

## Deployment

### Backend — [Render](https://render.com)

1. New **Web Service**, connect this repo.
2. **Root directory:** `backend`
3. **Build command:** `pip install -r requirements.txt`
4. **Start command:** `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
5. **Environment:** `CORS_ORIGINS` = your frontend origin(s), comma-separated, e.g. `https://your-app.vercel.app`

Optional: use the included `render.yaml` Blueprint from the repo root.

### Frontend — [Vercel](https://vercel.com)

1. Import the repo; leave **root** at repository root (this project includes `vercel.json`), or set **Root Directory** to `frontend` and remove/adjust top-level `vercel.json` accordingly.
2. **Environment variable:** `VITE_API_URL` = `https://<your-render-service>.onrender.com` (no path suffix).

After deploy, ensure Render `CORS_ORIGINS` includes your exact Vercel URL.

## Usage

1. Open the web app.
2. Paste a message (SMS, chat, or email body).
3. Click **Run AI check**.
4. Read the label, probabilities, and advice. **This is an educational prototype**, not a guarantee.

## Screenshots (for your submission)

Add PNGs under `docs/screenshots/` and reference them in your PDF report, for example:

- Home screen with empty form  
- Result showing **Likely spam** with high spam probability  
- Result showing **Likely legitimate** with high ham probability  

*(Capture these after `npm run dev` + backend running.)*

## Documentation PDFs

- Proposal: `docs/PROJECT_PROPOSAL.md`  
- Final report: `docs/FINAL_REPORT.md`  

Export to PDF with VS Code / Pandoc / your editor’s print-to-PDF.

## License

MIT — see `LICENSE` if present; otherwise treat code as your coursework submission.
=======
# Assignment_DibaSaha_CapstoneProject
>>>>>>> ea2ceea6b40aaf260abff44923f3730e2b444415
