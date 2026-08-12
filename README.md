# Life OS — Plumbing Vault

A stripped copy of the Life OS structure with **no personal content**. It exists to test
one thing: the **key terms / lexicon** mechanism, on a machine where the real vault
shouldn't live.

## What's here

Structure, templates, the constitution, and the `kb-compile` skill. That's it.

```
raw/key-terms.md              ← your glossary (empty scaffold)
raw/inbox.md                  ← header only
wiki/reference/concepts/      ← where concept notes land (empty)
wiki/reference/lexicon.md     ← generated registry (0 terms)
system/templates/concept.md   ← the note shape
.claude/skills/kb-compile/    ← the compiler, including the terms pass
```

**What's deliberately missing:** every compiled note, all raw material, the build plan,
the sync setup, and — most importantly — any git history connecting this to the primary
`life-os` repo. There is nothing here to leak.

## Hard rule

**Never add a remote pointing at the primary `life-os` repo. Never pull or push between
the two.** Terms travel home by copy-paste, not by git. Wiring them together would defeat
the entire reason this vault exists.

## Testing the terms mechanism

1. Add a few terms to `raw/key-terms.md`:

   ```
   ## the-place
   aliases: the place, our place, the property
   The property we actually want to live on. Not a house — land, view, room for people.
   ```

2. Say **"compile"**. Expect: a concept note per term in `wiki/reference/concepts/`,
   `wiki/reference/lexicon.md` regenerated with one row each, a log row, and a commit.
3. **Edit** one term's wording in `key-terms.md`. Compile again. Expect: only that note
   updates, `updated` bumps, and `## History` gains a timestamped line holding the prior
   text. Untouched terms should not be modified at all.
4. **Delete** a term from `key-terms.md`. Compile. Expect: `status: archived`, a History
   line, and a move to the lexicon's archived section — **not** a deleted file.
5. Add a `[define] term — meaning` line to `raw/inbox.md`. Compile. Expect: a concept
   note sourced from `inbox`, and that line cleared from the inbox afterward.

Steps 3 and 4 are the ones worth watching closely — they're the paths that have no eval
coverage yet in the primary vault.

## Carrying results home

Anything you want to keep: copy the term text out of this `raw/key-terms.md` and paste it
into the real one on your personal machine. Note anything the compiler got wrong so the
behavior can be fixed at the source.
