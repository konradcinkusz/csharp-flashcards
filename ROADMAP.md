# Roadmap

How this repository gets from a deck that has never been built by CI to one that
builds, ships, and says true things about itself.

Milestones carry *what* and *when*. This document carries the two things they
cannot: **why the order is what it is**, and **what must not break**. A future
session — human or agent — should be able to read this file alone and pick up
the work.

Tracking issue: **#30**. It hosts the running log and the decision log.

> **Status: complete.** All four phases and all 17 issues were delivered on
> 2026-09-01, in 18 pull requests, with no force-merges and no skipped issues.
> The measurements in §1 are the state this repository started from and are kept
> as the historical record; §2 records what each phase closed. The execution
> policy in §6 and the protected paths in §5 remain live for future work.

---

## 1. What "complete" means

Not a generic software checklist — this is a LaTeX Beamer flashcard deck, and
the definition is drawn from what the repository already is.

1. **The deck builds in CI and ships.** Every pull request compiles `main.tex`;
   a PDF is obtainable by a reader; both README badges resolve to something
   real.
2. **One authoring convention, applied uniformly.** A card is written with the
   deck's own macros rather than copy-pasted from its neighbour, and difficulty
   is a rendered element rather than raw asterisks in the question string.
3. **Claims match the artifact.** The card count, the edition year, and every
   link in `README.md` and `docs/index.html` are true — and checked by CI, not
   remembered.
