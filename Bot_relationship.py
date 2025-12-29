import os
import requests
from collections import defaultdict, deque

GROQ = os.getenv("GROQ")
API_URL = "https://api.groq.com/openai/v1/chat/completions"

_sessions = defaultdict(lambda: deque(maxlen=100))

HEADERS = {
    "Authorization": f"Bearer {GROQ}",
    "Content-Type": "application/json"
}

SYSTEM_PROMPT = (
    "You are a professional Vedic astrologer AI specializing in relationship compatibility. "
    "Use both birth charts accurately. "
    "Give clear compatibility insights. "
    "Do not ask questions. "
    "Use 20-25 simple English words."
)

def call_llm(prompt: str) -> str:
    payload = {
        "model": "llama-3.3-70b-versatile",
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.7,
        "max_tokens": 400
    }

    res = requests.post(API_URL, headers=HEADERS, json=payload)
    if res.status_code != 200:
        raise Exception(res.text)
    return res.json()["choices"][0]["message"]["content"]

def chat_relationship(
    session_id: str,
    message: str,
    summary: str,
    person_a: dict,
    person_b: dict
) -> str:

    history = _sessions[session_id]

    prompt = (
        "Person A Details:\n"
        f"Name: {person_a['name']}, DOB: {person_a['dob']}, TOB: {person_a['tob']}\n\n"
        "Person B Details:\n"
        f"Name: {person_b['name']}, DOB: {person_b['dob']}, TOB: {person_b['tob']}\n\n"
        f"Relationship Astrology Summary:\n{summary}\n\n"
        "Conversation History:\n"
    )

    for h in history:
        prompt += f"{h['role']}: {h['content']}\n"

    prompt += f"user: {message}\nassistant:"

    reply = call_llm(prompt)

    history.append({"role": "user", "content": message})
    history.append({"role": "assistant", "content": reply})

    return reply
