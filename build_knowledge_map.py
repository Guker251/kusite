from pathlib import Path
import re
import yaml

BOOK_DIR = Path("docs/book")
OUTPUT_FILE = BOOK_DIR / "knowledge-map.yaml"
IGNORE_FILES = {"index.md", "knowledge-map.yaml"}

def make_topic_id(filename: str) -> str:
    name = filename.removesuffix(".md").strip().lower()
    name = name.replace(" ", "-").replace("_", "-")
    name = re.sub(r"[^a-zA-Zа-яА-Я0-9\-]+", "-", name)
    name = re.sub(r"-{2,}", "-", name).strip("-")
    return name

def extract_headings(text: str):
    h1 = None
    subtopics = []

    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue

        if line.startswith("# "):
            if h1 is None:
                h1 = line[2:].strip()
        elif line.startswith("## "):
            subtopics.append(line[3:].strip())
        elif line.startswith("### "):
            subtopics.append(line[4:].strip())

    return h1, subtopics

def build_knowledge_map():
    topics = {}

    if not BOOK_DIR.exists():
        raise FileNotFoundError(f"Папка не найдена: {BOOK_DIR}")

    for file_path in sorted(BOOK_DIR.glob("*.md")):
        if file_path.name in IGNORE_FILES:
            continue

        text = file_path.read_text(encoding="utf-8")
        title, subtopics = extract_headings(text)

        topic_id = make_topic_id(file_path.name)

        if not title:
            title = file_path.stem

        # Убираем дубли и пустые значения, сохраняя порядок
        seen = set()
        clean_subtopics = []
        for item in subtopics:
            item = item.strip()
            if item and item not in seen:
                seen.add(item)
                clean_subtopics.append(item)

        topics[topic_id] = {
            "title": title,
            "description": "",
            "subtopics": clean_subtopics,
            "sources": [str(file_path).replace("\\", "/")]
        }

    data = {"topics": topics}

    with OUTPUT_FILE.open("w", encoding="utf-8") as f:
        yaml.dump(
            data,
            f,
            allow_unicode=True,
            sort_keys=False,
            width=1000
        )

    print(f"Готово: {OUTPUT_FILE}")

if __name__ == "__main__":
    build_knowledge_map()