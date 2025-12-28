from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from calculate import calculate_chart, summarize_chart
from Bot import chat_with_llm

app = FastAPI(title="NAKSH")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatInput(BaseModel):
    user_id: str          # actual name (user OR friend)
    profile_id: str       # memory/session id
    lat: float
    lon: float
    dob: str
    tob: str
    timezone: str
    message: str

@app.post("/chat")
def chat(data: ChatInput):
    chart = calculate_chart(
        data.lat, data.lon, data.dob, data.tob, data.timezone
    )

    summary = summarize_chart(chart)

    user_details = {
        "name": data.user_id,
        "dob": data.dob,
        "tob": data.tob,
        "lat": data.lat,
        "lon": data.lon,
        "timezone": data.timezone
    }

    reply = chat_with_llm(
        session_id=data.profile_id,   # memory isolation
        user_message=data.message,
        astro_summary=summary,
        user_details=user_details      # ✅ send full details
    )

    return {"reply": reply}

@app.get("/")
def root():
    return {"message": "NAKSH Backend is live"}
