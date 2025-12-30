from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional

# Import updated functions
from calculate import calculate_chart, get_current_transit_chart, summarize_chart_with_transits
from calculate_relationship import summarize_relationship

from Bot import chat_with_llm
from Bot_relationship import chat_relationship

app = FastAPI(title="NAKSH")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------- UPDATED INPUT SCHEMA ----------

class ChatInput(BaseModel):
    user_id: str
    profile_id: str
    lat: float
    lon: float
    dob: str
    tob: str
    timezone: str
    message: str
    # Naya field: Frontend se user ka current local time (ISO format)
    current_user_time: Optional[str] = None 

# ---------- UPDATED SINGLE PERSON CHAT ----------

@app.post("/chat")
def chat(data: ChatInput):
    # 1. Birth Chart (Janma Kundli)
    natal_chart = calculate_chart(
        data.lat, data.lon, data.dob, data.tob, data.timezone
    )

    # 2. Transit Chart (Gochar) - Current Sky
    transit_chart = get_current_transit_chart(
        data.lat, data.lon, data.timezone, data.current_user_time
    )

    # 3. Combine both for Naksh
    full_summary = summarize_chart_with_transits(natal_chart, transit_chart)

    reply = chat_with_llm(
        session_id=data.profile_id,
        user_message=data.message,
        astro_summary=full_summary,
        user_details=data.dict()
    )

    return {"reply": reply}

# ---------- UPDATED RELATIONSHIP CHAT ----------

class RelationshipInput(BaseModel):
    session_id: str
    message: str
    person_a: ChatInput
    person_b: ChatInput

@app.post("/relationship")
def relationship_chat(data: RelationshipInput):
    # Calculate charts for both people
    chart_a = calculate_chart(
        data.person_a.lat, data.person_a.lon, data.person_a.dob, data.person_a.tob, data.person_a.timezone
    )
    chart_b = calculate_chart(
        data.person_b.lat, data.person_b.lon, data.person_b.dob, data.person_b.tob, data.person_b.timezone
    )

    # Relationship focused summary
    summary = summarize_relationship(chart_a, chart_b)

    # Note: For relationship chat, we can also add transit logic if needed, 
    # but currently, we focus on their core compatibility.
    
    reply = chat_relationship(
        session_id=data.session_id,
        message=data.message,
        summary=summary,
        person_a={"name": data.person_a.user_id, "dob": data.person_a.dob, "tob": data.person_a.tob},
        person_b={"name": data.person_b.user_id, "dob": data.person_b.dob, "tob": data.person_b.tob}
    )

    return {"reply": reply}

@app.get("/")
def root():
    return {"message": "NAKSH Backend is live with Gochar support"}