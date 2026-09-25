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

# Deterministic color + icon per topic, so new topics automatically get a look.
PALETTES = [
    ("#EDE7FF", "#5B3FD6"),  # violet
    ("#FFE9DC", "#C05621"),  # amber
    ("#DFF3EA", "#1E7A57"),  # green
    ("#FFE4EC", "#B0356B"),  # pink
    ("#E3F1FF", "#1D5FA8"),  # blue
    ("#FFF3D6", "#9A6B00"),  # gold
]
ICONS = {
    "strength": "flame", "anxiety": "wave", "hope": "sunrise", "relationships": "heart",
    "marriage": "heart", "grief": "leaf", "fear": "shield", "patience": "hourglass",
    "gratitude": "star", "forgiveness": "dove", "trust": "anchor", "purpose": "compass",
    "perseverance": "mountain", "peace": "dove", "healing": "leaf", "prayer": "hands",
    "wisdom": "lamp", "joy": "sun", "love": "heart", "humility": "leaf",
    "generosity": "gift", "rest": "moon", "guidance": "compass", "courage": "shield",
    "identity": "star", "community": "hands", "beginnings": "sunrise", "calling": "compass",
    "career": "compass", "parenting": "heart", "contentment": "sun", "decisions": "compass",
}

def palette_for(topic):
    idx = sum(ord(c) for c in (topic or "")) % len(PALETTES)
    return PALETTES[idx]

def icon_for(topic):
    key = (topic or "").lower()
    for k, v in ICONS.items():
        if k in key: return v
    return "sun"

def svg_icon(name, color="currentColor", size=22):
    paths = {
        "flame": '<path d="M12 2c1 3-2 4-2 7a3 3 0 0 0 6 0c0-1-.5-2-1-2 1.5 1 3 3 3 5.5A6.5 6.5 0 0 1 5 12.5C5 8 8 6 8 3c1.5 1 2 2.5 1.5 4C10.5 5 11 3.5 12 2z"/>',
        "wave": '<path d="M2 12c1.5-2 3.5-2 5 0s3.5 2 5 0 3.5-2 5 0 3.5 2 5 0" fill="none" stroke-width="2"/>',
        "sunrise": '<circle cx="12" cy="14" r="4"/><path d="M12 3v3M4.2 9.2l2.1 2.1M19.8 9.2l-2.1 2.1M2 19h20" stroke-width="2" fill="none"/>',
        "heart": '<path d="M12 21s-7-4.5-9.5-9C.7 8.3 2.4 5 5.6 5c1.8 0 3.3 1 4.4 2.6C11.1 6 12.6 5 14.4 5 17.6 5 19.3 8.3 21.5 12 19 16.5 12 21 12 21z"/>',
        "leaf": '<path d="M20 4C10 4 4 10 4 20c10 0 16-6 16-16z"/><path d="M4 20 20 4" stroke-width="1.5" fill="none"/>',
        "shield": '<path d="M12 2l8 3v6c0 5-3.5 8.5-8 11-4.5-2.5-8-6-8-11V5l8-3z"/>',
        "hourglass": '<path d="M6 2h12M6 22h12M6 2c0 6 12 6 12 0M6 22c0-6 12-6 12 0" stroke-width="2" fill="none"/>',
        "star": '<path d="M12 2l2.9 6.6 7.1.6-5.4 4.7 1.7 7-6.3-3.9-6.3 3.9 1.7-7L2 9.2l7.1-.6z"/>',
        "dove": '<path d="M3 12c3-4 7-4 9-1 2-4 6-5 9-2-3 1-4 3-4 5-3 1-6 0-7-2-2 3-5 3-7 0z"/>',
        "anchor": '<circle cx="12" cy="5" r="2"/><path d="M12 7v14M6 14a6 6 0 0012 0M4 14H2M22 14h-2" stroke-width="2" fill="none"/>',
        "compass": '<circle cx="12" cy="12" r="9" fill="none" stroke-width="2"/><path d="M15 9l-2 6-4-2z"/>',
        "mountain": '<path d="M2 20l6-11 4 6 3-4 7 9z"/>',
        "hands": '<path d="M3 14c0-2 1-3 2-3s2 1 2 3v2M7 13c0-3 1.2-4 2.2-4s1.8 1 1.8 3v3M11 12c0-3 1.2-4.5 2.3-4.5S15 9 15 12v3M15 13c0-2 1-3 2-3s2 1 2 4c0 4-2.5 6-7 6s-8-2.5-8-6" fill="none" stroke-width="1.6"/>',
        "lamp": '<path d="M9 2h6l-1 7h2l-4 9-1-6H9l1-6H8z"/>',
        "sun": '<circle cx="12" cy="12" r="5"/><path d="M12 1v3M12 20v3M4.2 4.2l2.1 2.1M17.7 17.7l2.1 2.1M1 12h3M20 12h3M4.2 19.8l2.1-2.1M17.7 6.3l2.1-2.1" stroke-width="2"/>',
        "gift": '<rect x="3" y="9" width="18" height="12" rx="1"/><path d="M3 9h18M12 9v12M12 9C9 9 8 4 12 4s3 5 0 5zM12 9c3 0 4-5 0-5s-3 5 0 5z" fill="none" stroke-width="1.6"/>',
        "moon": '<path d="M20 14.5A8.5 8.5 0 119.5 4a7 7 0 0010.5 10.5z"/>',
    }
    p = paths.get(name, paths["sun"])
    return f'<svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="{color}" stroke="{color}" xmlns="http://www.w3.org/2000/svg">{p}</svg>'

