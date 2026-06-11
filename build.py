#!/usr/bin/env python3
"""
Worldbuilder - Generate a wiki from markdown files.
"""

import os
import re
import yaml
import markdown
from pathlib import Path
from datetime import datetime

WORLDS_DIR = Path("worlds")
SITE_DIR = Path("docs")
TEMPLATE_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title} - Worldbuilder</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: Georgia, serif; background: #1a1a2e; color: #eee; line-height: 1.6; }}
        .container {{ max-width: 900px; margin: 0 auto; padding: 2rem; }}
        header {{ border-bottom: 1px solid #333; padding-bottom: 1rem; margin-bottom: 2rem; }}
        header h1 {{ color: #ffd700; }}
        header a {{ color: #888; text-decoration: none; }}
        header a:hover {{ color: #ffd700; }}
        .meta {{ color: #888; font-size: 0.9rem; margin-bottom: 1rem; }}
        .meta span {{ background: #333; padding: 0.2rem 0.5rem; border-radius: 3px; margin-right: 0.5rem; }}
        .content h2 {{ color: #ffd700; margin-top: 1.5rem; }}
        .content p {{ margin: 1rem 0; }}
        .content a {{ color: #4ecdc4; }}
        .entry-list {{ list-style: none; }}
        .entry-list li {{ padding: 0.5rem 0; border-bottom: 1px solid #333; }}
        .entry-list a {{ color: #4ecdc4; text-decoration: none; }}
        .entry-list a:hover {{ color: #ffd700; }}
        .type-badge {{ background: #333; padding: 0.1rem 0.4rem; border-radius: 3px; font-size: 0.8rem; margin-left: 0.5rem; }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>{title}</h1>
            <a href="index.html">← Back to Index</a>
        </header>
        <div class="meta">{meta}</div>
        <div class="content">{content}</div>
    </div>
</body>
</html>
"""

INDEX_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Worldbuilder</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: Georgia, serif; background: #1a1a2e; color: #eee; line-height: 1.6; }}
        .container {{ max-width: 900px; margin: 0 auto; padding: 2rem; }}
        header {{ border-bottom: 1px solid #333; padding-bottom: 1rem; margin-bottom: 2rem; }}
        header h1 {{ color: #ffd700; }}
        h2 {{ color: #ffd700; margin-top: 2rem; margin-bottom: 1rem; }}
        .entry-list {{ list-style: none; }}
        .entry-list li {{ padding: 0.5rem 0; border-bottom: 1px solid #333; }}
        .entry-list a {{ color: #4ecdc4; text-decoration: none; }}
        .entry-list a:hover {{ color: #ffd700; }}
        .stats {{ color: #888; margin-top: 2rem; font-size: 0.9rem; }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>🌍 Worldbuilder</h1>
        </header>
        {sections}
        <div class="stats">
            {entry_count} entries | Generated {date}
        </div>
    </div>
</body>
</html>
"""

def parse_entry(filepath):
    """Parse a markdown file with YAML frontmatter."""
    content = filepath.read_text()
    if not content.startswith("---"):
        return None

    parts = content.split("---", 2)
    if len(parts) < 3:
        return None

    try:
        meta = yaml.safe_load(parts[1])
    except:
        return None

    body = parts[2].strip()
    meta["_body"] = body
    meta["_filepath"] = filepath
    meta["_slug"] = filepath.stem
    return meta

def auto_link(html, entries):
    """Replace entry names with links."""
    for entry in entries:
        name = entry.get("name", "")
        if not name:
            continue
        slug = entry["_slug"]
        pattern = re.compile(rf'\b{re.escape(name)}\b(?![^<]*>)')
        html = pattern.sub(f'<a href="{slug}.html">{name}</a>', html, count=1)
    return html

def build():
    """Build the wiki."""
    SITE_DIR.mkdir(exist_ok=True)

    if not WORLDS_DIR.exists():
        WORLDS_DIR.mkdir()
        print(f"Created {WORLDS_DIR}/ - add your entries there!")
        return

    entries = []
    for f in WORLDS_DIR.glob("*.md"):
        entry = parse_entry(f)
        if entry:
            entries.append(entry)

    if not entries:
        print("No entries found. Add markdown files to worlds/")
        return

    for entry in entries:
        body_html = markdown.markdown(entry["_body"])
        body_html = auto_link(body_html, entries)

        meta_parts = []
        if "type" in entry:
            meta_parts.append(f'<span>{entry["type"]}</span>')
        if "tags" in entry:
            for tag in entry["tags"]:
                meta_parts.append(f'<span>#{tag}</span>')

        html = TEMPLATE_HTML.format(
            title=entry.get("name", entry["_slug"]),
            meta=" ".join(meta_parts),
            content=body_html
        )

        out_path = SITE_DIR / f'{entry["_slug"]}.html'
        out_path.write_text(html)
        print(f"  → {out_path}")

    by_type = {}
    for entry in entries:
        t = entry.get("type", "other")
        if t not in by_type:
            by_type[t] = []
        by_type[t].append(entry)

    sections = []
    for t in sorted(by_type.keys()):
        items = sorted(by_type[t], key=lambda x: x.get("name", x["_slug"]))
        li = "\n".join(f'<li><a href="{e["_slug"]}.html">{e.get("name", e["_slug"])}</a></li>' for e in items)
        sections.append(f"<h2>{t.title()}s</h2>\n<ul class='entry-list'>{li}</ul>")

    index = INDEX_HTML.format(
        sections="\n".join(sections),
        entry_count=len(entries),
        date=datetime.now().strftime("%Y-%m-%d %H:%M")
    )
    (SITE_DIR / "index.html").write_text(index)
    print(f"  → {SITE_DIR}/index.html")
    print(f"\nBuilt {len(entries)} entries. Open docs/index.html to view.")

if __name__ == "__main__":
    build()
