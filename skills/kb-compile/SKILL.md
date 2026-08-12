---
name: kb-compile
description: >-
  Compile a cairn knowledge vault: sweep raw/ (inbox.md, key-terms.md, clips/) and turn
  unprocessed items into summarized, categorized, backlinked wiki notes. Use this skill
  whenever the user says "compile", "run the compiler", "process the inbox", "sweep raw",
  "file my clips", or "compile the KB" — and also during any scheduled maintenance routine,
  after a batch of web clips lands in raw/clips/, or whenever the user drops links, notes,
  or files into the vault and wants them organized. Also handles the terms pass — updating
  key terms and the lexicon after the user edits raw/key-terms.md or says "I updated my key
  terms", "process my glossary", or "define <term>". If you are working inside a cairn vault
  and raw/ contains unprocessed material, this skill is how it gets into the wiki.
---

# kb-compile — the cairn compiler

This skill is the executable form of the **Compile** behavior in the constitution
(`system/cairn/constitution.md`). The constitution defines the law; this skill is the
procedure. If they ever disagree, the constitution wins — flag the discrepancy.

**The job:** raw, messy human input goes in; organized, honest, interlinked wiki
knowledge comes out. The human never organizes; the compiler never loses information.
The user's trust in this system depends on every item being either filed or explicitly
reported — silent drops are the one unforgivable failure.

**This skill is engine-owned.** Do not edit it inside a vault; fixes go upstream to the
cairn repo and arrive via `cairn update`.

## 0. Preflight

1. **Locate the vault root** — the folder containing `system/vault-profile.yml` with
   `raw/` and `wiki/` beside it.
2. **Read `system/vault-profile.yml` first.** It declares this vault's domains, types,
   and conventions. *Everything downstream depends on it.* Never assume a vault has any
   particular domain or type — a personal vault and a work vault share no vocabulary.
   If the profile is missing or unparseable, stop and report; do not guess a schema.
3. **Read the constitution** (`system/cairn/constitution.md`) if you haven't this session.
4. **Sync state:** if the profile says `sync.multi_machine: true` and you have network
   access, `git pull` first. In a bridge session with no network, skip it and note in the
   report that the user should push afterward.
5. **Read `wiki/index.md`** — you need the current map to link new notes into it.
6. `git status` should be clean-ish. If there are uncommitted changes you didn't make,
   commit them separately first (`system: pre-compile snapshot`) so a rollback of this
   compile never destroys someone else's work.

## 1. Sweep

Collect the work list:

- **`raw/inbox.md`** — every dated bullet not marked processed. Entries tagged `[tagged]`
  are open questions, not compile fodder: leave them unless resolved. Entries tagged
  `[define]` are term definitions — they go to the terms pass (§2), not the item loop.
- **`raw/key-terms.md`** — the standing glossary. Always read, never cleared, never moved
  to `_processed/`, never edited by you. Feeds the terms pass (§2).
- **`raw/clips/`** — every file except `.gitkeep`. A clip and its companion images or
  asset folder are ONE item.

If the work list is empty, do not invent work and do not "improve" existing wiki notes
uninvited (that's the linter's job, on its own schedule). Do still append a
`| date | compile | 0 items, 0 terms — nothing to process |` row to `system/log.md` and
commit it: for unattended runs that heartbeat is the proof the compiler ran and found
nothing — silence would be indistinguishable from failure.

## 2. Terms pass (runs FIRST, before any item)

Terms are compiled before items so notes written later in the same run can link
newly-defined terms. The constitution's "Terms & concepts" section is the law here.

1. **Parse `raw/key-terms.md`.** Each `##` heading is a term (kebab-case slug); the text
   beneath it, up to the next heading, is that term's source block. An optional `aliases:`
   line lists alternate phrasings. Ignore everything above the `---` separator — that's
   the file's own instructions, not terms.
2. **Collect `[define]` lines** from `inbox.md`:
   `- YYYY-MM-DD — [define] term — meaning`.
3. **Resolve duplicates** by precedence: `key-terms.md` > `[define]` > conversation.
   The losing text goes in the note's `## History`, never in the trash.
4. **For each term, compare** its source block against the `## Source (verbatim)` block in
   `wiki/concepts/<term>.md` — a literal string compare:
   - **No note exists** → create from the resolved `concept` template. Write
     `## Definition` in your own words (not a paste of the source), fill `aliases`,
     `source`, `status`, and stamp `## History` with
     `YYYY-MM-DDTHH:MM — created from <source>`.
   - **Blocks match** → nothing changed. Don't touch the note, don't bump `updated`.
   - **Blocks differ** → rewrite `## Definition` and `## Source (verbatim)`, bump
     `updated`, and append a `## History` line with the timestamp, what changed, and the
     prior text. If the note carried a human edit that this overwrites, preserve the
     human's wording in History and **flag it in the report** — the one sanctioned
     exception to "human edits are authoritative," and it is never silent.
   - **Note exists but the term is gone from `key-terms.md`** → set `status: archived`,
     append a History line, move it to the lexicon's archived section. Never delete.
5. **Regenerate `wiki/lexicon.md`** from the concept notes on disk — one row per active
   term (term, one-line gloss, aliases, source), archived terms below. It is generated
   output: rewrite it wholesale, never hand-patch. Keep glosses to one line; a lexicon
   that grows into full definitions stops being loadable and the mechanism dies.