def thumb(topic, big=False):
    """Editorial 'photo' stand-in: gradient panel + large icon watermark, since the
    site has no photography. Mimics the image-driven thumbnails of a news/magazine theme."""
    bg, fg = palette_for(topic)
    size = 64 if big else 30
    icon = svg_icon(icon_for(topic), color=fg, size=size)
    cls = "thumb thumb-lg" if big else "thumb"
    return f'<div class="{cls}" style="background:linear-gradient(150deg,{bg} 0%,#fff 120%)">{icon}</div>'

CSS = """
:root{--bg:#F3F1EC;--card:#fff;--ink:#181614;--muted:#69645C;--line:#E4DFD3;--red:#A3241C;--red-dk:#7C1B15}
*{box-sizing:border-box}
html{-webkit-text-size-adjust:100%}
body{margin:0;background:var(--bg);color:var(--ink);font:15px/1.6 'Libre Franklin',system-ui,-apple-system,sans-serif;overflow-x:hidden}
h1,h2,h3{font-family:'Playfair Display',Georgia,serif;font-weight:800;line-height:1.12;margin:0 0 .3em}
a{color:inherit;text-decoration:none}
img,svg{display:block}
.wrap{max-width:1080px;margin:0 auto;padding:0 18px}

/* Topbar */
.topbar{background:var(--ink);color:#cfc9bd;font-size:12px}
.topbar .wrap{display:flex;justify-content:space-between;align-items:center;padding:7px 18px}
.topbar .date{letter-spacing:.03em}
.topbar .soc{display:flex;gap:12px;opacity:.8}

/* Masthead */
.masthead{background:var(--card);border-bottom:1px solid var(--line)}
.masthead .wrap{display:flex;flex-direction:column;align-items:center;padding:22px 18px 16px;text-align:center}
.brand{display:inline-flex;align-items:center;gap:10px;font-family:'Playfair Display',Georgia,serif;font-weight:900;font-size:clamp(28px,7vw,44px);letter-spacing:-.01em}
.brand .mark{width:38px;height:38px;background:var(--red);color:#fff;display:flex;align-items:center;justify-content:center;flex:none}
.masthead .lede{color:var(--muted);font-size:13px;letter-spacing:.04em;text-transform:uppercase;margin-top:6px}

/* Nav */
.nav{position:sticky;top:0;z-index:10;background:var(--red);border-bottom:3px solid var(--red-dk)}
.nav-in{max-width:1080px;margin:0 auto;padding:0 18px;display:flex;align-items:center;justify-content:center;gap:0;overflow-x:auto}
.navlinks{display:flex}
.navlinks a{padding:13px 16px;font:800 12px/1 'Libre Franklin',sans-serif;letter-spacing:.06em;text-transform:uppercase;color:#fff;white-space:nowrap;border-right:1px solid rgba(255,255,255,.15)}
.navlinks a:first-child{border-left:1px solid rgba(255,255,255,.15)}
.navlinks a:hover{background:var(--red-dk)}

main{padding:28px 0 60px}
.layout{display:grid;grid-template-columns:1fr;gap:34px}
@media (min-width:840px){.layout{grid-template-columns:2fr 1fr}}

/* Breadcrumbs */
.crumbs{font-size:12.5px;color:var(--muted);margin:0 0 14px}
.crumbs a{text-decoration:underline}
.crumbs a:hover{color:var(--ink)}

/* Tag */
.tag{display:inline-block;background:var(--red);color:#fff;font:800 10.5px/1 'Libre Franklin',sans-serif;letter-spacing:.07em;text-transform:uppercase;padding:6px 9px}

/* Thumbs (illustrated stand-ins for photography) */
.thumb{aspect-ratio:16/10;display:flex;align-items:center;justify-content:center;border:1px solid var(--line)}
.thumb-lg{aspect-ratio:16/9}

/* Hero / lead story */
.lead{background:var(--card);border:1px solid var(--line);margin-bottom:28px}
.lead .thumb-wrap{position:relative}
.lead .tag{position:absolute;top:14px;left:14px}
.lead-body{padding:20px}
.lead h1{font-size:clamp(26px,4.6vw,40px);margin:.3em 0 .2em}
.lead .dek{color:var(--muted);font-size:15.5px;margin:0 0 8px}
.byline{color:var(--muted);font-size:12.5px;letter-spacing:.03em;text-transform:uppercase}

/* Verse card */
.verse-card{background:var(--ink);color:#fff;padding:28px 24px;margin:0 0 28px;position:relative;border-left:5px solid var(--red)}
.verse-card::before{content:'\\201C';position:absolute;top:-14px;left:16px;font-family:'Playfair Display',Georgia,serif;font-size:110px;color:rgba(255,255,255,.10);line-height:1}
.verse-card p{position:relative;font-family:'Playfair Display',Georgia,serif;font-size:clamp(18px,3.2vw,23px);line-height:1.4;margin:0}
.verse-card .ref{position:relative;display:inline-flex;align-items:center;gap:8px;margin-top:16px;font:800 11px/1 'Libre Franklin',sans-serif;letter-spacing:.08em;text-transform:uppercase;color:#F4C67A}

article.post{background:var(--card)}
.article-head{border-bottom:2px solid var(--ink);padding-bottom:14px;margin-bottom:16px}
.meta{color:var(--muted);font-size:12.5px;margin-top:10px;letter-spacing:.03em;text-transform:uppercase}
h1.headline{font-size:clamp(28px,5.5vw,44px);margin-top:.35em}
h2{font-size:clamp(18px,3.6vw,22px);margin-top:1.6em;padding-top:1.1em;border-top:1px solid var(--line)}
p{margin:0 0 1.1em;font-size:16.5px}
article.post > p:first-of-type::first-letter{float:left;font-family:'Playfair Display',Georgia,serif;font-weight:800;font-size:56px;line-height:.82;padding:5px 9px 0 0;color:var(--red)}
.prayer{background:#F4EFE6;border-left:4px solid var(--red);padding:16px 18px;font-style:italic}

/* Grid of stories */
.section-title{display:flex;align-items:center;gap:10px;margin:8px 0 16px;font:800 13px/1 'Libre Franklin',sans-serif;letter-spacing:.08em;text-transform:uppercase;color:var(--red)}
.section-title::after{content:'';flex:1;height:2px;background:var(--ink)}
.grid{display:grid;grid-template-columns:1fr;gap:20px 22px;margin:0 0 30px}
@media (min-width:560px){.grid{grid-template-columns:1fr 1fr}}
.card{background:var(--card);border-bottom:1px solid var(--line);padding-bottom:16px}
.card .tag{margin-top:10px}
.card h3{font-size:18px;margin:8px 0 5px;line-height:1.25}
.card p.desc{color:var(--muted);font-size:13.5px;margin:0}

/* Sidebar */
.side-box{background:var(--card);border:1px solid var(--line);margin-bottom:26px}
.side-box .side-title{background:var(--ink);color:#fff;font:800 12px/1 'Libre Franklin',sans-serif;letter-spacing:.08em;text-transform:uppercase;padding:12px 16px}
.trend{list-style:none;margin:0;padding:6px 16px}
.trend li{display:flex;gap:12px;align-items:baseline;padding:12px 0;border-bottom:1px solid var(--line)}
.trend li:last-child{border-bottom:none}
.trend .num{font-family:'Playfair Display',Georgia,serif;font-weight:800;font-size:22px;color:var(--red);flex:none;width:26px}
.trend a{font-weight:700;font-size:14.5px;line-height:1.35}

.signup{background:var(--red);color:#fff;padding:22px 18px}
.signup h2{font-size:18px;margin:0 0 6px;font-family:'Playfair Display',Georgia,serif}
.signup p{color:rgba(255,255,255,.85);margin:0;font-size:13.5px}
.signup form{display:flex;flex-direction:column;gap:8px;margin-top:14px}
.signup input[type=email]{padding:12px 14px;border:0;font-size:15px;font-family:inherit}
.signup button{padding:12px 16px;background:var(--ink);color:#fff;border:0;font-size:13px;font-weight:800;letter-spacing:.05em;text-transform:uppercase;cursor:pointer}
.signup button:hover{background:#000}
.signup.block{margin:10px 0 34px}

footer{background:var(--ink);color:#a89f92;font-size:13px;padding:30px 18px 50px}
footer .wrap{max-width:1080px;margin:0 auto;text-align:center}
footer a{color:#fff;text-decoration:underline}
"""
FONT_LINK = ('<link rel="preconnect" href="https://fonts.googleapis.com">'
             '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>'
             '<link href="https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700;800;900&family=Libre+Franklin:wght@400;600;700;800&display=swap" rel="stylesheet">')

