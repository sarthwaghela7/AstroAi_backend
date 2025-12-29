# from fastapi import FastAPI
# from fastapi.middleware.cors import CORSMiddleware
# from pydantic import BaseModel
# from calculate import calculate_chart, summarize_chart
# from Bot import chat_with_llm

# app = FastAPI(title="NAKSH")

# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# class ChatInput(BaseModel):
#     user_id: str          # actual name (user OR friend)
#     profile_id: str       # memory/session id
#     lat: float
#     lon: float
#     dob: str
#     tob: str
#     timezone: str
#     message: str

# @app.post("/chat")
# def chat(data: ChatInput):
#     chart = calculate_chart(
#         data.lat, data.lon, data.dob, data.tob, data.timezone
#     )

#     summary = summarize_chart(chart)

#     user_details = {
#         "name": data.user_id,
#         "dob": data.dob,
#         "tob": data.tob,
#         "lat": data.lat,
#         "lon": data.lon,
#         "timezone": data.timezone
#     }

#     reply = chat_with_llm(
#         session_id=data.profile_id,   # memory isolation
#         user_message=data.message,
#         astro_summary=summary,
#         user_details=user_details      # ✅ send full details
#     )

#     return {"reply": reply}

# @app.get("/")
# def root():
#     return {"message": "NAKSH Backend is live"}



from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from calculate import calculate_chart, summarize_chart
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

# ---------- EXISTING SINGLE PERSON CHAT ----------

class ChatInput(BaseModel):
    user_id: str
    profile_id: str
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

    reply = chat_with_llm(
        session_id=data.profile_id,
        user_message=data.message,
        astro_summary=summary,
        user_details=data.dict()
    )

    return {"reply": reply}

# ---------- NEW RELATIONSHIP CHAT ----------

class RelationshipInput(BaseModel):
    session_id: str
    message: str

    person_a: ChatInput
    person_b: ChatInput

@app.post("/relationship")
def relationship_chat(data: RelationshipInput):

    chart_a = calculate_chart(
        data.person_a.lat,
        data.person_a.lon,
        data.person_a.dob,
        data.person_a.tob,
        data.person_a.timezone
    )

    chart_b = calculate_chart(
        data.person_b.lat,
        data.person_b.lon,
        data.person_b.dob,
        data.person_b.tob,
        data.person_b.timezone
    )

    summary = summarize_relationship(chart_a, chart_b)

    reply = chat_relationship(
        session_id=data.session_id,
        message=data.message,
        summary=summary,
        person_a={
            "name": data.person_a.user_id,
            "dob": data.person_a.dob,
            "tob": data.person_a.tob
        },
        person_b={
            "name": data.person_b.user_id,
            "dob": data.person_b.dob,
            "tob": data.person_b.tob
        }
    )

    return {"reply": reply}

@app.get("/")
def root():
    return {"message": "NAKSH Backend is live"}
