# reset_memory.py
"""
Memory Reset Utility

Responsibilities:
- Safely reset the memory file (conversation.json by default)
- Validate JSON structure
- Handle corrupted or missing files gracefully
- Provide utilities for inspection, backup, and restore
"""

import os
import json
import time
from typing import Any, List, Dict, Optional


FILENAME = "conversation.json"


# -----------------------------
# Utilities
# -----------------------------
def _validate_structure(data: Any) -> bool:
    """
    Validate that the memory file structure is a list of dicts
    with 'sender' and 'text' keys.
    """
    if not isinstance(data, list):
        return False
    for m in data:
        if not isinstance(m, dict):
            return False
        if "sender" not in m or "text" not in m:
            return False
    return True


def _backup_file(filename: str) -> Optional[str]:
    """
    Create a backup of the existing file before resetting.
    Returns the backup filename or None if backup failed.
    """
    try:
        backup_name = f"{filename}.bak.{int(time.time())}"
        os.rename(filename, backup_name)
        print(f"Backup created: {backup_name}")
        return backup_name
    except Exception as e:
        print(f"Warning: could not create backup: {e}")
        return None


def _write_empty(filename: str) -> None:
    """
    Write an empty list to the memory file.
    """
    try:
        with open(filename, "w", encoding="utf-8") as f:
            json.dump([], f, indent=2, ensure_ascii=False)
        print(f"{filename} reset successfully.")
    except Exception as e:
        print(f"Error writing empty memory file: {e}")


# -----------------------------
# Core Function
# -----------------------------
def reset_memory(filename: str = FILENAME) -> None:
    """
    Safely reset the memory file.
    - If file exists and is valid JSON with correct structure, leave it intact.
    - If file exists but is corrupted or invalid, back it up and overwrite with empty list.
    - If file doesn't exist, create a fresh one.
    """
    if os.path.exists(filename):
        try:
            with open(filename, "r", encoding="utf-8") as f:
                data = json.load(f)
            if _validate_structure(data):
                print(f"{filename} is valid JSON, no reset needed.")
            else:
                print(f"{filename} has invalid structure. Resetting...")
                _backup_file(filename)
                _write_empty(filename)
        except json.JSONDecodeError:
            print(f"{filename} is corrupted. Resetting...")
            _backup_file(filename)
            _write_empty(filename)
        except Exception as e:
            print(f"Error reading {filename}: {e}. Resetting...")
            _backup_file(filename)
            _write_empty(filename)
    else:
        print(f"{filename} not found. Creating fresh file...")
        _write_empty(filename)


# -----------------------------
# Inspection Utilities
# -----------------------------
def inspect_memory(filename: str = FILENAME) -> List[Dict[str, str]]:
    """
    Inspect and return the contents of the memory file.
    Returns an empty list if file is missing or invalid.
    """
    if not os.path.exists(filename):
        print(f"{filename} not found.")
        return []
    try:
        with open(filename, "r", encoding="utf-8") as f:
            data = json.load(f)
        if _validate_structure(data):
            return data
        else:
            print("Invalid structure in memory file.")
            return []
    except Exception as e:
        print(f"Error inspecting memory: {e}")
        return []


def clear_memory(filename: str = FILENAME) -> None:
    """
    Clear memory file contents without backup.
    """
    _write_empty(filename)
    print("Memory cleared.")


# -----------------------------
# Entry Point
# -----------------------------
if __name__ == "__main__":
    reset_memory()
    print("Current memory contents:", inspect_memory())
