---
name: kb-lint
description: >-
  Health-check a cairn knowledge vault: schema violations, undeclared domains and types,
  broken links, orphan notes, stale projects, lexicon drift, plus the judgment-level
  checks a parser can't do — contradictions between notes, gaps worth filling, and
  cross-domain connections worth surfacing. Use whenever the user says "lint", "run the
  linter", "health check", "check the vault", "what's stale", or "what's broken" — and as
  the second half of any scheduled maintenance routine, after kb-compile. Produces a dated
  report in system/lint-reports/. Do NOT use this to file new raw material; that is
  kb-compile's job.
---

# kb-lint — the cairn health check

This skill is the executable form of the **Lint** behavior in the constitution
(`system/cairn/constitution.md`). The constitution defines the law; this is the procedure.
If they disagree, the constitution wins — flag the discrepancy.

**The job:** tell the truth about the state of the vault. A linter that reports a clean
bill of health it didn't verify is worse than no linter, because it converts uncertainty
into false confidence. Every claim in the report must trace to something you actually
checked.

**The division of labour:**

- `system/cairn/bin/lint-scan.py` does the deterministic checks. It is fast, exact, and
  has no opinions. **Run it — do not re-implement its checks by reading files yourself.**
- You do the checks that need reading comprehension: contradictions, gaps, connections.
  A parser cannot tell that two notes disagree about a date; you can.

**This skill is engine-owned.** Don't edit it inside a vault; fixes go upstream.

## 0. Preflight

1. Locate the vault root (contains `system/vault-profile.yml`, `raw/`, `wiki/`).
2. Read `system/vault-profile.yml` and the constitution if you haven't this session.
3. If `sync.multi_machine` is true and you have network, `git pull` first.
4. Working tree should be clean-ish. Uncommitted changes you didn't make get committed
   separately first (`system: pre-lint snapshot`).

## 1. Mechanical scan

```
python3 system/cairn/bin/lint-scan.py . --json
```

Findings come back at three severities:

- **error** — the vault is internally inconsistent. Schema violations, undeclared domains
  or types, broken links, duplicate basenames, lexicon drift.
- **warn** — probably wrong, needs a human's eye. Orphans, stale projects, projects with
  no parent, date inconsistencies, notes filed under the wrong domain directory.
- **info** — not problems. Tag candidates and unused concepts are *queues*, not errors;
  never "fix" them by deleting anything.

If the scanner itself errors or can't find a profile, stop and report that. A vault you
can't parse is the finding.

## 2. Fix what is mechanically safe

Fix directly, then note it in the report:

- **Frontmatter:** add missing `updated`/`created` (use the file's last commit date via
  `git log -1 --format=%ad --date=short -- <path>`, never today's date — inventing a date
  is fabricating history), normalise date formats, add an empty `tags: []`.
- **Broken links** where the intended target is *unambiguous* — an obvious rename or
  typo with exactly one plausible match. If two notes could be meant, do not guess:
  report it.
- **Wrong domain directory:** move the file to match its declared `domain`, or correct
  the frontmatter if the directory is clearly right. Pick using the note's content, and
  say which you did and why.

**Never fix by deleting.** Never resolve a content contradiction. Never edit anything in
`raw/`. Never touch `system/cairn/` or `.claude/skills/` — if the scanner reports drift
there, that is a finding for the report, not something to repair locally.

Regenerating `wiki/lexicon.md` or filing raw items is **kb-compile's** job, not yours. If
the scanner reports lexicon drift, the correct fix is "run a compile" — say so.

## 3. The judgment pass

This is the half a script cannot do. Read the notes — actually read them.

1. **Contradictions.** Two notes asserting incompatible facts: different dates for the
   same event, a project whose status disagrees with its parent goal, a decision
   superseded in one note but still `status: active` in another, figures that don't
   reconcile. **Report these; never silently pick a winner.** Quote both sides with file
   paths so the user can adjudicate in seconds.
2. **Gaps.** A goal with no project serving it. A project with no next action. A vision
   with no goals. A person referenced repeatedly with no note. A domain that has been
   empty since the vault was created — that's a signal the domain is wrong for this
   vault, worth saying once.
3. **Connections.** Notes that clearly relate but don't link. Three or more notes
   circling a theme with no synthesis note — propose it, name what it would say that none
   of them says alone, and let the user decide. Don't write it here; that's compile's job.
4. **Terms worth defining.** The `tag-candidate` list plus any phrase that recurs across
   notes with vault-specific meaning. Propose additions to `raw/key-terms.md` — as
   suggestions the user copies in. **Never edit that file.**

Cap the judgment findings at what's genuinely worth acting on. A report with 40 items
gets skimmed and ignored; six real ones get read. If you cut things, say how many and why.

## 4. Report

Write `system/lint-reports/YYYY-MM-DD.md`:

```markdown
---
type: report
domain: <default domain from the profile>
created: YYYY-MM-DD
updated: YYYY-MM-DD
tags: [lint]
---
# Lint report — YYYY-MM-DD

**Scanned:** <n> notes · **Errors:** <n> · **Warnings:** <n> · **Fixed automatically:** <n>

## Fixed automatically
| What | Where | Change |

## Needs your decision
### Contradictions
> quote both sides, with paths

### Stale / blocked

## Suggestions
### Connections worth making
### Terms worth defining

## Clean
What was checked and found healthy — name the checks, so "clean" means something.
```

Reports are notes: they need valid frontmatter and must be reachable. Link the newest
from `wiki/index.md` (replace the previous report's link rather than accumulating — the
directory is the archive).

## 5. Close the loop

1. Log: `| YYYY-MM-DD | lint | <n> errors, <n> warnings, <n> fixed: <one-line> |`
2. Commit: `lint: <short summary>`. Never stage `system/cairn/` or `.claude/skills/`.
3. If `sync.multi_machine` and a remote is configured: `git push`.
4. Report to the user: the headline counts, what you fixed, and — first — anything
   needing their decision. Lead with what's broken, not with what's fine.

## Edge cases

- **Zero findings:** say so plainly and still write the report, log, and commit. The
  heartbeat is the proof the run happened.
- **A finding you can't safely fix or confidently judge:** report it with what you'd need
  to resolve it. Guessing in a health check is worse than the original defect.
- **The scanner disagrees with your reading** (e.g. it calls a link broken but you can see
  the target): trust the scanner about *files*, trust yourself about *meaning*, and report
  the disagreement — it usually means a real inconsistency such as a duplicate basename.
- **Huge vaults:** if findings exceed ~50, report counts by category, detail the errors,
  and sample the rest. Say explicitly that you sampled, and how many were dropped.
- **A human edit that looks like a defect:** human edits are authoritative (rule 2).
  Report it, never revert it.