def esc(s): return html.escape(s, quote=True)

def meta_desc(s, limit=155):
    """Trim a description to a search-snippet-friendly length without cutting mid-word."""
    s = (s or "").strip()
    if len(s) <= limit:
        return s
    cut = s[:limit].rsplit(" ", 1)[0]
    return cut.rstrip(",.;:") + "…"

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

def tag(topic):
    return f'<span class="tag">{esc(topic)}</span>'

def signup(block=True):
    cls = "signup block" if block else "signup"
    return f'''<div class="{cls}"><h2>Get today's devotional by email</h2>
<p>One verse, one short reflection, one prayer. Free, no spam.</p>
<form action="{FORM_ACTION}" method="post" target="_blank">
<input type="email" name="email" placeholder="Your email" required> <button type="submit">Subscribe</button></form></div>'''

def nav():
    today = datetime.date.today().strftime("%A, %B %-d, %Y") if os.name != "nt" else datetime.date.today().strftime("%A, %B %d, %Y")
    top = f'''<div class="topbar"><div class="wrap"><span class="date">{today}</span>
<span class="soc">{svg_icon("dove","#cfc9bd",14)}{svg_icon("sun","#cfc9bd",14)}{svg_icon("heart","#cfc9bd",14)}</span></div></div>'''
    head = f'''<div class="masthead"><div class="wrap">
<a class="brand" href="/"><span class="mark">{svg_icon("sunrise","#fff",22)}</span>{NAME}</a>
<div class="lede">{TAGLINE}</div></div></div>'''
    navbar = f'''<div class="nav"><div class="nav-in"><div class="navlinks">
<a href="/">Home</a><a href="/devotionals/">Devotionals</a><a href="/about/">About</a>
</div></div></div>'''
    return top + head + navbar

