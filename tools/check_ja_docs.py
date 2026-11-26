#!/usr/bin/env python3
"""Check the Japanese pages (docs/**/*.ja.md) against their English originals.

Run from the repository root after `mkdocs build` (the HTML checks read site/):

    .venv-docs/bin/mkdocs build --strict && python3 tools/check_ja_docs.py

Errors (exit code 1) are things that break the Japanese page or mean it no longer matches the English one:
code blocks, snippets, math, link targets, callouts and heading ids must be identical; raw HTML media paths
need one more "../" (the Japanese site lives in /ja/); the built pages must have the same structure.
Warnings point at places worth a look: numbers or inline code that differ, lines that look untranslated,
paragraphs split over several lines (a line break shows as a space in Japanese).
"""
import argparse
import collections
import html
import pathlib
import re
import sys

FENCE = re.compile(r"^(\s*)(```|~~~)")
CJK = re.compile(r"[぀-ヿ㐀-鿿！-｠　-〿]")
MD_LINK = re.compile(r"\]\(([^)\s]+)(?:\s+\"[^\"]*\")?\)")
RAW_URL = re.compile(r"<(?:source|img|video|a)\b[^>]*\b(?:src|href)=\"([^\"]+)\"")
INLINE_CODE = re.compile(r"`[^`\n]+`")
MATH = re.compile(r"\$\$.*?\$\$|\$[^$\n]+\$", re.S)
NUMBER = re.compile(r"(?<![\w.])[-−]?\d+(?:[.,]\d+)?")
CALLOUT = re.compile(r"<span class=\"callout\"[^\n]*")
SNIPPET = re.compile(r"--8<--[^\n]*")
HEAD_ID = re.compile(r"<h([1-6])[^>]*\bid=\"([^\"]+)\"")
TAGS = ["h1", "h2", "h3", "h4", "table", "tr", "pre", "img", "video", "figure", "details", "li", "ol", "ul"]
CLASSES = ["admonition", "tabbed-set", "callout", "arithmatex"]


def split_code(text):
    """Return (prose_lines, code_blocks). Code blocks keep their fence lines and indentation."""
    prose, blocks, cur, fence = [], [], None, None
    for line in text.split("\n"):
        m = FENCE.match(line)
        if fence is None and m:
            fence, cur = m.group(2), [line]
        elif fence is not None:
            cur.append(line)
            if m and m.group(2) == fence and line.strip() == fence:
                blocks.append("\n".join(cur))
                fence = cur = None
        else:
            prose.append(line)
    return prose, blocks


def article(path):
    text = path.read_text()
    return text[text.index("<article"): text.index("</article>")]


def html_page(site, rel):
    rel = rel.with_suffix("")
    return site / ("index.html" if rel.name == "index" else rel / "index.html")


class Report:
    def __init__(self):
        self.errors = self.warnings = 0

    def error(self, page, msg):
        self.errors += 1
        print(f"ERROR {page}: {msg}")

    def warn(self, page, msg):
        self.warnings += 1
        print(f"warn  {page}: {msg}")


def diff(a, b):
    ca, cb = collections.Counter(a), collections.Counter(b)
    return sorted((ca - cb).elements()), sorted((cb - ca).elements())


def check_markdown(rep, page, en_text, ja_text):
    en_prose, en_code = split_code(en_text)
    ja_prose, ja_code = split_code(ja_text)
    if en_code != ja_code:
        for i, (a, b) in enumerate(zip(en_code, ja_code)):
            if a != b:
                rep.error(page, f"code block {i + 1} differs from English (first line: {a.splitlines()[0].strip()!r})")
                break
        if len(en_code) != len(ja_code):
            rep.error(page, f"{len(en_code)} code blocks in English, {len(ja_code)} in Japanese")
    en_p, ja_p = "\n".join(en_prose), "\n".join(ja_prose)

    for name, rx in [("snippet", SNIPPET), ("callout", CALLOUT), ("math", MATH)]:
        missing, extra = diff(rx.findall(en_p), rx.findall(ja_p))
        if missing or extra:
            rep.error(page, f"{name} differs: missing {missing[:3]} extra {extra[:3]}")

    missing, extra = diff(MD_LINK.findall(en_p), MD_LINK.findall(ja_p))
    if missing or extra:
        rep.error(page, f"link targets differ: missing {missing[:5]} extra {extra[:5]}")

    en_raw = ["../" + u if not re.match(r"[a-z]+:|#|/", u) else u for u in RAW_URL.findall(en_p)]
    missing, extra = diff(en_raw, RAW_URL.findall(ja_p))
    if missing or extra:
        rep.error(page, f"raw HTML src/href must be the English path with one more '../': missing {missing[:3]} extra {extra[:3]}")

    if "｜" in ja_p or "　" in ja_p:
        rep.error(page, "full-width '｜' or full-width space (U+3000) outside code")

    strip = lambda s: MATH.sub(" ", INLINE_CODE.sub(" ", MD_LINK.sub("]", s)))
    missing, extra = diff(INLINE_CODE.findall(en_p), INLINE_CODE.findall(ja_p))
    if missing:
        rep.warn(page, f"inline code only in English: {missing[:6]}")
    missing, _ = diff(NUMBER.findall(strip(en_p)), NUMBER.findall(strip(ja_p)))
    missing = [n for n in missing if n.lstrip("-−") not in {"1", "2", "3"}]  # "one", "two", "three" are often words
    if missing:
        rep.warn(page, f"numbers only in English: {missing[:10]}")

    prev, fence, in_math = "", None, False
    for no, line in enumerate(ja_text.split("\n"), 1):
        body = line.strip()
        m = FENCE.match(line)
        if body == "$$" and fence is None:
            in_math = not in_math
        if fence is None and m:
            fence = m.group(2)
        elif fence is not None or in_math:
            if m and body == fence:
                fence = None
            body = ""
        else:
            words = re.findall(r"[A-Za-z][A-Za-z'’-]*", strip(body))
            if not CJK.search(body) and len(words) >= 8 and not body.startswith(("|", "<", "![", "--8<--")):
                rep.warn(page, f"line {no} looks untranslated: {body[:80]!r}")
            starts_block = re.match(r"([-*+]|\d+\.|\||<|#|!!!|\?\?\?|===|\$\$|\[\^|:)", body)
            if body and prev and CJK.search(prev[-1:]) and CJK.search(body[:1]) and not starts_block:
                rep.warn(page, f"line {no} continues a Japanese paragraph from the line before (shows as a space)")
        prev = body


