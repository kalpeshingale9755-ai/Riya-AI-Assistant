# runtime/lifecycle.py
# Lifecycle management (startup, shutdown, etc.) for the Riya runtime
# riya_engine/runtime/lifecycle.py

class TaskState:

    PENDING = "PENDING"

    RUNNING = "RUNNING"

    SUCCESS = "SUCCESS"

    FAILED = "FAILED"

    RETRYING = "RETRYING"