def page(title, desc, path, content, jsonld="", og_type="website"):
    desc = meta_desc(desc)
    url = f"{SITE}{path}"
    ga = (f'<script async src="https://www.googletagmanager.com/gtag/js?id={GA_ID}"></script>'
          f'<script>window.dataLayer=window.dataLayer||[];function gtag(){{dataLayer.push(arguments)}}gtag("js",new Date());gtag("config","{GA_ID}");</script>') if GA_ID else ""
    social = f'''<meta property="og:site_name" content="{esc(NAME)}">
<meta property="og:type" content="{og_type}"><meta property="og:title" content="{esc(title)}">
<meta property="og:description" content="{esc(desc)}"><meta property="og:url" content="{url}">
<meta name="twitter:card" content="summary"><meta name="twitter:title" content="{esc(title)}">
<meta name="twitter:description" content="{esc(desc)}">'''
    return f'''<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{esc(title)}</title><meta name="description" content="{esc(desc)}">
<meta name="robots" content="index, follow">
<link rel="canonical" href="{url}">{FONT_LINK}<style>{CSS}</style>{social}{jsonld}{ga}</head><body>
{nav()}
<main><div class="wrap">{content}</div></main>
<footer><div class="wrap">&copy; {datetime.date.today().year} {NAME}. Scripture quotations are from the King James Version (public domain).
<br><a href="/about/">About</a> &middot; <a href="/privacy/">Privacy</a></div></footer></body></html>'''

