#!/usr/bin/env python3
"""Faith Above static site generator. Usage: python3 build.py
Reads content/*.md (front matter + body), writes public/. No dependencies."""
import os, re, glob, html, shutil, datetime

SITE = "https://faithabove.com"
NAME = "Faith Above"
TAGLINE = "A daily verse, a short devotional, and a prayer."
# Replace with your email provider's embed form URL (Buttondown, ConvertKit, MailerLite)
FORM_ACTION = "https://buttondown.com/api/emails/embed-subscribe/YOUR-NEWSLETTER"
GA_ID = ""  # e.g. "G-XXXXXXXXXX"
TODAY = datetime.date.today().isoformat()

CSS = """
:root{--bg:#faf7f2;--ink:#2a2622;--muted:#6f675e;--accent:#8a5a2b;--card:#fff;--line:#e6dfd3}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--ink);font:18px/1.7 Georgia,serif}
a{color:var(--accent)}header,footer{max-width:720px;margin:0 auto;padding:20px 16px}
header a.logo{font-size:24px;font-weight:bold;text-decoration:none;color:var(--ink)}
nav{display:inline-block;float:right;font:15px system-ui}nav a{margin-left:14px;text-decoration:none}
main{max-width:720px;margin:0 auto;padding:0 16px 40px}
h1{font-size:32px;line-height:1.25}h2{font-size:22px}
.verse{background:var(--card);border-left:4px solid var(--accent);padding:14px 18px;margin:22px 0;font-style:italic}
.verse b{display:block;font-style:normal;color:var(--accent);margin-top:6px;font-size:16px}
.card{background:var(--card);border:1px solid var(--line);border-radius:10px;padding:16px 18px;margin:14px 0}
.card h3{margin:0 0 4px}.meta{color:var(--muted);font:14px system-ui}
.signup{background:#f1e9dc;border-radius:12px;padding:20px;margin:32px 0;text-align:center}
.signup input[type=email]{padding:10px;width:70%;max-width:320px;border:1px solid var(--line);border-radius:6px;font-size:16px}
.signup button{padding:10px 18px;background:var(--accent);color:#fff;border:0;border-radius:6px;font-size:16px;cursor:pointer}
.prayer{background:var(--card);border:1px solid var(--line);padding:16px 18px;border-radius:10px}
footer{color:var(--muted);font:14px system-ui;border-top:1px solid var(--line)}
"""

def esc(s): return html.escape(s, quote=True)

def parse(path):
    raw = open(path, encoding="utf-8").read()
    m = re.match(r"^---\n(.*?)\n---\n(.*)$", raw, re.S)
    meta, body = {}, raw
    if m:
        for line in m.group(1).splitlines():
            if ":" in line:
                k, v = line.split(":", 1)
                meta[k.strip()] = v.strip().strip('"')
        body = m.group(2)
    meta["slug"] = os.path.splitext(os.path.basename(path))[0]
    meta["body"] = body.strip()
    return meta

def md(body):
    out = []
    for block in re.split(r"\n\s*\n", body):
        b = block.strip()
        if not b: continue
        if b.startswith("## "): out.append(f"<h2>{esc(b[3:])}</h2>")
        elif b.startswith("PRAYER:"):
            out.append(f'<h2>Prayer</h2><div class="prayer">{esc(b[7:].strip())}</div>')
        else:
            t = esc(b)
            t = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", t)
            t = re.sub(r"\*(.+?)\*", r"<em>\1</em>", t)
            out.append(f"<p>{t}</p>")
    return "\n".join(out)

def signup():
    return f'''<div class="signup"><h2 style="margin-top:0">Get the daily devotional by email</h2>
<p class="meta" style="margin-top:0">One verse, one short reflection, one prayer. Free.</p>
<form action="{FORM_ACTION}" method="post" target="_blank">
<input type="email" name="email" placeholder="Your email" required> <button type="submit">Subscribe</button></form></div>'''

