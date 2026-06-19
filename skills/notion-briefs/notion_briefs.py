#!/usr/bin/env python3
"""Publish AI Briefs / Shift Reports to a CROSS-PROJECT Notion database.

One database ("Briefs") under Ray's "AI Briefs" Notion page holds briefs across
ALL projects/initiatives, sorted newest-first, tagged by Project. Project-specific
views are layered on top in Notion.

Config (cross-project, not tied to any one repo):
  ~/.config/ai-briefs/token        -> integration secret (chmod 600)
  ~/.config/ai-briefs/config.json  -> {"briefs_db": "<database_id>"}

Usage:
  notion_briefs.py bootstrap --parent <ai-briefs-page-url>     # create the DB, save its id
  notion_briefs.py publish --project "Smart Terminal" --date 2026-06-18 \
        --title "Shift Report 2026-06-18" --type "Shift Report" --status Active --file report.md
  notion_briefs.py list [--project "Smart Terminal"] [--status Active] [--type "Shift Report"]
  notion_briefs.py projects                                    # current Project pick-list options
  notion_briefs.py set-status <page-url-or-id> --status Superseded   # flip a brief's lifecycle status
  notion_briefs.py append <page-url-or-id> --file closeout.md [--divider]  # add a "what we did" footer

Brief lifecycle (Status select): Active (open, in front of the user) -> Superseded
(rolled forward into a newer report of the same kind) | Collected (fully worked
through; closed out with an appended "what we did" footer). The conversation with a
brief ends by appending the closeout and flipping status off Active.

Stdlib only (urllib + json). Notion auto-creates new select options (Project/Type/
Status) on write, so new projects/statuses just work without touching the schema.
"""
import json, os, sys, re, argparse, urllib.request, urllib.error

API = "https://api.notion.com/v1"
VERSION = "2022-06-28"
CFG_DIR = os.path.expanduser("~/.config/ai-briefs")
TOKEN_PATH = os.path.join(CFG_DIR, "token")
CONFIG_PATH = os.path.join(CFG_DIR, "config.json")


def _token():
    if os.environ.get("NOTION_TOKEN"):
        return os.environ["NOTION_TOKEN"].strip()
    try:
        with open(TOKEN_PATH) as f:
            return f.read().strip()
    except FileNotFoundError:
        sys.exit(f"No Notion token at {TOKEN_PATH} (chmod 600) or NOTION_TOKEN env. See `setup`.")


def _cfg():
    try:
        with open(CONFIG_PATH) as f:
            return json.load(f)
    except FileNotFoundError:
        return {}


def _save_cfg(cfg):
    os.makedirs(CFG_DIR, exist_ok=True)
    with open(CONFIG_PATH, "w") as f:
        json.dump(cfg, f, indent=2)


def _req(method, path, body=None):
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(API + path, data=data, method=method)
    req.add_header("Authorization", f"Bearer {_token()}")
    req.add_header("Notion-Version", VERSION)
    req.add_header("Content-Type", "application/json")
    try:
        with urllib.request.urlopen(req) as r:
            return json.load(r)
    except urllib.error.HTTPError as e:
        sys.exit(f"Notion API {e.code}: {e.read().decode()[:600]}")


def _id(s):
    # Notion page/db ids are 32 hex chars. In a URL they're the last hyphen/slash-
    # delimited token (slug words can contain digits, so DON'T strip hyphens first
    # and grab the front run — that merges a numeric slug into the id).
    s = s.split("?")[0].split("#")[0]
    for tok in reversed(re.split(r"[-/]", s)):
        if re.fullmatch(r"[0-9a-fA-F]{32}", tok):
            return tok
    m = re.search(r"([0-9a-fA-F]{32})", s.replace("-", ""))  # dashed-uuid fallback
    if not m:
        sys.exit(f"Couldn't find a Notion id in: {s}")
    return m.group(1)


