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
    parser.add_argument('--config', default='config.yaml')
    parser.add_argument('--experiment-name', default='Experiment', help='Name of the experiment (overrides config file)')
    parser.add_argument('--model-a', help='Model name for speaker A')
    parser.add_argument('--model-b', help='Model name for speaker B')
    parser.add_argument('--turns', type=int, default=None)
    parser.add_argument('--history-max-chars', type=int, default=0, help='If >0, truncate each appended message to this many characters (0 = unlimited)')
    parser.add_argument('--transcript', default=None, help='Path to save transcript (md)')
    parser.add_argument('--dry-run', action='store_true', help='Do not contact Ollama; use mock replies')
    args = parser.parse_args()

    cfg = load_config(args.config)
    
    # Read experiment_name from the config
    experiment_name = cfg.get('experiment_name', 'Unnamed-Experiment')
    
    model_a = args.model_a or cfg.get('model_a')
    model_b = args.model_b or cfg.get('model_b')
    turns = args.turns or cfg.get('turns', 6)
    system_a = cfg.get('system_prompt_a', 'You are Speaker A.')
    system_b = cfg.get('system_prompt_b', 'You are Speaker B.')
    initial_prompt = cfg.get('initial_prompt', 'Hello!')

    client = OllamaClient(dry_run=args.dry_run)
    tm = TranscriptManager(folder=cfg.get('transcript_folder', 'transcripts'))
    history_max = cfg.get('history_max_chars', 0)

    transcript_messages = []
    messages_a = [build_message('system', system_a), build_message('user', initial_prompt)]
    messages_b = [build_message('system', system_b)]

    now = time.strftime('%Y-%m-%dT%H:%M:%S')
    transcript_messages.append({'speaker': 'User', 'text': initial_prompt, 'timestamp': now})
    print(f"User: {initial_prompt}")

    # Main conversation loop...
    # (The rest of your conversation logic remains the same)
    # ...
    # Speaker A produces the first reply
    a_reply = client.chat(model_a, messages_a)
    now = time.strftime('%Y-%m-%dT%H:%M:%S')
    transcript_messages.append({'speaker': f'{model_a}', 'text': a_reply, 'timestamp': now})
    print(f"{model_a}: {a_reply}")
    messages_a.append(build_message('assistant', a_reply))
    user_for_b = a_reply if history_max == 0 else a_reply[-history_max:]
    messages_b.append(build_message('user', user_for_b))

    for i in range(turns - 1):
        b_reply = client.chat(model_b, messages_b)
        now = time.strftime('%Y-%m-%dT%H:%M:%S')
        transcript_messages.append({'speaker': f'{model_b}', 'text': b_reply, 'timestamp': now})
        print(f"{model_b}: {b_reply}")
        messages_b.append(build_message('assistant', b_reply))
        user_for_a = b_reply if history_max == 0 else b_reply[-history_max:]
        messages_a.append(build_message('user', user_for_a))

        a_reply = client.chat(model_a, messages_a)
        now = time.strftime('%Y-%m-%dT%H:%M:%S')
        transcript_messages.append({'speaker': f'{model_a}', 'text': a_reply, 'timestamp': now})
        print(f"{model_a}: {a_reply}")
        messages_a.append(build_message('assistant', a_reply))
        user_for_b = a_reply if history_max == 0 else a_reply[-history_max:]
        messages_b.append(build_message('user', user_for_b))
    # ... (end of loop)

    # Save transcript
    out_path = args.transcript
    if out_path is None:
        # --- (B) Use the new make_filename with the experiment name ---
        out_path = tm.make_filename(experiment_name=experiment_name)
    
    # --- (C) Pass the entire config object 'cfg' to save_transcript ---
    tm.save_transcript(transcript_messages, cfg, out_path)
    print(f"Saved transcript to {out_path}")

if __name__ == '__main__':
    main()