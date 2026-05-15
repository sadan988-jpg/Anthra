"""
ai_doctor.py — Gemini-powered personal doctor AI for SecurePredict Health.

Uses google-generativeai with a medical system prompt and per-session
conversation history so the chatbot can answer ANY health question
contextually, like a real personal physician.
"""
import os
import google.generativeai as genai

# ── API Configuration ─────────────────────────────────────────────────────────
# Set GEMINI_API_KEY as an environment variable for production.
# For the hackathon demo the key is read from env first, then falls back.
_API_KEY = os.environ.get("GEMINI_API_KEY", "")

SYSTEM_PROMPT = """You are Dr. SecurePredict, an empathetic and highly knowledgeable AI personal doctor assistant embedded inside a secure healthcare platform.

Your role:
• Answer ALL health-related questions thoroughly and clearly, like a real family physician would.
• For HEART or CHEST symptoms: Do NOT immediately shout emergency unless the user describes a clear heart attack (crushing pain, radiating to arm/jaw, sweating). Instead, ask 2-3 clarifying questions first: "Where exactly is the pain?", "Does it feel sharp, dull, or like pressure?", "Does it worsen with deep breaths or movement?".
• After triaging: If symptoms sound like acid reflux or muscle strain, provide gentle tips. If they sound cardiac but stable, advise consulting a doctor soon. If they sound like a heart attack, THEN advise calling 108 immediately.
• Cover symptoms, diseases, medications, dosages, nutrition, mental health, chronic conditions, and lifestyle advice.
• Structure answers clearly — use bullet points (•) for lists and bold key terms with asterisks like *this*.
• Be warm, compassionate, and non-judgmental.
• Keep responses concise but complete — under 200 words.
• Never refuse a genuine medical question.
• You are not replacing a real doctor — you provide evidence-based health information to help patients make informed decisions.
• Do NOT use markdown ## headers. Use bullet points and plain text with emoji where helpful."""

# Per-session conversation history {session_id: list of Content dicts}
_sessions: dict = {}

_model = None

def _get_model():
    global _model
    if _model is None:
        if not _API_KEY:
            raise RuntimeError("GEMINI_API_KEY is not set.")
        genai.configure(api_key=_API_KEY)
        _model = genai.GenerativeModel(
            model_name="gemini-1.5-flash",
            system_instruction=SYSTEM_PROMPT,
        )
    return _model


def chat(session_id: str, user_message: str) -> str:
    """
    Send a message and get a doctor-style AI response.
    Maintains multi-turn conversation history per session_id.
    Returns the assistant's reply as a plain string.
    """
    model = _get_model()

    # Retrieve or create chat session history
    history = _sessions.get(session_id, [])

    # Start a Gemini chat with the existing history
    chat_session = model.start_chat(history=history)

    # Send new user message
    response = chat_session.send_message(user_message)
    reply = response.text.strip()

    # Persist updated history (keep last 20 turns to avoid token overflow)
    _sessions[session_id] = chat_session.history[-40:]

    return reply


def clear_session(session_id: str):
    """Reset conversation history for a given session."""
    _sessions.pop(session_id, None)


def is_configured() -> bool:
    return bool(_API_KEY)
