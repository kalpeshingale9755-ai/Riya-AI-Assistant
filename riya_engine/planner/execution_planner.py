"""
Execution planner for RIYA v2.

This module converts intent dictionaries into ordered execution steps.
It does not execute any action.
"""


def _step(action, **kwargs):
    step = {"action": action}
    for key, value in kwargs.items():
        if value is not None:
            step[key] = value
    return step


def build_execution_plan(intent_data):
    """
    Convert an intent dictionary into an ordered execution plan.

    Expected input shape:
        {"intent": "<intent_name>", "entity": "<optional_entity>"}

    Returns:
        list[dict]: ordered action steps only.
    """
    intent_name = intent_data.get("intent") if isinstance(intent_data, dict) else None
    print(f"[Planner] Building execution plan for: {intent_name}")

    if not isinstance(intent_data, dict):
        plan = [_step("invalid_intent_payload")]
        print(f"[Planner] Plan created: {plan}")
        return plan

    entity = intent_data.get("entity")

    if not intent_name:
        plan = [_step("missing_intent")]
        print(f"[Planner] Plan created: {plan}")
        return plan

    # Focus mode is a workflow intent that expands to multiple steps.
    if intent_name == "focus_mode":
        session_name = entity or "default"
        plan = [
            _step("save_session"),
            _step("close_all_apps"),
            _step("restore_session", name=session_name),
        ]
        print(f"[Planner] Plan created: {plan}")
        return plan

    if intent_name == "save_session":
        plan = [_step("save_session", name=entity or "default")]
        print(f"[Planner] Plan created: {plan}")
        return plan

    if intent_name == "restore_session":
        plan = [_step("restore_session", name=entity or "default")]
        print(f"[Planner] Plan created: {plan}")
        return plan

    if intent_name == "open_app":
        plan = [_step("open_app", entity=entity)]
        print(f"[Planner] Plan created: {plan}")
        return plan

    if intent_name == "close_app":
        plan = [_step("close_app", entity=entity)]
        print(f"[Planner] Plan created: {plan}")
        return plan

    if intent_name == "close_all_apps":
        plan = [_step("close_all_apps")]
        print(f"[Planner] Plan created: {plan}")
        return plan

    # Keep unknown intents non-destructive and planner-only.
    plan = [_step("unsupported_intent", intent=intent_name, entity=entity)]
    print(f"[Planner] Plan created: {plan}")
    return plan