def check_html(rep, page, en_html, ja_html, site, ja_file):
    en_ids, ja_ids = HEAD_ID.findall(en_html), HEAD_ID.findall(ja_html)
    if en_ids != ja_ids:
        rep.error(page, f"heading ids differ: {sorted(set(en_ids) ^ set(ja_ids))[:6]}")
    for tag in TAGS:
        a = len(re.findall(rf"<{tag}\b", en_html))
        b = len(re.findall(rf"<{tag}\b", ja_html))
        if a != b:
            rep.error(page, f"<{tag}> count {a} in English, {b} in Japanese")
    for cls in CLASSES:
        a = len(re.findall(rf"class=\"[^\"]*\b{cls}\b", en_html))
        b = len(re.findall(rf"class=\"[^\"]*\b{cls}\b", ja_html))
        if a != b:
            rep.error(page, f"class {cls!r} count {a} in English, {b} in Japanese")
    text = re.sub(r"<(pre|code)\b.*?</\1>", " ", ja_html, flags=re.S)
    text = html.unescape(re.sub(r"<[^>]+>", " ", text))
    for bad in ["**", " _", "{ #", "{ ."]:
        if bad in text:
            rep.error(page, f"unrendered Markdown {bad!r} in the Japanese page: …{text[text.index(bad) - 30:text.index(bad) + 30]!r}…")
    for url in set(re.findall(r"\b(?:src|href)=\"([^\"#?]+)", ja_html)):
        if re.match(r"[a-z]+:|//|/", url) or not url:
            continue
        target = (ja_file.parent / url).resolve()
        if url.endswith("/"):
            target = target / "index.html"
        if not target.exists():
            rep.error(page, f"broken link/media in the built page: {url}")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--docs", default="docs", type=pathlib.Path)
    ap.add_argument("--site", default="site", type=pathlib.Path)
    ap.add_argument("--fix-media", action="store_true",
                    help="first add the extra '../' to raw HTML src/href paths that still equal the English ones")
    args = ap.parse_args()
    rep = Report()
    pages = sorted(p for p in args.docs.rglob("*.md") if not p.name.endswith(".ja.md"))
    if args.fix_media:
        for en in pages:
            ja = en.with_suffix(".ja.md")
            if not ja.exists():
                continue
            en_urls = set(RAW_URL.findall(en.read_text()))
            fixed = re.sub(r"(<(?:source|img|video|a)\b[^>]*\b(?:src|href)=\")([^\"]+)\"",
                           lambda m: m.group(1) + ("../" if m.group(2) in en_urls
                                                   and not re.match(r"[a-z]+:|#|/", m.group(2)) else "")
                           + m.group(2) + '"', ja.read_text())
            if fixed != ja.read_text():
                ja.write_text(fixed)
                print(f"fixed media paths in {ja}")
    for en in pages:
        ja = en.with_suffix(".ja.md")
        page = str(ja)
        if not ja.exists():
            rep.warn(str(en), "no Japanese page (the Japanese site shows the English one)")
            continue
        check_markdown(rep, page, en.read_text(), ja.read_text())
        rel = en.relative_to(args.docs)
        en_file, ja_file = html_page(args.site, rel), html_page(args.site / "ja", rel)
        if not en_file.exists() or not ja_file.exists():
            rep.error(page, f"built page missing ({en_file} / {ja_file}); run mkdocs build first")
            continue
        check_html(rep, page, article(en_file), article(ja_file), args.site, ja_file)
    print(f"{len(pages)} pages, {rep.errors} errors, {rep.warnings} warnings")
    sys.exit(1 if rep.errors else 0)


if __name__ == "__main__":
    main()
