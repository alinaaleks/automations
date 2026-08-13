import os
import csv

def analyze_folder_to_csv(root_folder, csv_file):
    # Use utf-8-sig so Excel correctly reads Russian letters
    with open(csv_file, "w", newline='', encoding="utf-8-sig") as f:
        writer = csv.writer(f)
        writer.writerow(["Folder", "Subfolders", "Files", "File Name", "Extension", "Size (KB)"])

        for dirpath, dirnames, filenames in os.walk(root_folder):
            for file in filenames:
                ext = os.path.splitext(file)[1] or "no_extension"
                path = os.path.join(dirpath, file)
                size_kb = os.path.getsize(path) / 1024
                writer.writerow([dirpath, len(dirnames), len(filenames), file, ext, round(size_kb, 2)])

# ✅ Make sure the path is a raw string (r"")
folder_path = r"O:\Sciences\The Teaching Company"
csv_output = "file_report.csv"

analyze_folder_to_csv(folder_path, csv_output)
print("✅ Analysis complete. CSV saved as:", csv_output)