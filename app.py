from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from calculate import calculate_chart, summarize_chart
from Bot import chat_with_llm

app = FastAPI(title="NAKSH")

# ----------------- CORS CONFIG -----------------
# Allow all origins for deployment
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # change to your frontend URL in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ----------------- INPUT SCHEMA -----------------
class ChatInput(BaseModel):
    user_id: str
    lat: float
    lon: float
    dob: str        # YYYY-MM-DD
    tob: str        # HH:MM (24h)
    timezone: str   # e.g., Asia/Kolkata
    message: str

# ----------------- CHAT ENDPOINT -----------------
@app.post("/chat")
def chat(data: ChatInput):
    try:
        # 1️⃣ Calculate astrology chart
        chart = calculate_chart(data.lat, data.lon, data.dob, data.tob, data.timezone)

        # 2️⃣ Summarize chart for LLM
        summary = summarize_chart(chart)

        # 3️⃣ Call LLM with session memory
        
        reply = chat_with_llm(
            user_id=data.user_id,
            user_message=data.message,
            astro_summary=summary,
            dob=data.dob
        )
        return {"reply": reply}

    except Exception as e:
        import traceback
        traceback.print_exc()   # prints full error in Render logs
        return {"error": str(e)}

# ----------------- ROOT ENDPOINT -----------------
@app.get("/")
def root():
    return {"message": "JYOTISH Backend is live!"}

# ----------------- RUN LOCALLY -----------------
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
