# Faith Above — daily devotional site

A fast, static, AI-content site built to run itself. No database, no CMS,
no monthly hosting cost required.

## What's here

- `build.py` — the entire site generator (pure Python, no dependencies).
  Reads every `content/devotionals/*.md` file and outputs a full static
  site into `public/`.
- `content/devotionals/` — 5 seed devotionals (today + next 4 days) so the
  site launches with real content instead of an empty shell.
- `TOPIC_CALENDAR.md` — the 30-day rotation of topics to keep content
  varied and search-relevant.
- `DAILY_PROMPT.md` — the exact prompt to automate daily content
  generation with little to no interaction from you.

## Launch in the next 20 minutes

1. **Domain:** point faithabove.com's DNS at your host (step 3).
2. **Email capture:** sign up for a free Buttondown or MailerLite account,
   grab your embed form URL, and paste it into the `FORM_ACTION` variable
   at the top of `build.py`.
3. **Hosting (free, fast):**
   - Create a GitHub repo, push this folder.
   - Connect it to Netlify, Vercel, or Cloudflare Pages (all free tiers).
   - Build command: `python3 build.py` — Publish directory: `public`.
   - Point faithabove.com's DNS at the host (each gives you exact records).
4. **Analytics:** create a free Google Analytics 4 property, paste the
   measurement ID into `GA_ID` in `build.py`.
5. Push. Site is live in a few minutes.

## Running daily content on autopilot

See `DAILY_PROMPT.md`. The short version: set up one scheduled task (daily,
early morning) that generates one new devotional, rebuilds the site, and
pushes to git — which triggers an automatic redeploy on Netlify/Vercel/
Cloudflare Pages. After the initial setup, this runs with no input from you
beyond an occasional spot-check.

## Monetization (needed to hit a $20k+ sale)

A brand-new site with zero revenue sells for domain value only — a few
hundred to low thousands. To reach $20k+, you need $500-650+/month in
verified profit sustained for several months (sites in this niche
typically sell at 30-40x monthly net profit). Add these once traffic
starts:

- **Affiliate links** in devotional bodies to relevant products (Bible
  study books, journals, "verse of the day" apps) via Amazon Associates
  or a Christian-retail affiliate program.
- **Email list monetization** — sponsorships or affiliate promos sent to
  your subscriber list once it's a few thousand people; buyers pay a
  premium for an owned list, not just pageviews.
- **Display ads** (Ezoic or Mediavine once you hit their traffic
  minimums) once you have meaningful pageviews.

## Traffic

- **Pinterest** is normally the fastest channel in this niche — pin a
  simple graphic per devotional linking back to the page.
- **SEO** compounds slower but is more durable — the topic pages
  (`/topic/strength/`, etc.) exist specifically to rank for
  "bible verses for strength"-style searches.

## Selling it

Once you have 3-6 months of verifiable profit (Stripe/affiliate dashboard
screenshots, GA4 traffic history, clean records), list it on Empire
Flippers, Flippa, or MicroAcquire/Acquire.com. Buyers will want to see the
content isn't personally dependent on you — the daily-automation setup
here is actually a selling point, since a buyer can keep it running with
minimal work themselves.
