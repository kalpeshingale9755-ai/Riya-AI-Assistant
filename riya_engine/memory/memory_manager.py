import json
from pathlib import Path

MEMORY_FILE = Path(__file__).parent / "memory_store.json"


def load_memory():
    if not MEMORY_FILE.exists():
        return {"facts": {}, "history": []}

    with open(MEMORY_FILE, "r") as f:
        return json.load(f)


def save_memory(memory):
    with open(MEMORY_FILE, "w") as f:
        json.dump(memory, f, indent=4)


def remember_fact(key, value):
    memory = load_memory()
    memory["facts"][key] = value
    save_memory(memory)


def recall_fact(key):
    memory = load_memory()
    return memory["facts"].get(key)


def add_history(user, riya):
    memory = load_memory()

    memory["history"].append({
        "user": user,
        "riya": riya
    })

    # keep last 10 messages only
    memory["history"] = memory["history"][-10:]

    save_memory(memory)


# -----------------------------
# 🧠 LEARNING SYSTEM
# -----------------------------

def learn_from_input(user_input: str):
    text = user_input.lower()

    # learn user's name
    if "my name is" in text:
        name = text.replace("my name is", "").strip()
        if name:
            remember_fact("user_name", name)
            print(f"[Memory] Learned user name: {name}")

    # learn user's city
    elif "i live in" in text:
        city = text.replace("i live in", "").strip()
        if city:
            remember_fact("user_city", city)
            print(f"[Memory] Learned city: {city}")


# -----------------------------
# 🧠 CONTEXT BUILDER
# -----------------------------

def build_context():
    memory = load_memory()

    facts = memory.get("facts", {})
    history = memory.get("history", [])

    context = ""

    # add known facts
    if "user_name" in facts:
        context += f"User name is {facts['user_name']}.\n"

    if "user_city" in facts:
        context += f"User lives in {facts['user_city']}.\n"

    # add recent conversation
    if history:
        context += "Recent conversation:\n"
        for item in history[-3:]:
            context += f"User: {item['user']}\n"
            context += f"Riya: {item['riya']}\n"

    return context