# Using a vault

`constitution.md` is the operating law, and it is written for Claude. This document is
written for you: what a normal session looks like once `cairn init` has run, what to say,
and what to leave alone.

## The one thing to internalize

**You own `raw/`. Claude owns `wiki/`.**

You dump things into `raw/` in whatever shape they arrive — a pasted link, half a
thought, a downloaded PDF. You never organize it. Compiling is what turns that pile into
summarized, categorized, cross-linked notes in `wiki/`, and that is Claude's job, not
yours.

Everything below is a consequence of that split.

## Say it, don't type it

There is no `cairn` executable. The actions you invoke most are **things you say to
Claude** inside a session in the vault directory. A few genuinely are shell commands.
Keeping these straight is most of the learning curve:

| You want to | Kind | What you do |
|---|---|---|
| File your raw material into the wiki | say | `compile` |
| Health-check the vault | say | `lint` |
| Ask a question of your own knowledge | say | just ask it |
| Capture a link or thought | say | just say it |
| Check project status | say | "what's active?" / "what's stalled?" |
| Create another vault | say | `cairn init <path>` |
| Run the deterministic linter alone | **shell** | `python3 system/cairn/bin/lint-scan.py .` |
| Refresh the engine | **shell** | `sh system/cairn/bin/cairn-update.sh <cairn-repo> . --apply` |

Typing `compile` at a shell prompt does nothing bad. You'll get `command not found`.

## Starting a session

```sh
cd ~/Projects/your-vault
claude
```

Start Claude **inside the vault**, not in its parent. The vault's `CLAUDE.md` points the
session at the constitution, the profile, and the lexicon, and that only loads if the
vault is the working directory.

If your vault is on more than one machine, `git pull` first and push when you're done.
Never run compile or lint on two machines at once.

## The five behaviors, in practice

Three of these have skills behind them. Two are just conversation — which is the part
that isn't obvious.

### Ingest — capture something (no skill; just talk)

Mid-conversation, hand Claude a link, a file, or a stray thought and say to hang onto it.
It gets appended to `raw/inbox.md` with today's date and a one-line note of context, or
saved into `raw/clips/` if it's a file. It sits there until the next compile.

You can also just open `raw/inbox.md` and type into it. That's the same thing. Dump
freely — no formatting rules, no need to categorize.

### Compile — turn raw into wiki (skill: `kb-compile`)

> compile

This is the workhorse. It reads your profile, does the terms pass first, then for each
unprocessed item: reads it fully, picks a domain and type **from your profile**, writes a
note from the matching template with a summary in Claude's own words, links it into
related notes with a `## Connections` section, regenerates `wiki/index.md`, moves the
processed items into `raw/_processed/`, clears the handled entries out of `inbox.md`,
logs a row, and commits.

Run it whenever raw has piled up. There is no penalty for running it often, and running
it on an empty inbox just logs a heartbeat.

**Related phrasings that hit the same skill:** "process the inbox", "file my clips",
"sweep raw", "I updated my key terms".

### Answer — ask your own knowledge base (no skill; just ask)

Ask a question in plain language. The session reads `wiki/lexicon.md` first so your
loaded words mean what you mean, then walks `wiki/index.md` and follows links, and
answers **citing the notes it used**. If the wiki doesn't know, it says so rather than
guessing, and offers to research and compile the findings in.

Anything substantial it produces should land as a file — a wiki note or something in
`outputs/` — and get linked in, so the next answer is better than this one.

### Manage — projects (no skill; just ask)

If your profile declares a `project` type, ask things like "what's active?", "what's
blocked?", "what haven't I touched?". Projects with no update inside
`stale_project_days` (default 14) get flagged as stale.

### Lint — health check (skill: `kb-lint`)

> lint

Two halves. The deterministic half is `bin/lint-scan.py` — schema violations, undeclared
domains and types, broken links, orphans, stale projects, lexicon drift. The judgment
half needs actual reading: contradictions between notes, gaps worth filling, cross-domain
connections worth surfacing.

It writes a dated report to `system/lint-reports/YYYY-MM-DD.md`, logs, and commits.
Mechanical problems get fixed directly; contradictions in your content get **reported**,
never silently resolved. That's your call to make.

Compile, then lint, is the natural pairing.

## Reading severity

The linter's three levels mean different things, and only two are work:

- **error** — actually broken. Broken links, undeclared domains, schema violations. Fix.
- **warn** — probably wrong, wants your eye. Orphans, stale projects, notes filed under
  the wrong domain.
- **info** — **not problems.** Tag candidates and unused concepts are *queues*, not a
  backlog. A tag used on ten notes with no concept note isn't debt — it's the linter
  noticing a word carries weight for you and asking whether you want to define it. Ignore
  them indefinitely if you like. Never "fix" one by deleting something.

## Teaching the vault your vocabulary

Some words mean something specific in your world. `raw/key-terms.md` is where you say so,
and it's the highest-leverage file in the vault — it's what makes answers sound like your
domain instead of a dictionary's.

Three ways in, one place it lives:

1. **Edit `raw/key-terms.md`** — the curated glossary, bulk edits, whenever you want.
2. **`[define] term — meaning`** on a line in `raw/inbox.md` — capture in the moment.
3. **Say it mid-conversation** — "when I say X, I mean Y" — and Claude writes a
   `[define]` line into the inbox for you.

