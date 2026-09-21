# Daily devotional generation prompt

This is the exact prompt to hand to Claude (or another LLM) every day, or to
wire into a scheduled task, so a new devotional is produced with near-zero
input from you.

---

**Prompt to send each day:**

> Write one devotional in the file format used in `content/devotionals/` for
> faithabove.com. Today's date is {{TODAY}}. Pick a topic from
> `TOPIC_CALENDAR.md` for this day of the 30-day cycle (cycle repeats
> monthly — use day-of-month modulo 30). Do not repeat a Bible verse already
> used in an existing file in `content/devotionals/`.
>
> Requirements:
> - Front matter fields: title, date ({{TODAY}}), topic, verse_ref,
>   verse_text (verse text must be the actual, accurate King James Version
>   wording — do not paraphrase or invent a translation), description
>   (one sentence, under 160 characters, for SEO).
> - Body: 250-400 words. Give real insight — historical/textual context,
>   a concrete way to apply it today, no generic filler ("in today's
>   fast-paced world..."). End with a `PRAYER:` line containing a short,
>   specific, first-person prayer (3-5 sentences).
> - Tone: warm, direct, conversational — like a thoughtful friend, not a
>   sermon or a greeting card.
> - Save the file as `content/devotionals/{{TODAY}}-{{slug}}.md` where
>   slug is a short kebab-case version of the title.
> - After saving, run `python3 build.py` and confirm it built without
>   errors, then report the file path and topic.

---

## Automating it fully (no daily prompt needed from you)

Use this environment's scheduled-task tool to create a recurring task, once,
with this prompt (adjust the repo/deploy path for wherever you end up
hosting):

> Every day at 5:00 AM America/New_York: go to the faithabove.com project
> (pull latest from its git remote if applicable). Generate one new
> devotional per the instructions in DAILY_PROMPT.md, using today's date.
> Run `python3 build.py`. Commit the new content file and the rebuilt
> `public/` folder, push to the git remote connected to the hosting
> provider (Netlify/Vercel/Cloudflare Pages auto-deploy on push), and stop.
> Do not ask for approval — this is a fully automated, low-stakes content
> task. If verse accuracy is in doubt, prefer well-known, easily verified
> KJV passages over obscure ones.

Set that scheduled task's approval mode to automatic so it doesn't stall
waiting on you, since the whole point is minimal interaction. Spot-check
the output every few days, especially early on, to make sure quality and
verse accuracy stay high — a wrong Bible quote is the fastest way to lose
credibility (and buyer confidence) in this niche.

## Weekly quality pass (recommended, ~10 min/week)

Once a week, skim the last 7 devotionals for:
- Any Bible reference or quote that reads oddly (spot-check against
  biblegateway.com)
- Repetition of the same verses/topics
- Email signup form actually working (send yourself a test signup)
- Analytics: is traffic moving, and from where (Pinterest vs. search)
