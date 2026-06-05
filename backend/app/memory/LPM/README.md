# Layer 3: Learning Profile Memory

Layer 3 is the learning-profile memory layer for the Personal AI STEM Copilot.

Its job is to read recent tutoring conversation data, extract learning signals, and update the student's local learning profile.

## Main Idea

```text
Layer 1 raw chat log
        ↓
Layer 3 learning signal extraction
        ↓
local learning profile update
        ↓
Layer 5 semantic memory summaries
```

Layer 3 does not ask the student to manually say:

```text
my weakness is chain rule
my learning style is step by step
```

Instead, it analyzes the raw chat and the tutor response.

Example:

```text
Student: I think derivative of sin(x^2) is cos(x^2).
Tutor: That is not correct because you forgot the chain rule.
Student: I made the same mistake again. Can you break it down step by step?
```

Layer 3 should extract:

```text
weakness: differentiation
mistake: forgot inner derivative / chain rule issue
learning style: step by step
confidence: lower than before
```

## Recommended Folder

Use the cleaned version here:

```text
layer3_learning_profile/improvement/
```

That folder removes old leftover logic:

```text
no hardcoded phrase-list extractor in extractor.py
no multi-student logic
no Gemini extractor alias
no old ChatTurn/manual extraction path
no policy.py dependency
```

## Clean Flow

```text
raw chat messages
        ↓
analyzer.py sends recent transcript to Ollama
        ↓
Ollama returns JSON learning signals
        ↓
extractor.py updates scores/profile from those signals
        ↓
storage.py saves one local profile
        ↓
background.py runs this automatically every 5 minutes
```

## Local Student Only

This project is local-only and Gemini-based, with no login/profile selector.

So Layer 3 uses one fixed local student:

```python
LOCAL_STUDENT_ID = "local_student"
```

That means:

```text
one device = one learner profile
```

## Ollama Extractor

Layer 3 uses a free local Ollama model for extraction:

```text
qwen3:4b
```

Install Ollama and pull the model:

```powershell
ollama pull qwen3:4b
```

The analyzer calls:

```text
http://localhost:11434/api/generate
```

This avoids using Gemini quota for memory extraction.

Gemini can remain the visible tutor model. Ollama handles background memory extraction.

## Files In `improvement`

```text
model.py
```

Defines the schemas:

```text
ConversationMessage
ConversationAnalysisRequest
ExtractedLearningSignal
LearningProfile
TopicLearningSignal
MemoryAdapterEntry
SemanticMemoryEvent
ProfileExtraction
```

```text
analyzer.py
```

Sends recent raw chat to Ollama and expects JSON signals back.

```text
extractor.py
```

Takes model-extracted signals and updates the learning profile.

It does not do phrase-list extraction. Ollama does the extraction.

```text
storage.py
```

Loads and saves the one local learning profile as JSON.

```text
background.py
```

Stores raw chat messages in a local buffer and runs extraction every 5 minutes.

It tracks:

```text
processed_count
```

so the same messages are not analyzed again and again.

```text
test_background.py
```

Demo test for the cleaned pipeline. It uses a fake analyzer so the test can run even when Ollama is not running.

```text
__init__.py
```

Exports the clean public package API.

## How To Use In Chat Endpoint

After Gemini gives the visible tutor response, log the completed turn:

```python
service.log_chat_turn(
    subject="math",
    topic="differentiation",
    student_message=user_message,
    assistant_reply=gemini_reply,
)
```

Do this after the normal tutor response is generated.

The user does not see Layer 3 extraction.

## Background Run

Start the background service when the backend starts:

```python
import asyncio
from app.memory.LPM.improvement import Layer3BackgroundService

layer3_service = Layer3BackgroundService()
asyncio.create_task(layer3_service.run_forever())
```

By default it runs every 5 minutes:

```python
interval_seconds=300
```

Every run:

```text
checks for new messages
uses recent messages only
asks Ollama for JSON learning signals
updates local profile
marks messages as processed
```

## Output

Layer 3 returns a `ProfileExtraction`.

Important fields:

```python
result.profile
```

The updated local learning profile.

```python
result.student_info_update
```

Data shaped for your profile API:

```text
learning_style
strong_points
weak_points
```

```python
result.memory_updates
```

Simple memory entries:

```text
memory_type
subject
topic
detail
confidence
```

```python
result.semantic_memory_events
```

Summaries that can later go to Layer 5 semantic/vector memory.

```python
result.mastery_scores
```

Topic mastery scores like:

```python
{"differentiation": 42}
```

## Layer 1 And Layer 5

Layer 3 currently does not directly import functions from Layer 1 or Layer 5.

It is designed to connect by data shape:

```text
Layer 1 gives raw chat messages
Layer 3 produces profile updates and semantic memory events
Layer 5 can store those semantic memory events
```

Direct integration can be added later by calling your Layer 1 and Layer 5 functions from the backend.

## Test

From the folder above `layer3_learning_profile`, run:

```powershell
python -m layer3_learning_profile.improvement.test_background
```

Expected result:

```text
weakness: differentiation
mistake: forgot inner derivative
learning style: step by step
student_id: local_student
```

## Important Notes

The cleaned `improvement` version is the one to use.

The older files outside `improvement` may still contain previous draft logic.

If copying into your backend, copy the contents of:

```text
layer3_learning_profile/improvement/
```

into your backend Layer 3 folder.
