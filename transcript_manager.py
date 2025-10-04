import os
import json
from datetime import datetime

class TranscriptManager:
    def __init__(self, folder="transcripts"):
        self.folder = folder
        os.makedirs(self.folder, exist_ok=True)

    def make_filename(self, base_name=None):
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        if base_name:
            safe = base_name.replace(' ', '_')
            invalid = '<>:"/\\|?*'
            for ch in invalid:
                safe = safe.replace(ch, '')
            if len(safe) > 200:
                safe = safe[:200]
            return os.path.join(self.folder, f"{ts}_{safe}.md")
        return os.path.join(self.folder, f"{ts}_transcript.md")
    
    # --- THIS IS THE KEY FUNCTION THAT WAS MODIFIED ---
    def _extract_content(self, raw_text):
        """
        Parses a string containing one or more concatenated JSON objects,
        extracts the content from each, and joins them into a single string.
        """
        if not isinstance(raw_text, str):
            return str(raw_text)

        full_content = []
        decoder = json.JSONDecoder()
        pos = 0
        
        # Trim whitespace to avoid errors with the decoder
        raw_text = raw_text.strip()
        
        while pos < len(raw_text):
            try:
                # Decode one JSON object from the string
                obj, end_pos = decoder.raw_decode(raw_text[pos:])
                
                # Extract content from the common API shape {'message': {'content': '...'}}
                if isinstance(obj, dict):
                    message = obj.get('message', {})
                    if isinstance(message, dict):
                        content = message.get('content')
                        if content:
                            full_content.append(content)
                
                # Move position to the start of the next object
                pos += end_pos
            except json.JSONDecodeError:
                # If it's not JSON or there's an error, stop processing this string
                # This handles cases where the raw_text might be simple text
                return raw_text

        return "".join(full_content)

    def save_transcript(self, messages, file_path=None):
        """Saves a new transcript, parsing the content from raw message text."""
        if file_path is None:
            file_path = self.make_filename()

        lines = []
        title_ts = datetime.now().isoformat()
        lines.append(f"# Transcript — {title_ts}\n")
        
        for m in messages:
            t = m.get('timestamp') or datetime.now().isoformat()
            speaker = m.get('speaker', 'unknown')
            raw = m.get('text', '')
            
            # Use the new extraction logic
            text = self._extract_content(raw) 
            
            lines.append(f"## {speaker} — {t}\n")
            lines.append(text + "\n")

        with open(file_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(lines))
        return file_path

    def append_to_transcript(self, messages, file_path):
        """Appends to an existing transcript, also parsing the content."""
        if not os.path.exists(file_path):
            return self.save_transcript(messages, file_path)

        lines = []
        for m in messages:
            t = m.get('timestamp') or datetime.now().isoformat()
            speaker = m.get('speaker', 'unknown')
            raw = m.get('text', '')
            
            # --- FIX: This method now also uses the parsing function ---
            text = self._extract_content(raw)
            
            lines.append(f"\n## {speaker} — {t}\n")
            lines.append(text + "\n")

        with open(file_path, 'a', encoding='utf-8') as f:
            f.write('\n'.join(lines))
        return file_path