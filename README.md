LLM Dialogue Sandbox — orchestrate, transcribe, and analyze LLM-to-LLM conversations

## Overview

LLM Dialogue Sandbox is a Python framework designed for orchestrating, transcribing, and analyzing dialogues between two Large Language Models (LLMs). It serves as an experimental sandbox to study emergent behaviors, conversational patterns, and the influence of external information on AI interactions. The primary goal of this project is to provide a simple yet powerful tool for researchers, developers, and enthusiasts to explore how LLMs converse with each other.

Future development will focus on enhancing the ability to manually inject specific context into either agent during a conversation, allowing for targeted experiments on influence and reasoning.

## Features

- Orchestrate a back-and-forth conversation between two models (local Ollama models by default).
- Command-line runner with configurable experiment name, model names, turn count, history truncation, and transcript output.
- Dry-run mode that uses a mock client for fast testing without contacting Ollama.
- Saves readable, timestamped markdown transcripts under the `transcripts/` folder by default.
- Simple character-based history truncation (configurable); easy to extend to token-based truncation.

## Quick start (Windows PowerShell)

1. Create a virtual environment and activate it:

```powershell
python -m venv .venv; .\.venv\Scripts\Activate.ps1
```

2. Install dependencies:

```powershell
python -m pip install -r requirements.txt
```

3. Run a dry-run conversation (no Ollama calls):

```powershell
python run.py --dry-run --turns 4
```

4. Run for real (ensure Ollama is running locally and models are available):

```powershell
python run.py --model-a llama2 --model-b vicuna --turns 10 --transcript transcripts/session.md
```

## CLI reference

The main runner is `run.py`. Relevant flags (and defaults) are:

- `--config` (default: `config.yaml`) — path to YAML config file.
- `--experiment-name` (default: from config or `Experiment`) — name used in generated transcript filenames.
- `--model-a` — model name for speaker A (overrides config).
- `--model-b` — model name for speaker B (overrides config).
- `--turns` (int) — number of turns to run (overrides config; default in config or 6).
- `--history-max-chars` (int, default 0) — if >0, truncate appended previous messages to this many characters per message (0 = unlimited).
- `--transcript` — path to save the transcript (Markdown). If omitted, a timestamped file is created under `transcripts/`.
- `--dry-run` — do not contact Ollama; use mock replies instead (useful for testing).

The YAML config (default `config.yaml`) can set:

- `experiment_name`, `model_a`, `model_b`, `turns`, `system_prompt_a`, `system_prompt_b`, `initial_prompt`, `transcript_folder`, `history_max_chars`.

## Important implementation notes

- `run.py` contains the CLI and conversation loop. It builds message lists for each agent, calls the LLM client, and appends assistant replies as new user input for the other model.
- `llm_client.py` is a thin wrapper that calls Ollama when available and returns deterministic/mock responses when `--dry-run` is enabled.
- `transcript_manager.py` handles creation of timestamped filenames and saving transcripts (it expects a list of message dicts with `speaker`, `text`, and `timestamp`).
- By default the project assumes Ollama is reachable at `http://localhost:11434`; change `llm_client.py` if your setup differs.

## History truncation and tokens

Current truncation is character-based (`history_max_chars`). This is simple but imperfect because characters != tokens. For long-running experiments consider switching to token-budget truncation (for example using `tiktoken`) — the codebase is structured so this can be added in `run.py` or inside the client.

## Files

- `run.py` — main runner/CLI and conversation loop.
- `llm_client.py` — Ollama client wrapper with a dry-run fallback.
- `transcript_manager.py` — utilities for generating filenames and writing transcripts.
- `config.yaml.example` — example configuration.
- `requirements.txt` — Python dependencies.
- `transcripts/` — folder where transcripts are saved.

## Future work

- Manual injection of targeted context into either agent mid-run (controlled experiments on influence).
- Token-aware truncation and per-model token budgets.
- Better experiment metadata and structured transcript formats (JSON/Parquet) for analysis.

## License

MIT