def page(title, desc, path, content, jsonld=""):
    ga = (f'<script async src="https://www.googletagmanager.com/gtag/js?id={GA_ID}"></script>'
          f'<script>window.dataLayer=window.dataLayer||[];function gtag(){{dataLayer.push(arguments)}}gtag("js",new Date());gtag("config","{GA_ID}");</script>') if GA_ID else ""
    return f'''<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{esc(title)}</title><meta name="description" content="{esc(desc)}">
<link rel="canonical" href="{SITE}{path}"><style>{CSS}</style>{jsonld}{ga}</head><body>
<header><a class="logo" href="/">{NAME}</a><nav><a href="/devotionals/">Devotionals</a><a href="/about/">About</a></nav></header>
<main>{content}</main>
<footer>&copy; {datetime.date.today().year} {NAME}. Scripture quotations are from the King James Version (public domain).
<br><a href="/about/">About</a> &middot; <a href="/privacy/">Privacy</a></footer></body></html>'''

def write(path, text):
    full = os.path.join("public", path.lstrip("/"))
    if full.endswith("/"): full += "index.html"
    os.makedirs(os.path.dirname(full), exist_ok=True)
    open(full, "w", encoding="utf-8").write(text)

def main():
    shutil.rmtree("public", ignore_errors=True)
    posts = [parse(p) for p in glob.glob("content/devotionals/*.md")]
    posts = [p for p in posts if p.get("date", "9999") <= TODAY]  # future-dated posts stay hidden until their day
    posts.sort(key=lambda p: p["date"], reverse=True)
    urls = ["/", "/devotionals/", "/about/", "/privacy/"]

    for p in posts:
        path = f"/devotional/{p['slug']}/"
        urls.append(path)
        content = f'''<p class="meta">{esc(p["date"])} &middot; {esc(p.get("topic",""))}</p><h1>{esc(p["title"])}</h1>
<div class="verse">{esc(p["verse_text"])}<b>{esc(p["verse_ref"])} (KJV)</b></div>{md(p["body"])}{signup()}'''
        write(path, page(f'{p["title"]} | {NAME}', p.get("description", p["title"]), path, content))

    def card(p):
        return f'<div class="card"><p class="meta">{esc(p["date"])} &middot; {esc(p.get("topic",""))}</p><h3><a href="/devotional/{p["slug"]}/">{esc(p["title"])}</a></h3><p style="margin:4px 0">{esc(p.get("description",""))}</p></div>'

    latest = posts[:1]
    home = f'<h1>{NAME}</h1><p>{TAGLINE}</p>' + "".join(card(p) for p in latest) + signup() + "<h2>Recent devotionals</h2>" + "".join(card(p) for p in posts[1:8])
    write("/", page(f"{NAME} | Daily Bible Verse and Devotional", TAGLINE, "/", home))
    write("/devotionals/", page(f"All Devotionals | {NAME}", "Browse every daily devotional.", "/devotionals/",
          "<h1>All devotionals</h1>" + "".join(card(p) for p in posts)))

    topics = sorted({p.get("topic", "") for p in posts if p.get("topic")})
    for t in topics:
        tslug = re.sub(r"[^a-z0-9]+", "-", t.lower()).strip("-")
        path = f"/topic/{tslug}/"; urls.append(path)
        write(path, page(f"Bible Verses and Devotionals on {t} | {NAME}", f"Devotionals about {t.lower()}.", path,
              f"<h1>{esc(t)}</h1>" + "".join(card(p) for p in posts if p.get("topic") == t)))

    write("/about/", page(f"About | {NAME}", "About Faith Above.", "/about/",
          f"<h1>About {NAME}</h1><p>{NAME} publishes a short daily devotional to help you start the day grounded in Scripture. Content is prepared with the help of AI tools and reviewed before publication.</p>"))
    write("/privacy/", page(f"Privacy | {NAME}", "Privacy policy.", "/privacy/",
          "<h1>Privacy Policy</h1><p>We collect your email address only if you subscribe, and use it solely to send the devotional. You can unsubscribe at any time. We use basic analytics and may use affiliate links, for which we may earn a commission at no cost to you.</p>"))
    write("/robots.txt", f"User-agent: *\nAllow: /\nSitemap: {SITE}/sitemap.xml\n")
    sm = "".join(f"<url><loc>{SITE}{u}</loc></url>" for u in urls)
    write("/sitemap.xml", f'<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">{sm}</urlset>')
    print(f"Built {len(posts)} devotionals, {len(urls)} pages -> public/")

if __name__ == "__main__":
    main()
