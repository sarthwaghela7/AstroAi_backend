import os
import requests
from collections import defaultdict, deque


GROQ = os.environ.get("GROQ")
API_URL = "https://api.groq.com/openai/v1/chat/completions"

# Memory management: Stores the last 100 messages to keep the vibe consistent
_sessions = defaultdict(lambda: deque(maxlen=100))

HEADERS = {
    "Authorization": f"Bearer {GROQ}",
    "Content-Type": "application/json"
}

SYSTEM_PROMPT = ("Your name is NAKSH. You are a wise, neutral, and empathetic Relationship Expert and Astrologer. PERSONALITY: You are the 'mutual friend' who understands both sides. Always use 'aap' for the User and their partner. STRICT CONVERSATION RULE: You must NEVER speak more than 2 sentences per message. No exceptions. Keep replies extremely brief but deep. No formatting like bold text or lists. ANALYSIS LOGIC: Look at the 'summary' to find the core vibe between Person A and Person B. Focus on emotional sync (Moon) or attraction (Venus). Give one insight and ask one question to keep the chat moving. Be relatable and supportive. If you write a third sentence, you are being too robotic. Stay human, stay brief.")
def call_llm(messages: list) -> str:
    """Sends the conversation stack to the LLM"""
    payload = {
        "model": "llama-3.3-70b-versatile",
        "messages": messages,
        "temperature": 0.8, # Higher temperature for more natural, less repetitive advice
        "max_tokens": 600
    }

    try:
        res = requests.post(API_URL, headers=HEADERS, json=payload)
        res.raise_for_status()
        return res.json()["choices"][0]["message"]["content"]
    except Exception as e:
        return (
            "Sarth ji, maafi chahta hoon, thoda technical connection issue hai. "
            "Kya aap apni baat phir se keh sakte hain?"
        )

def chat_relationship(session_id: str, message: str, relationship_summary: str, person_a: dict, person_b: dict) -> str:
    """
    Main function to handle relationship queries.
    person_a/b: Dictionaries containing 'name', 'dob', etc.
    relationship_summary: The technical output from calculate_relationship.py
    """
    history = _sessions[session_id]

    # Injecting the secret context so the AI knows the data without being robotic
    relationship_context = (
        f"PARTNERSHIP DATA:\n"
        f"Person A: {person_a.get('name', 'User')} ji.\n"
        f"Person B: {person_b.get('name', 'Partner')} ji.\n"
        f"ASTRO LOGIC: {relationship_summary}\n"
        f"GOAL: Help them navigate their connection respectfully using the above logic."
    )

    # Building the message list for the LLM
    messages = [{"role": "system", "content": SYSTEM_PROMPT + "\n\n" + relationship_context}]
    
    # Adding history for context awareness
    for h in history:
        messages.append(h)
    
    # Adding the current message
    messages.append({"role": "user", "content": message})

    # Get the expert reply
    reply = call_llm(messages)

    # Store in history
    history.append({"role": "user", "content": message})
    history.append({"role": "assistant", "content": reply})

    return reply