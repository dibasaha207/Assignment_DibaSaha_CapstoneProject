import json
import os

from starlette.applications import Starlette
from starlette.middleware.cors import CORSMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.routing import Route

from app.nb_model import get_model


async def startup() -> None:
    get_model()


_origins = os.getenv("CORS_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173").split(",")
_origins = [o.strip() for o in _origins if o.strip()]


async def health(request: Request) -> JSONResponse:
    return JSONResponse({"status": "ok", "service": "spamguard-api"})


async def predict(request: Request) -> JSONResponse:
    try:
        body = await request.json()
    except json.JSONDecodeError:
        return JSONResponse({"detail": "Invalid JSON"}, status_code=400)

    text = body.get("text") if isinstance(body, dict) else None
    if not isinstance(text, str):
        return JSONResponse({"detail": "Field 'text' must be a string"}, status_code=400)
    text = text.strip()
    if not text:
        return JSONResponse({"detail": "Text cannot be empty"}, status_code=400)
    if len(text) > 8000:
        return JSONResponse({"detail": "Text exceeds 8000 characters"}, status_code=400)

    model = get_model()
    proba = model.predict_proba(text)
    p_spam = float(proba["spam"])
    p_ham = float(proba["ham"])
    label = "spam" if p_spam >= 0.5 else "ham"

    if label == "spam":
        advice = (
            "This resembles known spam patterns. Do not click links, reply with personal data, "
            "or send money. If it claims to be your bank, contact them through an official channel."
        )
    else:
        advice = (
            "This looks like a normal message by model standards. Stay cautious with unexpected "
            "attachments and requests for passwords or OTP codes."
        )

    return JSONResponse(
        {
            "label": label,
            "spam_probability": round(p_spam, 4),
            "ham_probability": round(p_ham, 4),
            "advice": advice,
        }
    )


routes = [
    Route("/health", endpoint=health, methods=["GET"]),
    Route("/predict", endpoint=predict, methods=["POST"]),
]

app = Starlette(routes=routes, on_startup=[startup])
app.add_middleware(
    CORSMiddleware,
    allow_origins=_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
