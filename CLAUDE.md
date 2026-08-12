# CLAUDE.md — Life OS Constitution (Plumbing Vault)

> **This is an isolated test bench, not the real vault.** It carries the structure and
> the key-terms/lexicon mechanism, and nothing else — no personal content, no financial
> data, no shared git history with the primary Life OS repo. It exists so the terms pass
> can be exercised on a work machine safely.
>
> **Never configure a remote that points at the primary `life-os` repo, and never
> pull from or push to it.** Terms written here move home by copy-paste, not by git.
> The two vaults must stay permanently unlinked.

This folder is B.J.'s personal knowledge base ("Life OS"), modeled on Andrej Karpathy's LLM knowledge base workflow. Any Claude session (Cowork, Claude Code, or scheduled task) operating in this folder follows this document. When in doubt, this file wins.

**The system in one sentence:** B.J. dumps raw material into `raw/`; Claude compiles it into an interlinked markdown wiki, answers questions from it, manages projects with it, and lints it — so the knowledge base compounds over time.

---

## Golden rules

1. **`raw/` is human territory.** Never reorganize, rename, or edit raw items. The only permitted operation is the compiler moving fully-ingested items into `raw/_processed/`. `raw/key-terms.md` is a *standing* file — read every run, never cleared, never moved, never edited by Claude.
2. **`wiki/` is AI territory.** Claude creates, updates, links, and maintains wiki notes. B.J. reads them and rarely edits — but if a human edit is found, it is authoritative: preserve it, never revert it.
3. **Files over chat.** Substantial answers, analyses, and deliverables become files (a wiki note or an item in `outputs/`), not just chat text — then get linked into the wiki so they compound.
4. **Plain text, no magic.** Markdown files, wikilinks, and a good index. No vector databases, no RAG, no hidden state. To find things: read `wiki/index.md`, follow links.
5. **Never destroy knowledge.** Don't delete wiki notes; supersede them (update in place) or mark them `status: archived` in frontmatter. Deletions only with B.J.'s explicit per-file approval.
6. **Every run leaves a trail.** System-level operations (compile, lint, migrations) append a row to `system/log.md` and end with a git commit.
7. **Privacy default.** Nothing in this vault is pushed to any remote, service, or third party unless B.J. explicitly asks.

---

## Folder map

