# The Cairn Constitution

The operating law for a cairn vault — an AI-compiled personal knowledge base.
Any Claude session working inside a vault follows this document. When in doubt,
this file wins over habit, convenience, or a user's in-the-moment convenience.

**This file is engine-owned.** It is replaced wholesale by `cairn update` and must
never be hand-edited inside a vault. Vault-specific configuration belongs in
`system/vault-profile.yml`; vault-specific instructions belong in the vault's root
`CLAUDE.md`.

**The system in one sentence:** the human dumps raw material into `raw/`; Claude
compiles it into an interlinked markdown wiki, answers questions from it, manages
work with it, and lints it — so the knowledge base compounds over time.

---

## Golden rules

1. **`raw/` is human territory.** Never reorganize, rename, or edit raw items. The only permitted operation is the compiler moving fully-ingested items into `raw/_processed/`. `raw/key-terms.md` is a *standing* file — read every run, never cleared, never moved, never edited by Claude.
2. **`wiki/` is AI territory.** Claude creates, updates, links, and maintains wiki notes. The human reads them and rarely edits — but if a human edit is found, it is authoritative: preserve it, never revert it.
3. **Files over chat.** Substantial answers, analyses, and deliverables become files (a wiki note or an item in `outputs/`), not just chat text — then get linked into the wiki so they compound.
4. **Plain text, no magic.** Markdown files, wikilinks, and a good index. No vector databases, no RAG, no hidden state. To find things: read `wiki/index.md`, follow links. A vault must remain fully usable by a human with a text editor and no AI at all.
5. **Never destroy knowledge.** Don't delete wiki notes; supersede them (update in place) or mark them `status: archived` in frontmatter. Deletions only with the human's explicit per-file approval.
6. **Every run leaves a trail.** System-level operations (compile, lint, migrations) append a row to `system/log.md` and end with a git commit.
7. **Privacy default.** Nothing in a vault is pushed to any remote, service, or third party unless the human explicitly asks. A vault's contents are assumed sensitive.

---

## Vault shape

| Path | Owner | Purpose |
|---|---|---|
| `raw/inbox.md` | Human | Quick captures, pasted links, stray thoughts |
| `raw/key-terms.md` | Human | Glossary of loaded terms — standing file, edit anytime |
| `raw/clips/` | Human | Clipped articles, dropped files |
| `raw/_processed/` | Compiler | Ingested raw items (audit trail; never re-compile) |
| `wiki/index.md` | Compiler | Master map — every note reachable from here |
| `wiki/<domain>/` | AI | One directory per domain declared in the profile |
| `wiki/concepts/` | Compiler | One note per key term — the canonical definition store |
| `wiki/lexicon.md` | Compiler | Generated term registry (never hand-edit) |
| `outputs/` | AI | Generated deliverables: reports, decks, charts |
| `system/vault-profile.yml` | Human | This vault's domains, types, and conventions |
| `system/cairn/` | **Engine** | Vendored engine — replaced by `cairn update`, never hand-edit |
| `system/templates/` | Human | Store-local templates; override or extend the engine's |
| `system/lint-reports/` | Linter | Dated health-check reports |
| `system/log.md` | AI | Run history |
| `CLAUDE.md` | Human | Vault-specific instructions; points here |

`wiki/concepts/` and `wiki/lexicon.md` are **engine-reserved** — a profile may not
declare a domain named `concepts`, and nothing else may occupy those paths.

---

## Note conventions

**Filenames:** kebab-case, descriptive, no dates in names (dates live in frontmatter).

**Links:** Obsidian-style wikilinks `[[note-name]]`. Every wiki note must be reachable from `wiki/index.md` (directly or via links) — orphans are lint errors. Notes end with a `## Connections` section linking related notes.

**Dates:** ISO format `YYYY-MM-DD` everywhere.

**Frontmatter (required on every wiki note):**

```yaml
---
type: article        # from the base registry or the profile's additions
domain: research     # must be a domain declared in system/vault-profile.yml
created: 2026-08-12
updated: 2026-08-12  # bump on every edit
tags: []
---
```

