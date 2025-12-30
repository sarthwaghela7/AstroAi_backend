from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional

# Import updated functions from your calculation files
from calculate import calculate_chart, get_current_transit_chart, summarize_chart_with_transits
from calculate_relationship import summarize_relationship

# Import Naksh's chat functions
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

# ---------- INPUT SCHEMA ----------

class ChatInput(BaseModel):
    user_id: str
    profile_id: str
    lat: float
    lon: float
    dob: str
    tob: str
    timezone: str
    message: str
    current_user_time: Optional[str] = None 

# ---------- SINGLE PERSON CHAT (With Transit Support) ----------

@app.post("/chat")
def chat(data: ChatInput):
    # 1. Birth Chart Calculation
    natal_chart = calculate_chart(
        data.lat, data.lon, data.dob, data.tob, data.timezone
    )

    # 2. Current Sky (Transit) Calculation
    transit_chart = get_current_transit_chart(
        data.lat, data.lon, data.timezone, data.current_user_time
    )

    # 3. Create a unified summary of both charts
    full_summary = summarize_chart_with_transits(natal_chart, transit_chart)

    # Calling Naksh - Syncing variable names to match Bot.py
    reply = chat_with_llm(
        session_id=data.profile_id,
        user_message=data.message,
        full_astro_summary=full_summary, # Matches the 'full_astro_summary' in Bot.py
        user_details=data.dict()
    )

    return {"reply": reply}

# ---------- RELATIONSHIP CHAT ----------

class RelationshipInput(BaseModel):
    session_id: str
    message: str
    person_a: ChatInput
    person_b: ChatInput

@app.post("/relationship")
def relationship_chat(data: RelationshipInput):
    # Calculate charts for both individuals
    chart_a = calculate_chart(
        data.person_a.lat, data.person_a.lon, data.person_a.dob, data.person_a.tob, data.person_a.timezone
    )
    chart_b = calculate_chart(
        data.person_b.lat, data.person_b.lon, data.person_b.dob, data.person_b.tob, data.person_b.timezone
    )

    # Relationship Synastry Summary
    rel_summary = summarize_relationship(chart_a, chart_b)
    
    # Calling Naksh Relationship Expert
    reply = chat_relationship(
        session_id=data.session_id,
        user_message=data.message, # Ensure this matches Bot_relationship.py arg name
        relationship_summary=rel_summary, # Ensure this matches Bot_relationship.py arg name
        person_a={"name": data.person_a.user_id, "dob": data.person_a.dob, "tob": data.person_a.tob},
        person_b={"name": data.person_b.user_id, "dob": data.person_b.dob, "tob": data.person_b.tob}
    )

    return {"reply": reply}

@app.get("/")
def root():
    return {"message": "NAKSH Backend is live with Gochar and Relationship support"}