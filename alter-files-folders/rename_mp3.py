from pathlib import Path
from mutagen.mp3 import MP3
import re

# Folder containing your MP3 files
folder = Path(r"O:\MUSIC\MOOD SELECTIONS\from my mp3")


def sanitize_filename(text):
    # Characters not allowed in Windows filenames:
    # < > : " / \ | ? *
    text = re.sub(r'[<>:"/\\|?*]', '', text)

    # Remove control characters
    text = re.sub(r'[\x00-\x1f]', '', text)

    # Windows does not allow filenames to end with a space or period
    text = text.rstrip(' .')

    return text


for file in folder.rglob("*.mp3"):
    try:
        audio = MP3(file)

        # Read Artist and Title from metadata
        artist = audio.get("TPE1")
        title = audio.get("TIT2")

        if not artist or not title:
            print(f"SKIPPED — missing Artist or Title: {file.name}")
            continue

        artist = artist.text[0].strip()
        title = title.text[0].strip()

        # Make Artist and Title safe for Windows filenames
        safe_artist = sanitize_filename(artist)
        safe_title = sanitize_filename(title)

        new_name = f"{safe_artist} - {safe_title}.mp3"
        new_file = file.with_name(new_name)

        if file.name == new_name:
            print(f"ALREADY CORRECT: {file.name}")

        elif new_file.exists():
            print(f"SKIPPED — target already exists:")
            print(f"  {file.name}")
            print(f"  → {new_name}")
            print()

        else:
            # ACTUALLY RENAME THE FILE
            file.rename(new_file)

            print(f"RENAMED:")
            print(f"  {file.name}")
            print(f"  → {new_name}")
            print()

    except Exception as e:
        print(f"ERROR: {file}")
        print(f"  {e}")
        print()