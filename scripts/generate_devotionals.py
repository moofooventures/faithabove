#!/usr/bin/env python3
"""Generate today's devotionals using the Anthropic API and write them into
content/devotionals/. Run via GitHub Actions (see
.github/workflows/daily-devotionals.yml). Requires ANTHROPIC_API_KEY in the
environment. No other dependencies besides the `anthropic` package.

This script is "top-up" style rather than fire-once: each run checks how
many devotionals already exist for today and only generates however many
more are needed to reach TARGET_POSTS_PER_DAY. That way, if GitHub's cron
scheduler delays or drops some of the day's scheduled runs (a known,
undocumented-frequency behavior -- see
https://docs.github.com/actions/using-workflows/events-that-trigger-workflows#schedule),
the day still ends up with the right number of posts as long as at least
one run near the end of the window fires. If today's target is already
met, the script exits immediately without calling the API (no wasted
cost).
"""
import os, re, glob, datetime
from zoneinfo import ZoneInfo
import anthropic

SITE_TZ = ZoneInfo("America/New_York")

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEVO_DIR = os.path.join(REPO_ROOT, "content", "devotionals")
CALENDAR_PATH = os.path.join(REPO_ROOT, "TOPIC_CALENDAR.md")
TARGET_POSTS_PER_DAY = 4
RECENT_WINDOW = 40  # how many recent files to check when avoiding repeats

MODEL = "claude-sonnet-5"


def load_recent_posts():
    files = sorted(glob.glob(os.path.join(DEVO_DIR, "*.md")))[-RECENT_WINDOW:]
    recent = []
    for path in files:
        raw = open(path, encoding="utf-8").read()
        m = re.match(r"^---\n(.*?)\n---", raw, re.S)
        if not m:
            continue
        meta = {}
        for line in m.group(1).splitlines():
            if ":" in line:
                k, v = line.split(":", 1)
                meta[k.strip()] = v.strip().strip('"')
        recent.append({
            "topic": meta.get("topic", ""),
            "verse_ref": meta.get("verse_ref", ""),
            "title": meta.get("title", ""),
        })
    return recent


def count_today(today):
    return len(glob.glob(os.path.join(DEVO_DIR, f"{today}-*.md")))


def slugify(s):
    s = re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")
    return s[:60].rstrip("-")


def build_prompt(recent, today, count):
    calendar = open(CALENDAR_PATH, encoding="utf-8").read() if os.path.exists(CALENDAR_PATH) else ""
    recent_lines = "\n".join(f"- topic: {r['topic']}, verse: {r['verse_ref']}" for r in recent) or "(none yet)"
    recent_titles = "\n".join(f'- "{r["title"]}"' for r in recent if r.get("title")) or "(none yet)"
    return f'''You are writing content for Faith Above, a daily Bible-devotional website (faithabove.com). Generate {count} completely distinct devotionals for today, {today}.

Topic calendar for reference (30-topic rotation, prioritize high-search-volume topics like Anxiety, Grief, Strength, Healing, Marriage/Relationships, New Beginnings when in doubt -- but still rotate through the full calendar rather than defaulting to the same few topics every time):
{calendar}

Recently published topics/verses (DO NOT repeat any of these topics or verses):
{recent_lines}

Recently published titles (for format reference only -- see title rule below):
{recent_titles}

For EACH of the {count} devotionals, produce:
- topic: one short topic word/phrase from the calendar (all {count} must be DISTINCT from each other and from the recent list)
- title: specific, keyword-rich, and click-worthy (not generic) -- include the topic or a natural search phrase someone would type. IMPORTANT: do not default to the template "Bible Verses for X: ..." -- look at the recently published titles above and use a DIFFERENT opening format than whatever was used most recently. Vary the format across posts, rotating naturally through styles such as: a direct question ("What Do You Do When Grief Feels Endless?"), a short evocative statement ("The Weight You Weren't Meant to Carry"), a "What [Verse] Really Means/Teaches" framing, a "How to..." framing, or an emotionally resonant phrase pulled from the verse itself. A title may reference the topic and verse without ever using the literal words "Bible Verses for" or "Bible Verse for".
- verse_ref: a real Bible reference (e.g. "Philippians 4:6-7")
- verse_text: the EXACT, accurate King James Version wording of that verse -- never paraphrase or invent it
- description: one sentence, under 155 characters, written like a search-result snippet (this becomes the page meta description)
- body: 600-900 words, warm and direct (not sermon-y or generic), with real historical/textual/cultural insight about the verse and a clear, practical application for today. Break it into 2-4 sections using "## Heading" markdown lines (natural phrases, not keyword-stuffed). Naturally (not forced) reuse the topic and a couple of closely related search terms a few times so it reads well for search without sounding stuffed.
- prayer: a short first-person prayer in the reader's voice, 4-6 sentences

Call the write_devotionals tool exactly once with all {count} entries. Do not repeat a topic or verse across the {count} entries.'''


