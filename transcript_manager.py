import os
import json
from datetime import datetime
import yaml # <-- Import the yaml library

class TranscriptManager:
    def __init__(self, folder="transcripts"):
        self.folder = folder
        os.makedirs(self.folder, exist_ok=True)

    # this method creates a filename based on the current date and an experiment name
    def make_filename(self, experiment_name="Unnamed-Experiment"):
        """
        Creates a filename in the format 'Experiment-X-mm-dd-yyyy.md'.
        If the file exists, it appends an incrementing number (X2, X3, etc.).
        """
        date_str = datetime.now().strftime("%m-%d-%Y")
        
        # Sanitize the base experiment name
        safe_name = experiment_name.replace(' ', '_')
        invalid_chars = '<>:"/\\|?*'
        for char in invalid_chars:
            safe_name = safe_name.replace(char, '')
        
        # --- New logic to check for existing files ---

        # 1. Check the base filename first (e.g., "Experiment-A-date.md")
        base_filename = f"Experiment-{safe_name}-{date_str}.md"
        full_path = os.path.join(self.folder, base_filename)
        
        if not os.path.exists(full_path):
            return full_path
            
        # 2. If the base file exists, start a loop to find the next available number
        counter = 2
        while True:
            # Create a new name with the counter (e.g., "Experiment-A2-date.md")
            incremented_name = f"{safe_name}{counter}"
            new_filename = f"Experiment-{incremented_name}-{date_str}.md"
            new_path = os.path.join(self.folder, new_filename)
            
            if not os.path.exists(new_path):
                return new_path  # Found an available filename
            
            counter += 1

    # this method saves a transcript to a file, including config data at the top
    def save_transcript(self, messages, config_data, file_path=None):
        """Saves a new transcript, including the experiment config at the top."""
        if file_path is None:
            # Note: The experiment_name from config should be passed to make_filename
            # This is just a fallback.
            exp_name = config_data.get('experiment_name', 'Unnamed-Experiment')
            file_path = self.make_filename(experiment_name=exp_name)

        lines = []
        title_ts = datetime.now().isoformat()
        lines.append(f"# Transcript — {title_ts}\n")
        
        # Add the configuration data to the transcript
        lines.append("## Experiment Configuration\n")
        # Use yaml.dump to format the config dictionary nicely
        config_yaml_str = yaml.dump(config_data, default_flow_style=False, sort_keys=False)
        lines.append("```yaml\n")
        lines.append(config_yaml_str)
        lines.append("```\n")

        for m in messages:
            t = m.get('timestamp') or datetime.now().isoformat()
            speaker = m.get('speaker', 'User') # Default to User for the initial prompt
            text = m.get('text', '')
            
            lines.append(f"## {speaker} — {t}\n")
            lines.append(text + "\n")

        with open(file_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(lines))
        return file_path

    # this method appends to an existing transcript
    # Note: _extract_content is no longer needed here if llm_client handles parsing, but we'll leave it for now.
    def _extract_content(self, raw_text):
        return str(raw_text) # Simplified since llm_client now returns clean strings
    
    # this method appends to an existing transcript
    def append_to_transcript(self, messages, file_path):
        """Appends to an existing transcript."""
        if not os.path.exists(file_path):
            # This path is less likely to be used now, but we'll leave it.
            # It's missing config_data, so creating a new file should be done via save_transcript.
            print("Warning: Appending to a non-existent file. Config will be missing.")
            return self.save_transcript(messages, {}, file_path)

        lines = []
        for m in messages:
            t = m.get('timestamp') or datetime.now().isoformat()
            speaker = m.get('speaker', 'unknown')
            text = m.get('text', '')
            
            lines.append(f"\n## {speaker} — {t}\n")
            lines.append(text + "\n")

        with open(file_path, 'a', encoding='utf-8') as f:
            f.write('\n'.join(lines))
        return file_path