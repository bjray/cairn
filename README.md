# cairn

An AI-compiled personal knowledge base. You dump raw material in; Claude compiles it
into an interlinked markdown wiki, answers questions from it, and keeps it honest.

A cairn is a stack of stones you build by hand to mark a route — each one added by
whoever came through, so the next person can find the way. That's the idea: knowledge
that compounds, in plain files you'll still be able to read in twenty years.

## Engine and store

**cairn is the engine. Your vault is the store.** They live in separate repositories.

The engine holds the operating law, the note templates, and the compiler skill. A vault
holds *your* content plus a profile declaring what that content is made of. The engine is
vendored into each vault under `system/cairn/` and refreshed with one command — so a fix
made once reaches every vault, and a bare `git clone` of any vault still works with no
bootstrap.

This split is what lets one person keep a personal vault on a private remote and a work
vault on a work-owned remote, running the same engine, sharing nothing.

```
cairn/                          your-vault/
├── constitution.md             ├── CLAUDE.md              ← points at the engine
├── templates/                  ├── system/
├── skills/                     │   ├── vault-profile.yml  ← domains, types, conventions
│   ├── kb-compile/             │   ├── cairn/             ← vendored engine
│   └── cairn-init/             │   └── templates/         ← your overrides
├── bin/                        ├── raw/                   ← human territory
├── profile.schema.yml          ├── wiki/                  ← AI territory
└── vault-skeleton/             └── outputs/
```

## Nothing is hard-coded

Domains and note types are **declared per vault**, not baked into the engine. A personal
vault might use `vision / projects / research / health / reference`; a work vault might
use `product / meetings / people / decisions / reference` with types like `meeting-note`
and `retro`. Same engine, different vocabulary.

See `profile.schema.yml` for the schema and `docs/examples/` for both shapes side by side.

## Getting started

```
# create a vault (interviews you about domains and types)
"cairn init ~/Projects/my-kb"

# then, from inside the vault
"compile"
```

Refresh a vault's engine later:

```
sh system/cairn/bin/cairn-update.sh <path-to-cairn> . --apply
```

It's a dry run without `--apply`, and it refuses to run if you've edited engine files
inside the vault — that drift belongs upstream.

## The five behaviors

**Compile** raw material into linked wiki notes · **Answer** questions from the wiki,
citing notes · **Manage** projects and what's stalled · **Lint** for contradictions,
orphans, and schema violations · **Ingest** links and thoughts mid-conversation.

Full definitions in `constitution.md`.

## Key terms

Some words mean something specific to you. `raw/key-terms.md` is a plain glossary you
edit whenever you like; the compiler turns it into concept notes and a one-line-per-term
lexicon that every session reads before answering. Three ways in — the glossary, a
`[define]` marker in the inbox, or just saying it mid-conversation — and one canonical
place it lives.

## Design commitments

- **Plain text, no magic.** Markdown, wikilinks, an index. No vector database, no hidden
  state. A vault must stay fully usable by a human with a text editor and no AI at all.
- **Never destroy knowledge.** Notes are superseded or archived, never deleted.
- **Silence is failure.** Every raw item is either filed or explicitly reported. A run
  that finds nothing still logs a heartbeat.
- **Git is the sync layer.** Two machines, one private remote, no infrastructure.

## Status

Early. The engine works; the terms pass has partial eval coverage (see
`skills/kb-compile/evals/evals.json` — ids 3–7 are written but not yet run).
Built as a DIY answer to one person's actual needs, then generalized.

Run `sh bin/scrub-check.sh` before sharing this repo — it's the gate that keeps vault
content out of the engine.
