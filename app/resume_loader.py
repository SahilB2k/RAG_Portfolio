# app/resume_loader.py
def load_markdown(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        return f.read()