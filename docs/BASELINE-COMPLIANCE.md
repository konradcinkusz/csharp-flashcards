# Baseline compliance

`architecture-standards`' [`REPO-BASELINE.md`](https://github.com/konradcinkusz/architecture-standards/blob/main/docs/guides/REPO-BASELINE.md)
§7 is titled **"Standards adoption is declared, not remembered"**. This is that
declaration for `csharp-flashcards`, one row per §9 checklist item.

The useful column is the third. Several baseline items genuinely do not apply to
a LaTeX deck, and without a stated reason each absence looks like neglect — so
every **N/A** carries both why it does not apply *and* the condition under which
it would start to.

Written after the work rather than alongside it: every **Yes** links to a file
that exists in this repository today. A compliance document describing intentions
is the staleness §8 warns about.

---

## §1 The baseline

| Item | Answer | Evidence, or why not |
|---|---|---|
| `CODEOWNERS` | **Yes** | [`.github/CODEOWNERS`](../.github/CODEOWNERS). Blanket ownership, with `main.tex`, `mybeamer.cls`, `mybeamer.sty`, `.github/workflows/`, `scripts/` and `.gitleaks.toml` called out separately — those are [`ROADMAP.md`](../ROADMAP.md) §5's protected paths, and breaking one breaks every *later* pull request rather than only its own. `areas/*.tex` are deliberately not listed: a LaTeX error in one card is contained, obvious, and named by the compiler |
| Dependency update automation | **Yes, one ecosystem** | [`.github/dependabot.yml`](../.github/dependabot.yml) covers `github-actions`. No `npm` or `nuget` entry because there is no package manifest anywhere: the C# in this repository is illustrative listings inside slides and is never compiled, and the scripts under `scripts/` import only the Python standard library. The eight pinned Actions are the only third-party code in the tree — and `ci.yml`'s release job runs with `contents: write`, so they execute with credentials that can write here |
| `.editorconfig` | **Yes** | [`.editorconfig`](../.editorconfig). `trim_trailing_whitespace` is off for `*.md` deliberately: `README.md` lines 34 and 98 end in exactly two spaces, which is a Markdown hard line break, so a trimming editor would silently reflow the rendered page. `LICENSE` has its own carve-out — it ships with no final newline and nothing should reformat verbatim licence text |
| `Directory.Build.props` + `Directory.Packages.props` | **N/A** | Central *package* management for a repository with no packages. There is no `.csproj` and no dependency to centralise; the C# here is never built. **Applies the day this repository acquires a real project** — for instance if the code listings were ever extracted into a compiled sample solution that CI checks |
| PR + issue templates | **Yes** | [`pull_request_template.md`](../.github/pull_request_template.md) asks for the card count before and after, a green run rather than an assertion that one would be green, and — for a change to the class or style file — what was checked in the rendered PDF, because a style change is invisible in the diff and obvious on the page. Two issue forms, [`card-correction`](../.github/ISSUE_TEMPLATE/card-correction.yml) and [`build-problem`](../.github/ISSUE_TEMPLATE/build-problem.yml), split the two genuinely different reports this repository receives |
| Real `.gitattributes` | **Yes** | [`.gitattributes`](../.gitattributes). Rules, not a commented-out template: LF normalisation, explicit `text` for every format present, `binary` for PDFs and fonts. The normalisation was a no-op when added — all 38 tracked files were already LF — which is exactly when to write it down, so no reformatting commit is ever tangled into a content change |
| `.dockerignore`, exclusion-based | **N/A** | Nothing here is containerised. There is no Dockerfile and no image; the artifact is a PDF built by CI. **Applies if the deck is ever built inside a container image** rather than by `xu-cheng/latex-action` on a runner |
| Secret scanning: pre-commit **and** CI | **Yes** | §2 below |
| CodeQL / SAST + dependency audit | **N/A for SAST; N/A for audit**, and both are closer than they were | There is no compiled first-party code. The nearest thing is `scripts/lint-cards.py` and two migration scripts, which read files in the tree and write files in the tree. **SAST applies the day a script here takes untrusted input or touches a credential** — neither does today. No dependency audit because there is nothing to audit beyond the Actions, which Dependabot covers |
| CI runs the linters and tests the repo claims | **Yes** | [`build.yml`](../.github/workflows/build.yml) runs `scripts/lint-cards.py` and then compiles `main.tex`, on every push and pull request. This is the item this repository failed hardest: before the roadmap, its only workflow triggered on `v*` tags, no tag had ever been pushed, and **7,617 lines of LaTeX had reached the default branch with no build behind them** while the README promised contributors that "automated checks will compile the PDF" |

---

## §2 Secret hygiene

