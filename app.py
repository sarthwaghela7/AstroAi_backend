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

# ---------- 1. INPUT SCHEMAS (Defined first to avoid Pylance errors) ----------

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

class RelationshipInput(BaseModel):
    session_id: str
    message: str
    person_a: ChatInput
    person_b: ChatInput

# ---------- 2. SINGLE PERSON CHAT ENDPOINT ----------

@app.post("/chat")
def chat(data: ChatInput):
    # Calculate Birth Chart (Natal)
    natal_chart = calculate_chart(
        data.lat, data.lon, data.dob, data.tob, data.timezone
    )

    # Calculate Current Sky (Transit)
    transit_chart = get_current_transit_chart(
        data.lat, data.lon, data.timezone, data.current_user_time
    )

    # Combine for Naksh
    full_summary = summarize_chart_with_transits(natal_chart, transit_chart)

    # Clean user details so Naksh knows who he's talking to
    user_info = {
        "name": data.user_id,
        "dob": data.dob,
        "tob": data.tob,
        "timezone": data.timezone
    }

    # Calling Bot.py (Ensure full_astro_summary matches Bot.py argument name)
    reply = chat_with_llm(
        session_id=data.profile_id,
        user_message=data.message,
        full_astro_summary=full_summary,
        user_details=user_info
    )

    return {"reply": reply}

# ---------- 3. RELATIONSHIP CHAT ENDPOINT ----------

@app.post("/relationship")
def relationship_chat(data: RelationshipInput):
    # Calculate charts for both people
    chart_a = calculate_chart(
        data.person_a.lat, data.person_a.lon, data.person_a.dob, data.person_a.tob, data.person_a.timezone
    )
    chart_b = calculate_chart(
        data.person_b.lat, data.person_b.lon, data.person_b.dob, data.person_b.tob, data.person_b.timezone
    )

    # Generate compatibility summary
    rel_summary = summarize_relationship(chart_a, chart_b)
    
    # Calling Bot_relationship.py
    # Note: Ensure arguments here match the first line of your chat_relationship function
    reply = chat_relationship(
        session_id=data.session_id,
        message=data.message,
        summary=rel_summary,
        person_a={"name": data.person_a.user_id, "dob": data.person_a.dob, "tob": data.person_a.tob},
        person_b={"name": data.person_b.user_id, "dob": data.person_b.dob, "tob": data.person_b.tob}
    )

    return {"reply": reply}

# ---------- 4. ROOT/HEALTH CHECK ----------

@app.get("/")
def root():
    return {"message": "NAKSH Backend is live and synced!"}