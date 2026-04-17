"""
Генератор поискового индекса для alkonorm.ru.
Запуск: python build_search_index.py
Только стандартная библиотека Python.
"""

import re
from html.parser import HTMLParser
from pathlib import Path
from typing import Optional


BASE_DIR = Path("/Users/guker/Desktop/ku")
OUTPUT_FILE = BASE_DIR / "search_index.js"

# Файлы, которые не являются страницами сайта
EXCLUDED_FILES = {
    "docs/article-skeleton.html",
    "sidebar-menu-prototype.html",
    "newmain.html",
}

# Папки верхнего уровня, которые не трогаем
EXCLUDED_TOP_DIRS = {"arhiv", "assets", "books", "docs", "pic"}

HEADING_TAGS = {"h1", "h2", "h3"}
SKIP_TAGS = {"script", "style", "noscript"}


class PageParser(HTMLParser):
    """Парсит HTML, извлекая заголовок, текст и секции."""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self._skip_depth = 0

        self._in_title = False
        self._title_parts: list[str] = []

        self._texts: list[str] = []

        # Для построения секций
        self._current_h_tag: Optional[str] = None  # "h2" / "h3" и т.д.
        self._current_h_text: Optional[str] = None
        self._in_heading = False
        self._h_parts: list[str] = []
        self._section_parts: list[str] = []

        self.sections: list[dict] = []

    # ------------------------------------------------------------------ #

    def handle_starttag(self, tag: str, attrs):
        if tag in SKIP_TAGS:
            self._skip_depth += 1
            return
        if self._skip_depth:
            return

        if tag == "title":
            self._in_title = True
            return

        if tag in HEADING_TAGS:
            # Закрываем предыдущую секцию h2/h3
            if self._current_h_tag in ("h2", "h3"):
                self._flush_section()
            self._in_heading = True
            self._current_h_tag = tag
            self._h_parts = []

    def handle_endtag(self, tag: str):
        if tag in SKIP_TAGS:
            self._skip_depth = max(0, self._skip_depth - 1)
            return
        if self._skip_depth:
            return

        if tag == "title":
            self._in_title = False
            return

        if tag in HEADING_TAGS and self._in_heading and tag == self._current_h_tag:
            self._in_heading = False
            self._current_h_text = " ".join(self._h_parts).strip()
            self._section_parts = []

    def handle_data(self, data: str):
        if self._skip_depth:
            return
        text = data.strip()
        if not text:
            return

        if self._in_title:
            self._title_parts.append(text)
            return

        self._texts.append(text)

        if self._in_heading:
            self._h_parts.append(text)
        elif self._current_h_text is not None and self._current_h_tag in ("h2", "h3"):
            self._section_parts.append(text)

    # ------------------------------------------------------------------ #

    def _flush_section(self):
        if self._current_h_text:
            section_text = " ".join(self._section_parts)
            section_text = re.sub(r"\s+", " ", section_text).strip()
            self.sections.append({
                "heading": self._current_h_text,
                "text": section_text[:300],
            })
        self._current_h_text = None
        self._current_h_tag = None
        self._section_parts = []

    def close(self):
        super().close()
        # Закрываем последнюю открытую секцию
        if self._current_h_tag in ("h2", "h3"):
            self._flush_section()

    # ------------------------------------------------------------------ #

    @property
    def title(self) -> str:
        return " ".join(self._title_parts).strip()

    @property
    def content(self) -> str:
        raw = " ".join(self._texts)
        raw = re.sub(r"\s+", " ", raw).strip()
        return raw[:3000]


# ------------------------------------------------------------------ #

def strip_site_suffix(title: str) -> str:
    """Убирает суффикс ' | КУ' и похожие."""
    for suffix in (" | КУ", " — КУ", " - КУ", " | alkonorm.ru", " | Alkonorm"):
        if title.endswith(suffix):
            return title[: -len(suffix)].strip()
    return title


