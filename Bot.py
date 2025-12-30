import os
import requests
from collections import defaultdict, deque


GROQ = os.environ.get("GROQ")
API_URL = "https://api.groq.com/openai/v1/chat/completions"

# Memory for 100 messages per session to maintain context
_sessions = defaultdict(lambda: deque(maxlen=100))

HEADERS = {
    "Authorization": f"Bearer {GROQ}",
    "Content-Type": "application/json"
}

# HIGH-DETAIL SYSTEM PROMPT
SYSTEM_PROMPT = ("Your name is NAKSH. You are a respectful, warm, and deeply intuitive human-like friend and professional Vedic Astrologer. STRICT PERSONALITY RULES: 1. THE 'AAP' PROTOCOL: Always use 'aap' and 'aapka'. Never use 'tu' or 'tum'. Treat the User with high respect and tehzeeb. 2. HUMAN CHAT STYLE: No long paragraphs. Max 2-3 short sentences. Think: 'One thought per text'. Do not use robotic formatting like bullet points, bold headers, or line breaks. 3. HINGLISH MASTERY: Mix Hindi and English naturally like a modern friend. Use words like 'tension', 'vibes', 'mausam', 'life path', 'upaya'. 4. DATA LOGIC: Use 'Natal' data for personality and 'Transit' data for today's events. If the User mentions a specific incident, look at current planetary transits in the summary to find the trigger. 5. CONVERSATION FLOW: Acknowledge the User's emotion first. Mention ONE key placement. End with a short question like 'Kya aapne aisa feel kiya?' to keep it interactive. Never mention you are an AI or a bot.")

def call_llm(messages: list) -> str:
    """Internal function to communicate with Groq LLM"""
    payload = {
        "model": "llama-3.3-70b-versatile",
        "messages": messages,
        "temperature": 0.8,  # Slightly higher for human-like spontaneity
        "max_tokens": 600
    }

    try:
        res = requests.post(API_URL, headers=HEADERS, json=payload)
        res.raise_for_status()
        return res.json()["choices"][0]["message"]["content"]
    except Exception as e:
        return f"Arre Sarth ji, thoda technical issue aa gaya hai. Bas ek minute rukiye. (Error: {str(e)})"

def chat_with_llm(session_id: str, user_message: str, full_astro_summary: str, user_details: dict) -> str:
    """
    session_id: Unique ID for chat history
    user_message: Current text from user
    full_astro_summary: Combined string of Natal + Transit insights from calculate.py
    user_details: Dictionary containing name, etc.
    """
    history = _sessions[session_id]

    # Injecting real-time context into the system's memory
    user_name = user_details.get('user_id', 'Sarth')
    context_data = (
        f"USER PROFILE: Name is {user_name} ji. \n"
        f"ASTROLOGY DATA: {full_astro_summary}\n"
        f"CURRENT ENVIRONMENT: Use the Transit data in the summary to explain today's situation."
    )

    # Building the message stack
    messages = [{"role": "system", "content": SYSTEM_PROMPT + "\n\n" + context_data}]
    
    # Add previous chat history
    for h in history:
        messages.append(h)
    
    # Add current user message
    messages.append({"role": "user", "content": user_message})

    # Get response from Naksh
    reply = call_llm(messages)

    # Save to session memory
    history.append({"role": "user", "content": user_message})
    history.append({"role": "assistant", "content": reply})

    return reply