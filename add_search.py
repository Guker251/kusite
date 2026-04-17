#!/usr/bin/env python3
"""Add search overlay and script to HTML files that have nav-search but no searchOverlay."""

from pathlib import Path

ROOT = Path("/Users/guker/Desktop/ku")

FILES = [
    "articles/uznaki-alkogolizma/kak-snyat-pokhmelye/index.html",
    "articles/uznaki-alkogolizma/vyvedenie-alkogolya/index.html",
    "articles/uznaki-alkogolizma/toshnit-posle-alkogolya/index.html",
    "articles/uznaki-alkogolizma/index.html",
    "articles/uznaki-alkogolizma/zhenskiy-alkogolizm/index.html",
    "articles/uznaki-alkogolizma/rand-issledovanie-alkogolizm/index.html",
    "articles/uznaki-alkogolizma/provaly-pamyati/index.html",
    "articles/uznaki-alkogolizma/kak-ne-spitsya/index.html",
    "articles/uznaki-alkogolizma/alkogolnaya-intoksikatsiya/index.html",
    "articles/uznaki-alkogolizma/kak-izbavitsya-ot-pokhmele/index.html",
    "articles/uznaki-alkogolizma/brosit-pit/index.html",
    "articles/uznaki-alkogolizma/pivnoy-alkogolizm/index.html",
    "articles/uznaki-alkogolizma/alkogolik-ili-pyyanitsa/index.html",
    "articles/uznaki-alkogolizma/priznaki-alkogolizma/index.html",
    "articles/uznaki-alkogolizma/pokhmelye/index.html",
    "articles/uznaki-alkogolizma/alkogolnaya-zavisimost/index.html",
    "articles/uznaki-alkogolizma/slabost-posle-alkogolya/index.html",
    "articles/pochemu-hochetsya-alkogolya/pyu-ot-stressa/index.html",
    "articles/pochemu-hochetsya-alkogolya/index.html",
    "articles/pochemu-hochetsya-alkogolya/pochemu-hochetsya-piva-vecherom/index.html",
    "articles/pochemu-hochetsya-alkogolya/prichiny-upotrebleniya/index.html",
    "articles/pochemu-hochetsya-alkogolya/alkogol-i-zhenshchiny/index.html",
    "articles/pochemu-hochetsya-alkogolya/alkogol-i-beremennost/index.html",
    "articles/pochemu-hochetsya-alkogolya/vidy-alkogolnykh-napitkov/index.html",
    "articles/pochemu-hochetsya-alkogolya/kak-zhit-s-pyushchim/index.html",
    "articles/pochemu-hochetsya-alkogolya/pochemu-lyudi-pyut/index.html",
    "articles/pochemu-hochetsya-alkogolya/alkogol-i-semya/index.html",
    "articles/pochemu-hochetsya-alkogolya/alkogol-i-trevoga/index.html",
    "articles/pochemu-hochetsya-alkogolya/stress-i-alkogol/index.html",
    "articles/pochemu-hochetsya-alkogolya/vliyanie-alkogolya-na-cheloveka/index.html",
    "articles/skolko-mozhno-pit/kak-rasschitat-dozu/index.html",
    "articles/skolko-mozhno-pit/alkogolnaya-depressiya/index.html",
    "articles/skolko-mozhno-pit/norma-alkogolya-za-rulem/index.html",
    "articles/skolko-mozhno-pit/alkogolnoe-opyanenie/index.html",
    "articles/skolko-mozhno-pit/index.html",
    "articles/skolko-mozhno-pit/sostoyanie-opyaneniya/index.html",
    "articles/skolko-mozhno-pit/alkogol-i-son/index.html",
    "articles/skolko-mozhno-pit/priznaki-opyaneniya/index.html",
    "articles/skolko-mozhno-pit/norma-v-nedelyu/index.html",
    "articles/skolko-mozhno-pit/dopustimaya-norma-alkogolya/index.html",
    "articles/skolko-mozhno-pit/skolko-pyut-rossiyane/index.html",
    "articles/skolko-mozhno-pit/alkogol-i-sport/index.html",
    "articles/skolko-mozhno-pit/vliyanie-na-organizm/index.html",
    "articles/skolko-mozhno-pit/kak-pit-bez-vreda/index.html",
    "articles/skolko-mozhno-pit/alkogol-i-beremennost/index.html",
    "articles/skolko-mozhno-pit/polza-umerennogo-alkogolya/index.html",
    "articles/skolko-mozhno-pit/alkogol-i-davlenie/index.html",
    "articles/skolko-mozhno-pit/mozhno-li-pit/index.html",
    "articles/skolko-mozhno-pit/promille-alkogolya/index.html",
    "articles/skolko-mozhno-pit/voz-ob-alkogole/index.html",
    "articles/skolko-mozhno-pit/kalkulator-opyaneniya/index.html",
    "articles/skolko-mozhno-pit/stadii-opyaneniya/index.html",
    "articles/skolko-mozhno-pit/alkogol-i-pechen/index.html",
    "articles/skolko-mozhno-pit/vred-alkogolya/index.html",
    "articles/skolko-mozhno-pit/cherez-skolko-mozhno-pit/index.html",
    "articles/skolko-mozhno-pit/norma-alkogolya/index.html",
    "articles/skolko-mozhno-pit/alkogol-i-lekarstva/index.html",
    "articles/kak-menshe-pit/alkogol-i-rabota/index.html",
    "articles/kak-menshe-pit/pyu-kazhdyy-den/index.html",
    "articles/kak-menshe-pit/index.html",
    "articles/kak-menshe-pit/kak-ne-napitsya/index.html",
    "articles/kak-menshe-pit/umerennoe-upotreblenie/index.html",
    "articles/kak-menshe-pit/kultura-pitiya/index.html",
    "articles/kak-menshe-pit/pokhmele-na-rabote/index.html",
    "articles/kak-menshe-pit/alkogol-v-prazdniki/index.html",
    "articles/kak-menshe-pit/kak-otkazatsya-v-kompanii/index.html",
    "articles/kak-menshe-pit/kak-menshe-pit/index.html",
    "articles/kak-menshe-pit/snizhenie-potrebleniya-alkogolya/index.html",
    "articles/kak-menshe-pit/kak-perestat-pit-kazhdyy-vecher/index.html",
    "articles/kak-menshe-pit/kak-ne-pit-alkogol/index.html",
    "articles/kak-menshe-pit/kak-pit-i-ne-pyanet/index.html",
    "articles/kak-menshe-pit/ne-mogu-ostanovitsya/index.html",
    "articles/kak-menshe-pit/pivo-kazhdyy-den/index.html",
    "articles/kak-menshe-pit/tolerantnost-k-alkogolyu/index.html",
]

