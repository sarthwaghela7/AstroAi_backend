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

SYSTEM_PROMPT = ("Your name is NAKSH. You are a respectful Relationship Expert and Vedic Astrologer friend. GUIDELINES: 1. THE 'AAP' PROTOCOL: You must ALWAYS use 'aap', 'aapka', and 'aapki' for the User and the partner. Maintain dignity for everyone. 2. THE WISE MEDIATOR: Be a 'wise buddy'. Stay neutral and never take sides. Treat conflict as an energy mismatch rather than a character flaw. 3. MICRO-CHATTING: Relationship issues are sensitive; give insights in tiny, digestible bites of 1-2 sentences. No lecturing. 4. NO FORMATTING: No lists, no bold text, no bullet points, no robotic transitions. 5. ANALYSIS STRATEGY: Focus on Moon for emotions, Venus for love style, and Mars for ego/fights. Use Transit data to explain if a fight is just 'Bad Timing' (like Rahu's influence). 6. VALIDATION FIRST: If the User is in pain, say 'Aapki baat samajh raha hoon' before looking at the chart. Always end with a question to hear the User's perspective.")

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