import os
import json

FILENAME = "conversation.json"

def reset_memory():
    """
    Safely reset the memory file.
    - If file exists and is corrupted, overwrite with empty list.
    - If file doesn't exist, create a fresh one.
    """
    if os.path.exists(FILENAME):
        try:
            with open(FILENAME, "r", encoding="utf-8") as f:
                json.load(f)  # try to parse
            print(f"{FILENAME} is valid JSON, no reset needed.")
        except Exception:
            print(f"{FILENAME} is corrupted. Resetting...")
            with open(FILENAME, "w", encoding="utf-8") as f:
                json.dump([], f, indent=2, ensure_ascii=False)
            print("Memory file reset successfully.")
    else:
        print(f"{FILENAME} not found. Creating fresh file...")
        with open(FILENAME, "w", encoding="utf-8") as f:
            json.dump([], f, indent=2, ensure_ascii=False)
        print("Memory file created successfully.")

if __name__ == "__main__":
    reset_memory()
