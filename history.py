"""History persistence manager for snake length leaderboard records.

This class encapsulates loading, migrating, and saving persistent leaderboard
records to a JSON file. Records are dictionaries containing ``name``,
``length``, and a ``timestamp``. The loader performs a safe migration of the
legacy ``score`` field to the new ``length`` field to maintain compatibility
with older files.
"""

import json
import os
from decorators import history_pipeline

class GameHistoryManager:
    """Manage history logging and persistent leaderboard records."""
    def __init__(self, filename="snake_history.json"):
        self.filename = filename

    def load_history(self):
        """Load the persisted leaderboard history from a JSON file."""
        if not os.path.exists(self.filename):
            return []
        try:
            with open(self.filename, "r", encoding="utf-8") as f:
                data = json.load(f)
                if not isinstance(data, list):
                    return []

            # Migrate legacy records that used the 'score' key to the new 'length' key.
            migrated = False
            for rec in data:
                if isinstance(rec, dict) and "score" in rec:
                    rec["length"] = rec.pop("score")
                    migrated = True

            if migrated:
                try:
                    with open(self.filename, "w", encoding="utf-8") as f:
                        json.dump(data, f, indent=4)
                except IOError:
                    # If migration write fails, continue using the in-memory migrated data
                    pass

            return data
        except (json.JSONDecodeError, IOError):
            return []

    @history_pipeline
    def save_record(self, name, length):
        """Save a leaderboard record and sort the table by descending length."""
        history = self.load_history()
        history.append({
            "name": name,
            "length": length,
        })
        history.sort(key=lambda r: r.get("length", 0), reverse=True)


        try:
            with open(self.filename, "w", encoding="utf-8") as f:
                json.dump(history, f, indent=4)
        except IOError as e:
            print(f"[IO EXCEPTION] Failed flushing database pipeline: {e}")
