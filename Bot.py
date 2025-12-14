import os
import json
import requests
from collections import defaultdict, deque
from keys import GROQ

GROQJYO = GROQ
API_URL = "https://api.groq.com/openai/v1/chat/completions"

# Session memory: last 5 messages per user
_sessions = defaultdict(lambda: deque(maxlen=100))

HEADERS = {
    "Authorization": f"Bearer {GROQJYO}",
    "Content-Type": "application/json"
}

SYSTEM_PROMPT = (
    "You are a professional Vedic astrologer AI. "
    "Always use simplest english and direct words to talk and have conversations"
    "Answer in 15-20 words with empathy and insight."
    "Use the astrology summary to give conversational, insightful guidance. "
    "Do give absolute predictions about future events."
    "If asked questions, donot reply with a question back, instead provide the best possible answer."
)

def call_llm(prompt: str) -> str:
    """Call Groq LLM with a text prompt"""
    payload = {
        "model": "llama-3.3-70b-versatile",
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.7,
        "max_tokens": 500
    }

    response = requests.post(API_URL, headers=HEADERS, json=payload)

    if response.status_code != 200:
        raise Exception(f"Groq API Error {response.status_code}: {response.text}")

    return response.json()["choices"][0]["message"]["content"]

def chat_with_llm(user_id: str, user_message: str, astro_summary: str) -> str:
    """LLM conversation with session memory"""
    history = _sessions[user_id]

    prompt = f"Astrology Summary:\n{astro_summary}\n\nConversation:\n"
    for h in history:
        prompt += f"{h['role']}: {h['content']}\n"

    prompt += f"user: {user_message}\nassistant:"

    reply = call_llm(prompt)

    # Update session memory
    history.append({"role": "user", "content": user_message})
    history.append({"role": "assistant", "content": reply})

    return reply
