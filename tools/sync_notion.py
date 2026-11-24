"""Publish ✅ child pages of one Notion page as Jekyll posts."""

import argparse
import html
import json
import os
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
POSTS = ROOT / "_posts"
ASSETS = ROOT / "assets" / "img" / "posts" / "notion"
API = "https://api.notion.com/v1"
VERSION = "2022-06-28"
FILENAME = re.compile(r"^(\d{4}-\d{2}-\d{2})-([a-z0-9][a-z0-9-]*)\.md$")
NOTE = re.compile(r"^\s*(.+?)\s*:\s*(.+?)\s*$", re.S)
COLORS = {"gray", "brown", "orange", "yellow", "green", "blue", "purple", "pink", "red"}


class SyncError(Exception):
    pass


def request(path, token, query=None):
    url = API + path
    if query:
        url += "?" + urllib.parse.urlencode(query)
    req = urllib.request.Request(url, headers={
        "Authorization": f"Bearer {token}", "Notion-Version": VERSION,
        "Content-Type": "application/json",
    })
    for attempt in range(5):
        try:
            with urllib.request.urlopen(req, timeout=30) as response:
                return json.load(response)
        except urllib.error.HTTPError as error:
            if error.code in (429, 500, 502, 503, 504) and attempt < 4:
                time.sleep(int(error.headers.get("Retry-After", "2")))
                continue
            raise SyncError(f"Notion API {error.code}: {error.read().decode('utf-8', 'replace')}") from error
    raise SyncError("Notion API retry limit reached")


def children(block_id, token):
    result = []
    cursor = None
    while True:
        query = {"page_size": 100}
        if cursor:
            query["start_cursor"] = cursor
        data = request(f"/blocks/{block_id}/children", token, query)
        result.extend(data["results"])
        cursor = data.get("next_cursor")
        if not data.get("has_more"):
            return result


def plain(rich_text):
    return "".join(item.get("plain_text", item.get("text", {}).get("content", "")) for item in rich_text)


def liquid_arg(value):
    # Liquid's quoted include arguments cannot safely contain quotes or newlines.
    # Reject instead of publishing malformed markup or silently changing text.
    if '"' in value or "{%" in value or "{{" in value:
        raise SyncError("설명 카드의 용어/설명에 큰따옴표나 Liquid 구문을 사용할 수 없습니다")
    return value.replace("\n", "\\n")


def collect_notes(blocks):
    notes = {}
    content = []
    for block in blocks:
        kind = block["type"]
        rich = block.get(kind, {}).get("rich_text", [])
        marked = [item for item in rich if item.get("annotations", {}).get("italic")
                  and item.get("annotations", {}).get("color") == "gray"]
        if kind == "paragraph" and marked and len(marked) != len(rich):
            raise SyncError("설명 줄은 문단 전체를 회색+기울기로 표시해야 합니다")
        if kind == "paragraph" and rich and len(marked) == len(rich):
            match = NOTE.match(plain(rich))
            if not match:
                raise SyncError("회색+기울기 설명 줄은 '용어: 설명' 형식이어야 합니다")
            term, explanation = match.groups()
            if term in notes:
                raise SyncError(f"중복된 설명 용어: {term}")
            notes[term] = explanation
        else:
            content.append(block)
    return notes, content


def inline(rich_text, notes, used):
    out = []
    for item in rich_text:
        value = item.get("plain_text", item.get("text", {}).get("content", ""))
        annotations = item.get("annotations", {})
        if annotations.get("underline"):
            if value not in notes:
                raise SyncError(f"밑줄 용어에 해당하는 설명이 없습니다: {value}")
            used.add(value)
            out.append('{% include annotation.html text="' + liquid_arg(value) + '" note="' + liquid_arg(notes[value]) + '" %}')
            continue
        rendered = html.escape(value, quote=False)
        link = item.get("text", {}).get("link")
        href = item.get("href") or (link or {}).get("url")
        if annotations.get("code"):
            rendered = "<code>" + rendered + "</code>"
        if annotations.get("bold"):
            rendered = "<strong>" + rendered + "</strong>"
        if annotations.get("italic"):
            rendered = "<em>" + rendered + "</em>"
        if annotations.get("strikethrough"):
            rendered = "<s>" + rendered + "</s>"
        color = annotations.get("color", "default")
        if color != "default":
            if color not in COLORS and color.removesuffix("_background") not in COLORS:
                raise SyncError(f"지원하지 않는 색상: {color}")
            rendered = f'<span class="notion-color-{color}">{rendered}</span>'
        if href:
            if not href.startswith(("https://", "http://", "mailto:")):
                raise SyncError(f"지원하지 않는 링크: {href}")
            rendered = f'<a href="{html.escape(href, quote=True)}">{rendered}</a>'
        out.append(rendered)
    return "".join(out)


def image(block, token, page_id, dry_run):
    data = block["image"]
    source = data[data["type"]]["url"]
    extension = Path(urllib.parse.urlparse(source).path).suffix.lower()
    if extension not in {".png", ".jpg", ".jpeg", ".gif", ".webp", ".svg"}:
        extension = ".png"
    name = f"{page_id}-{block['id']}{extension}"
    target = ASSETS / name
    if not dry_run:
        req = urllib.request.Request(source)
        with urllib.request.urlopen(req, timeout=60) as response:
            raw = response.read()
        ASSETS.mkdir(parents=True, exist_ok=True)
        if not target.exists() or target.read_bytes() != raw:
            target.write_bytes(raw)
    caption = html.escape(plain(data.get("caption", [])), quote=True)
    return f'![{caption}](/assets/img/posts/notion/{name})'


