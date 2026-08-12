---
name: cairn-init
description: >-
  Create a new cairn knowledge vault. Use when the user says "cairn init", "create a new
  vault", "set up a knowledge base here", "start a work KB", or otherwise asks to stand up
  a fresh cairn-managed knowledge base. Interviews the user about domains and note types,
  scaffolds the directory structure, writes system/vault-profile.yml, vendors the engine,
  and makes the first commit. Do NOT use this to modify an existing vault — a vault that
  already has system/vault-profile.yml is initialized; edit the profile instead.
---

# cairn-init — stand up a new vault

A vault is data plus a declaration of what that data is made of. This skill produces the
declaration by *asking*, not by assuming — the domains that fit a personal life vault are
wrong for a work one, and guessing wastes the user's time re-filing notes later.

## 0. Preflight

1. **Confirm the target path** with the user before creating anything. If it exists and is
   non-empty, stop and ask — never scaffold over existing files.
2. **Refuse if `system/vault-profile.yml` already exists** — that vault is initialized.
   Point the user at the profile instead.
3. **Locate the engine.** You need the cairn repo (constitution, templates, skills,
   vault-skeleton). If you can't find it, ask for its path rather than reconstructing it
   from memory — a hand-rebuilt engine is drift on day one.

## 1. Interview

Ask in this order. **One question at a time** — this is a design conversation, not a form.
Propose a concrete starting set each time rather than asking open-ended; it is far easier
to react to a draft than to invent from nothing.

1. **What is this vault for?** One line. Becomes `vault.description`.
2. **Domains.** Propose 4–6 based on their answer, each with a one-line purpose. Push back
   on more than about seven — domains are top-level shelves, and too many means nothing
   ever feels like it belongs anywhere. Ask which should be the `default` for items that
   fit nowhere.
3. **Types beyond the base registry.** Show them the base
   (`note article synthesis person decision idea reference project concept index`) and ask
   what's missing for their work. For each addition, get its required frontmatter keys.
   Zero additions is a perfectly good answer.
4. **Conventions.** Does a project ladder up to something (`project_parent`)? How long
   before a project counts as stale?
5. **Sync.** One machine or several? Will there be a remote? Anything a future session
   must know before pushing — especially if this is a work-owned repository.

Read the answers back as a summary before writing anything.

## 2. Scaffold

1. Copy `vault-skeleton/` to the target path.
2. Create `wiki/<id>/` for each declared domain, each with a `.gitkeep`.
3. Vendor the engine into `system/cairn/`: `constitution.md`, `templates/`, `bin/`, and a
   `VERSION` file recording the engine commit this vault was initialized from.
4. Install the engine skills into `.claude/skills/` (`kb-compile`, and `cairn-init` only
   if the user wants to create further vaults from inside this one).
5. Write `system/vault-profile.yml` from the interview. Follow `profile.schema.yml`.
6. **Render every `.tmpl` in the skeleton, then remove the `.tmpl` files.** There are
   three, and missing one leaves raw `{{placeholders}}` in a live vault:
   - `CLAUDE.md.tmpl` → `CLAUDE.md` — vault name, description, sync specifics
   - `wiki/index.md.tmpl` → `wiki/index.md` — one section per domain, in profile order,
     each purpose as its subtitle. Empty domains are listed with no entries; that's
     correct, not a gap.
   - `wiki/lexicon.md.tmpl` → `wiki/lexicon.md` — the empty registry, dated today

   Don't hardcode this list — render whatever `.tmpl` files the skeleton actually
   contains, so a template added later can't be silently skipped.
8. Leave `raw/inbox.md` and `raw/key-terms.md` as the skeleton's empty scaffolds. Do not
   seed example content — a vault that ships with fake notes teaches the compiler to
   treat fiction as knowledge.

## 3. Verify before committing

- Every declared domain has a directory; every directory maps to a declared domain.
- `wiki/concepts/` and `wiki/lexicon.md` exist and no domain is named `concepts`.
- No template placeholder (`{{...}}`) survives in any rendered file.
- **Run `system/cairn/bin/scrub-check.sh`** if this vault will live anywhere shared —
  a fresh vault should be trivially clean, and a hit means the skeleton is contaminated.

## 4. Commit and report

1. `git init` if not already a repo. Do **not** add a remote — the user configures that
   themselves, deliberately. Never point a new vault at another vault's remote.
2. Append the first row to `system/log.md`:
   `| YYYY-MM-DD | init | Vault created — <n> domains, <n> added types, engine <version> |`
3. Commit: `init: <vault-name> — cairn vault scaffolded`.
4. Report: the domains and types created, where the vault lives, the engine version
   vendored, and the next step — add terms to `raw/key-terms.md` and say "compile".

## Edge cases

- **The user wants domains that overlap heavily** ("projects" and "work"): say so once,
  propose a merge, then do what they choose. It is their vault.
- **The user asks to copy an existing vault's profile:** fine, and faster — read that
  profile, confirm each section still applies, then write it. Copy the *schema*, never
  the content.
- **A work-owned target repo:** flag once, before the first commit, that engine
  improvements made inside it may be work product, and that personal content must never
  land there. Then proceed.
- **No engine repo reachable:** stop and ask. Do not reconstruct the constitution or
  templates from memory — a vault built on a hallucinated engine will silently disagree
  with every other vault.