def jsonld_tag(data):
    import json as _json
    return f'<script type="application/ld+json">{_json.dumps(data)}</script>'

def breadcrumb_jsonld(items):
    """items: list of (name, url_or_None-for-current)"""
    return jsonld_tag({
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": i + 1, "name": name,
             **({"item": f"{SITE}{url}"} if url else {})}
            for i, (name, url) in enumerate(items)
        ],
    })

def breadcrumb_html(items):
    """items: list of (name, url_or_None-for-current)"""
    parts = [f'<a href="{url}">{esc(name)}</a>' if url else f'<span aria-current="page">{esc(name)}</span>'
             for name, url in items]
    return f'<nav class="crumbs" aria-label="Breadcrumb">{" &rsaquo; ".join(parts)}</nav>'

def article_jsonld(p):
    return jsonld_tag({
        "@context": "https://schema.org",
        "@type": "BlogPosting",
        "headline": p["title"],
        "description": meta_desc(p.get("description", p["title"])),
        "datePublished": p["date"],
        "dateModified": p["date"],
        "author": {"@type": "Organization", "name": NAME},
        "publisher": {"@type": "Organization", "name": NAME,
                      "url": SITE},
        "mainEntityOfPage": {"@type": "WebPage", "@id": f"{SITE}/devotional/{p['slug']}/"},
        "about": p.get("topic", ""),
        "keywords": f'{p.get("topic","")}, {p.get("verse_ref","")}, daily devotional, bible verse',
    })

def website_jsonld():
    return jsonld_tag({
        "@context": "https://schema.org",
        "@type": "WebSite",
        "name": NAME,
        "url": SITE,
        "description": TAGLINE,
        "publisher": {"@type": "Organization", "name": NAME, "url": SITE},
    })

def write(path, text):
    full = os.path.join("public", path.lstrip("/"))
    if full.endswith("/"): full += "index.html"
    os.makedirs(os.path.dirname(full), exist_ok=True)
    open(full, "w", encoding="utf-8").write(text)

def sidebar(posts):
    trend = "".join(f'<li><span class="num">{i+1:02d}</span><a href="/devotional/{p["slug"]}/">{esc(p["title"])}</a></li>'
                     for i, p in enumerate(posts[:5]))
    return f'''<aside>
<div class="side-box"><div class="side-title">Trending Now</div><ul class="trend">{trend}</ul></div>
{signup(block=False)}
</aside>'''

def card(p):
    return f'''<div class="card">{thumb(p.get("topic",""))}
{tag(p.get("topic",""))}
<h3><a href="/devotional/{p["slug"]}/">{esc(p["title"])}</a></h3>
<p class="desc">{esc(p.get("description",""))}</p></div>'''

