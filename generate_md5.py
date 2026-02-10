#!/usr/bin/env python3
import hashlib
import os

# katalog z raportami
DATA_DIR = "raporty"  # <-- zmienione na folder z Twoimi plikami

def make_md5(path):
    with open(path, "rb") as f:
        data = f.read()
        return hashlib.md5(data).hexdigest()

def main():
    for fname in os.listdir(DATA_DIR):
        if fname.endswith((".csv", ".jsonld", ".xlsx", ".xml")):
            fpath = os.path.join(DATA_DIR, fname)
            md5 = make_md5(fpath)
            md5path = fpath + ".md5"
            with open(md5path, "w") as out:
                out.write(md5)
            print(f"✔ {md5path} zapisany ({md5})")

if __name__ == "__main__":
    main()