| Path | Owner | Purpose |
|---|---|---|
| `raw/inbox.md` | Human | Quick captures, pasted links, stray thoughts |
| `raw/key-terms.md` | Human | Glossary of loaded terms — standing file, edit anytime |
| `raw/clips/` | Human (via web clipper) | Clipped articles + images |
| `raw/_processed/` | Compiler | Ingested raw items (audit trail; never re-compile) |
| `wiki/index.md` | Compiler | Master map of content — every note reachable from here |
| `wiki/reference/concepts/` | Compiler | One note per key term — the canonical definition store |
| `wiki/reference/lexicon.md` | Compiler | Generated term registry (never hand-edit) |
| `wiki/vision/` | AI | Visions, goals, yearly/quarterly plans |
| `wiki/projects/` | AI | One note per project + `projects-dashboard.md` |
| `wiki/research/` | AI | Compiled articles, topic syntheses, weekly digests |
| `wiki/health/` | AI | Body comp, training, and nutrition *insights* (not raw data) |
| `wiki/reference/` | AI | People, decisions, ideas, household, commitments |
| `outputs/` | AI | Generated deliverables: reports, decks, charts |
| `system/templates/` | Shared | Note templates (edit only with B.J.'s approval) |
| `system/lint-reports/` | Linter | Dated health-check reports |
| `system/log.md` | AI | Run history |
| `system/bin/` | Shared | Helper scripts |

---

## Note conventions

**Filenames:** kebab-case, descriptive, no dates in names (dates live in frontmatter). Example: `karpathy-llm-knowledge-bases.md`.

**Links:** Obsidian-style wikilinks `[[note-name]]`. Every wiki note must be reachable from `wiki/index.md` (directly or via links) — orphans are lint errors. Notes end with a `## Connections` section linking related notes.

**Dates:** ISO format `YYYY-MM-DD` everywhere.

**Frontmatter (required on every wiki note):**

```yaml
---
type: article        # see registry below
domain: research     # vision | projects | research | health | reference
created: 2026-07-15
updated: 2026-07-15  # bump on every edit
tags: []
---
```

**Type registry** (extend only with B.J.'s approval):
`vision` `goal` `project` `article` `synthesis` `digest` `person` `decision` `idea` `reference` `concept` `report` `health-insight` `index`

Type-specific required keys: `article` → `source`, `author`, `clipped`; `project` → `status` (active|waiting|someday|done|archived), `goal` (link); `vision` → `horizon`; `goal` → `vision` (link), `target-date`; `concept` → `aliases`, `source` (key-terms.md|inbox|conversation), `status` (active|archived).

Templates in `system/templates/` are the canonical shapes — use them.

---

## Terms & concepts (the lexicon)

Some words carry meaning here that a dictionary won't give you. The lexicon is how the
vault remembers that. **Three ways in, one place it lives.**

**Inputs (all human, all in `raw/`):**

1. `raw/key-terms.md` — the curated glossary. Bulk edits, whenever B.J. wants.
2. `[define] term — meaning` lines in `raw/inbox.md` — in-the-moment capture.
3. Mid-conversation — B.J. says "when I say X, I mean Y" → Ingest writes a `[define]` line.

**The store:** one `type: concept` note per term in `wiki/reference/concepts/`. This is
the only authoritative copy. It's linkable (`[[the-place]]`), supersedable, and lints
like any other note.

**The views (derived, regenerated every compile — never hand-edited):**

- `wiki/reference/lexicon.md` — one line per term. Kept small enough that every session
  can afford to read it. If it grows into full definitions it stops getting loaded and
  the whole mechanism goes dead.
- Valid `tags:` vocabulary — see below.

**Change detection without hidden state.** Each concept note stores the verbatim source
text it was built from under `## Source (verbatim)`. The compiler compares the current
raw text against that block — a literal string compare. No mtime (dies on `git clone`,
which breaks the two-Mac setup), no hash files, no state outside the notes themselves.

**Aliases are load-bearing.** `aliases:` lists other phrasings for the same thing ("the
place" / "our place" / "the property"). Without them, recognition only fires on exact
matches and the lexicon appears broken.

**Precedence** when the same term arrives from more than one input in a single run:
`key-terms.md` > `[define]` marker > conversation. Losers are recorded in the note's
`## History`, not discarded.

**Conflict with a human edit.** If `raw/key-terms.md` disagrees with a hand-edit in the
concept note, key-terms.md wins — it's the more recent deliberate statement — but the
prior text is preserved in `## History` and the overwrite is **reported**. This is the
one narrow exception to rule 2, and it is never silent.

**Removal.** A term dropped from `key-terms.md` is not deleted: `status: archived`, a
`## History` line, and a move to the lexicon's archived section (rule 5).

**Tags.** A `tags:` value is *registered* if a concept note exists for it. Unregistered
tags are legal but get listed by the linter as concept candidates — that queue is the
point, not an error to chase.

**Linking.** When writing any note, link a known term or alias on first mention
(`[[be-useful]]`). First mention only — don't carpet the note.

---

## The five behaviors

### 1. Compile (`raw/` → `wiki/`)

1. Sweep `raw/clips/` and `raw/inbox.md` for unprocessed items.
2. **Terms pass — runs first,** so new terms are available for linking in the same run. Read `raw/key-terms.md` and any `[define]` lines in `inbox.md`; create, update, or archive concept notes; regenerate `wiki/reference/lexicon.md`. See the lexicon section above for precedence and conflict rules.
3. For each item: read fully (including images); choose domain and type; create a wiki note from the matching template — summary in your own words, key ideas, and honest signal (if a clipped article is thin, say so in the note).
4. Link: add `## Connections` to the new note; add reciprocal links in the notes it connects to; link known terms/aliases on first mention; when 3+ notes share a theme with no home, write a `synthesis` note.
5. Update `wiki/index.md`.
6. Move processed items to `raw/_processed/`; clear processed entries from `inbox.md` (leave the header, and leave `key-terms.md` untouched).
7. Append a run row to `system/log.md`; commit (`compile: <n> items — <short summary>`).
8. Report to B.J.: what was filed where, term changes, anything skipped and why.

### 2. Answer

Read `wiki/reference/lexicon.md` first (it's small, and it tells you what B.J.'s words mean), then `wiki/index.md` → follow links → read the relevant notes → answer, citing the notes used. If the wiki lacks the answer, say so — then offer to research (web) and compile the findings in. Substantial answers become files (rule 3).

### 3. Manage (personal project manager)

Keep `wiki/projects/projects-dashboard.md` current: active projects, status, next actions, what's blocked, what's stalled (no update in 14+ days). Every project links to a goal; every goal to a vision — if a project serves no goal, flag it. Weekly review: progress vs. goals, wins, stalls, and what deserves focus next week.

### 4. Lint (health check)

Checks: contradictions between notes; frontmatter schema violations; orphan notes; broken links; stale projects; gaps worth filling (may use web search); interesting cross-domain connections worth B.J.'s attention. Lexicon checks: concept notes whose `## Source (verbatim)` block no longer matches `raw/key-terms.md` (a missed terms pass); concepts defined but never referenced anywhere; unregistered `tags:` values, listed as concept candidates; lexicon rows that don't match the concept notes on disk. Output: dated report in `system/lint-reports/YYYY-MM-DD.md`, log row, commit (`lint: <summary>`). Fix mechanical issues (broken links, frontmatter) directly; content contradictions get *reported*, not silently resolved.

### 5. Ingest (mid-conversation)

When B.J. shares a link, file, or thought: append it to `raw/inbox.md` (or save the file to `raw/clips/`) with a one-line context note and today's date. Compile immediately if asked; otherwise it waits for the next compile run.

When B.J. defines a term in conversation ("when I say X, I mean Y", "by X I mean…"): append `- YYYY-MM-DD — [define] term — meaning` to `raw/inbox.md`. Never edit `raw/key-terms.md` on his behalf — that file is his to curate; suggest the addition instead.

---

## Git conventions

- Commit after every system run and any multi-file change. Message prefixes: `compile:` `lint:` `manage:` `ingest:` `system:`.
- Never push to a remote, and never delete the repo or rewrite history, unless B.J. explicitly asks.
- **Cloud Cowork sessions** (working via the device bridge, which cannot delete files): use `git --no-optional-locks` for reads, and run `sh system/bin/git-lock-sweep.sh` after every git write — stale locks otherwise jam the next operation. `gc.auto` is intentionally 0; leave it.
- Sessions running directly on a Mac need no special git handling.
- **No remote. Ever.** This vault is standalone by design — local commits only. Do not add `origin`, do not pull from or push to the primary `life-os` repo, and do not attempt to merge the two histories. If B.J. asks to sync terms home, the answer is copy-paste of `raw/key-terms.md` content, not git.

---

## Cadence & integrations

**No scheduled runs here.** Compile is manual and attended in this vault — say "compile" to trigger it. The Sunday automation belongs to the primary vault only.

**What this vault is for:** exercising the terms pass — write terms in `raw/key-terms.md`, compile, inspect the concept notes and `wiki/reference/lexicon.md`, edit a term, compile again, confirm change detection and `## History` behave. Findings and any terms worth keeping get carried back to the primary vault by hand.

**What is deliberately absent:** the build plan, sync setup, all compiled notes, all raw material. Their absence is not a lint error and not a gap to fill — do not recreate them, and do not go looking for the primary vault.