The next compile turns each into a concept note in `wiki/concepts/` and regenerates the
one-line-per-term `wiki/lexicon.md`.

Spend your effort on `aliases:`. Without them, recognition only fires on exact matches
and the whole mechanism looks broken.

Unlike `inbox.md`, `key-terms.md` is a **standing file**. It is never cleared and never
moved to `_processed/`. Editing a term updates its note; removing a term archives the
note rather than deleting it.

## What not to do

**Don't organize `raw/`.** Don't rename, sort, or tidy it. Dumping is the whole point,
and the compiler is what imposes order. The only thing that moves items out is compile.

**Don't edit anything under `system/cairn/` or `.claude/skills/`.** These are vendored
engine copies, replaced wholesale on update — your edit is silently destroyed the next
time you refresh. Engine fixes go upstream to the cairn repo, then come back through
`cairn-update.sh`. The update script refuses to run when it detects drift here, which is
the guardrail, not an obstacle.

**Don't hand-edit `wiki/lexicon.md`.** It's regenerated from the concept notes on every
compile. Edit the term in `raw/key-terms.md` instead.

**Don't hand-edit `wiki/index.md`.** Same reason — regenerated from your profile plus
what's on disk.

**Don't ask Claude to edit `raw/key-terms.md`.** That file is yours to curate. Claude
proposes additions and you copy them in. This is deliberate: it's the one file where your
exact wording matters more than tidiness.

**Don't delete wiki notes to clean up.** Nothing in a vault is destroyed. Notes get
superseded in place or marked `status: archived`. Deletion requires your explicit
per-file approval, and it should stay rare.

**Don't remove a domain or type from `system/vault-profile.yml` casually.** Every
existing note using it instantly becomes a lint error. Adding is cheap; removing is a
migration.

**Don't expect anything to be pushed anywhere.** Privacy is the default — nothing leaves
the vault for any remote or service unless you explicitly ask. If you want a remote, you
configure it yourself; `cairn init` deliberately doesn't.

### Editing `wiki/` by hand

Allowed, just not the normal path. `wiki/` is Claude's territory and you should mostly
read it — but if you do edit a note, that edit is **authoritative**: it gets preserved,
never reverted.

One narrow exception, and it's never silent: if `raw/key-terms.md` disagrees with a
hand-edit inside a concept note, key-terms.md wins — it's the more recent deliberate
statement. Your prior text is kept under `## History` and the overwrite is reported to
you.

## A normal week

There's no required cadence. A vault *may* schedule a recurring compile + lint, and if it
does, that's declared in the vault's own `CLAUDE.md` — the engine assumes nothing.

Absent that, the rhythm that works:

- **As things come up** — capture. Say it to Claude, or type into `raw/inbox.md`. Seconds.
- **When raw has piled up** — `compile`. The pile becomes linked notes.
- **After a compile, or weekly** — `lint`. Read the errors and warns; let the infos sit.
- **Whenever you need to know something** — just ask, and let substantial answers become
  files so they compound.
- **Occasionally** — edit `raw/key-terms.md` when you notice you've explained the same
  word twice.

## Where things live

| Path | Yours or Claude's | What it's for |
|---|---|---|
| `raw/inbox.md` | **Yours** | Dump zone. Cleared by compile. |
| `raw/key-terms.md` | **Yours** | Glossary. Standing file, never cleared. |
| `raw/clips/` | **Yours** | Dropped files and articles. |
| `raw/_processed/` | Compiler | Audit trail of what's been ingested. |
| `wiki/index.md` | Compiler | The map. Everything is reachable from here. |
| `wiki/<domain>/` | Claude | Your notes, one directory per declared domain. |
| `wiki/concepts/` | Compiler | One note per key term. |
| `wiki/lexicon.md` | Compiler | Generated term registry. |
| `outputs/` | Claude | Deliverables — reports, decks, charts. |
| `system/vault-profile.yml` | **Yours** | Domains, types, conventions. |
| `system/templates/` | **Yours** | Your template overrides. |
| `system/cairn/` | **Engine** | Vendored. Never edit. |
| `system/lint-reports/` | Linter | Dated health checks. |
| `system/log.md` | Claude | Run history. |
| `CLAUDE.md` | **Yours** | Vault-specific instructions. |

## When something looks wrong

**"It filed a note in the wrong place."** Say so. Domain and type come from your profile,
and if notes keep landing wrong, the profile's domain `purpose` lines are probably too
vague — that's what Claude is choosing from.

**"It doesn't know a term I've used for months."** It's not in `raw/key-terms.md`, or it
is but your `aliases:` don't cover how you actually phrase it.

**"Compile didn't pick up my file."** Check it's in `raw/clips/` or referenced from
`raw/inbox.md`, and that it isn't already sitting in `raw/_processed/` from an earlier
run.

**"The update script refuses to run."** You edited something under `system/cairn/` or
`.claude/skills/`. That's the drift guard doing its job. Commit or discard the change,
and move the actual fix upstream to the cairn repo.

**Nothing was reported at all.** That's a bug, not a quiet success. A run that finds
nothing still logs a heartbeat row and commits — silence is never supposed to be
indistinguishable from failure.
