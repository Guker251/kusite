#!/usr/bin/env python3
"""
Получение малоценных страниц из Яндекс.Вебмастер API
и обновление реестра docs/seo/excluded-registry.md

Статусы страниц:
  todo     — контентная страница, требует SEO-проверки
  done     — проверена и исправлена, ждём индексации
  indexed  — исчезла из EXCLUDED в API → Яндекс проиндексировал
  skip     — не требует работы (редирект, дубль, служебная)
"""

import os
import json
import urllib.request
from datetime import date
from pathlib import Path

# --- конфиг ---

ROOT = Path(__file__).parent.parent
ENV_FILE = ROOT / ".env"
REGISTRY_FILE = ROOT / "docs" / "seo" / "excluded-registry.md"

API_BASE = "https://api.webmaster.yandex.net/v4"

# суффиксы — проверяются substring в имени файла
SERVICE_SUFFIXES = ("-ku.html", "-lcha.html")

# точные сегменты пути (проверяются по-сегментно, без подстрок)
SERVICE_SEGMENTS = {
    "faq", "karta-sayta", "stati", "knigi",
}

# точные имена файлов / последних сегментов
SERVICE_FILENAMES = {
    "kniga-ku.html", "triggery-ku.html", "strategiya-ku.html",
    "shablony-upotrebleniya.html", "uchet-epizodov-ku.html",
    "distsiplina-ucheta-ku.html", "korrektsiyu-taktiki-ku.html",
    "pamyat-o-strategii-ku.html", "sovershenstvovanie-sistemy-ku.html",
    "nastroy-podschet-lcha.html", "kalendarnyy-plan-lcha.html",
    "7-shagov-ku.html", "chto-takoe-ku.html", "zhelanie-menyatsya.html",
    "test-plan-ku.html", "test-veroyatnost-ku.html", "test-gotovnost-k-izmeneniyam.html",
    "testy.html", "soobschestvo.html", "hub-zhizn.html",
}

NOTES_MAP = {
    "redirect":  "301-редирект — обновить в Вебмастере",
    "forbidden": "403 — закрыта от индексации",
    "duplicate": "Дубль — index.html или .html-версия директории",
    "service":   "Служебная страница — закрыть от индексации",
    "content":   "Контентная страница — требует SEO-проверки",
}

# статусы, для которых отслеживаем исчезновение из EXCLUDED
TRACKABLE_STATUSES = {"todo", "done", "new"}


def load_env() -> dict:
    env = {}
    if ENV_FILE.exists():
        for line in ENV_FILE.read_text().splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                env[k.strip()] = v.strip()
    for key in ("YANDEX_TOKEN", "YANDEX_USER_ID", "YANDEX_HOST_ID"):
        if key in os.environ:
            env[key] = os.environ[key]
    return env


def api_get(path: str, token: str) -> dict:
    url = f"{API_BASE}{path}"
    req = urllib.request.Request(url, headers={"Authorization": f"OAuth {token}"})
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read())


def fetch_excluded(token: str, user_id: str, host_id: str) -> list[dict]:
    """Возвращает все записи из EXCLUDED с пагинацией."""
    samples = []
    offset = 0
    while True:
        path = (
            f"/user/{user_id}/hosts/{host_id}/indexing/samples"
            f"?samplesType=EXCLUDED&limit=100&offset={offset}"
        )
        data = api_get(path, token)
        batch = data.get("samples", [])
        samples.extend(batch)
        if len(batch) < 100:
            break
        offset += 100
    return samples


def categorize(url: str, http_code: int) -> str:
    if http_code in (301, 302):
        return "redirect"
    if http_code == 403:
        return "forbidden"
    path = url.replace("https://alkonorm.ru", "")
    if path.endswith("/index.html"):
        return "duplicate"
    segments = [s for s in path.split("/") if s]
    last = segments[-1] if segments else ""
    if any(last.endswith(sfx) for sfx in SERVICE_SUFFIXES):
        return "service"
    if last in SERVICE_FILENAMES:
        return "service"
    if any(seg in SERVICE_SEGMENTS for seg in segments):
        return "service"
    return "content"


