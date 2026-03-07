def execute(intent):
    print(f"[Executor] Executing intent: {intent}")

    result = f"Executed {intent.intent} for {intent.entity}"

    return result