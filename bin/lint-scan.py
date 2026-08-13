#!/usr/bin/env python3
"""
lint-scan — deterministic health checks for a cairn vault.

    python3 lint-scan.py [vault-path] [--json]

Emits the mechanical findings: schema violations, undeclared domains and types,
broken links, orphans, stale projects, and lexicon drift. It deliberately does
NOT judge content — contradictions, gaps, and interesting connections are the
skill's job, because they need reading comprehension rather than a parser.

Stdlib only, by design: a vault should stay lintable on any machine with python3
and nothing installed.

Exit code is 0 unless --strict is passed, in which case any error-severity
finding exits 1. Findings are not failures; a vault with findings is normal.
"""

import sys, os, re, json, glob, datetime

# ---------------------------------------------------------------- yaml subset

def _scalar(v):
    v = v.strip()
    # strip trailing inline comment (YAML requires whitespace before '#'),
    # but never inside a quoted scalar
    if v[:1] not in ("\"", "'"):
        v = re.sub(r"\s+#.*$", "", v).strip()
    if not v or v in ("~", "null"):
        return None
    if v[0] in "[":                                   # inline list
        inner = v[1:v.rindex("]")] if "]" in v else v[1:]
        return [_scalar(x) for x in inner.split(",") if x.strip()]
    if v[0] in "\"'" and v[-1] == v[0] and len(v) > 1:
        return v[1:-1]
    if v in ("true", "True"):  return True
    if v in ("false", "False"): return False
    if re.fullmatch(r"-?\d+", v): return int(v)
    return v

def parse_yaml(text):
    """Minimal YAML: nested maps, block sequences of maps, inline lists, folded
    scalars. Enough for cairn frontmatter and vault-profile.yml; not general."""
    root = {}
    stack = [(-1, root)]
    lines = text.splitlines()
    i = 0
    while i < len(lines):
        raw = lines[i]; i += 1
        if not raw.strip() or raw.lstrip().startswith("#"):
            continue
        indent = len(raw) - len(raw.lstrip())
        line = raw.strip()

        while len(stack) > 1 and indent <= stack[-1][0]:
            stack.pop()
        parent = stack[-1][1]

        if line.startswith("- "):                     # sequence item
            item = line[2:].strip()
            if not isinstance(parent, list):
                continue
            if ":" in item and not item.startswith(("\"", "'")):
                k, _, v = item.partition(":")
                d = {k.strip(): _scalar(v)}
                parent.append(d)
                stack.append((indent, d))
            else:
                parent.append(_scalar(item))
            continue

        if ":" not in line:
            continue
        key, _, val = line.partition(":")
        key, val = key.strip(), val.strip()

        if val in (">-", ">", "|", "|-"):             # folded/literal block
            buf = []
            while i < len(lines) and (not lines[i].strip() or
                                      len(lines[i]) - len(lines[i].lstrip()) > indent):
                buf.append(lines[i].strip()); i += 1
            if isinstance(parent, dict):
                parent[key] = " ".join(b for b in buf if b)
            continue

        if val == "":
            nxt = None
            for j in range(i, len(lines)):
                if lines[j].strip() and not lines[j].lstrip().startswith("#"):
                    nxt = lines[j]; break
            child = [] if (nxt and nxt.strip().startswith("- ")
                           and len(nxt) - len(nxt.lstrip()) >= indent) else {}
            if isinstance(parent, dict):
                parent[key] = child
            stack.append((indent, child))
        else:
            if isinstance(parent, dict):
                parent[key] = _scalar(val)
    return root

def frontmatter(path):
    try:
        text = open(path, encoding="utf-8").read()
    except Exception as e:
        return None, f"unreadable: {e}"
    if not text.startswith("---"):
        return None, "no frontmatter block"
    end = text.find("\n---", 3)
    if end == -1:
        return None, "unterminated frontmatter block"
    try:
        return parse_yaml(text[4:end]), None
    except Exception as e:
        return None, f"unparseable frontmatter: {e}"

# ---------------------------------------------------------------- the checks

BASE_TYPES = {"note", "article", "synthesis", "person", "decision", "idea",
              "reference", "project", "concept", "index"}
