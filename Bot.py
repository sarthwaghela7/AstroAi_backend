# import os
# import requests
# from collections import defaultdict, deque

# GROQ = os.getenv("GROQ")

# API_URL = "https://api.groq.com/openai/v1/chat/completions"

# _sessions = defaultdict(lambda: deque(maxlen=100))

# HEADERS = {
#     "Authorization": f"Bearer {GROQ}",
#     "Content-Type": "application/json"
# }

# SYSTEM_PROMPT = (
#     "You are a professional Vedic astrologer AI. "
#     "Always use simplest english and direct words. "
#     "Answer in 15-20 words. "
#     "Never ask questions back. "
#     "Always remember the user's name and birth date."
# )

# def call_llm(prompt: str) -> str:
#     payload = {
#         "model": "llama-3.3-70b-versatile",
#         "messages": [
#             {"role": "system", "content": SYSTEM_PROMPT},
#             {"role": "user", "content": prompt}
#         ],
#         "temperature": 0.7,
#         "max_tokens": 500
#     }

#     response = requests.post(API_URL, headers=HEADERS, json=payload)

#     if response.status_code != 200:
#         raise Exception(response.text)

#     return response.json()["choices"][0]["message"]["content"]

# def chat_with_llm(
#     user_id: str,
#     user_message: str,
#     astro_summary: str,
#     dob: str
# ) -> str:
#     history = _sessions[user_id]

#     # ✅ THIS is the fix
#     prompt = (
#         f"User Name: {user_id}\n"
#         f"Date of Birth: {dob}\n"
#         f"Astrology Summary:\n{astro_summary}\n\nConversation:\n"
#     )

#     for h in history:
#         prompt += f"{h['role']}: {h['content']}\n"

#     prompt += f"user: {user_message}\nassistant:"

#     reply = call_llm(prompt)

#     history.append({"role": "user", "content": user_message})
#     history.append({"role": "assistant", "content": reply})

#     return reply


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
    "Use simple English. "
    "Answer in 15-20 words. "
    "Never ask questions back."
)

def call_llm(prompt: str) -> str:
    payload = {
        "model": "llama-3.3-70b-versatile",
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.7,
        "max_tokens": 300
    }

    res = requests.post(API_URL, headers=HEADERS, json=payload)
    return res.json()["choices"][0]["message"]["content"]

def chat_with_llm(
    session_id: str,
    user_message: str,
    astro_summary: str,
    dob: str,
    name: str
) -> str:
    history = _sessions[session_id]

    prompt = (
        f"Name: {name}\n"
        f"Date of Birth: {dob}\n"
        f"Astrology Summary: {astro_summary}\n\n"
        "Conversation:\n"
    )

    for h in history:
        prompt += f"{h['role']}: {h['content']}\n"

    prompt += f"user: {user_message}\nassistant:"

    reply = call_llm(prompt)

    history.append({"role": "user", "content": user_message})
    history.append({"role": "assistant", "content": reply})

    return reply