| Item | Answer | Evidence, or why not |
|---|---|---|
| Pre-commit hook **and** CI job | **Yes** | [`scripts/hooks/pre-commit`](../scripts/hooks/pre-commit) and [`secret-scan.yml`](../.github/workflows/secret-scan.yml), sharing [`.gitleaks.toml`](../.gitleaks.toml). CI scans full history at `fetch-depth: 0`, plus weekly — a commit clean in March can be a finding in June. The hook **fails** rather than warns when no scanner is available: protection that depends on the developer's toolchain is the "enforced only by human recall" failure §1 names. Both halves were proved by planting a synthetic key and watching each refuse it |
| Local scripts read secrets from a gitignored `.env` with a committed example | **N/A** | No script here reads a secret. They read `.tex` files and write `.tex` files; the secret scanner takes no credential of its own. There is no variable whose value a `secrets.env.example` could document. **Applies the moment a script needs to authenticate to anything** — and `.gitleaks.toml` records the corollary: the first secret introduced gets its detection rule in the same commit |
| Rotate before scrubbing history | **Yes, as procedure** | Stated in `.gitleaks.toml`, in the workflow's failure summary, and in the hook's refusal message. Never exercised — no genuine finding has occurred |

---

## §4 Operational scripts

| Item | Answer | Evidence, or why not |
|---|---|---|
| CI jobs mirrored locally | **Yes** | `python3 scripts/lint-cards.py` is literally the command CI runs, and [`scan-secrets.sh`](../scripts/scan-secrets.sh) reproduces the secret-scan job, so "it passed locally" means something |
| Numbered, delegating runbook scripts; hand-off token files; destroy lists | **N/A** | §4's runbook shape is for a repository with a deploy sequence. There is nothing here to deploy: the outputs are a PDF built on a runner and a static page on GitHub Pages, neither of which has ordered teardown |
| Scripts README with variable tiers | **N/A** | Five scripts, none taking an environment variable. What a contributor needs to know about them is in [`CONTRIBUTING.md`](../CONTRIBUTING.md), which is where they will look |

---

## §3, §4a, §4b, §4c, §5, §6

| Item | Answer | Evidence, or why not |
|---|---|---|
| §3 One-command interactive setup | **Partly** | [`scripts/install-hooks.sh`](../scripts/install-hooks.sh) is the only setup step there is, and `CONTRIBUTING.md` names it. There is no secret store to initialise and no mandatory secret to generate, so the interactive onboarding §3 describes would be a script with nothing to ask |
| §4a A script that onboards the *product's* user | **N/A** | The product is a PDF. Its user opens it |
| §4b Per-project dependency counts published | **Yes, trivially** | Zero runtime dependencies. The build needs a TeX distribution with `minted`, `tikz`, `fontawesome5` and Pygments, which `CONTRIBUTING.md` states with the command that uses them |
| §4c Research artifacts in-repo; PDFs built in CI rather than committed | **Yes** | The deck itself is the case in point: `.gitignore` excludes `*.pdf`, and [`build.yml`](../.github/workflows/build.yml) uploads it as a run artifact. No PDF is committed. There is no algorithm here whose correctness is arguable, so the reference-notebook half does not apply |
| §5 Retired workflows archived, never comment-disabled | **Yes, vacuously** | No workflow has been retired. All four are live and triggered. Recorded so that the first retirement goes to `workflows-archive/` rather than behind a comment |
| §6 AI agent definitions in-repo | **N/A** | No agent definitions exist here. **Applies the day one is added** — it goes in `.claude/agents/` with allowlisted tools and repo-relative paths, not in someone's local configuration |

---

## §7 Standards adoption

| Item | Answer | Evidence, or why not |
|---|---|---|
| `.claude/settings.json` declares the marketplace and enables `architecture-core` | **Yes** | [`.claude/settings.json`](../.claude/settings.json). This repository *is* meant to conform: the whole of the roadmap's Phase 4 is `REPO-BASELINE.md` applied here. Declaring conformance while omitting the item that declares it would be incoherent. Standing cost is about 990 tokens of skill descriptions; remove the file to opt out |
| This document | **Yes** | You are reading it |

---

## §8 Documentation staleness

| Item | Answer | Evidence, or why not |
|---|---|---|
| README claims verified in review | **Yes, and mechanically** | Three roadmap issues did nothing else: #15 fixed two badges that resolved to nothing and a Contributing section promising CI that did not exist, #20 reconciled an edition year that said 2025 on the artifact and 2026 on the front page, and #22 found the landing page claiming 13 topic areas against 24 — listing 13, so LINQ was missing entirely. **`scripts/lint-cards.py` now checks the landing page's counts against the deck on every run**, so the class of defect cannot return silently |
| One named source of truth per environment variable | **N/A** | This repository defines no environment variables. The nearest equivalent is the repository URL, which used to be hardcoded twice — both copies naming a repository that is not this one — and is now `\RepoURL`, defined once in `mybeamer.cls` |

---

## What is not claimed

**The deck's content has not been audited for correctness.** 269 cards assert things about C#, .NET, Azure, Kubernetes and OAuth, and nothing in this repository checks any of them. CI checks that the deck *builds* and that cards are *written* correctly, which is a different question. The `card-correction` issue form exists because that gap is expected to be closed by readers rather than by a tool.

**No release has been cut.** The PDF is obtainable by running the release workflow; `releases/latest` links do not work yet, and `scripts/lint-cards.py` fails if one is added before a release exists. Delete that check in the same commit that pushes the first `v*` tag.
