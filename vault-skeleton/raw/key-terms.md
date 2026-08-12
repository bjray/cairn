# Key Terms

Your glossary. Terms, names, and phrases that carry special meaning in this vault —
so any Claude session reads them the way you mean them, not the way a dictionary does.

**This is a standing file.** Unlike `inbox.md`, it is never cleared and never moved to
`_processed/`. Edit it whenever you want. The compiler reads it on every run, detects
what changed, and updates the matching concept notes in `wiki/concepts/`.

## Format

Each term is a `##` heading (kebab-case) followed by free-form text. An optional
`aliases:` line lists other phrasings that mean the same thing — this is what lets
sessions recognize the term when you phrase it differently.

```
## the-place
aliases: the place, our place, the property
Free-form definition. As many lines as you want. Write it however you think about it.
```

## Notes

- Editing a term's text updates its concept note and logs the change with a timestamp.
- Removing a term does **not** delete its note — it gets archived (nothing is destroyed).
- Terms defined here win over `[define]` markers in `inbox.md` if both exist.
- You can also define terms on the fly: put `[define] term — meaning` in `inbox.md`,
  or just tell Claude "when I say X, I mean Y" mid-conversation.

---

<!-- Add your terms below this line. -->