4. **The estate's own baseline applied at the right scale.** The owner's
   [`REPO-BASELINE.md`](https://github.com/konradcinkusz/architecture-standards/blob/main/docs/guides/REPO-BASELINE.md)
   governs this repository too. Several of its items genuinely do not apply to a
   document repository; those are *declared* N/A with a re-activation trigger,
   not silently skipped.
5. **A contributor path.** How to add a card, what the difficulty levels mean,
   what CI will check, and how to build locally.

### The state this starts from

Measured on `main` at `d3333e4`, not assumed:

| | |
|---|---|
| Cards (`\QuestionSlide`) | 269 across 24 area files |
| Tags / releases | **0** — `ci.yml` triggers on `v*` only, so it has never run |
| Workflows triggered by `pull_request` | **0** |
| Uses of `\AnswerSlide`, the macro `mybeamer.sty` defines for answers | **0** |
| Badge-overlay boilerplate in `areas/` | 1,926 of 7,554 lines (26%) — the figure first recorded here was 1,122, from a grep matching only one of the two spellings the overlay had drifted into; #17 measured the real total when it removed them |
| Cards whose question text begins with a literal `*` | 261 of 269; 8 unrated. The figure first recorded here was "188 of 195 parsed", because the parser could not read a call whose arguments were separated by a comment |
| `.gitignore` patterns dead to inline comments | 3 |
| Landing page card claim vs. actual | "300+" vs 269 |
| Baseline files present | **0 of 6** |

---

## 2. Phases

| Phase | Label | Due | Issues | Goal | Status |
|---|---|---|---|---|---|
| 1 — The build is real | `phase-1-build` | 2026-09-15 | #13, #14, #15 | The deck compiles on every PR, and a reader can obtain the PDF | ✅ closed |
| 2 — One authoring convention | `phase-2-authoring` | 2026-09-29 | #16, #17, #18, #19 | Cards are written one way, and CI enforces it | ✅ closed |
| 3 — Claims match the deck | `phase-3-claims` | 2026-10-13 | #20, #21, #22 | Nothing the repository says about itself is false | ✅ closed |
| 4 — Repo baseline | `phase-4-baseline` | 2026-10-27 | #23, #24, #25, #26, #27, #28, #29 | The estate baseline, applied and declared | ✅ closed |

Phases are represented by the `phase-*` labels above rather than by GitHub
milestones — see §7.

**Cadence.** Two-week phases, assuming a solo maintainer. The commit history is
bursty rather than periodic (Aug 2025, Sep 2025, Apr 2026, Jul 2026), so no
cadence is inferable from it; two weeks is a stated default, not a measurement.
Dates are ordering, not deadlines.

---

## 3. Why this order

**Phase 1 is first because nothing else can be verified without it.** This
repository has no pull-request CI at all, so no change to a 7,617-line LaTeX
tree can currently be shown to compile. Every later phase edits that tree — Phase 2
rewrites all 269 cards. Doing that before there is a build is how a deck
acquires an error nobody notices for four months. #13 is also what makes this
roadmap's own execution policy ("never merge without CI having run") satisfiable.

**Phase 2 before Phase 3** because Phase 3 fixes *claims*, and one of the claims
is a card count that Phase 2's linter is the natural place to enforce. Fixing the
number by hand first would mean fixing it twice.

**Phase 2's own internal order** — macro pilot (#16) → bulk migration (#17) →
difficulty (#18) → linter (#19) — is the expensive lesson made cheap. A defect in
a shared macro is found on 9 cards rather than 269, and the linter is written
against the finished convention rather than an intermediate one that would make
it need rewriting twice.

**Phase 4 last, and its own declaration (#29) last within it**, because a
compliance document that describes intentions rather than files is precisely the
staleness `REPO-BASELINE.md` §8 warns about.

One cross-phase edge runs backwards: **#27 (`.gitattributes`) should land before
#17's bulk migration**, so a 1,100-line mechanical rewrite is not competing with
a line-ending normalisation in the same history.

---

## 4. Dependencies

Every `Blocked by` in one place.

| Issue | Blocked by | Why |
|---|---|---|
| #14 | #13 | House workflow conventions land in #13; #14 should match rather than invent a second style |
| #15 | #13, #14 | A badge should point at workflows in their final form |
| #16 | #13 | The macro change must not be what discovers the deck does not compile |
| #17 | #16, #27 | Pilot proves the macro first; `.gitattributes` normalises before the bulk rewrite |
| #18 | #17 | Both rewrite every card; sequencing avoids one large conflicted diff |
| #19 | #18 | The linter should encode the finished convention |
| #22 | #19 | The count check belongs in the card linter |
| #24 | #18, #19 | Documents the finished convention and the real linter |
| #26 | #25 (soft) | So the two weekly schedules are chosen together rather than colliding |
| #29 | #23–#28 | The phase's closing statement; its "Yes" rows must link to files that exist |

Everything else is parallel-safe. If a blocker is skipped under §6, proceed
anyway and note it in the PR body — these are orderings, not hard gates, except
where an acceptance criterion literally references the blocker's output.

---

## 5. Protected paths

Files whose breakage compromises **every later PR**, not just their own:

| Path | Why |
|---|---|
| `main.tex` | The document root. Broken, nothing in the repository builds |
| `mybeamer.cls` | Loads every package and defines every section colour |
| `mybeamer.sty` | Defines `\QuestionSlide` / `\AnswerSlide`; after Phase 2 every one of 269 cards depends on it |
| `.github/workflows/**` | The build itself |
| `scripts/lint-cards.py` | A broken validator turns every later PR into three-retries-and-force-merge |
| `.gitleaks.toml`, `scripts/hooks/pre-commit` | A scanner that passes vacuously is worse than none |

`areas/*.tex` are deliberately **not** protected. A LaTeX error in one card does
break the build, but it is contained, obvious, and named by the compiler. A
broken validator is none of those things.

---

## 6. Execution policy

- **One issue, one PR.** Never batched. The PR body carries `Closes #N`.
- **CI must actually run** on the pushed branch before merge. Not "this would
  obviously pass".
- **Retry cap: three** fix attempts per PR for a code-caused failure. Fixed, not
  renegotiable mid-run.
- **After three failures**, the diff decides:
  - touches **no** protected path → force-merge, say so explicitly in the PR and
    the tracker, and open a `Fix CI: <title>` issue in the same phase labelled
    `tech-debt`;
  - touches a **protected path** → do **not** merge. Leave the PR open, label it
    and its issue `blocked`, comment with the diagnosis and all three attempts.
- **Infrastructure failures** (auth, quota, outage, runner unavailable — no code
  path in the log) do not consume the retry cap. Re-run once, then force-merge
  and open **one** `Fix CI: pipeline` issue for the whole degraded period.
- **After the second force-merge in a phase**, open `Review: <phase> specs` in
  that phase. A signal for later review, not a brake.
- Merge convention: **squash**. All twelve merged PRs in this repository's
  history are merge commits from the GitHub UI; squash is chosen for the
  roadmap's one-issue-one-PR shape and recorded here so a future session does not
  re-derive it.

Both logs live on **#30**.

---

## 7. Milestones are labels here

The GitHub tooling available to the agent running this roadmap exposes issues,
labels, pull requests and workflows — but **no milestone API**, and no generic
REST passthrough. Milestones cannot be created.

Phases are therefore carried by three things that *are* creatable and that
together do the same job: the `phase-*` labels, the table in §2, and the
checklist on #30. "The current phase" — which the execution loop needs in order
to pick the next issue — is the earliest phase in §2 with an open, non-`blocked`
issue.

If milestones become available later, they should be created to match §2
exactly, and this section replaced with a note saying so. The labels are not a
preference; they are the closest available representation.

---

## 8. Non-goals

- **Not a code project.** The C# in this repository is illustrative listings
  inside slides. There is no `.csproj`, nothing is compiled, and no test
  framework is wanted. "Tests" here means: does it compile, and does it follow
  the card conventions.
- **No new content in this roadmap.** Adding cards or areas is ordinary
  contribution and needs no roadmap; every issue here is about the deck's
  machinery, its truthfulness, or its baseline.
- **No redesign of the visual theme.** Phase 2 changes how a card is *authored*,
  and is done when the rendered PDF is byte-for-byte equivalent in page count and
  visually identical.
- **Cutting the first release tag is the maintainer's call.** #14 makes the PDF
  obtainable without one; choosing a first version number is not automated.