def build_tool(count):
    return {
        "name": "write_devotionals",
        "description": "Submit the finished devotionals.",
        "input_schema": {
            "type": "object",
            "properties": {
                "devotionals": {
                    "type": "array",
                    "minItems": count,
                    "maxItems": count,
                    "items": {
                        "type": "object",
                        "properties": {
                            "topic": {"type": "string"},
                            "title": {"type": "string"},
                            "verse_ref": {"type": "string"},
                            "verse_text": {"type": "string"},
                            "description": {"type": "string"},
                            "body": {"type": "string"},
                            "prayer": {"type": "string"},
                        },
                        "required": ["topic", "title", "verse_ref", "verse_text", "description", "body", "prayer"],
                    },
                }
            },
            "required": ["devotionals"],
        },
    }


def generate(recent, today, count):
    client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
    prompt = build_prompt(recent, today, count)
    tool = build_tool(count)
    resp = client.messages.create(
        model=MODEL,
        max_tokens=8000,
        tools=[tool],
        tool_choice={"type": "tool", "name": "write_devotionals"},
        messages=[{"role": "user", "content": prompt}],
    )
    for block in resp.content:
        if block.type == "tool_use" and block.name == "write_devotionals":
            return block.input["devotionals"]
    raise RuntimeError("Model did not return structured devotionals")


def write_file(d, today, used_slugs):
    slug = slugify(d.get("title", "")) or slugify(d.get("topic", "")) or "devotional"
    base, n = slug, 2
    while slug in used_slugs:
        slug = f"{base}-{n}"
        n += 1
    used_slugs.add(slug)
    filename = f"{today}-{slug}.md"
    path = os.path.join(DEVO_DIR, filename)
    body = d["body"].strip()
    prayer = d["prayer"].strip()
    content = (
        "---\n"
        f"title: {d['title'].strip()}\n"
        f"date: {today}\n"
        f"topic: {d['topic'].strip()}\n"
        f"verse_ref: {d['verse_ref'].strip()}\n"
        f"verse_text: {d['verse_text'].strip()}\n"
        f"description: {d['description'].strip()}\n"
        "---\n"
        f"{body}\n\n"
        f"PRAYER: {prayer}\n"
    )
    os.makedirs(DEVO_DIR, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    return filename


def main():
    today = datetime.datetime.now(SITE_TZ).date().isoformat()
    already = count_today(today)
    needed = TARGET_POSTS_PER_DAY - already
    if needed <= 0:
        print(f"Already have {already} devotional(s) for {today} (target {TARGET_POSTS_PER_DAY}). Nothing to do.")
        return
    recent = load_recent_posts()
    devotionals = generate(recent, today, needed)
    used_slugs = set()
    written = [write_file(d, today, used_slugs) for d in devotionals]
    print(f"Had {already}/{TARGET_POSTS_PER_DAY} for {today}. Wrote {len(written)} more devotional(s):")
    for w in written:
        print(" -", w)


if __name__ == "__main__":
    main()
