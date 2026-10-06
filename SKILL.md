---
name: calendar-discovery-skill
description: "Find people and their publicly published booking links (Calendly, Cal.com, Google Calendar appointments, SavvyCal, Topmate, etc.) for outreach. Use when the user wants to find someone to talk to, book or schedule a call, line up problem-discovery / customer-discovery / user-research interviews for a startup, find office hours, build a cold-outreach list, or asks for a person's scheduling or booking link. Trigger even if they don't say \"booking link\": e.g. \"who can I talk to about X\", \"find me people open to chatting\", \"get me user calls\", \"find founders/users I can interview\", \"mine HN/GitHub for scheduling links\", or pastes a scheduler link to investigate. Distinct from idea-finder — that generates problem ideas; this finds the humans to validate them with. Generalizable beyond startups to any 'who can I talk to about X, and how do I book them' task."
---

# Calendar Discovery

Find people open to a conversation, and the booking link they published.

Find **specific people** who are open to a conversation on a topic, and the
**public booking link** they chose to share. Built for problem-discovery / user
calls at a startup, but generalizes to recruiting, sales, research, mentorship,
and community.

## The one big idea

**Never search for booking pages directly — they are undiscoverable by design.**
Calendly/Google appointment pages are JavaScript apps, `noindex`, and behind
Cloudflare; search engines index only vendor docs about them. So invert the
search:

> Find **people** first, then find the **place they self-published a link**,
> then extract the link.

There are only four vectors that actually yield bookable humans, in order of
precision. Search engines are best at #1 and worst at #3.

| # | Vector | Why it works | Yield |
|---|--------|--------------|-------|
| 1 | **Curated opt-in registries** | People volunteer to be bookable and pre-tag their topics | Highest precision, pre-labelled |
| 2 | **User-generated threads** where people self-post a link | Self-published, in machine-readable HTML | High volume, needs filtering |
| 3 | **Personal "office hours" / "coffee chat" pages** (blogs, READMEs, sites) | The host links their own scheduler | Low volume, high intent |
| 4 | **Bookable programs / marketplaces** (ADPList, SCORE, SBDC, Topmate) | Their job is taking strangers' bookings | Reliable but not a specific person |

GitHub/GitLab README mining mostly yields **aggregators** (vector 1), not
individual links. Treat finding a good registry as a win, not a shortcut.

## Step 0 — Define the target profile before searching

Fit is the point for problem-discovery calls. Write down:

- **Topic / domain** (e.g. "API rate limiting", "pickleball scheduling")
- **Target identity** — who counts as a match: a *domain expert*, a *target
  user*, or *an interested hobbyist*? These need different sources.
- **Role / seniority** (founder, engineer, PM, end user)
- **Company type / stage** (pre-seed, dev-tools, B2B SaaS, consumer)
- **Geography / timezone / language**
- **Online vs in-person**
- **Why them** — the fit signal you'll rank on

Do not skip this. It converts "find a booking link" into "find a bookable
person who matches X," which is the actual task.

> **Fit is not interest.** A person listing "Trail Running" among 15 hobbies is
> not a running expert nor necessarily a running target user — they're a
> software person who jogs. Only count a topic as fit when it shows up in the
> person's **professional identity / offer** (title, company, what they say
> they'll advise on), or when the **source is domain-native** (see Step 1).

## Step 1 — Source hierarchy (concrete recipes)

> **Sources carry their community's bias.** A registry of DevRel/OSS people
> tags its members with hobbies (running, cats, beer), but the people are
> still software people. Topic-tags inside a biased source match *hobbies*,
> not domain fit. Before trusting any source's tags, ask: **what is this source
> for?** If it isn't about your domain, a tag match is weak evidence — and for
> a non-technical topic, a dev-heavy registry is the wrong primary source
> entirely. Prefer **domain-native sources**: the forum, club, association, or
> marketplace for the topic itself.