# ---------- markdown -> Notion blocks ----------
def _rt(text):
    out = []
    for part in re.split(r"(\*\*[^*]+\*\*|`[^`]+`)", text):
        if not part:
            continue
        if part.startswith("**") and part.endswith("**"):
            out.append({"type": "text", "text": {"content": part[2:-2][:2000]}, "annotations": {"bold": True}})
        elif part.startswith("`") and part.endswith("`"):
            out.append({"type": "text", "text": {"content": part[1:-1][:2000]}, "annotations": {"code": True}})
        else:
            out.append({"type": "text", "text": {"content": part[:2000]}})
    return out or [{"type": "text", "text": {"content": ""}}]


def md_to_blocks(md):
    blocks, lines, i = [], md.splitlines(), 0
    def blk(t, key):
        return {"object": "block", "type": t, t: {"rich_text": _rt(key)}}
    while i < len(lines):
        ln = lines[i]
        if ln.strip() == "":
            i += 1; continue
        if ln.startswith("```"):
            buf = []; i += 1
            while i < len(lines) and not lines[i].startswith("```"):
                buf.append(lines[i]); i += 1
            i += 1
            blocks.append({"object": "block", "type": "code",
                           "code": {"rich_text": [{"type": "text", "text": {"content": "\n".join(buf)[:2000]}}],
                                    "language": "plain text"}})
            continue
        if ln.startswith("### "): blocks.append(blk("heading_3", ln[4:]))
        elif ln.startswith("## "): blocks.append(blk("heading_2", ln[3:]))
        elif ln.startswith("# "): blocks.append(blk("heading_1", ln[2:]))
        elif ln.startswith("> "): blocks.append(blk("quote", ln[2:]))
        elif re.match(r"^\s*[-*] ", ln): blocks.append(blk("bulleted_list_item", re.sub(r"^\s*[-*] ", "", ln)))
        elif re.match(r"^\s*\d+\. ", ln): blocks.append(blk("numbered_list_item", re.sub(r"^\s*\d+\. ", "", ln)))
        elif ln.startswith("|") and i + 1 < len(lines) and re.match(r"^\s*\|[-:\s|]+\|\s*$", lines[i + 1]):
            header = [c.strip() for c in ln.strip().strip("|").split("|")]; i += 2
            while i < len(lines) and lines[i].strip().startswith("|"):
                cells = [c.strip() for c in lines[i].strip().strip("|").split("|")]
                blocks.append(blk("bulleted_list_item", " · ".join(f"{h}: {c}" for h, c in zip(header, cells) if c)))
                i += 1
            continue
        elif ln.startswith("---"): blocks.append({"object": "block", "type": "divider", "divider": {}})
        else: blocks.append(blk("paragraph", ln))
        i += 1
    return blocks


def cmd_bootstrap(args):
    parent = _id(args.parent)
    db = _req("POST", "/databases", {
        "parent": {"type": "page_id", "page_id": parent},
        "is_inline": True,  # render as a live table on the parent page, not a linked sub-page
        "title": [{"type": "text", "text": {"content": "Briefs"}}],
        "description": [{"type": "text", "text": {"content":
            "AI-generated briefs & shift reports across all projects. Newest first; filter by Project."}}],
        "properties": {
            "Name": {"title": {}},
            "Date": {"date": {}},
            "Project": {"select": {"options": [{"name": "Smart Terminal", "color": "blue"}]}},
            "Type": {"select": {"options": [
                {"name": "Shift Report", "color": "purple"}, {"name": "Brief", "color": "default"},
                {"name": "Plan", "color": "orange"}]}},
            "Status": {"select": {"options": [
                {"name": "Active", "color": "green"}, {"name": "Superseded", "color": "gray"},
                {"name": "Collected", "color": "blue"}]}},
        },
    })
    cfg = _cfg(); cfg["briefs_db"] = db["id"]; _save_cfg(cfg)
    print(f"database {db['id']}\n{db.get('url')}")


