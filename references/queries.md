# Calendar discovery — query & API catalog

Ready-made sources, queries, and parsing recipes. Pair with
`scripts/extract_booking_links.py`.

## Hacker News (Algolia API — no auth, no Cloudflare, full text)

Find people who self-posted a link (query the **link string**, not the tool
name):

```
https://hn.algolia.com/api/v1/search?tags=comment&hitsPerPage=100&query=calendly.com
https://hn.algolia.com/api/v1/search?tags=comment&hitsPerPage=100&query=cal.com/
https://hn.algolia.com/api/v1/search?tags=comment&hitsPerPage=100&query=calendar.app.google
https://hn.algolia.com/api/v1/search?tags=comment&hitsPerPage=100&query=savvycal.com
https://hn.algolia.com/api/v1/search?tags=comment&hitsPerPage=100&query=meettempi.com
https://hn.algolia.com/api/v1/search?tags=comment&hitsPerPage=100&query=booktime.xyz
```

- `nbHits` = density signal before parsing.
- Parse `hit.comment_text` and `hit.story_title`; **`html.unescape` first**.
- `hit.author`, `hit.created_at`, and the story title give fit/context.
- Pull a whole thread recursively:
  `https://hn.algolia.com/api/v1/items/<objectID>` → walk `children[].text`.

Highest-yield stories (recurring monthly):
- "Ask HN: Who wants to be hired?"
- "Ask HN: Freelancer? Seeking freelancer?"
- "Ask HN: Who is hiring?"
- "Open source projects should run office hours" (thread 26351053)

Other useful comment queries: `"office hours"`, `"happy to chat"`,
`"coffee chat"`, `"grab 15 min"`, `"calendar link"`.

## Curated registries

- **fharper/coffeechat** —
  `https://raw.githubusercontent.com/fharper/coffeechat/main/people.json`
  (~54 people, ~49 live links; fields incl. `topics`, `languages`,
  `online-only`, `scheduling`). Schema at `.../schema.json`.
- Search pattern for more: GitHub repo search for
  `coffeechat`, `"office hours" in:readme`, `awesome mentors`,
  `open to chatting`.

## GitHub / GitLab

- Structured lists: fetch `raw.githubusercontent.com/<owner>/<repo>/<branch>/<path>`.
- GitLab handbook (`handbook.gitlab.com`) is process docs — no individual
  booking links. Don't mine it for links.
- Individual links live in **profile READMEs** and personal sites; web search
  surfaces the *list repos*, not the people.

## Web search phrasing (avoid brand names)

Brand names return vendor blogs / how-to pages. Use invitation phrasing:

- `"open office hours" free Zoom`
- `"grab 15 minutes"` / `"happy to chat about"`
- `"who should schedule this appointment?" anyone`
- `"no appointment needed"` / `"open to all"` / `"general public"`

Then fetch each surviving page and extract the scheduler link.

## Program / marketplace fallbacks

- **ADPList** — free 1:1 mentors, filter by skill/city (incl. AI).
- **SCORE** / **MicroMentor** — free mentoring, request-based matching.
- **SBDC** — free small-business advising; some 1:1.
- **Topmate** — paid bookable experts.
- **Office Hours** (officehours.com) — paid expert calls; strong AI/ML bench
  (ex-OpenAI/Meta/Google people), each with a "Request a call" page.
- **AI/ML specific:** AI Tinkerers meetups (demo-first, easy to talk to),
  MLOps community Slacks, university lab pages (e.g. `.edu` labs list members
  with contact pages). Many AI engineers run personal `/office-hours` pages.

## Domain-native sources (use these FIRST for non-technical topics)

For a topic like running, medicine, law, crafts, etc., go where practitioners
are — not to a dev registry.

- **Associations with a "find a club/coach/member" directory** — e.g. RRCA
  (`rrca.org/coaches`, `rrca.org/clubs`), trade guilds, professional bodies.
  Named people, often public email/contact forms.
- **The topic's subreddit / Discord / forum** — e.g. `r/running` (~4.3M),
  The Running Channel Club, Hive Index lists communities per topic. Reach via
  posts/DMs.
- **Topic newsletters & podcasts** — Substack "about" pages often have contact
  or occasional office hours.
- **Local clubs / community orgs** — public `info@` emails and contact forms
  for organizers.

Domain-native search phrases: `"find a <coach/club/expert>"`,
`<topic> association directory`, `<topic> community`, `<topic> Discord`.

**A reachable channel with no booking link is a valid result.** Don't fall back
to an off-domain registry just to produce bookable names.

## Noise denylist (reject)

`calendly.com` docs/help, `cal.com/blog|pricing|docs|enterprise|teams`,
`api-evangelist/*`, `*-cli` repos, clones, `producthunt`, `wikipedia`,
"alternatives" listicles, university how-to pages, grammar guides.

## Parsing gotchas

- **HTML entities:** `&#x2F;` = `/`. Unescape before regex or you parse nothing.
- **Cloudflare/JS pages:** plain fetches of Calendly and `claude.ai/share/...`
  return metadata/empty. Use raw or API endpoints (e.g.
  `claude.ai/api/chat_snapshots/<uuid>`).
- **Match on link shape** (must have a personal handle/slug), then check the
  handle against the author's name.

## Field numbers (Oct 2026 run)

- HN `calendly.com`: 746 hits; 100 comments → 37 unique personal links.
- HN `cal.com/`: 322 hits → 17 (mixed with blog links; filter hard).
- HN `calendar.app.google`: 21 hits → 15 unique (near-zero noise).
- HN `savvycal.com`: 14 → 1. `meettempi.com`: 0. `booktime.xyz`: 2 → 2.
- Office-hours thread: 266 comments → 5 unique links; 7/8 resolved HTTP 200.
- fharper/coffeechat: 54 people, 49 live booking links
  (Calendly 24, Google-appt 8, cal.com 8, self-hosted 3, email-only 5).