**Domains are not fixed.** They are declared per vault in `system/vault-profile.yml`.
A note whose `domain` is not declared there is a lint error. Never invent a domain,
and never assume a vault has any particular one — read the profile.

The single exception: **`domain: concepts` is a reserved value**, always valid and never
declared in a profile. Only concept notes use it.

**Base type registry** (every vault has these):
`note` `article` `synthesis` `person` `decision` `idea` `reference` `project` `concept` `index`

Base type-specific required keys:

| Type | Also requires |
|---|---|
| `article` | `source`, `author`, `clipped` |
| `project` | `status` (active\|waiting\|someday\|done\|archived), plus the profile's `project_parent` link if one is declared |
| `concept` | `aliases`, `source` (key-terms.md\|inbox\|conversation), `status` (active\|archived) |
| `person` | — |

**Vaults extend the registry** via `types.add` in the profile — each addition names its
required keys and optionally a template. A type not in the base registry and not in the
profile is a lint error. Extending the registry is a human decision: propose, don't
self-authorize.

**Template resolution:** `system/templates/<type>.md` (store-local) wins over
`system/cairn/templates/<type>.md` (engine). If neither exists, use `note.md`
and say so in the run report.

---

## Terms & concepts (the lexicon)

Some words carry meaning in a vault that a dictionary won't give you. The lexicon is how
the vault remembers that. **Three ways in, one place it lives.**

**Inputs (all human, all in `raw/`):**

1. `raw/key-terms.md` — the curated glossary. Bulk edits, whenever.
2. `[define] term — meaning` lines in `raw/inbox.md` — in-the-moment capture.
3. Mid-conversation — "when I say X, I mean Y" → Ingest writes a `[define]` line.

**The store:** one `type: concept` note per term in `wiki/concepts/`. This is the only
authoritative copy. It's linkable (`[[the-place]]`), supersedable, and lints like any
other note. Concept notes carry the reserved `domain: concepts` — they live outside the
domain tree and are valid in every vault regardless of what its profile declares.

**The view:** `wiki/lexicon.md` — one line per term, regenerated every compile, never
hand-edited. Kept small enough that every session can afford to read it. If it grows into
full definitions it stops getting loaded and the whole mechanism goes dead.

**Change detection without hidden state.** Each concept note stores the verbatim source
text it was built from under `## Source (verbatim)`. The compiler compares the current raw
text against that block — a literal string compare. No mtime (it does not survive
`git clone`, which breaks multi-machine vaults), no hash files, no state outside the notes.

**Aliases are load-bearing.** `aliases:` lists other phrasings for the same thing.
Without them, recognition only fires on exact matches and the lexicon appears broken.

**Precedence** when a term arrives from more than one input in a run:
`key-terms.md` > `[define]` marker > conversation. Losers go in `## History`, not the trash.

**Conflict with a human edit.** If `raw/key-terms.md` disagrees with a hand-edit in the
concept note, key-terms.md wins — it is the more recent deliberate statement — but the
prior text is preserved in `## History` and the overwrite is **reported**. This is the one
narrow exception to rule 2, and it is never silent.

**Removal — scoped by source.** A term dropped from `key-terms.md` is not deleted:
`status: archived`, a `## History` line, and a move to the lexicon's archived section
(rule 5).

**This applies only to notes whose `source:` is `key-terms.md`.** A concept sourced from
`inbox` or `conversation` came from a transient input that the compiler itself clears
after processing — its absence from `key-terms.md` is the normal steady state, not a
removal. Archiving those would silently destroy every `[define]`-sourced term on its
second compile. Absence is only meaningful for the input a term actually came from.

**Tags.** A `tags:` value is *registered* if a concept note exists for it. Unregistered
tags are legal but get listed by the linter as concept candidates — that queue is the
point, not an error to chase.

**Linking.** When writing any note, link a known term or alias on first mention.
First mention only — don't carpet the note.

---

## The five behaviors

### 1. Compile (`raw/` → `wiki/`)

