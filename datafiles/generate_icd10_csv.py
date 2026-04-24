import csv
import os

txt_path = "icd10cm_codes_2026.txt"
csv_path = "icd10.csv"

def convert():
    print(f"Converting {txt_path} to {csv_path}...")
    with open(txt_path, 'r', encoding='utf-8') as fin, open(csv_path, 'w', encoding='utf-8', newline='') as fout:
        writer = csv.writer(fout)
        writer.writerow(["code", "description"])
        for line in fin:
            if not line.strip():
                continue
            # The code is up to 7 characters, then there is whitespace, then the description
            # E.g., "A000    Cholera due to..."
            parts = line.strip().split(maxsplit=1)
            if len(parts) == 2:
                writer.writerow([parts[0], parts[1]])
            else:
                writer.writerow([parts[0], ""])
    print("Done.")

if __name__ == "__main__":
    convert()