def get_url(filepath: Path) -> str:
    rel = filepath.relative_to(BASE_DIR)
    parts = rel.parts
    if parts[-1] == "index.html":
        return "/" + "/".join(parts[:-1]) + "/"
    return "/" + "/".join(parts)


def should_include(filepath: Path) -> bool:
    rel_str = str(filepath.relative_to(BASE_DIR))
    if rel_str in EXCLUDED_FILES:
        return False
    parts = filepath.relative_to(BASE_DIR).parts
    if parts[0] in EXCLUDED_TOP_DIRS:
        return False
    return True


def collect_files() -> list[Path]:
    files: list[Path] = []

    # Главная
    main = BASE_DIR / "index.html"
    if main.exists():
        files.append(main)

    arts = BASE_DIR / "articles"
    if arts.exists():
        # Корень articles/: только .html файлы (не в подпапках)
        for f in arts.glob("*.html"):
            if should_include(f):
                files.append(f)

        # articles/*/index.html  — хабы
        for f in arts.glob("*/index.html"):
            if should_include(f):
                files.append(f)

        # articles/*/*/index.html  — статьи уровня 2
        for f in arts.glob("*/*/index.html"):
            if should_include(f):
                files.append(f)

        # articles/*/*/*/index.html  — статьи уровня 3
        for f in arts.glob("*/*/*/index.html"):
            if should_include(f):
                files.append(f)

    # Дедупликация
    seen: set[Path] = set()
    result: list[Path] = []
    for f in files:
        resolved = f.resolve()
        if resolved not in seen:
            seen.add(resolved)
            result.append(f)
    result.sort()
    return result


def parse_file(filepath: Path) -> Optional[dict]:
    try:
        html = filepath.read_text(encoding="utf-8", errors="replace")
    except Exception as e:
        print(f"  ОШИБКА чтения {filepath}: {e}")
        return None

    parser = PageParser()
    try:
        parser.feed(html)
        parser.close()
    except Exception as e:
        print(f"  ОШИБКА парсинга {filepath}: {e}")
        return None

    raw_title = parser.title
    title = strip_site_suffix(raw_title) if raw_title else filepath.stem
    url = get_url(filepath)
    content = parser.content
    sections = parser.sections

    return {"title": title, "url": url, "content": content, "sections": sections}


def js_escape(s: str) -> str:
    s = s.replace("\\", "\\\\")
    s = s.replace('"', '\\"')
    s = s.replace("\n", " ").replace("\r", " ").replace("\t", " ")
    return s


def build_js(records: list[dict]) -> str:
    lines = ["const SEARCH_INDEX = ["]
    last = len(records) - 1
    for i, rec in enumerate(records):
        sec_parts = []
        for sec in rec["sections"]:
            h = js_escape(sec["heading"])
            t = js_escape(sec["text"])
            sec_parts.append(f'{{"heading": "{h}", "text": "{t}"}}')
        sections_str = "[" + ", ".join(sec_parts) + "]"

        t = js_escape(rec["title"])
        u = js_escape(rec["url"])
        c = js_escape(rec["content"])
        comma = "," if i < last else ""
        lines.append(
            f'  {{"title": "{t}", "url": "{u}", "content": "{c}", "sections": {sections_str}}}{comma}'
        )
    lines.append("];")
    return "\n".join(lines) + "\n"


def main():
    print("Собираем файлы...")
    files = collect_files()
    print(f"Файлов найдено: {len(files)}\n")

    records = []
    for f in files:
        rel = f.relative_to(BASE_DIR)
        rec = parse_file(f)
        if rec:
            records.append(rec)
            print(f"  OK  {rel}  ({len(rec['sections'])} секций)")
        else:
            print(f"  ПРОПУСК  {rel}")

    print(f"\nЗаписей: {len(records)}")
    js = build_js(records)
    OUTPUT_FILE.write_text(js, encoding="utf-8")
    size = OUTPUT_FILE.stat().st_size
    print(f"Сохранено: {OUTPUT_FILE}  ({size:,} байт)")


if __name__ == "__main__":
    main()
