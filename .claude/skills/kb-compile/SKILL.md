---
name: kb-compile
description: >-
  Compile the Life OS knowledge base: sweep raw/ (inbox.md and clips/) and turn
  unprocessed items into summarized, categorized, backlinked wiki notes. Use this
  skill whenever the user says "compile", "run the compiler", "process the inbox",
  "sweep raw", "file my clips", or "compile the KB" — and also during any Sunday
  maintenance routine, after a batch of web clips lands in raw/clips/, or whenever
  the user drops links/notes/files into the vault and wants them organized. Also
  handles the terms pass — updating key terms and the lexicon after the user edits
  raw/key-terms.md or says "I updated my key terms", "process my glossary", or
  "define <term>". If you are working inside a LifeOS vault and raw/ contains
  unprocessed material, this skill is how it gets into the wiki.
---

# kb-compile — the Life OS compiler

This skill is the executable form of the **Compile** behavior in the vault's
`CLAUDE.md`. The constitution defines the law; this skill is the procedure.
If they ever disagree, `CLAUDE.md` wins — flag the discrepancy to the user.

**The job:** raw, messy human input goes in; organized, honest, interlinked
wiki knowledge comes out. The human never organizes; the compiler never loses
information. The user's trust in this system depends on every item being either
filed or explicitly reported — silent drops are the one unforgivable failure.

## 0. Preflight

1. Locate the vault root (the folder containing `CLAUDE.md` with `raw/` and
   `wiki/`). Read `CLAUDE.md` if you haven't this session — frontmatter schema,
   type registry, and golden rules all live there.
2. Sync state: if the vault has a git remote and you have network access, `git
   pull` first. In a cloud Cowork session (device bridge — no network), skip the
   pull and note in your report that B.J. should push afterward.
3. Read `wiki/index.md` — you need the current map to link new notes into it.
4. `git status` should be clean-ish before you start; if there are uncommitted
   changes you didn't make, commit them separately first (`system: pre-compile
   snapshot`) so a rollback of this compile never destroys someone else's work.

## 1. Sweep

Collect the work list:

- **`raw/inbox.md`** — every dated bullet not marked processed. Entries tagged
  `[tagged]` are open questions, not compile fodder: leave them unless resolved.
  Entries tagged `[define]` are term definitions — they go to the terms pass (§2),
  not the item loop.
- **`raw/key-terms.md`** — the standing glossary. Always read, never cleared, never
  moved to `_processed/`, never edited by you. Feeds the terms pass (§2).
- **`raw/clips/`** — every file except `.gitkeep`. Web clips may arrive with
  companion image files or asset folders — treat a clip and its images as ONE item.

If the work list is empty, do not invent work and do not "improve" existing wiki
notes uninvited (that's the linter's job, on its own schedule). Do still append a
`| date | compile | 0 items — nothing to process |` row to `system/log.md` and
commit it: for unattended scheduled runs, that heartbeat is the proof the
compiler ran and found nothing — silence would be indistinguishable from failure.

## 2. Terms pass (runs FIRST, before any item)

Terms are compiled before items so that notes written later in the same run can link
newly-defined terms. The constitution's "Terms & concepts" section is the law here;
this is the procedure.

1. **Parse `raw/key-terms.md`.** Each `##` heading is a term (kebab-case slug); the
   text beneath it, up to the next heading, is that term's source block. An optional
   `aliases:` line lists alternate phrasings. Ignore everything above the `---`
   separator — that's the file's own instructions, not terms.
2. **Collect `[define]` lines** from `inbox.md`: `- YYYY-MM-DD — [define] term — meaning`.
3. **Resolve duplicates** by precedence: `key-terms.md` > `[define]` > conversation.
   The losing text goes in the note's `## History`, never in the trash.
4. **For each term, compare** its source block against the `## Source (verbatim)` block
   in `wiki/reference/concepts/<term>.md` — a literal string compare:
   - **No note exists** → create from `system/templates/concept.md`. Write `## Definition`
     in your own words (not a paste of the source), fill `aliases`, `source`, `status`,
     and stamp `## History` with `YYYY-MM-DDTHH:MM — created from <source>`.
   - **Blocks match** → nothing changed. Don't touch the note, don't bump `updated`.
   - **Blocks differ** → rewrite `## Definition` and `## Source (verbatim)`, bump
     `updated`, and append a `## History` line with the timestamp, what changed, and
     the prior text. If the note carried a human edit that this overwrites, preserve
     the human's wording in History and **flag it in the report** — this is the one
     sanctioned exception to "human edits are authoritative," and it is never silent.
   - **Note exists but the term is gone from `key-terms.md`** → set `status: archived`,
     append a History line, move it to the lexicon's archived section. Never delete.
5. **Regenerate `wiki/reference/lexicon.md`** from the concept notes on disk — one row
   per active term (term, one-line gloss, aliases, source), archived terms below. It is
   generated output: rewrite it wholesale, never hand-patch. Keep glosses to one line;
   a lexicon that grows into full definitions stops being loadable and the mechanism dies.
