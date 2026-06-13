"""
Smart deduplication script that removes duplicate images while keeping
each image in the most appropriate character folder.

Priority rules:
1. Keep in the folder matching the character name in the path
2. For same-character cross-subfolder dupes: keep in the most specific folder
   (fan-art-nsfw > fan-art > game-screens for nsfw content, game-screens first for game content)
3. For cross-character dupes: keep in the folder whose character name appears in the path
"""

import json
import re
import os
from pathlib import Path

MEDIA_DIR = Path(__file__).parent / "media" / "marvel-rivals"
DUPLICATES_FILE = Path(__file__).parent / "duplicates_exact.json"

CHARACTERS = [
    "angela", "black-cat", "black-widow", "cloak-&-dagger",
    "elsa-bloodstone", "emma-frost", "hela", "invisible-woman",
    "luna-snow", "magik", "mantis", "peni-parker", "phoenix",
    "psylocke", "rogue", "scarlet-witch", "squirrel-girl",
    "storm", "white-fox",
]

SUBFOLDER_PRIORITY = {
    "fan-art-nsfw": 3,
    "fan-art": 2,
    "game-screens": 1,
}


def get_character_from_path(filepath: str) -> str | None:
    """Extract the character folder name from the path."""
    path = Path(filepath)
    for part in path.parts:
        if part in CHARACTERS:
            return part
    return None


def get_subfolder_from_path(filepath: str) -> str | None:
    """Extract the subfolder type from the path."""
    for subfolder in SUBFOLDER_PRIORITY:
        if subfolder in filepath:
            return subfolder
    return None


def score_file(filepath: str) -> int:
    """
    Score a file for how much it "belongs" where it is.
    Higher score = more reason to keep it.
    """
    score = 0
    path = Path(filepath)
    char = get_character_from_path(filepath)
    subfolder = get_subfolder_from_path(filepath)

    if char and char in path.name:
        score += 10

    if subfolder:
        score += SUBFOLDER_PRIORITY.get(subfolder, 0)

    score += path.stat().st_size // 10000

    return score


def process_duplicates():
    with open(DUPLICATES_FILE) as f:
        data = json.load(f)

    total_removed = 0
    total_kept = 0
    removed_files = []

    for size_key, groups in data.items():
        for group in groups:
            if len(group) < 2:
                continue

            files = [item["path"] for item in group]
            scored = [(score_file(f), f) for f in files]
            scored.sort(key=lambda x: x[0], reverse=True)

            keep = scored[0][1]
            to_remove = [f for _, f in scored[1:]]

            for filepath in to_remove:
                removed_files.append(filepath)
                total_removed += 1
            total_kept += 1

    print(f"Duplicate groups processed: {total_kept}")
    print(f"Files to remove: {total_removed}")
    print(f"\nSample removals:")
    for f in removed_files[:10]:
        print(f"  DEL: {Path(f).relative_to(MEDIA_DIR)}")

    confirm = input(f"\nProceed with removing {total_removed} files? (y/n): ")
    if confirm.lower() != "y":
        print("Aborted.")
        return

    actually_removed = 0
    for filepath in removed_files:
        try:
            os.remove(filepath)
            actually_removed += 1
        except OSError as e:
            print(f"  Error removing {filepath}: {e}")

    print(f"\nRemoved {actually_removed} duplicate files.")


if __name__ == "__main__":
    process_duplicates()