OVERLAY_HTML = (
    '\n<div class="search-overlay" id="searchOverlay">\n'
    '    <span class="search-close" id="searchClose">\u2715</span>\n'
    '    <div class="search-overlay-inner">\n'
    '        <div class="search-label">\u041f\u043e\u0438\u0441\u043a \u043f\u043e \u0441\u0430\u0439\u0442\u0443</div>\n'
    '        <div class="search-input-row">\n'
    '            <input type="text" id="searchInput" placeholder="\u0412\u0432\u0435\u0434\u0438\u0442\u0435 \u0437\u0430\u043f\u0440\u043e\u0441...">\n'
    '        </div>\n'
    '        <div class="search-results" id="searchResults"></div>\n'
    '    </div>\n'
    '</div>'
)

JS_BODY = r"""(function() {
    const overlay  = document.getElementById('searchOverlay');
    const input    = document.getElementById('searchInput');
    const closeBtn = document.getElementById('searchClose');
    const results  = document.getElementById('searchResults');
    let debounce;
    function openSearch() { overlay.classList.add('active'); setTimeout(() => input.focus(), 50); }
    function closeSearch() { overlay.classList.remove('active'); input.value = ''; results.innerHTML = ''; }
    function highlight(text, words) {
        let out = text;
        words.forEach(w => { if (!w) return; const re = new RegExp('(' + w.replace(/[.*+?^${}()|[\]\\]/g, '\\$&') + ')', 'gi'); out = out.replace(re, '<mark>$1</mark>'); });
        return out;
    }
    function getSnippet(content, words) {
        const lower = content.toLowerCase(); let best = 0;
        words.forEach(w => { const idx = lower.indexOf(w.toLowerCase()); if (idx !== -1) best = idx; });
        const start = Math.max(0, best - 60);
        let snippet = content.slice(start, start + 200);
        if (start > 0) snippet = '\u2026' + snippet;
        if (start + 200 < content.length) snippet += '\u2026';
        return snippet;
    }
    function doSearch() {
        const q = input.value.trim(); results.innerHTML = '';
        if (!q || q.length < 2) return;
        const words = q.toLowerCase().split(/\s+/).filter(Boolean);
        if (typeof SEARCH_INDEX === 'undefined') { results.innerHTML = '<div class="search-empty">\u0418\u043d\u0434\u0435\u043a\u0441 \u0437\u0430\u0433\u0440\u0443\u0436\u0430\u0435\u0442\u0441\u044f\u2026</div>'; return; }
        const scored = SEARCH_INDEX.map(doc => {
            let score = 0;
            const titleL = doc.title.toLowerCase(); const contentL = doc.content.toLowerCase();
            words.forEach(w => {
                if (titleL.includes(w)) score += 10;
                if (contentL.includes(w)) score += contentL.split(w).length - 1;
                (doc.sections || []).forEach(s => { if (s.heading.toLowerCase().includes(w)) score += 5; if (s.text.toLowerCase().includes(w)) score += 2; });
            });
            return {doc, score};
        }).filter(x => x.score > 0).sort((a, b) => b.score - a.score).slice(0, 7);
        if (!scored.length) { results.innerHTML = '<div class="search-empty">\u041d\u0438\u0447\u0435\u0433\u043e \u043d\u0435 \u043d\u0430\u0439\u0434\u0435\u043d\u043e</div>'; return; }
        scored.forEach(({doc}) => {
            const snippet = highlight(getSnippet(doc.content, words), words);
            const title = highlight(doc.title, words);
            const a = document.createElement('a');
            a.className = 'search-result'; a.href = doc.url;
            a.innerHTML = `<div class="search-result-title">${title}</div><div class="search-result-snippet">${snippet}</div><div class="search-result-url">alkonorm.ru${doc.url}</div>`;
            a.addEventListener('click', closeSearch);
            results.appendChild(a);
        });
    }
    document.querySelector('.nav-search').addEventListener('click', openSearch);
    closeBtn.addEventListener('click', closeSearch);
    overlay.addEventListener('click', e => { if (e.target === overlay) closeSearch(); });
    document.addEventListener('keydown', e => { if (e.key === 'Escape') closeSearch(); });
    input.addEventListener('input', function() { clearTimeout(debounce); debounce = setTimeout(doSearch, 200); });
})();"""