6. **Report term changes separately** from item changes (§6) — created, updated (with
   what changed), archived, and any conflict overwrites.

If `key-terms.md` doesn't exist yet or has no terms below the separator, that's fine and
expected — skip to §3 and note "0 terms" in the report (the run is still valid — a
compile with 0 terms and 0 items still logs and commits per §1). Don't invent terms, and don't
mine the wiki for candidates: that's the linter's job.

## 3. Compile each item

For each item, in this order:

1. **Read it fully.** Open images — diagrams often carry the argument. For PDFs,
   use the pdf skill. For bare URLs in the inbox, fetch the page if you have web
   access; if you can't, file a stub note with the URL and flag it in the report.
2. **Check for an existing home.** Search the wiki (grep titles, index, tags)
   before creating anything. If a note on this exact subject exists, UPDATE it
   (bump `updated`, add the new source/material) rather than spawning a duplicate.
3. **Classify:** choose `domain` and `type` from the registry in `CLAUDE.md`.
   Genuinely torn between two domains? Pick the best fit and note the call in
   your report — a wrong-but-visible filing beats a stalled compile.
4. **Create the note** from the matching template in `system/templates/`
   (kebab-case filename, full frontmatter, honest dates).
5. **Summarize in your own words** — never paste walls of source text. Include
   an honest signal note: if a clipped article is thin, derivative, or secondhand,
   say so in the note. Future-you answering questions from this wiki needs to
   know how much to trust each source.
6. **Extract key ideas** as scannable bullets — these are what Q&A sessions
   will actually read.
7. **Link:** end the note with `## Connections` naming related notes and *why*
   they relate. Add reciprocal links in the connected notes (a one-line addition
   to their Connections section — don't rewrite them).

## 4. Synthesize (when earned)

When three or more notes now share a theme that has no home note, write a
`synthesis` note that ties them together and says something none of them says
alone. Don't force this — a synthesis that merely lists its sources is noise.
This is the compiler's highest-value output; it's also optional on any given run.

## 5. Close the loop

1. **Update `wiki/index.md`:** new notes under their domain sections, bump the
   `updated` date, refresh the Status line. Every note must be reachable from
   the index — an unreachable note is invisible to future Q&A.
2. **Clear the processed raw:** move ingested clip files to `raw/_processed/`;
   rewrite `inbox.md` keeping the header and any unprocessed/`[tagged]` entries.
   `[define]` lines that became concept notes are processed — drop them from
   `inbox.md` (the definition and its provenance now live in the note's History).
   **Leave `raw/key-terms.md` completely untouched** — it is a standing human file.
   Never delete raw material — `_processed/` is the audit trail.
3. **Log:** append a row to `system/log.md`:
   `| YYYY-MM-DD | compile | <n> items, <n> terms: <one-line summary> |`
4. **Commit:** `compile: <n> items — <short summary>`. In a cloud session, run
   `sh system/bin/git-lock-sweep.sh` after the commit (stale git locks otherwise
   jam the next run) and use `git --no-optional-locks` for status/log reads.
   On-machine with a remote configured: `git push`.

## 6. Report

End with a short report to the user — a table beats prose here:

| Item | Filed as | Domain | Notes |
|---|---|---|---|
| (raw item) | [[note-name]] | research | — |
| (raw item) | skipped | — | why, and what would unblock it |

If the terms pass did anything, report it as its own table:

| Term | Change | Source | Notes |
|---|---|---|---|
| [[the-place]] | created | key-terms.md | — |
| [[be-useful]] | updated | key-terms.md | definition narrowed; prior text in History |
| [[old-term]] | archived | — | removed from key-terms.md |

Plus: any judgment calls (ambiguous classifications, updated-instead-of-created),
any conflict overwrites of human edits (always call these out explicitly),
any new synthesis notes, and the reminder to push if this was a cloud session.

## Edge cases

- **Human edits found in wiki notes you're touching:** preserve them verbatim —
  human edits are authoritative (constitution rule 2).
- **An item that's really a task or project, not knowledge** ("call the roofer",
  "plan the application timeline"): file it toward `wiki/projects/` or flag it as a
  candidate project in the report — don't shoehorn it into research.
- **Sensitive material** (finances, health): compile it normally — this vault is
  private by design — but never let it leave the vault (no web lookups that
  embed personal figures in queries).
- **Something you can't classify at all:** leave it in raw, report it, ask.
  One stuck item must never stall the rest of the run.
- **A `key-terms.md` edit that contradicts a hand-edited concept note:** key-terms.md
  wins (it's the more recent deliberate statement), but preserve the human's wording
  in `## History` and flag the overwrite in the report. Never resolve this silently.
- **A term whose definition you don't understand well enough to paraphrase:** copy the
  source block into `## Source (verbatim)`, leave `## Definition` as a direct restatement,
  and say so in the report. A thin-but-honest concept note beats a confident wrong one.
