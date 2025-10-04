"""Small Ollama client wrapper with a dry-run fallback.

This module intentionally keeps network calls optional: use `dry_run=True` to avoid contacting Ollama.
"""
import json
import requests

class OllamaClient:
    def __init__(self, host="http://localhost:11434", dry_run=False, timeout=60):
        self.host = host.rstrip('/')
        self.dry_run = dry_run
        self.timeout = timeout

    def chat(self, model: str, messages: list) -> str:
        """
        Send a chat-style request to Ollama and return the complete, concatenated text reply.
        """
        if self.dry_run:
            joined = messages[-1]["content"] if messages else "(no input)"
            return f"[dry-run] Mock reply from {model} to: {joined}"

        # To handle streaming, we must set stream=True in the request
        url = f"{self.host}/api/chat"
        # Set "stream": False in the payload to get a single JSON response
        payload = {"model": model, "messages": messages, "stream": False}

        try:
            r = requests.post(url, json=payload, timeout=self.timeout)
            r.raise_for_status()  # Raise an exception for bad status codes (4xx or 5xx)

            # --- MODIFIED RESPONSE HANDLING ---
            # With "stream": False, the response is a single JSON object.
            response_data = r.json()
            
            # Extract content from the standard Ollama response structure
            if 'message' in response_data and 'content' in response_data['message']:
                return response_data['message']['content']
            
            # Fallback for other possible structures, though less common for /api/chat
            if 'response' in response_data:
                return response_data['response']

            # If no known content key is found, return the raw JSON as a string for debugging
            return r.text

        except requests.exceptions.ConnectionError as e:
            raise RuntimeError(f"Failed to connect to Ollama at {self.host} — is Ollama running?") from e
        except requests.exceptions.HTTPError as e:
            raise RuntimeError(f"Ollama returned an error: {r.status_code} - {r.text}") from e
        except json.JSONDecodeError:
            raise RuntimeError(f"Failed to decode JSON response from Ollama: {r.text}")