1. Read `system/vault-profile.yml` — domains, types, conventions. Everything below depends on it.
2. Sweep `raw/clips/` and `raw/inbox.md` for unprocessed items.
3. **Terms pass — runs first,** so new terms are available for linking in the same run. Read `raw/key-terms.md` and any `[define]` lines; create, update, or archive concept notes; regenerate `wiki/lexicon.md`.
4. For each item: read fully (including images); choose a domain and type **from the profile**; create a note from the resolved template — summary in your own words, key ideas, and honest signal (if a source is thin, say so in the note).
5. Link: add `## Connections`; add reciprocal links in the notes it connects to; link known terms/aliases on first mention; when 3+ notes share a theme with no home, write a `synthesis` note.
6. Regenerate `wiki/index.md` from the profile's declared domains plus the notes on disk.
7. Move processed items to `raw/_processed/`; clear processed entries from `inbox.md` (leave the header, and leave `key-terms.md` untouched).
8. Append a run row to `system/log.md`; commit (`compile: <n> items — <short summary>`).
9. Report: what was filed where, term changes, anything skipped and why.

### 2. Answer

Read `wiki/lexicon.md` first (it's small, and it tells you what the human's words mean),
then `wiki/index.md` → follow links → read the relevant notes → answer, citing the notes
used. If the wiki lacks the answer, say so — then offer to research and compile the
findings in. Substantial answers become files (rule 3).

### 3. Manage

If the vault declares a `project` type, keep a projects dashboard current: active work,
status, next actions, what's blocked, what's stalled (no update in `stale_project_days`,
default 14). If the profile declares a `project_parent` type, every project links up to
one — a project serving no parent gets flagged, not silently accepted. If no
`project_parent` is declared, projects stand alone and that is not an error.

### 4. Lint (health check)

The deterministic half runs as `system/cairn/bin/lint-scan.py` (stdlib python3, no
dependencies); the judgment half needs reading and is the session's job. Checks:
contradictions between notes; frontmatter schema violations *against the profile*;
undeclared domains or types; orphan notes; broken links; stale projects; gaps worth
filling; cross-domain connections worth surfacing. Lexicon checks: concept notes whose
`## Source (verbatim)` no longer matches `raw/key-terms.md` (a missed terms pass);
concepts defined but never referenced; unregistered `tags:` values, listed as concept
candidates; lexicon rows that don't match the concept notes on disk. Output: dated report
in `system/lint-reports/YYYY-MM-DD.md`, log row, commit (`lint: <summary>`). Fix
mechanical issues directly; content contradictions get *reported*, not silently resolved.

### 5. Ingest (mid-conversation)

When the human shares a link, file, or thought: append it to `raw/inbox.md` (or save the
file to `raw/clips/`) with a one-line context note and today's date. Compile immediately
if asked; otherwise it waits for the next compile run.

When the human defines a term in conversation ("when I say X, I mean Y"): append
`- YYYY-MM-DD — [define] term — meaning` to `raw/inbox.md`. Never edit `raw/key-terms.md`
on their behalf — that file is theirs to curate; suggest the addition instead.

---

## Git conventions

- Commit after every system run and any multi-file change. Message prefixes: `compile:` `lint:` `manage:` `ingest:` `system:`.
- Never push to a remote, and never delete the repo or rewrite history, unless the human explicitly asks.
- **Never commit engine-owned paths from inside a vault.** Fixes to `system/cairn/` or the engine skills belong upstream in the cairn repo, then arrive via `cairn update`. Editing them in a vault creates drift that the next update silently destroys.
- **Cloud/bridge sessions** (which cannot delete files): use `git --no-optional-locks` for reads, and run `sh system/cairn/bin/git-lock-sweep.sh` after every git write — stale locks otherwise jam the next operation.
- **Multi-machine vaults:** `git pull` at the start of any working session; `git push` after committing at the end. Never run compile or lint on two machines at once. Specifics live in the vault's `CLAUDE.md`, not here.

---

## Cadence

A vault may schedule a recurring compile + lint. Whether it does, and when, is declared in
the vault's own `CLAUDE.md` — the engine assumes nothing. An unattended run that finds
nothing still logs a heartbeat row and commits: silence must never be indistinguishable
from failure.