6. **Report term changes separately** from item changes (§6).

If `key-terms.md` has no terms below the separator, that's fine and expected — note
"0 terms" and continue. Don't invent terms, and don't mine the wiki for candidates:
that's the linter's job.

## 3. Compile each item

For each item, in this order:

1. **Read it fully.** Open images — diagrams often carry the argument. For PDFs, use the
   pdf skill. For bare URLs, fetch the page if you have web access; if not, file a stub
   note with the URL and flag it.
2. **Check for an existing home.** Search the wiki (titles, index, tags, lexicon) before
   creating anything. If a note on this exact subject exists, UPDATE it (bump `updated`,
   add the new source) rather than spawning a duplicate.
3. **Classify against the profile.** Pick a `domain` from `domains[].id` and a `type` from
   the base registry plus `types.add[].id`. **Never invent either.** If nothing fits,
   use the domain marked `default: true`; if there is no default and you are genuinely
   torn, pick the best fit and note the call in your report — a wrong-but-visible filing
   beats a stalled compile. If the item needs a type the vault doesn't declare, file it
   under the closest existing type and *propose* the new type in the report; extending
   the registry is the human's decision.
4. **Resolve the template:** `system/templates/<type>.md` (store-local) wins over
   `system/cairn/templates/<type>.md` (engine). Neither exists → use `note.md` and say so.
5. **Create the note** (kebab-case filename, full frontmatter per the profile's required
   keys, honest dates).
6. **Summarize in your own words** — never paste walls of source text. Include an honest
   signal note: if a source is thin, derivative, or secondhand, say so. Future sessions
   answering questions from this wiki need to know how much to trust each source.
7. **Extract key ideas** as scannable bullets — these are what Q&A actually reads.
8. **Link:** end with `## Connections` naming related notes and *why* they relate. Add
   reciprocal links in the connected notes (a one-line addition — don't rewrite them).
   Link known terms and aliases on first mention if
   `conventions.link_terms_on_first_mention` is true.

## 4. Synthesize (when earned)

When three or more notes now share a theme with no home note, write a `synthesis` note
tying them together that says something none of them says alone. Don't force it — a
synthesis that merely lists its sources is noise. This is the compiler's highest-value
output; it is also optional on any given run.

## 5. Close the loop

1. **Regenerate `wiki/index.md`** from the profile: one section per declared domain, in
   profile order, using each domain's `purpose` as its subtitle, then the notes on disk
   under each. Plus the engine-reserved Lexicon link. Every note must be reachable —
   an unreachable note is invisible to future Q&A.
2. **Clear the processed raw:** move ingested clip files to `raw/_processed/`; rewrite
   `inbox.md` keeping the header and any unprocessed/`[tagged]` entries. `[define]` lines
   that became concept notes are processed — drop them (the definition and its provenance
   now live in the note's History). **Leave `raw/key-terms.md` completely untouched.**
   Never delete raw material — `_processed/` is the audit trail.
3. **Log:** append a row to `system/log.md`:
   `| YYYY-MM-DD | compile | <n> items, <n> terms: <one-line summary> |`
4. **Commit:** `compile: <n> items — <short summary>`. Never stage anything under
   `system/cairn/` — engine paths are upstream-owned; if they show as modified, stop and
   report it as drift. In a bridge session run `sh system/cairn/bin/git-lock-sweep.sh`
   after the commit and use `git --no-optional-locks` for status/log reads. If the profile
   says `sync.multi_machine: true` and a remote is configured: `git push`.

## 6. Report

End with a short report — tables beat prose:

| Item | Filed as | Domain | Notes |
|---|---|---|---|
| (raw item) | [[note-name]] | research | — |
| (raw item) | skipped | — | why, and what would unblock it |

If the terms pass did anything:

| Term | Change | Source | Notes |
|---|---|---|---|
| [[the-place]] | created | key-terms.md | — |
| [[be-useful]] | updated | key-terms.md | definition narrowed; prior text in History |
| [[old-term]] | archived | — | removed from key-terms.md |

Plus: judgment calls (ambiguous classifications, updated-instead-of-created), any
**proposed new types or domains**, any conflict overwrites of human edits (always call
these out explicitly), new synthesis notes, and the reminder to push if this was a
bridge session.

## Edge cases

- **Human edits found in wiki notes you're touching:** preserve them verbatim (rule 2).
- **An item that's really a task or project, not knowledge** ("call the roofer", "plan the
  application timeline"): file it toward a project-typed note or flag it as a candidate in
  the report — don't shoehorn it into research.
- **Sensitive material** (finances, health, personnel): compile it normally — vaults are
  private by design — but never let it leave the vault (no web lookups that embed personal
  figures or names in queries).
- **A `key-terms.md` edit that contradicts a hand-edited concept note:** key-terms.md wins,
  but preserve the human's wording in `## History` and flag the overwrite. Never silent.
- **A term you can't paraphrase confidently:** copy the source into `## Source (verbatim)`,
  make `## Definition` a direct restatement, and say so. A thin-but-honest concept note
  beats a confident wrong one.
- **Engine-owned files appear modified:** stop. That's drift, and the next `cairn update`
  will destroy it. Report it rather than committing it.
- **Something you can't classify at all:** leave it in raw, report it, ask. One stuck item
  must never stall the rest of the run.
