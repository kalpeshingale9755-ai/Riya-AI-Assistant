from voice.listener import listen
from riya_engine.engine import process
from riya_engine.execution.executor import execute
from personality.riya_personality import generate_response
from voice.speech import speak
from riya_engine.router import route_input
from online.online_brain import think_online
from personality.state import set_state
from personality.behavior import update_state
from riya_engine.memory.memory_manager import add_history
from riya_engine.memory.memory_manager import recall_fact
from riya_engine.memory.memory_manager import learn_from_input
from riya_engine.memory.memory_manager import build_context




def main():
    print("=== RIYA v2 STARTED ===")

    while True:
        user_input = input("You: ")

        # 🧠 automatic learning
        learn_from_input(user_input)

        # ⭐ STEP 3 — MEMORY RECALL (ADD HERE)
        name = recall_fact("user_name")
        if name:
            print(f"[Memory] Known user: {name}")

        route = route_input(user_input)
        print(f"[Router] Mode selected: {route}")


        # ✅ OFFLINE PATH
        if route == "offline":
            intent = process(user_input)

            # ⭐ NEW: automatic personality decision
            update_state(route, intent)

            if intent.confidence < 0.5:
                print("[Router] Low confidence → switching to online brain")
                response = think_online(user_input)
            else:
                execute(intent)
                response = generate_response(intent)


        # ✅ ONLINE PATH (temporary placeholder)
        else:
            context = build_context()
            
            print("\n[DEBUG CONTEXT]")
            print(context)

            response = think_online(context + "\nUser: " + user_input)



        speak(response)
        add_history(user_input, response)
if __name__ == "__main__":
    main()