### 1a. Curated opt-in registries — highest precision
Look for a repo/list of people offering their time, usually with structured
data. Known seed: **[fharper/coffeechat](https://github.com/fharper/coffeechat)**
— `people.json` (~54 people, ~49 with live booking links). Schema fields map
directly onto fit: `name, title, company, city, country, languages,
scheduling, online-only, topics[]`. Fetch the raw JSON, filter by `topics`.

Pattern to search for more: `awesome` lists, `coffeechat`, `office hours`,
`open to chatting`, `mentors` repos. `raw.githubusercontent.com` serves JSON
with no scraping.

### 1b. User-generated threads — highest volume
These are where individuals self-post their own link, often with context that
tells you their fit. Best sources and access:

- **Hacker News via the Algolia API** (no auth, no Cloudflare, full-text).
  Query the *link string itself* to find people who posted one:
  `https://hn.algolia.com/api/v1/search?tags=comment&hitsPerPage=100&query=calendly.com`
  Highest-yield stories are the recurring **"Ask HN: Who wants to be hired? /
  Freelancer? Seeking freelancer? / Who is hiring?"** monthly threads.
- **Reddit** (`old.reddit.com` / `.json`), **X/Bluesky/Mastodon bios**,
  **Substack "about" pages**, **Luma host profiles**.
- **GitHub profile bios & READMEs** (vector 3) and **personal sites'
  "book a call" pages**.

### 1c. Personal office-hours pages
Search phrasing, not brand names (brand names return vendor blogs):
`"open office hours" free`, `"grab 15 minutes"`, `"happy to chat about"`,
`"who should schedule this appointment?" anyone`. Then fetch the page and pull
the scheduler link.

This pattern is **especially common among AI/ML and indie engineers**, who run
personal `/<something>` booking pages — `/office-hours`, `/book`, `/meet`,
`/chat`, `/call`. Search `<role> office hours` / `<role> book a call` and look
for *personal sites* (`name.dev`, `name.xyz`, `github.io`) rather than vendor
pages. These are often genuine open offers ("coffee chat, anyone in X space")
and are the best non-registry source for technical domains.

### 1d. Program / marketplace fallbacks
When no individual link exists: **ADPList** (mentors by skill/city, incl. AI),
**SCORE** and **MicroMentor** (free mentoring, request-based), **SBDC**
(free business advising). Good when any qualified human works.

### 1e. Source behavior by topic type — and domain adjacency

The decisive question for any registry is **adjacency**: does this source's
community overlap your domain? A dev/DevRel registry is *domain-native* for
dev-adjacent topics (AI/ML, infra, devtools, data, security) and *biased* for
everything else. This is why the same registry yielded real AI/ML fits and zero
running fits.

| Domain | Example | Best vectors |
|---|---|---|
| Dev-adjacent technical | AI/ML, infra, devtools, data | dev registries, personal office-hours pages, HN/UGC |
| Non-adjacent technical | a niche science/engineering field | that field's forums, conferences, labs — not dev registries |
| Non-technical / consumer | running, gardening, parenting | **topic-native registries/communities** + clubs (events) |

- Dev registries: strong for dev-adjacent, misleading for anything else (a
  "Trail Running" tag on a DevRel person is not running fit).
- For non-technical topics, **clubs/communities are first-class**: usually
  **drop-in with no booking link** — the offer is a recurring event, so output a
  schedule/venue, not a scheduler URL. Don't force a link.
- HN and web search are weak for non-adjacent and non-technical topics.

### 1f. Domain-native directories & communities

The single best move for any topic is to go where the practitioners already
are, then work outward from there:

- **Association / directory "find a X"**: e.g. RRCA "find a club / coaches"
  for running, state bar for lawyers, guild/registry for a trade. These list
  named people and often public emails or contact forms.
- **The topic's subreddit / Discord / forum** (e.g. r/running, running club
  Discords) — participants are target users; reach via DMs/posts, not a link.
- **Topic-native newsletters/podcasts** (e.g. Substack writers) — often have an
  "about/contact" or occasional office hours.

These frequently yield **a reachable person but no booking link**. That's still
a win: return the best channel (email, contact form, community, coach
directory) instead.

> **"No open booking link" is a legitimate result.** Do not pad a shortlist
> with off-domain people just to have bookable names. If the domain has no
> bookable individuals, say so and hand back the reachable channels
> (organizers, coaches, communities) plus, if relevant, commercial free
> intro-calls clearly labelled.

## Step 2 — Extract and classify links

Run `scripts/extract_booking_links.py` on any text/URL. Platform shapes:

