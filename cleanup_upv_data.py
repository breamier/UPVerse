"""
upv_data.json Cleanup Script
=============================
Fixes the following issues:
  1. Generic "PDF Document" titles  → derived from URL slug
  2. Truncated URLs                 → flagged in issues report
  3. Near-empty content (< 200 chars) → flagged for re-scrape / OCR
  4. Thin webpage content (nav-only scrapes) → flagged for re-scrape

Outputs:
  upv_data_cleaned.json   — fixed dataset
  upv_data_issues.json    — entries that still need manual attention
"""

import json
import re
from pathlib import Path

# ── helpers ──────────────────────────────────────────────────────────────────

ORDINAL_FIX = {
    "1St": "1st", "2Nd": "2nd", "3Rd": "3rd", "4Th": "4th",
    "5Th": "5th", "6Th": "6th", "7Th": "7th", "8Th": "8th",
}
ABBREV_FIX = {
    "Upv":  "UPV",
    "Ppa":  "PPA",
    "Sdrp": "SDRP",
    "Co":   "CO",
    "Upviews": "UPViews",
}

def fix_casing(title: str) -> str:
    """Fix title-case artifacts: ordinals (1St→1st) and known acronyms."""
    words = title.split()
    fixed = []
    for w in words:
        w = ORDINAL_FIX.get(w, w)
        w = ABBREV_FIX.get(w, w)
        fixed.append(w)
    return " ".join(fixed)

def derive_title_from_url(url: str) -> str:
    """Turn a URL slug into a readable title."""
    slug = url.rstrip("/").split("/")[-1]
    slug = re.sub(r"\.pdf$", "", slug, flags=re.IGNORECASE)
    slug = slug.replace("-", " ").replace("_", " ")
    title = slug.title()
    title = fix_casing(title)
    return title

def is_truncated_url(url: str) -> bool:
    """Detect URLs that were cut off mid-path (no extension, ends abruptly)."""
    last = url.rstrip("/").split("/")[-1]
    # has no dot at all in the last segment → likely truncated PDF path
    has_no_ext = "." not in last
    # ends without a slash or known extension
    known_exts = (".pdf", ".html", ".php", ".htm", ".jpg", ".png")
    has_known_ext = any(url.lower().endswith(e) for e in known_exts)
    # index.php routes are fine
    is_php_route = "index.php" in url
    return has_no_ext and not has_known_ext and not is_php_route

def content_length(item: dict) -> int:
    return len((item.get("content") or "").strip())

# ── main ─────────────────────────────────────────────────────────────────────

INPUT  = Path("C:\\Users\\ASUS\\Documents\\GitHub\\AI-Agent\\careers1.json")
OUTPUT = Path("C:\\Users\\ASUS\\Documents\\GitHub\\AI-Agent\\careers1_cleaned.json")
ISSUES = Path("C:\\Users\\ASUS\\Documents\\GitHub\\AI-Agent\\careers1_issues.json")

with open(INPUT, "r", encoding="utf-8") as f:
    data = json.load(f)

cleaned = []
issues  = []

THIN_WEBPAGE_THRESHOLD = 200   # chars — below this a webpage scrape is considered nav-only
THIN_PDF_THRESHOLD     = 200   # chars — below this a PDF likely needs OCR

for i, item in enumerate(data):
    entry  = dict(item)   # shallow copy so we don't mutate original
    flags  = []

    url     = entry.get("url", "")
    title   = entry.get("title", "")
    ctype   = entry.get("type", "")
    clen    = content_length(entry)

    # ── Fix 1: generic title ────────────────────────────────────────────────
    if title == "PDF Document":
        derived = derive_title_from_url(url)
        entry["title"] = derived
        entry["title_source"] = "derived_from_url"   # audit trail
        flags.append("title_was_generic__derived_from_url")

    # ── Fix 2: truncated URL ────────────────────────────────────────────────
    if is_truncated_url(url) and ctype == "pdf":
        flags.append("url_may_be_truncated__verify_and_re_scrape")

    # ── Fix 3: near-empty PDF content (image-based PDF, needs OCR) ─────────
    if ctype == "pdf" and clen < THIN_PDF_THRESHOLD:
        flags.append(
            f"content_too_short_({clen}_chars)__likely_image_pdf__needs_ocr"
        )

    # ── Fix 4: thin webpage content (JS-rendered or nav-only) ───────────────
    if ctype == "webpage" and clen < THIN_WEBPAGE_THRESHOLD:
        flags.append(
            f"content_too_short_({clen}_chars)__likely_js_rendered__needs_headless_browser"
        )

    # count low-sentence-density webpages (nav dumps)
    if ctype == "webpage" and clen > 200:
        words     = len((entry.get("content") or "").split())
        sentences = (entry.get("content") or "").count(".")
        if words > 100 and sentences < 5:
            flags.append(
                "webpage_content_looks_like_nav_dump__few_sentences__consider_re_scraping"
            )

    cleaned.append(entry)

    if flags:
        issues.append({
            "index":  i,
            "url":    url,
            "title":  entry["title"],
            "type":   ctype,
            "flags":  flags,
        })

# ── write outputs ─────────────────────────────────────────────────────────

OUTPUT.parent.mkdir(parents=True, exist_ok=True)

with open(OUTPUT, "w", encoding="utf-8") as f:
    json.dump(cleaned, f, ensure_ascii=False, indent=2)

with open(ISSUES, "w", encoding="utf-8") as f:
    json.dump(issues, f, ensure_ascii=False, indent=2)

# ── summary ───────────────────────────────────────────────────────────────

title_fixes     = sum(1 for e in cleaned if e.get("title_source") == "derived_from_url")
truncated_urls  = sum(1 for issue in issues if any("url_may_be_truncated" in f for f in issue["flags"]))
thin_pdfs       = sum(1 for issue in issues if any("needs_ocr" in f for f in issue["flags"]))
thin_webpages   = sum(1 for issue in issues if any("needs_headless_browser" in f or "nav_dump" in f for f in issue["flags"]))

print("=" * 55)
print("  UPV Data Cleanup Complete")
print("=" * 55)
print(f"  Total entries          : {len(cleaned)}")
print(f"  Titles auto-fixed      : {title_fixes}")
print(f"  Truncated URLs flagged : {truncated_urls}")
print(f"  PDFs needing OCR       : {thin_pdfs}")
print(f"  Webpages needing re-scrape : {thin_webpages}")
print(f"  Entries with issues    : {len(issues)}")
print()
print(f"  → Cleaned data : {OUTPUT}")
print(f"  → Issues report: {ISSUES}")
print()
print("Next steps for flagged entries:")
print("  • url_may_be_truncated   — fix the URL and re-fetch the PDF")
print("  • needs_ocr              — run pdf2image + pytesseract on that PDF")
print("  • needs_headless_browser — re-scrape with Playwright/Puppeteer")
print("  • nav_dump               — same as above, JS-rendered content")