BASE_REQUIRED = {"type", "domain", "created", "updated"}
TYPE_REQUIRED = {
    "article": ["source", "author", "clipped"],
    "project": ["status"],
    "concept": ["aliases", "source", "status"],
}
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}")

class Scan:
    def __init__(self, root):
        self.root = root
        self.findings = []
        self.profile = {}
        self.notes = {}          # basename -> relpath

    def add(self, sev, cat, msg, path=None, fix=None):
        self.findings.append({"severity": sev, "category": cat, "message": msg,
                              "path": path, "mechanical_fix": fix})

    # -- setup ------------------------------------------------------------
    def load_profile(self):
        p = os.path.join(self.root, "system", "vault-profile.yml")
        if not os.path.exists(p):
            self.add("error", "profile", "system/vault-profile.yml missing — "
                     "cannot validate domains or types. Is this a cairn vault?")
            return False
        self.profile = parse_yaml(open(p, encoding="utf-8").read())
        return True

    def domains(self):
        return [d.get("id") for d in (self.profile.get("domains") or [])
                if isinstance(d, dict)]

    def types(self):
        add = ((self.profile.get("types") or {}).get("add")) or []
        return BASE_TYPES | {t.get("id") for t in add if isinstance(t, dict)}

    def type_requirements(self):
        req = {k: list(v) for k, v in TYPE_REQUIRED.items()}
        for t in ((self.profile.get("types") or {}).get("add")) or []:
            if isinstance(t, dict) and t.get("id"):
                extra = t.get("requires") or []
                req.setdefault(t["id"], [])
                req[t["id"]] += [e for e in extra if e]
        return req

    def conv(self, key, default=None):
        return (self.profile.get("conventions") or {}).get(key, default)

    # -- checks -----------------------------------------------------------
    def scan_notes(self):
        declared, types, reqs = set(self.domains()), self.types(), self.type_requirements()
        wiki = os.path.join(self.root, "wiki")
        for path in sorted(glob.glob(os.path.join(wiki, "**", "*.md"), recursive=True)):
            rel = os.path.relpath(path, self.root)
            base = os.path.splitext(os.path.basename(path))[0]
            if base in self.notes:
                self.add("error", "duplicate", f"two notes share the basename "
                         f"'{base}' — wikilinks to it are ambiguous", rel)
            self.notes[base] = rel

            fm, err = frontmatter(path)
            if err:
                self.add("error", "frontmatter", err, rel)
                continue

            # `index` notes are generated maps, not knowledge notes: they carry
            # no domain and no creation date by design (see the engine template).
            required = {"type", "updated"} if fm.get("type") == "index" else BASE_REQUIRED
            for k in sorted(required - set(fm)):
                self.add("error", "frontmatter", f"missing required key '{k}'", rel,
                         fix=f"add {k}:")

            t, d = fm.get("type"), fm.get("domain")
            if t and t not in types:
                self.add("error", "type", f"type '{t}' is not in the base registry "
                         f"and not declared in the profile", rel)
            if d and d != "concepts" and d not in declared:
                self.add("error", "domain", f"domain '{d}' is not declared in "
                         f"system/vault-profile.yml", rel)

            for k in reqs.get(t, []):
                if k not in fm:
                    self.add("error", "frontmatter",
                             f"type '{t}' requires key '{k}'", rel, fix=f"add {k}:")

            for k in ("created", "updated"):
                v = fm.get(k)
                if v is not None and not DATE_RE.match(str(v)):
                    self.add("error", "dates", f"{k}: '{v}' is not ISO YYYY-MM-DD", rel)
            c, u = str(fm.get("created", "")), str(fm.get("updated", ""))
            if DATE_RE.match(c) and DATE_RE.match(u) and u < c:
                self.add("warn", "dates", f"updated ({u}) precedes created ({c})", rel)

            # location must match declared domain
            parts = rel.split(os.sep)
            if len(parts) > 2 and d and d != "concepts":
                if parts[1] != d:
                    self.add("warn", "location",
                             f"filed under wiki/{parts[1]}/ but declares domain '{d}'", rel)

            # the constitution requires notes to end with a Connections section;
            # generated maps and reports are exempt
            if fm.get("type") not in ("index", "report"):
                body = open(path, encoding="utf-8").read()
                if not re.search(r"^##+\s+Connections\s*$", body, re.M):
                    self.add("warn", "connections",
                             "no '## Connections' section — the note cannot be "
                             "reached by following links from its neighbours", rel)

            fm["_path"], fm["_rel"] = path, rel
            self.notes[base] = rel
            self.meta = getattr(self, "meta", {})
            self.meta[base] = fm

    def check_links(self):
        extra = {"CLAUDE", "README", "constitution", "build-plan", "sync-setup",
                 "vault-profile"}
        known = set(self.notes) | extra
        self.graph = {}
        for base, rel in self.notes.items():
            text = open(os.path.join(self.root, rel), encoding="utf-8").read()
            targets = []
            for m in re.findall(r"\[\[([^\]]+)\]\]", text):
                t = m.split("|")[0].strip()
                if t.startswith("wiki/") or t.endswith("/"):
                    continue
                targets.append(t)
                if t not in known:
                    self.add("error", "link", f"broken wikilink [[{t}]]", rel)
            self.graph[base] = targets

    def check_orphans(self):
        if "index" not in self.notes:
            self.add("error", "index", "wiki/index.md is missing — nothing is reachable")
            return
        seen, stack = set(), ["index"]
        while stack:
            n = stack.pop()
            if n in seen:
                continue
            seen.add(n)
            stack.extend(self.graph.get(n, []))
        for base, rel in sorted(self.notes.items()):
            if base not in seen:
                self.add("warn", "orphan",
                         "not reachable from wiki/index.md by following links", rel)

    def check_projects(self):
        parent = self.conv("project_parent")
        stale_days = self.conv("stale_project_days", 14) or 14
        today = datetime.date.today()
        for base, fm in getattr(self, "meta", {}).items():
            if fm.get("type") != "project":
                continue
            rel = fm["_rel"]
            if fm.get("status") == "active":
                u = str(fm.get("updated", ""))
                if DATE_RE.match(u):
                    age = (today - datetime.date.fromisoformat(u[:10])).days
                    if age > stale_days:
                        self.add("warn", "stale",
                                 f"active project not updated in {age} days "
                                 f"(threshold {stale_days})", rel)
            if parent:
                text = open(os.path.join(self.root, rel), encoding="utf-8").read()
                linked = [t.split("|")[0].strip()
                          for t in re.findall(r"\[\[([^\]]+)\]\]", text)]
                if not any(getattr(self, "meta", {}).get(l, {}).get("type") == parent
                           for l in linked):
                    self.add("warn", "orphan-project",
                             f"project links to no '{parent}' note "
                             f"(conventions.project_parent)", rel)

    # -- lexicon ----------------------------------------------------------
    def parse_key_terms(self):
        p = os.path.join(self.root, "raw", "key-terms.md")
        if not os.path.exists(p):
            return {}
        text = open(p, encoding="utf-8").read()
        if "\n---\n" not in text:
            return {}
        body = text.split("\n---\n", 1)[1]
        terms, cur, buf = {}, None, []
        for line in body.splitlines():
            if line.startswith("## "):
                if cur:
                    terms[cur] = "\n".join(buf).strip()
                cur, buf = line[3:].strip(), []
            elif cur:
                buf.append(line)
        if cur:
            terms[cur] = "\n".join(buf).strip()
        return terms

    def check_lexicon(self):
        cdir = os.path.join(self.root, "wiki", "concepts")
        concepts = {}
        for path in sorted(glob.glob(os.path.join(cdir, "*.md"))):
            base = os.path.splitext(os.path.basename(path))[0]
            fm, err = frontmatter(path)
            if err:
                continue
            text = open(path, encoding="utf-8").read()
            m = re.search(r"## Source \(verbatim[^)]*\)\s*\n```\n(.*?)\n```",
                          text, re.S)
            concepts[base] = {"fm": fm, "src": (m.group(1).strip() if m else None),
                              "rel": os.path.relpath(path, self.root)}

        raw_terms = self.parse_key_terms()

        for term, block in raw_terms.items():
            if term not in concepts:
                self.add("warn", "lexicon",
                         f"term '{term}' is in raw/key-terms.md but has no concept "
                         f"note — a terms pass has not run since it was added")

        for name, c in concepts.items():
            src, status = c["src"], c["fm"].get("status")
            if src is None:
                self.add("error", "lexicon",
                         "concept note has no '## Source (verbatim)' block — "
                         "change detection cannot work for it", c["rel"])
                continue
            if name in raw_terms:
                if raw_terms[name] != src and status == "active":
                    self.add("error", "lexicon",
                             "source block does not match raw/key-terms.md — "
                             "a terms pass was missed; the wiki disagrees with the "
                             "glossary", c["rel"])
                if status == "archived":
                    self.add("warn", "lexicon",
                             "archived, but the term is present in raw/key-terms.md "
                             "again — should be reactivated", c["rel"])
            else:
                if status == "active" and c["fm"].get("source") == "key-terms.md":
                    self.add("error", "lexicon",
                             "active and sourced from key-terms.md, but the term is "
                             "gone from that file — should be archived", c["rel"])

        # lexicon table vs disk
        lex = os.path.join(self.root, "wiki", "lexicon.md")
        if not os.path.exists(lex):
            if concepts:
                self.add("error", "lexicon", "wiki/lexicon.md is missing")
        else:
            ltext = open(lex, encoding="utf-8").read()
            listed = set(re.findall(r"\|\s*\[\[([^\]]+)\]\]", ltext))
            for name, c in concepts.items():
                if name not in listed:
                    self.add("error", "lexicon",
                             f"concept '{name}' exists on disk but is not in "
                             f"wiki/lexicon.md — regenerate the lexicon", c["rel"])
            for name in listed:
                if name not in concepts:
                    self.add("error", "lexicon",
                             f"wiki/lexicon.md lists '{name}' but no concept note "
                             f"exists", "wiki/lexicon.md")

        # unregistered tags -> concept candidates
        counts = {}
        for base, fm in getattr(self, "meta", {}).items():
            for t in (fm.get("tags") or []):
                if t:
                    counts[t] = counts.get(t, 0) + 1
        for tag, n in sorted(counts.items(), key=lambda x: -x[1]):
            if tag not in concepts:
                self.add("info", "tag-candidate",
                         f"tag '{tag}' used on {n} note(s) has no concept note — "
                         f"candidate for raw/key-terms.md")

        # concepts defined but never referenced
        body_refs = set()
        for base, rel in self.notes.items():
            if rel.startswith(os.path.join("wiki", "concepts")) or base == "lexicon":
                continue
            text = open(os.path.join(self.root, rel), encoding="utf-8").read()
            body_refs |= {t.split("|")[0].strip()
                          for t in re.findall(r"\[\[([^\]]+)\]\]", text)}
        for name, c in concepts.items():
            if name not in body_refs and c["fm"].get("status") == "active":
                self.add("info", "unused-concept",
                         "defined but never linked from any note", c["rel"])

    def run(self):
        if not self.load_profile():
            return self.findings
        self.scan_notes()
        self.check_links()
        self.check_orphans()
        self.check_projects()
        self.check_lexicon()
        return self.findings


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    flags = {a for a in sys.argv[1:] if a.startswith("--")}
    root = os.path.abspath(args[0]) if args else os.getcwd()

    s = Scan(root)
    findings = s.run()
    order = {"error": 0, "warn": 1, "info": 2}
    findings.sort(key=lambda f: (order.get(f["severity"], 9), f["category"],
                                 f["path"] or ""))

    if "--json" in flags:
        print(json.dumps({"vault": root, "counts": {
            k: sum(1 for f in findings if f["severity"] == k)
            for k in ("error", "warn", "info")}, "findings": findings}, indent=2))
    else:
        print(f"lint-scan: {root}")
        print(f"  notes scanned: {len(s.notes)}")
        for sev in ("error", "warn", "info"):
            group = [f for f in findings if f["severity"] == sev]
            if not group:
                continue
            print(f"\n{sev.upper()} ({len(group)})")
            for f in group:
                loc = f" [{f['path']}]" if f["path"] else ""
                print(f"  - ({f['category']}) {f['message']}{loc}")
        if not findings:
            print("\n  clean — no mechanical findings.")
        print("\nNote: contradictions, gaps, and cross-domain connections are NOT "
              "checked here.\nThose need reading comprehension — see the kb-lint skill.")

    if "--strict" in flags and any(f["severity"] == "error" for f in findings):
        sys.exit(1)


if __name__ == "__main__":
    main()
