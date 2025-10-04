"""Runner that has two models talk to each other via Ollama.

Supports --dry-run to avoid calling Ollama for tests.
"""
import argparse
import yaml
import time
from llm_client import OllamaClient
from transcript_manager import TranscriptManager


def load_config(path):
    with open(path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)


def build_message(role, content):
    return {"role": role, "content": content}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--config', default='config.yaml.example')
    parser.add_argument('--model-a', help='Model name for speaker A')
    parser.add_argument('--model-b', help='Model name for speaker B')
    parser.add_argument('--turns', type=int, default=None)
    parser.add_argument('--history-max-chars', type=int, default=0, help='If >0, truncate each appended message to this many characters (0 = unlimited)')
    parser.add_argument('--transcript', default=None, help='Path to save transcript (md)')
    parser.add_argument('--dry-run', action='store_true', help='Do not contact Ollama; use mock replies')
    args = parser.parse_args()

    cfg = load_config(args.config)
    model_a = args.model_a or cfg.get('model_a')
    model_b = args.model_b or cfg.get('model_b')
    turns = args.turns or cfg.get('turns', 6)
    system_a = cfg.get('system_prompt_a', 'You are Speaker A.')
    system_b = cfg.get('system_prompt_b', 'You are Speaker B.')
    initial_prompt = cfg.get('initial_prompt', 'Hello!')

    client = OllamaClient(dry_run=args.dry_run)
    tm = TranscriptManager(folder=cfg.get('transcript_folder', 'transcripts'))
    history_max = args.history_max_chars or 0

    transcript_messages = []

    # Prepare full conversation histories for both models
    # Each messages list is a chronological list of dicts: {role, content}
    messages_a = [build_message('system', system_a), build_message('user', initial_prompt)]
    messages_b = [build_message('system', system_b)]

    # --- FIX: Log the initial prompt that starts the conversation ---
    now = time.strftime('%Y-%m-%dT%H:%M:%S')
    transcript_messages.append({'speaker': 'User', 'text': initial_prompt, 'timestamp': now})
    print(f"User: {initial_prompt}")
    # --- END FIX ---

    # Speaker A produces the first reply
    a_reply = client.chat(model_a, messages_a)
    now = time.strftime('%Y-%m-%dT%H:%M:%S')
    transcript_messages.append({'speaker': f'{model_a}', 'text': a_reply, 'timestamp': now})
    print(f"{model_a}: {a_reply}")

    # Append A's reply as assistant in A's history, and as user input in B's history
    messages_a.append(build_message('assistant', a_reply))
    # Optionally truncate the user-visible history before sending to the other model
    user_for_b = a_reply if history_max == 0 else a_reply[-history_max:]
    messages_b.append(build_message('user', user_for_b))

    # Continue alternating: for each remaining turn produce B then A replies
    for i in range(turns - 1):
        # B responds given its full history
        b_reply = client.chat(model_b, messages_b)
        now = time.strftime('%Y-%m-%dT%H:%M:%S')
        transcript_messages.append({'speaker': f'{model_b}', 'text': b_reply, 'timestamp': now})
        print(f"{model_b}: {b_reply}")

        # Append B's reply as assistant in B history and as user input in A history
        messages_b.append(build_message('assistant', b_reply))
        user_for_a = b_reply if history_max == 0 else b_reply[-history_max:]
        messages_a.append(build_message('user', user_for_a))

        # A responds given its full history
        a_reply = client.chat(model_a, messages_a)
        now = time.strftime('%Y-%m-%dT%H:%M:%S')
        transcript_messages.append({'speaker': f'{model_a}', 'text': a_reply, 'timestamp': now})
        print(f"{model_a}: {a_reply}")

        # Append A's reply into both histories for the next round
        messages_a.append(build_message('assistant', a_reply))
        user_for_b = a_reply if history_max == 0 else a_reply[-history_max:]
        messages_b.append(build_message('user', user_for_b))

    # Save transcript
    out_path = args.transcript
    if out_path is None:
        out_path = tm.make_filename(base_name=f"{model_a}_vs_{model_b}")
    tm.save_transcript(transcript_messages, out_path)
    print(f"Saved transcript to {out_path}")


if __name__ == '__main__':
    main()
