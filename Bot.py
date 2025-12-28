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
    "You are a professional Vedic astrologer AI. "
    "Always refer to the user's exact details provided (name, DOB, birth time, location). "
    "Use the astrology chart to answer predictions. "
    "Use simple English, 15-20 words. "
    "Never ask questions back. "
    "Always remember user details and chart."
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

def chat_with_llm(
    session_id: str,
    user_message: str,
    astro_summary: str,
    user_details: dict
) -> str:
    """
    user_details: {
        "name": str,
        "dob": str,
        "tob": str,
        "lat": float,
        "lon": float,
        "timezone": str
    }
    """
    history = _sessions[session_id]

    # Structured prompt to ensure LLM knows details + chart
    prompt = (
        f"User Details:\n"
        f"Name: {user_details.get('name')}\n"
        f"DOB: {user_details.get('dob')}\n"
        f"TOB: {user_details.get('tob')}\n"
        f"Latitude: {user_details.get('lat')}\n"
        f"Longitude: {user_details.get('lon')}\n"
        f"Timezone: {user_details.get('timezone')}\n\n"
        f"Astrology Summary:\n{astro_summary}\n\n"
        "Conversation History:\n"
    )

    for h in history:
        prompt += f"{h['role']}: {h['content']}\n"

    prompt += f"user: {user_message}\nassistant:"

    reply = call_llm(prompt)

    history.append({"role": "user", "content": user_message})
    history.append({"role": "assistant", "content": reply})

    return reply
