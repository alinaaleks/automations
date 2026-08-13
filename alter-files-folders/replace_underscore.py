from pathlib import Path

folder = Path(r"O:\MUSIC\MOOD SELECTIONS\recent music")

for file in folder.rglob("*"):
    if not file.is_file():
        continue

    if "_" not in file.name:
        continue

    new_name = file.name.replace("_", " ")
    new_file = file.with_name(new_name)

    if new_file.exists():
        print(f"SKIPPED — target exists:")
        print(f"  {file.name}")
        print(f"  → {new_name}")
        print()
        continue

    file.rename(new_file)

    print(f"RENAMED:")
    print(f"  {file.name}")
    print(f"  → {new_name}")
    print()