| Platform | Injectable shape |
|---|---|
| Calendly | `calendly.com/<handle>/<slug>` (bare `calendly.com/<handle>` too) |
| Cal.com | `cal.com/<handle>[/<slug>]` |
| Google appointments | `calendar.app.google/<id>` |
| Google schedules | `calendar.google.com/calendar/appointments/schedules/<id>` |
| SavvyCal | `savvycal.com/<handle>` |
| Topmate | `topmate.io/<handle>` |
| Clarity.fm | `clarity.fm/<handle>` |
| Tempi | `meettempi.com/<handle>[/<slug>]` |
| Clockwise | `getclockwise.com/c/<slug>` |
| Booktime | `booktime.xyz/p/<slug>` |
| Setmore | `<handle>.setmore.com` |
| TidyCal | `tidycal.com/<handle>` |
| Office Hours (marketplace) | `officehours.com/<handle>` |
| Self-hosted | `*.coffee`, `*/coffee`, `*/book`, `*/chat` (e.g. `fred.dev/coffee`) |

**Noise filter (critical).** Reject anything without a personal handle/slug:
- `cal.com/blog/...`, `/pricing`, `/docs`, `producthunt`, "alternatives",
  grammar guides, university how-to pages, Wikipedia.
- Repos/docs *about* schedulers (`calendly-cli`, `api-evangelist`, clones).
- **Handle should plausibly match the author's name.** People sharing their
  own link match; people discussing the tool almost never do.

**Gotcha:** HN and many APIs store link HTML entity-encoded
(`https:&#x2F;&#x2F;calendly.com&#x2F;<handle>&#x2F;<slug>`). Run `html.unescape`
*before* regex, or you'll parse zero links (a real bug from the field notes).

**Booking may be behind a gateway.** The script extracts only *direct* scheduler
URLs. A link can instead be exposed via a chatbot/assistant, a contact form, or
a DM ("say you'd like to book and I'll share my link"). When you find no link
but the person is clearly open, record the **gateway** (assistant, form, DM,
email) as the channel and say so — don't drop the person.

## Step 3 — Gate for fit (the reason this exists)

**First, the hard gate — domain alignment.** A candidate only proceeds if at
least one holds:

