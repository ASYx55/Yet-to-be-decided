# Ollama-First Layer 3

**Layer 3: Learning Profile Memory**.

Layer 3 analyzes a completed student-AI chat turn, extracts learning signals with a local Ollama model, and updates one local student profile.

## Flow

```text
student message + Gemini reply
        ↓
Layer3MessageProcessor.process_chat_turn(...)
        ↓
Ollama extracts learning signals
        ↓
LearningProfileExtractor updates profile
        ↓
LearningProfileStore saves local JSON memory
```

There is no timer and no polling. The API already knows when a new message happens, so the chat endpoint should call Layer 3 after Gemini returns a reply.

## What It Extracts

Layer 3 can store signals like:

- weaknesses
- strengths
- repeated mistakes
- confidence
- learning speed
- preferred learning style

## Files

- `model.py`: data schemas for chat messages, extracted signals, profile memory, and outputs
- `analyzer.py`: sends raw chat to local Ollama, default model `qwen3:4b`
- `extractor.py`: updates the learning profile from Ollama-extracted signals
- `storage.py`: saves and loads one local student profile
- `background.py`: event-based processor for each new completed chat turn
- `test_background.py`: demo test using a fake analyzer
- `__init__.py`: package exports

## Local Student

This project is local-only, with no login or profile selector.

So Layer 3 uses:

```python
LOCAL_STUDENT_ID = "local_student"
```

## Ollama Setup

Install Ollama and pull the extractor model:

```powershell
ollama pull qwen3:4b
```

The analyzer calls:

```text
http://localhost:11434/api/generate
```

## Usage In `/chat`

After Gemini creates the normal tutor reply, call Layer 3:

```python
from app.memory.LPM import Layer3MessageProcessor

layer3 = Layer3MessageProcessor()

result = layer3.process_chat_turn(
    subject=request.subject,
    topic=request.topic,
    student_message=request.message,
    assistant_reply=reply,
)
```

The user does not need to ask for memory extraction. It happens automatically when the API processes a new chat turn.

## Test

From the backend root, run:

```powershell
python -m app.memory.LPM.test_background
```

The demo should show a local profile with a detected weakness and learning style.
