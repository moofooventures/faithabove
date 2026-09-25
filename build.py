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
:root{--bg:#FBF7EE;--card:#fff;--ink:#181A2E;--muted:#5C5A6E;--line:#E9E3D3;--navy:#13188C;--navy-dk:#0B0C55;--gold:#D8A62B;--gold-dk:#B5871A}
*{box-sizing:border-box}
html{-webkit-text-size-adjust:100%}
body{margin:0;background:var(--bg);color:var(--ink);font:16px/1.65 'Inter',system-ui,-apple-system,sans-serif}
h1,h2,h3{font-family:'Lora',Georgia,serif;font-weight:700;line-height:1.18;margin:0 0 .35em;color:var(--ink)}
a{color:inherit;text-decoration:none}
.wrap{max-width:740px;margin:0 auto;padding:0 20px}

.topstrip{background:var(--navy);height:6px;background-image:linear-gradient(90deg,var(--navy) 0%,var(--navy) 60%,var(--gold) 60%,var(--gold) 100%)}
header.site{border-bottom:3px solid var(--ink);background:var(--card)}
header.site .wrap{padding:36px 20px 22px;text-align:center}
.brand{display:inline-block}
.brand img{height:76px;width:auto;display:block;margin:0 auto}
.tagline{color:var(--muted);font-size:14.5px;margin-top:12px;font-style:italic;font-family:'Lora',Georgia,serif}
nav.main{display:flex;justify-content:center;gap:0;margin-top:22px;font-size:13px;letter-spacing:.06em;text-transform:uppercase;font-weight:700;background:var(--navy)}
nav.main a{color:#fff;padding:12px 22px;border-right:1px solid rgba(255,255,255,.15)}
nav.main a:first-child{border-left:1px solid rgba(255,255,255,.15)}
nav.main a:hover{background:var(--gold);color:var(--ink)}

main{padding:44px 0 64px}

.crumbs{font-size:13px;color:var(--muted);margin:0 0 20px}
.crumbs a{text-decoration:underline}
.crumbs a:hover{color:var(--navy)}

.tag{display:inline-block;background:var(--navy);color:#fff;font-size:11.5px;font-weight:800;letter-spacing:.08em;text-transform:uppercase;padding:5px 10px;border-radius:3px}

.verse-card{background:var(--navy);color:#F5EFE6;padding:34px 30px;margin:24px 0 32px;border-radius:4px;position:relative;border-left:6px solid var(--gold);box-shadow:0 8px 24px -8px rgba(19,24,140,.4)}
.verse-card p{font-family:'Lora',Georgia,serif;font-style:italic;font-size:clamp(20px,3.2vw,25px);line-height:1.5;margin:0}
.verse-card .ref{display:block;margin-top:18px;font-size:12.5px;font-weight:800;letter-spacing:.1em;text-transform:uppercase;color:var(--gold)}

article.post .article-head{margin-bottom:6px}
.meta{color:var(--muted);font-size:13px;margin-top:8px;font-weight:600}
h1.headline{font-size:clamp(30px,5.8vw,42px);margin-top:.3em}
h2{font-size:21px;margin-top:1.8em;padding-top:1.2em;border-top:2px solid var(--gold);color:var(--navy)}
p{margin:0 0 1.15em}
.prayer{background:#EEF0FF;border-left:4px solid var(--navy);padding:18px 22px;font-style:italic;border-radius:0 4px 4px 0}

.section-title{display:flex;align-items:center;gap:10px;font-size:13px;font-weight:800;letter-spacing:.1em;text-transform:uppercase;color:var(--navy);margin:42px 0 18px}
.section-title::after{content:'';flex:1;height:3px;background:var(--gold)}

.list{display:flex;flex-direction:column}
.item{padding:22px 0;border-bottom:1px solid var(--line);transition:padding-left .15s}
.item:first-child{padding-top:0}
.item:hover{padding-left:8px;border-bottom-color:var(--gold)}
.item .tag{margin-bottom:8px}
.item h3{font-size:20px;margin:4px 0 6px;line-height:1.3}
.item .desc{color:var(--muted);font-size:14.5px;margin:0}
.item .date{color:var(--muted);font-size:12.5px;margin-left:8px;font-weight:600;text-transform:none;letter-spacing:0;background:none;padding:0}

.intro{margin-bottom:6px;padding-bottom:30px;border-bottom:3px double var(--line)}
.intro .tag{margin-bottom:10px}
.intro h1{font-size:clamp(28px,5.5vw,38px)}
.intro .dek{color:var(--muted);font-size:16.5px;margin:10px 0 0}
.byline{color:var(--gold-dk);font-size:12.5px;letter-spacing:.06em;text-transform:uppercase;font-weight:800}

.signup{background:var(--navy);border-radius:6px;padding:30px 26px;margin:46px 0 8px;text-align:center;box-shadow:0 10px 30px -12px rgba(19,24,140,.5)}
.signup h2{font-size:20px;margin:0 0 6px;color:#fff}
.signup p{color:#C7CAF0;margin:0;font-size:14px}
.signup form{display:flex;gap:8px;margin-top:18px;max-width:380px;margin-left:auto;margin-right:auto}
.signup input[type=email]{flex:1;padding:12px 14px;border:0;border-radius:4px;font-size:15px;font-family:inherit}
.signup button{padding:12px 20px;background:var(--gold);color:var(--ink);border:0;border-radius:4px;font-size:13px;font-weight:800;letter-spacing:.04em;text-transform:uppercase;cursor:pointer}
.signup button:hover{background:var(--gold-dk);color:#fff}

footer{border-top:1px solid var(--line);color:var(--muted);font-size:13px;padding:34px 20px 54px;background:var(--ink);color:#B9B7C9}
footer .wrap{text-align:center}
footer a{color:#fff;text-decoration:underline}
"""
FONT_LINK = ('<link rel="preconnect" href="https://fonts.googleapis.com">'
             '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>'
             '<link href="https://fonts.googleapis.com/css2?family=Lora:wght@500;600;700&family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">')

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

def signup():
    return f'''<div class="signup"><h2>Get today's devotional by email</h2>
<p>One verse, one short reflection, one prayer. Free, no spam.</p>
<form action="{FORM_ACTION}" method="post" target="_blank">
<input type="email" name="email" placeholder="Your email" required> <button type="submit">Subscribe</button></form></div>'''

def nav():
    head = f'''<div class="topstrip"></div><header class="site"><div class="wrap">
<a class="brand" href="/"><img src="/assets/logo.png" alt="{esc(NAME)}" width="400" height="118"></a>
<div class="tagline">{TAGLINE}</div>
</div><nav class="main"><a href="/">Home</a><a href="/devotionals/">Devotionals</a><a href="/about/">About</a></nav></header>'''
    return head

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
<link rel="canonical" href="{url}"><link rel="icon" type="image/png" href="/assets/logo.png">{FONT_LINK}<style>{CSS}</style>{social}{jsonld}{ga}</head><body>
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

def item(p):
    return f'''<div class="item">{tag(p.get("topic",""))}<span class="date">&middot; {esc(p["date"])}</span>
<h3><a href="/devotional/{p["slug"]}/">{esc(p["title"])}</a></h3>
<p class="desc">{esc(p.get("description",""))}</p></div>'''

def main():
    shutil.rmtree("public", ignore_errors=True)
    if os.path.isdir("content/assets"):
        shutil.copytree("content/assets", "public/assets")
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
            related_html = ('<div class="section-title">Related Devotionals</div><div class="list">'
                             + "".join(item(x) for x in related) + "</div>")
        content = f'''<article class="post">
{breadcrumb_html(crumbs)}
<div class="article-head">{tag(topic)}<p class="meta">{esc(p["date"])}</p></div>
<h1 class="headline">{esc(p["title"])}</h1>
<div class="verse-card"><p>{esc(p["verse_text"])}</p><span class="ref">{esc(p["verse_ref"])} &middot; KJV</span></div>
{md(p["body"])}
{related_html}
{signup()}
</article>'''
        page_jsonld = article_jsonld(p) + breadcrumb_jsonld(crumbs)
        write(path, page(f'{p["title"]} | {NAME}', p.get("description", p["title"]), path, content,
                          jsonld=page_jsonld, og_type="article"))

    latest = posts[:1]
    rest = posts[1:]

    if latest:
        lp = latest[0]
        lead = f'''<div class="intro">{tag(lp.get("topic",""))}
<p class="byline">Today&rsquo;s Devotional &middot; {esc(lp["date"])}</p>
<h1><a href="/devotional/{lp["slug"]}/">{esc(lp["title"])}</a></h1>
<p class="dek">{esc(lp.get("description",""))}</p></div>'''
    else:
        lead = ""

    list_html = ('<div class="section-title">Recent Devotionals</div><div class="list">'
                 + "".join(item(p) for p in rest[:10]) + "</div>") if rest else ""
    home_main = f'{lead}{list_html}{signup()}'

    write("/", page(f"{NAME} | Daily Bible Verse and Devotional", TAGLINE, "/", home_main,
                     jsonld=website_jsonld()))

    devo_crumbs = [("Home", "/"), ("Devotionals", None)]
    devo_main = (breadcrumb_html(devo_crumbs) + '<h1 class="headline">All Devotionals</h1><div class="list">'
                 + "".join(item(p) for p in posts) + "</div>")
    write("/devotionals/", page(f"All Devotionals | {NAME}", "Browse every daily devotional, sorted by newest first.",
          "/devotionals/", devo_main, jsonld=breadcrumb_jsonld(devo_crumbs)))

    topics = sorted({p.get("topic", "") for p in posts if p.get("topic")})
    for t in topics:
        tslug = re.sub(r"[^a-z0-9]+", "-", t.lower()).strip("-")
        path = f"/topic/{tslug}/"; urls.append(path)
        t_crumbs = [("Home", "/"), ("Devotionals", "/devotionals/"), (t, None)]
        tmain = (breadcrumb_html(t_crumbs) + f'<h1 class="headline">{esc(t)} Devotionals</h1><div class="list">'
                 + "".join(item(p) for p in posts if p.get("topic") == t) + "</div>")
        write(path, page(f"Bible Verses and Devotionals on {t} | {NAME}",
              f"Daily devotionals, bible verses, and prayers about {t.lower()} to encourage you today.",
              path, tmain, jsonld=breadcrumb_jsonld(t_crumbs)))

    write("/about/", page(f"About | {NAME}", f"About {NAME}, a daily devotional publishing a short Bible verse, reflection, and prayer every day.", "/about/",
          f'<h1 class="headline">About {NAME}</h1><p>{NAME} publishes a short daily devotional to help you start the day grounded in Scripture. Content is prepared with the help of AI tools and reviewed before publication.</p>'))
    write("/privacy/", page(f"Privacy | {NAME}", "Privacy policy for Faith Above: what we collect and how we use it.", "/privacy/",
          '<h1 class="headline">Privacy Policy</h1><p>We collect your email address only if you subscribe, and use it solely to send the devotional. You can unsubscribe at any time. We use basic analytics and may use affiliate links, for which we may earn a commission at no cost to you.</p>'))
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
