with open('main.py', 'a', encoding='utf-8') as f:
    f.write("""

# ─── MODULE: AI Personal Doctor Chat (Gemini) ────────────────────────────────

import ai_doctor

class ChatRequest(BaseModel):
    session_id: str
    message: str
    patient_name: str = "Patient"

@app.post("/api/v1/chat")
async def ai_chat(req: ChatRequest):
    \"\"\"Gemini-powered personal doctor chatbot with multi-turn history.\"\"\"
    if not ai_doctor.is_configured():
        raise HTTPException(status_code=503, detail="AI Doctor not configured. Set GEMINI_API_KEY.")
    try:
        reply = ai_doctor.chat(req.session_id, req.message)
        return {"reply": reply, "session_id": req.session_id}
    except Exception as e:
        err = str(e)
        if "API_KEY" in err or "quota" in err.lower() or "invalid" in err.lower():
            raise HTTPException(status_code=401, detail="AI service unavailable — check API key or quota.")
        raise HTTPException(status_code=500, detail=f"AI error: {err}")

@app.delete("/api/v1/chat/{session_id}")
async def clear_chat(session_id: str):
    ai_doctor.clear_session(session_id)
    return {"status": "cleared"}
""")
print("Done")