- **Professional alignment:** the topic appears in their **title, company,
  role, or stated offer** ("run coach", "founder of a running app", "I advise
  on X"), or
- **Domain-native source:** the source itself is about the domain, so the
  person's presence there implies topical relevance, or
- **Target-user alignment:** their *context* (the post they wrote) shows
  they're the user you want to learn from, not merely a fan of the topic.

**A hobby in a topic list is NOT alignment.** Drop it (or mark it explicitly as
weak). A DevRel engineer listing "Trail Running" is neither a running expert
nor a running target user — don't spend a discovery call there.

**Match roles, not substrings.** Tokenize and use word boundaries: `search`
matches "re**search**er" (a cybersecurity person wrongly passed the AI gate in
testing). Prefer role tokens (`ml engineer`, `ai`, `llm`, `data scientist`) and
confirm with the title/company, not a grep hit.

**Tie-break for adjacent sources.** When the source is domain-adjacent but the
person's title is generic (e.g. a "Tech Lead" listing AI/ML, an "AWS Solutions
Architect" tagging MLOps), the topic tag is *medium* evidence: keep it, but mark
`needs qualification — adjacent` and confirm in outreach. Never rank it above a
title/company match, and never let it sit unqualified in the shortlist. Non-
adjacent + hobby tag = reject.

Then rank the survivors:
1. **Professional alignment** (title/company/offer matches the domain) — top.
2. **Domain-native source + self-described offer** — strong.
3. **Contextual intent** — the surrounding text: *inviting* ("grab 15 min",
   "office hours") vs *marketing/opinion*.
4. **Language, location/timezone, online-only.**
5. **Link live and open to strangers** (Step 4).

Output a *funnel*: candidates → hard gate (domain alignment) → fit-scored
shortlist → confirmed bookable. **Report the rejections too** — especially
tech/DevRel people surfaced by a biased registry, so the user can see the gate
working. If everything on the shortlist is from a source whose community is
unrelated to the topic, say so: the result is "wrong source", not "good fit".

## Step 4 — Verify live & open (cheap, low-effort)

- Resolve the link (HTTP status). In experiments 7/8 office-hour links resolved
  200. Treat a hard 404 as dead; a 200 does **not** guarantee an open calendar.
- Classify **open to strangers** vs **gated** (own students/customers/company).
  Drop gated ones unless the user is in that group.
- **Beware the sales funnel — and the word "discovery."** A coach/consultant's
  "Book a free call", "free intro session", or even "**Discovery Call**" /
  "AI Employee Discovery Call" is lead-gen, not an open offer: the exact word
  you use for your goal is a sales label too. Judge by **who benefits** (vendor
  pipeline vs. peer research) and mark it **commercial**, not open-to-strangers,
  unless the user actually wants to buy a service.
- **Do not over-invest in reading calendar slots.** The user's stance: slot
  exposure is secondary; basic fit + a working link is enough. Live slot reading
  needs the scheduler's API (Tempi, Cal.com, OpenCalendar) and Calendly/Google
  pages don't expose slots to a plain fetch. Prefer to just hand over the link.

## Step 5 — Respect the person (non-negotiable)

The whole approach is "index only what people chose to publish":

- Index **only** the booking link + the display name/topics they shared.
- **Never** scrape or store busy/free data, and don't build a calendar
  database. No precrawling of calendars.
- Skip anything login-gated.
- Rate-limit queries; **no bulk export**; honor removal requests.
- Prefer **ad-hoc, on-demand** lookup over a standing crawl.
- For outreach, send a note: who you are, the specific thing you want to learn,
  a 15-min window, and no sales angle.

## Step 6 — Output format

Return a table, one row per candidate:

| person | title / company | fit (topic match) | booking link / channel | platform | status (open/gated/commercial/gateway) | source-url |
|---|---|---|---|---|---|---|

Use `source-url` so every row is traceable. For problem-discovery, add a
`why-them` note. Keep it to a short ranked list, not a dump.

## Tooling notes

- **HN:** Algolia API is the cleanest corpus — `search?tags=comment&query=...`.
  `nbHits` tells you density before you parse. Unescape HTML. Dig into a thread
  with `items/<id>` (recursive `children`).
- **GitHub:** `raw.githubusercontent.com/<owner>/<repo>/<branch>/<file>` for
  structured data; the search API for repos, but code search needs auth.
- **webfetch caveat:** JS-rendered pages (Calendly, Google appointments) and
  Cloudflare-protected APIs return empty/metadata. Prefer a raw/API endpoint.
  Example: a claude.ai/share link has no content in the page HTML, but
  `claude.ai/api/chat_snapshots/<uuid>` returns the full conversation JSON.
- **Script:** `scripts/extract_booking_links.py <file-or-url> [--check]`.
- **Query catalog:** `references/queries.md`.

## Field evidence (why the ranking above)

- Direct search for individual READMEs → almost all vendor/clone noise; the
  yield came from one aggregator repo (fharper/coffeechat, 54 people).
- HN full-text: `calendly.com` = 746 hits; scanning 100 comments → 37 unique
  personal links. `calendar.app.google` = only 21 hits but 15 unique links
  (near-zero noise). `meettempi.com` = 0. Raw search engines = vendor blogs.
- Conclusion: **aggregators + UGC threads > web search; match on link shape,
  not keywords.**
- Calibration by domain (same method, same seed registry): **AI/ML** is
  dev-adjacent → registry tags are real fits, plus many native personal
  `/office-hours` pages → direct yield. **Running** is non-adjacent → every
  registry "match" was a hobby tag, and zero open bookable individuals existed;
  correct output was clubs/communities + labelled commercial coaches. Expect
  dense vs. sparse yield accordingly, and report the honest zero.

## Checklist

- [ ] Target profile written (topic/domain, **target identity**, role, stage,
      geo, language, online).
- [ ] Classify the domain: dev-adjacent / non-adjacent technical / non-technical
      — pick sources accordingly (§1e).
- [ ] Check registry **adjacency** before trusting its topic tags.
- [ ] Search domain-native sources: personal office-hours pages,
      associations/communities, topic marketplaces — not just dev registries.
- [ ] Mine UGC threads (HN Algolia, Reddit, X/Substack) where relevant.
- [ ] For each hit, extract link; `html.unescape` first; note any gateway.
- [ ] Reject non-personal / vendor / docs links; confirm handle↔name.
- [ ] Apply the **hard gate** (professional alignment / domain-native source /
      target-user context) — no hobby tags, no substring matches; mark adjacent
      cases "needs qualification."
- [ ] Verify link resolves; mark open / gated / commercial.
- [ ] Respect rules applied (no slot scraping, no bulk export).
- [ ] Output ranked table with source URLs + why-them. **"No open link" is a
      valid result** — hand back reachable channels instead of padding with
      off-domain names.
