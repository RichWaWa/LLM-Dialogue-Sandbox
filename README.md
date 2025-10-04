LLMSnitch — two local LLMs talking via Ollama

Overview

This project runs two locally-hosted LLMs (via ollama) and has them talk to each other while transcribing the conversation to a readable file.

Features
- Start two LLMs locally using Ollama (you must have Ollama installed and models available).
- Run the two models talking to each other for N turns.
- Save transcripts in markdown format (timestamped files under `transcripts/`).
- `--dry-run` mode that doesn't contact Ollama (useful for testing).

Quick start (Windows PowerShell)

1. Create a virtual environment and activate it:

```powershell
python -m venv .venv; .\.venv\Scripts\Activate.ps1
```

2. Install dependencies:

```powershell
python -m pip install -r requirements.txt
```

3. Run the conversation (dry run):

```powershell
python run.py --dry-run --turns 4
```

4. Run for real (ensure Ollama is running locally and models are available):

```powershell
python run.py --model-a llama2 --model-b vicuna --turns 10 --transcript transcripts/session.md
```

History management and truncation

Long conversations can cause the message history to grow without bound. This project provides a simple character-based truncation flag to control how much of the previous model output is appended to the other model's input.

- No truncation (default):

```powershell
python run.py --dry-run --turns 6
```

- Limit appended history to the last 1000 characters:

```powershell
python run.py --dry-run --turns 20 --history-max-chars 1000
```

- Real run with history limit (example):

```powershell
python run.py --model-a llama2 --model-b vicuna --turns 50 --history-max-chars 2000 --transcript transcripts/session.md
```

Why transcripts looked truncated before

Earlier versions of the dry-run helper returned only the first 200 characters of the last message; that caused subsequent messages to be built from truncated input and made the transcript appear to "run out". The dry-run mock has been updated to return the full message content. Note that when using a real LLM, truncation can still happen if you intentionally limit history or if you parse only part of the model's response.

Token-based truncation (recommended)

Character-based truncation is a simple option but not ideal because tokens and characters don't map 1:1. For robust long-running conversations consider token-budget truncation (keep the last N tokens) using a tokenizer such as `tiktoken`. If you'd like, I can add token-based truncation with a per-model token budget and unit tests.

Files
- `run.py` — main runner/CLI.
- `llm_client.py` — small Ollama client wrapper with a dry-run fallback.
- `transcript_manager.py` — utilities to write transcripts.
- `config.yaml.example` — example configuration.
- `requirements.txt` — dependencies.

Notes
- This project assumes Ollama is exposed on `http://localhost:11434`. If your Ollama API differs or requires the CLI, update `llm_client.py` accordingly.

License: MIT