def render_blocks(blocks, token, page_id, notes, used, dry_run, depth=0):
    if depth > 8:
        raise SyncError("블록 중첩이 너무 깊습니다")
    output = []
    list_kind = None
    for block in blocks:
        kind = block["type"]
        data = block.get(kind, {})
        rich = data.get("rich_text", [])
        if kind in {"bulleted_list_item", "numbered_list_item"}:
            text = inline(rich, notes, used)
            prefix = "- " if kind == "bulleted_list_item" else "1. "
            if list_kind != kind:
                output.append("")
            output.append("  " * depth + prefix + text)
            list_kind = kind
            if block.get("has_children"):
                output.extend(render_blocks(children(block["id"], token), token, page_id, notes, used, dry_run, depth + 1).splitlines())
            continue
        list_kind = None
        if kind == "paragraph":
            output.append(inline(rich, notes, used))
        elif kind in {"heading_1", "heading_2", "heading_3"}:
            output.append("#" * int(kind[-1]) + " " + inline(rich, notes, used))
        elif kind == "quote":
            output.append("> " + inline(rich, notes, used).replace("\n", "\n> "))
        elif kind == "callout":
            title = inline(rich, notes, used)
            body = ""
            if block.get("has_children"):
                body = render_blocks(children(block["id"], token), token, page_id, notes, used, dry_run, depth + 1)
            output.append(f'<aside class="case-callout" markdown="1">\n\n<p class="case-callout-title">{title}</p>\n\n{body}\n\n</aside>')
        elif kind == "code":
            code = plain(rich)
            language = data.get("language", "text").split()[0].lower()
            if "```" in code:
                raise SyncError("코드 블록에 ```가 포함되어 있습니다")
            output.append(f"```{language}\n{code}\n```")
        elif kind == "image":
            output.append(image(block, token, page_id, dry_run))
        elif kind == "divider":
            output.append("---")
        else:
            raise SyncError(f"지원하지 않는 노션 블록: {kind} ({block['id']})")
        output.append("")
    return "\n".join(output).strip()


def post_title(page):
    for property_value in page.get("properties", {}).values():
        if property_value.get("type") == "title":
            return plain(property_value.get("title", []))
    raise SyncError("페이지 제목을 찾을 수 없습니다")


def page_to_post(page, token, dry_run):
    filename = post_title(page)
    match = FILENAME.fullmatch(filename)
    if not match:
        raise SyncError(f"글 제목은 YYYY-MM-DD-english-slug.md 형식이어야 합니다: {filename}")
    raw = children(page["id"], token)
    notes, content = collect_notes(raw)
    used = set()
    body = render_blocks(content, token, page["id"].replace("-", ""), notes, used, dry_run)
    unused = set(notes) - used
    if unused:
        raise SyncError("밑줄 용어와 일치하지 않는 설명: " + ", ".join(sorted(unused)))
    title = match.group(2).replace("-", " ")
    for block in content:
        if block["type"] == "heading_1":
            title = plain(block["heading_1"].get("rich_text", []))
            break
    marker = f"# notion_page_id: {page['id']}"
    front = "\n".join([
        "---", marker, "title: " + json.dumps(title, ensure_ascii=False),
        "date: " + match.group(1) + " 12:00:00 +0900",
        "categories: []", "tags: []", "---", "", body, "",
    ])
    return filename, front


def sync(token, parent_id, dry_run):
    failures = []
    changes = 0
    for block in children(parent_id, token):
        if block["type"] != "child_page":
            continue
        page = request(f"/pages/{block['id']}", token)
        icon = page.get("icon") or {}
        if icon.get("type") != "emoji" or icon.get("emoji") != "✅":
            continue
        try:
            filename, result = page_to_post(page, token, dry_run)
            target = POSTS / filename
            if target.exists():
                current = target.read_text(encoding="utf-8")
                if f"# notion_page_id: {page['id']}" not in current:
                    raise SyncError(f"기존 수동 작성 글과 파일명이 겹칩니다: {filename}")
                if current == result:
                    continue
            print(("Would update " if dry_run else "Updated ") + str(target.relative_to(ROOT)))
            if not dry_run:
                target.write_text(result, encoding="utf-8")
            changes += 1
        except (SyncError, urllib.error.URLError) as error:
            failures.append(f"{post_title(page)}: {error}")
    for failure in failures:
        print("ERROR: " + failure, file=sys.stderr)
    print(f"{changes} post(s) changed; {len(failures)} error(s)")
    return 1 if failures else 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    token = os.environ.get("NOTION_TOKEN")
    parent = os.environ.get("NOTION_PARENT_PAGE_ID")
    if not token or not parent:
        parser.error("NOTION_TOKEN and NOTION_PARENT_PAGE_ID are required")
    try:
        sys.exit(sync(token, parent, args.dry_run))
    except (SyncError, urllib.error.URLError) as error:
        print(f"ERROR: {error}", file=sys.stderr)
        sys.exit(1)
