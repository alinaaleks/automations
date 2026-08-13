from pathlib import Path
import re
from mutagen.flac import FLAC

# Folder containing your music
folder = Path(r"C:\Users\alinaaleks\Downloads\Melody Gardot - Currency of Man")

for file in folder.rglob("*.flac"):
    try:
        audio = FLAC(file)

        # Read artist from FLAC metadata
        artist = audio.get("artist", ["Unknown Artist"])[0].strip()

        # Remove track number from filename
        # "01 - Don't Misunderstand" → "Don't Misunderstand"
        title = re.sub(r"^\d+\s*-\s*", "", file.stem).strip()

        new_name = f"{artist} - {title}{file.suffix}"

        if file.name == new_name:
            print(f"ALREADY CORRECT: {file.name}")
        else:
            print(f"WOULD RENAME:")
            print(f"  {file.name}")
            print(f"  → {new_name}")
            file.rename(file.with_name(new_name))

    except Exception as e:
        print(f"ERROR: {file}")
        print(f"  {e}")
        print()