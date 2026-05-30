# RIYA — Project Context (Permanent AI Memory)

## Project Vision
RIYA (Responsive Intelligence with Yielded Authority) is a Python-based AI operating assistant designed to control and manage the user's digital environment like Jarvis.

Primary goal:
A real usable personal OS assistant before becoming a product.

---

## Core Philosophy
- Offline-first system
- Fast execution over heavy AI responses
- Modular architecture
- Stability over rapid feature growth
- Human command → Intent → Capability → Execution

---

## Current Architecture (v2)

### Main Systems
- Offline/Online Router
- Intent Detection System (NLU)
- Capability Manager
- Command Executor
- Session Manager
- Runtime Memory (tracks opened apps)
- Focus Mode (in development)

---

### Modules
- riya.py → main loop & orchestration
- listener.py → speech recognition
- speech.py → text-to-speech
- commands.py → system/app commands
- config.py → constants & settings

---

## Behavior Rules
1. Never rewrite working modules completely.
2. Prefer minimal safe edits.
3. Maintain modular separation.
4. Do not introduce heavy dependencies.
5. Always preserve offline capability.
6. Stability is more important than cleverness.

---

## Development Style
- Small incremental improvements
- Debug before redesign
- Explain reasoning briefly before changes
- Avoid unnecessary refactoring

---

## Current Goal
Build RIYA into a stable OS-level assistant capable of:
- controlling apps
- managing sessions
- executing workflows
- acting as a digital operating intelligence

---

## Role of AI Assistant
You are a senior software engineer working ON RIYA.

Your job:
- diagnose problems
- suggest minimal fixes
- implement features safely
- respect existing architecture