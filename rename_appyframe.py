import os
import re

OLD = "appyframe"
NEW = "appyframe"
EXCLUDE_DIRS = {'.git', '__pycache__', 'node_modules', 'venv', '.idea', '.vscode'}

def replace_in_file(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        new_content = content
        new_content = re.sub(r'\bfrappe\b', NEW, new_content)
        new_content = re.sub(r'\bFrappe\b', NEW.capitalize(), new_content)
        new_content = re.sub(r'\bFRAPPE\b', NEW.upper(), new_content)

        if content != new_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            print(f"[✔] Updated content: {file_path}")
    except Exception as e:
        print(f"[!] Error in {file_path}: {e}")

def rename_if_needed(path):
    base = os.path.basename(path)
    parent = os.path.dirname(path)
    new_base = base.replace(OLD, NEW).replace(OLD.capitalize(), NEW.capitalize()).replace(OLD.upper(), NEW.upper())
    new_path = os.path.join(parent, new_base)

    if new_path != path:
        try:
            os.rename(path, new_path)
            print(f"[✔] Renamed: {path} → {new_path}")
            return new_path
        except Exception as e:
            print(f"[!] Rename failed: {path} → {new_path} | {e}")
    return path

def walk_and_replace(root_dir):
    # أولاً: استبدال النصوص داخل الملفات
    for root, dirs, files in os.walk(root_dir):
        dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS]
        for file in files:
            replace_in_file(os.path.join(root, file))

    # ثانياً: إعادة تسمية الملفات
    for root, dirs, files in os.walk(root_dir, topdown=False):
        dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS]
        for file in files:
            path = os.path.join(root, file)
            rename_if_needed(path)

        for dir in dirs:
            path = os.path.join(root, dir)
            rename_if_needed(path)

if __name__ == "__main__":
    print("[*] Starting rename process...")
    walk_and_replace(os.getcwd())
    print("[✓] Done.")