def cmd_publish(args):
    db = _cfg().get("briefs_db")
    if not db:
        sys.exit("No database configured. Run bootstrap first.")
    md = open(args.file).read() if args.file else sys.stdin.read()
    blocks = md_to_blocks(md)
    page = _req("POST", "/pages", {
        "parent": {"database_id": db},
        "properties": {
            "Name": {"title": [{"type": "text", "text": {"content": args.title}}]},
            "Date": {"date": {"start": args.date}},
            "Project": {"select": {"name": args.project}},
            "Type": {"select": {"name": args.type}},
            "Status": {"select": {"name": args.status}},
        },
        "children": blocks[:100],
    })
    pid = page["id"]
    for j in range(100, len(blocks), 100):
        _req("PATCH", f"/blocks/{pid}/children", {"children": blocks[j:j + 100]})
    print(page.get("url"))


def cmd_list(args):
    db = _cfg().get("briefs_db")
    if not db:
        sys.exit("No database configured.")
    body = {"sorts": [{"property": "Date", "direction": "descending"}]}
    conds = []
    if args.project: conds.append({"property": "Project", "select": {"equals": args.project}})
    if args.status: conds.append({"property": "Status", "select": {"equals": args.status}})
    if args.type: conds.append({"property": "Type", "select": {"equals": args.type}})
    if len(conds) == 1: body["filter"] = conds[0]
    elif conds: body["filter"] = {"and": conds}
    for r in _req("POST", f"/databases/{db}/query", body).get("results", []):
        p = r["properties"]
        title = "".join(t["plain_text"] for t in p["Name"]["title"])
        date = (p["Date"]["date"] or {}).get("start", "?")
        proj = (p["Project"]["select"] or {}).get("name", "?")
        status = (p["Status"]["select"] or {}).get("name", "?")
        print(f"{date}  [{proj}]  ({status})  {title}  {r['url']}")


def cmd_projects(args):
    db = _cfg().get("briefs_db")
    if not db:
        sys.exit("No database configured.")
    meta = _req("GET", f"/databases/{db}")
    for o in meta["properties"]["Project"]["select"]["options"]:
        print(o["name"])


def cmd_status(args):
    pid = _id(args.page)
    _req("PATCH", f"/pages/{pid}", {"properties": {"Status": {"select": {"name": args.status}}}})
    print(f"{pid} -> Status={args.status}")


def cmd_append(args):
    pid = _id(args.page)
    md = open(args.file).read() if args.file else sys.stdin.read()
    blocks = md_to_blocks(md)
    if args.divider:
        blocks = [{"object": "block", "type": "divider", "divider": {}}] + blocks
    for j in range(0, len(blocks), 100):
        _req("PATCH", f"/blocks/{pid}/children", {"children": blocks[j:j + 100]})
    print(f"appended {len(blocks)} block(s) to {pid}")


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    b = sub.add_parser("bootstrap"); b.add_argument("--parent", required=True); b.set_defaults(fn=cmd_bootstrap)
    pub = sub.add_parser("publish")
    pub.add_argument("--project", required=True); pub.add_argument("--date", required=True)
    pub.add_argument("--title", required=True); pub.add_argument("--type", default="Shift Report")
    pub.add_argument("--status", default="Active"); pub.add_argument("--file")
    pub.set_defaults(fn=cmd_publish)
    ls = sub.add_parser("list")
    ls.add_argument("--project"); ls.add_argument("--status"); ls.add_argument("--type")
    ls.set_defaults(fn=cmd_list)
    pr = sub.add_parser("projects"); pr.set_defaults(fn=cmd_projects)
    st = sub.add_parser("set-status"); st.add_argument("page"); st.add_argument("--status", required=True)
    st.set_defaults(fn=cmd_status)
    apc = sub.add_parser("append"); apc.add_argument("page"); apc.add_argument("--file")
    apc.add_argument("--divider", action="store_true"); apc.set_defaults(fn=cmd_append)
    args = ap.parse_args(); args.fn(args)


if __name__ == "__main__":
    main()