def main():
    shutil.rmtree("public", ignore_errors=True)
    posts = [parse(p) for p in glob.glob("content/devotionals/*.md")]
    posts = [p for p in posts if p.get("date", "9999") <= TODAY]  # future-dated posts stay hidden until their day
    posts.sort(key=lambda p: p["date"], reverse=True)
    urls = ["/", "/devotionals/", "/about/", "/privacy/"]

    for p in posts:
        path = f"/devotional/{p['slug']}/"
        urls.append(path)
        topic = p.get("topic", "")
        tslug = re.sub(r"[^a-z0-9]+", "-", topic.lower()).strip("-")
        crumbs = [("Home", "/"), ("Devotionals", "/devotionals/")]
        if topic:
            crumbs.append((topic, f"/topic/{tslug}/"))
        crumbs.append((p["title"], None))
        related = [x for x in posts if x["slug"] != p["slug"] and x.get("topic") == topic][:3]
        if len(related) < 3:
            related += [x for x in posts if x["slug"] != p["slug"] and x not in related][: 3 - len(related)]
        related_html = ""
        if related:
            related_html = ('<div class="section-title">Related Devotionals</div><div class="grid">'
                             + "".join(card(x) for x in related) + "</div>")
        content = f'''<div class="layout"><article class="post">
{breadcrumb_html(crumbs)}
<div class="article-head">{tag(topic)}<p class="meta">{esc(p["date"])}</p></div>
<h1 class="headline">{esc(p["title"])}</h1>
<div class="verse-card"><p>{esc(p["verse_text"])}</p><span class="ref">{svg_icon("star","#F4C67A",13)}{esc(p["verse_ref"])} &middot; KJV</span></div>
{md(p["body"])}
{related_html}
</article>{sidebar([x for x in posts if x["slug"] != p["slug"]])}</div>'''
        page_jsonld = article_jsonld(p) + breadcrumb_jsonld(crumbs)
        write(path, page(f'{p["title"]} | {NAME}', p.get("description", p["title"]), path, content,
                          jsonld=page_jsonld, og_type="article"))

    latest = posts[:1]
    rest = posts[1:]

    if latest:
        lp = latest[0]
        lead = f'''<div class="lead"><div class="thumb-wrap">{thumb(lp.get("topic",""), big=True)}{tag(lp.get("topic",""))}</div>
<div class="lead-body"><p class="byline">Today&rsquo;s Devotional &middot; {esc(lp["date"])}</p>
<h1><a href="/devotional/{lp["slug"]}/">{esc(lp["title"])}</a></h1>
<p class="dek">{esc(lp.get("description",""))}</p></div></div>'''
    else:
        lead = ""

    grid_html = '<div class="section-title">Recent Devotionals</div><div class="grid">' + "".join(card(p) for p in rest[:8]) + "</div>"
    home_main = f'<div class="layout"><div>{lead}{grid_html}</div>{sidebar(posts)}</div>'

    write("/", page(f"{NAME} | Daily Bible Verse and Devotional", TAGLINE, "/", home_main,
                     jsonld=website_jsonld()))

    devo_crumbs = [("Home", "/"), ("Devotionals", None)]
    devo_main = (breadcrumb_html(devo_crumbs) + "<h1 class=\"headline\">All Devotionals</h1><div class=\"layout\"><div class=\"grid\">"
                 + "".join(card(p) for p in posts) + "</div>" + sidebar(posts) + "</div>")
    write("/devotionals/", page(f"All Devotionals | {NAME}", "Browse every daily devotional, sorted by newest first.",
          "/devotionals/", devo_main, jsonld=breadcrumb_jsonld(devo_crumbs)))

    topics = sorted({p.get("topic", "") for p in posts if p.get("topic")})
    for t in topics:
        tslug = re.sub(r"[^a-z0-9]+", "-", t.lower()).strip("-")
        path = f"/topic/{tslug}/"; urls.append(path)
        t_crumbs = [("Home", "/"), ("Devotionals", "/devotionals/"), (t, None)]
        tmain = (breadcrumb_html(t_crumbs) + f"<h1 class=\"headline\">{esc(t)} Devotionals</h1><div class=\"layout\"><div class=\"grid\">"
                 + "".join(card(p) for p in posts if p.get("topic") == t) + "</div>" + sidebar(posts) + "</div>")
        write(path, page(f"Bible Verses and Devotionals on {t} | {NAME}",
              f"Daily devotionals, bible verses, and prayers about {t.lower()} to encourage you today.",
              path, tmain, jsonld=breadcrumb_jsonld(t_crumbs)))

    write("/about/", page(f"About | {NAME}", f"About {NAME}, a daily devotional publishing a short Bible verse, reflection, and prayer every day.", "/about/",
          f"<h1 class=\"headline\">About {NAME}</h1><p>{NAME} publishes a short daily devotional to help you start the day grounded in Scripture. Content is prepared with the help of AI tools and reviewed before publication.</p>"))
    write("/privacy/", page(f"Privacy | {NAME}", "Privacy policy for Faith Above: what we collect and how we use it.", "/privacy/",
          "<h1 class=\"headline\">Privacy Policy</h1><p>We collect your email address only if you subscribe, and use it solely to send the devotional. You can unsubscribe at any time. We use basic analytics and may use affiliate links, for which we may earn a commission at no cost to you.</p>"))
    write("/robots.txt", f"User-agent: *\nAllow: /\nSitemap: {SITE}/sitemap.xml\n")
    dates_by_slug = {p["slug"]: p["date"] for p in posts}
    def lastmod_for(u):
        slug = u.rstrip("/").rsplit("/", 1)[-1]
        return dates_by_slug.get(slug, TODAY)
    sm = "".join(f"<url><loc>{SITE}{u}</loc><lastmod>{lastmod_for(u)}</lastmod></url>" for u in urls)
    write("/sitemap.xml", f'<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">{sm}</urlset>')
    print(f"Built {len(posts)} devotionals, {len(urls)} pages -> public/")

if __name__ == "__main__":
    main()