def load_registry() -> dict[str, dict]:
    """Читает реестр, возвращает dict url → row."""
    rows = {}
    if not REGISTRY_FILE.exists():
        return rows
    for line in REGISTRY_FILE.read_text().splitlines():
        if not line.startswith("| http"):
            continue
        parts = [p.strip() for p in line.split("|")]
        if len(parts) < 6:
            continue
        url, category, status, found, notes = parts[1], parts[2], parts[3], parts[4], parts[5]
        rows[url] = {
            "url": url,
            "category": category,
            "status": status,
            "found": found,
            "notes": notes,
        }
    return rows


def save_registry(rows: dict[str, dict]) -> None:
    today = date.today().isoformat()
    counts = {s: sum(1 for r in rows.values() if r["status"] == s)
              for s in ("todo", "done", "indexed", "skip")}
    header = (
        f"# Реестр малоценных страниц alkonorm.ru\n\n"
        f"Обновлён: {today}  \n"
        f"Всего: {len(rows)} | "
        f"todo: {counts['todo']} | "
        f"done: {counts['done']} | "
        f"indexed: {counts['indexed']} | "
        f"skip: {counts['skip']}  \n\n"
        f"| url | category | status | found | notes |\n"
        f"|---|---|---|---|---|\n"
    )
    order = {"content": 0, "forbidden": 1, "duplicate": 2, "service": 3, "redirect": 4}
    status_order = {"todo": 0, "new": 1, "done": 2, "indexed": 3, "skip": 4}
    sorted_rows = sorted(
        rows.values(),
        key=lambda r: (order.get(r["category"], 9), status_order.get(r["status"], 9), r["url"]),
    )
    lines = [
        f"| {r['url']} | {r['category']} | {r['status']} | {r['found']} | {r['notes']} |"
        for r in sorted_rows
    ]
    REGISTRY_FILE.write_text(header + "\n".join(lines) + "\n")


def main() -> None:
    env = load_env()
    token = env.get("YANDEX_TOKEN", "")
    user_id = env.get("YANDEX_USER_ID", "")
    host_id = env.get("YANDEX_HOST_ID", "")

    if not token:
        print("Ошибка: YANDEX_TOKEN не задан в .env")
        return

    print("Получаю малоценные страницы из API...")
    samples = fetch_excluded(token, user_id, host_id)
    today = date.today().isoformat()

    # дедупликация — последний http_code для каждого URL
    url_to_code: dict[str, int] = {}
    for s in samples:
        url_to_code[s["url"]] = s["http_code"]

    registry = load_registry()

    added: list[tuple[str, str]] = []
    newly_indexed: list[str] = []

    # --- проверяем исчезнувшие страницы ---
    for url, row in registry.items():
        if row["status"] in TRACKABLE_STATUSES and url not in url_to_code:
            registry[url] = {**row, "status": "indexed",
                             "notes": f"Проиндексирован {today}"}
            newly_indexed.append(url)

    # --- добавляем новые из API ---
    for url, http_code in url_to_code.items():
        if url in registry:
            continue
        category = categorize(url, http_code)
        status = "todo" if category == "content" else "skip"
        registry[url] = {
            "url": url,
            "category": category,
            "status": status,
            "found": today,
            "notes": NOTES_MAP[category],
        }
        added.append((url, category))

    save_registry(registry)

    # --- итоговый отчёт ---
    counts = {s: sum(1 for r in registry.values() if r["status"] == s)
              for s in ("todo", "done", "indexed", "skip")}

    print(f"\n{'='*60}")
    print(f"Страниц в EXCLUDED (API):  {len(url_to_code)}")
    print(f"Новых добавлено:           {len(added)}")
    print(f"Стали проиндексированы:    {len(newly_indexed)}")
    print(f"\nРеестр итого:              {len(registry)}")
    print(f"  todo    (нужно исправить): {counts['todo']}")
    print(f"  done    (ждём индексации): {counts['done']}")
    print(f"  indexed (победа):          {counts['indexed']}")
    print(f"  skip    (не нужно):        {counts['skip']}")
    print(f"{'='*60}")

    if newly_indexed:
        print("\n🎯 Вышли из EXCLUDED (проиндексированы):")
        for url in newly_indexed:
            print(f"  {url}")

    if added:
        print("\nНовые исключённые страницы:")
        for url, cat in sorted(added, key=lambda x: x[1]):
            print(f"  [{cat:10s}] {url}")

    print(f"\nРеестр: {REGISTRY_FILE.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
