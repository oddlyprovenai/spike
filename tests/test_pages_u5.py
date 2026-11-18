"""U5 — Zero-tracker static GitHub Pages site (`docs/site/`) with simulated `lab@mac-studio ~ %` replay."""

from __future__ import annotations

import re
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[1]
DOCS_SITE = ROOT / "docs" / "site"
PAGES = {"en": DOCS_SITE / "index.html", "es": DOCS_SITE / "es" / "index.html"}
ODDLY_PROVEN_PALETTE = {
    "ink": "#0E1116",
    "paper": "#F7F5EF",
    "lab-green": "#88D445",
    "cage-orange": "#F0592A",
    "signal-blue": "#3B82F6",
    "warning-red": "#E5484D",
}
BANNED_BRAND_COLORS = {"#141413", "#FAF9F5", "#D97757", "#6A9BCC", "#788C5D"}
PUBLIC_REPO = "https://github.com/oddlyprovenai/spike"


class _TagCollector(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.tags: list[tuple[str, dict[str, str]]] = []
        self.text_parts: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        self.tags.append((tag, {k: v or "" for k, v in attrs}))

    def handle_data(self, data: str) -> None:
        self.text_parts.append(data)


def _luminance(hex_color: str) -> float:
    rgb = [int(hex_color[i : i + 2], 16) / 255 for i in (1, 3, 5)]
    lin = [c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4 for c in rgb]
    return 0.2126 * lin[0] + 0.7152 * lin[1] + 0.0722 * lin[2]


def _contrast(a: str, b: str) -> float:
    hi, lo = sorted((_luminance(a), _luminance(b)), reverse=True)
    return (hi + 0.05) / (lo + 0.05)


def test_docs_site_files_exist_with_zero_trackers_and_strict_csp() -> None:
    assert (DOCS_SITE / ".nojekyll").is_file()
    assert (DOCS_SITE / "assets" / "pages.css").is_file()
    assert (DOCS_SITE / "assets" / "replay.js").is_file()

    js = (DOCS_SITE / "assets" / "replay.js").read_text(encoding="utf-8")
    assert not re.search(r"\b(fetch|XMLHttpRequest|WebSocket|sendBeacon)\b", js)
    assert "document.cookie" not in js and "localStorage" not in js

    for lang, path in PAGES.items():
        assert path.is_file(), f"Missing {path}"
        html = path.read_text(encoding="utf-8")
        assert "connect-src 'none'" in html, f"{lang}: missing strict connect-src 'none' CSP"
        assert not re.search(r"gtag|googletagmanager|plausible|matomo|analytics|document\.cookie", html, re.I)

        parser = _TagCollector()
        parser.feed(html)
        for _tag, attrs in parser.tags:
            for attr in ("href", "src", "srcset", "action"):
                val = attrs.get(attr, "").strip()
                if not val or val.startswith("#"):
                    continue
                parsed = urlsplit(val)
                if parsed.scheme in ("http", "https"):
                    # Only outbound links (<a href>) to public GitHub / Hugging Face are allowed; never external scripts/styles/images
                    assert _tag == "a", f"{lang}: external resource load on <{_tag} {attr}={val!r}>"
                    assert val.startswith((PUBLIC_REPO, "https://huggingface.co/")), f"{lang}: unexpected external link {val}"
                else:
                    target = (path.parent / unquote(parsed.path)).resolve()
                    assert target.exists(), f"{lang}: missing local asset {val}"


def test_oddly_proven_palette_and_wcag_aa_contrast() -> None:
    css = (DOCS_SITE / "assets" / "pages.css").read_text(encoding="utf-8")
    found_hex = {c.upper() for c in re.findall(r"#[0-9A-Fa-f]{6}\b", css)}
    assert BANNED_BRAND_COLORS.isdisjoint(found_hex), f"Disallowed external brand palette found: {found_hex & BANNED_BRAND_COLORS}"

    for token, hex_val in ODDLY_PROVEN_PALETTE.items():
        assert re.search(rf"--{re.escape(token)}:\s*{re.escape(hex_val)}\b", css, re.I), f"Missing --{token}: {hex_val}"

    assert _contrast(ODDLY_PROVEN_PALETTE["ink"], ODDLY_PROVEN_PALETTE["paper"]) >= 12.0
    assert _contrast(ODDLY_PROVEN_PALETTE["ink"], ODDLY_PROVEN_PALETTE["lab-green"]) >= 8.0
    assert ":focus-visible" in css and "prefers-reduced-motion" in css


def test_simulated_terminal_replay_and_honest_figures() -> None:
    js = (DOCS_SITE / "assets" / "replay.js").read_text(encoding="utf-8")
    assert "lab@mac-studio ~ %" in js
    assert "116/130" in js and "0.89" in js
    assert "409" in js and "1,000" in js

    overstated = "0." + "92"
    unannounced = "For" + "ge"
    macos_home = "/" + "Users" + "/"

    for lang, path in PAGES.items():
        html = path.read_text(encoding="utf-8")
        assert "lab@mac-studio ~ %" in html
        assert "116/130" in html and "0.89" in html
        assert "409" in html and "1,000" in html
        assert overstated not in html and overstated not in js
        assert unannounced not in html and unannounced not in js
        assert macos_home not in html and macos_home not in js
        assert 'role="tablist"' in html and 'role="tabpanel"' in html
        assert 'aria-live="polite"' in html, f"{lang}: terminal output should announce changes politely"


def test_bilingual_parity_and_landmarks() -> None:
    en_html = PAGES["en"].read_text(encoding="utf-8")
    es_html = PAGES["es"].read_text(encoding="utf-8")
    assert 'lang="en"' in en_html and 'lang="es"' in es_html
    assert 'href="es/index.html"' in en_html
    assert 'href="../index.html"' in es_html
    for lang, html in (("en", en_html), ("es", es_html)):
        assert "<main " in html and "<header " in html and "<footer " in html, lang
        assert 'class="skip-link"' in html, lang