def get_search_index_path(rel_path: str) -> str:
    """Calculate relative path to search_index.js based on file depth."""
    parts = rel_path.split("/")
    depth = len(parts) - 1  # number of directories from ku/ root
    return "../" * depth + "search_index.js"


def build_script_block(search_index_path: str) -> str:
    return (
        f'<script src="{search_index_path}"></script>\n'
        '<script>\n'
        + JS_BODY
        + '\n</script>'
    )


def process_file(rel_path: str) -> tuple[bool, str]:
    """Process a single HTML file. Returns (success, message)."""
    filepath = ROOT / rel_path

    if not filepath.exists():
        return False, f"NOT FOUND: {rel_path}"

    content = filepath.read_text(encoding="utf-8")

    if "searchOverlay" in content:
        return False, f"SKIP (already has searchOverlay): {rel_path}"

    if "nav-search" not in content:
        return False, f"SKIP (no nav-search): {rel_path}"

    if "</header>" not in content:
        return False, f"SKIP (no </header>): {rel_path}"

    if "</body>" not in content:
        return False, f"SKIP (no </body>): {rel_path}"

    search_index_path = get_search_index_path(rel_path)
    script_block = build_script_block(search_index_path)

    content = content.replace("</header>", "</header>\n" + OVERLAY_HTML, 1)
    content = content.replace("</body>", script_block + "\n</body>", 1)

    filepath.write_text(content, encoding="utf-8")
    return True, f"OK [{search_index_path}]: {rel_path}"


def main():
    processed = 0
    skipped = 0
    errors = 0

    for rel_path in FILES:
        success, msg = process_file(rel_path)
        print(msg)
        if success:
            processed += 1
        elif msg.startswith("SKIP"):
            skipped += 1
        else:
            errors += 1

    print(f"\n--- ИТОГ ---")
    print(f"Обработано:  {processed}")
    print(f"Пропущено:   {skipped}")
    print(f"Ошибок:      {errors}")


if __name__ == "__main__":
    main()
