# Contributing

A card in this deck is a question slide followed by an answer slide. Everything
below is what you need to add one, change one, or add a whole area.

If you only read one thing: **run `python3 scripts/lint-cards.py` before you
push.** It is the same command CI runs, and it catches the mistakes this
repository has actually made.

---

## Building locally

```bash
latexmk -xelatex -shell-escape main.tex
```

Three parts of that are not optional:

| | Why |
|---|---|
| `latexmk` | The deck needs two passes. `latexmk` reruns as many times as the document requires; a single `xelatex` leaves the outline frames wrong. |
| `-xelatex` | `main.tex` sets a 1080×1920 pt geometry before `\documentclass`, and the class loads `fontawesome5`. |
| `-shell-escape` | `mybeamer.cls` loads `minted`, which shells out to Pygments. Without this the run dies on the first of 197 code frames, with an error that does not mention minted. |

Prefer a browser? Import the repository into Overleaf and press *Re-compile*.

Building leaves `main.pdf` in the repository root. It is **not** committed —
PDFs are build output. Get one from CI instead: **Actions → Build & Release
PDF → Run workflow**, then download `CSharp_FlashCards` from the run's
Artifacts.

---

## Install the hooks, once per clone

```bash
./scripts/install-hooks.sh
```

This points `core.hooksPath` at `scripts/hooks/`, so the pre-commit secret scan
runs before anything becomes history. It needs either the `gitleaks` binary or
Docker, and it **fails rather than warns** when neither is present — a hook whose
protection depends on your toolchain is not a hook.

---

## The anatomy of a card

This is a complete card, copied from `areas/4-LINQ.tex`. Paste it, change the
words, and it will build:

```latex
% 1 ── What is LINQ?
\QuestionSlide[\CategoryBadge[LinqColor!20]{LINQ}]<2>{What is LINQ?}
\begin{frame}[fragile]
  \frametitle{\AnswerTitle[\CategoryBadge[LinqColor!20]{LINQ}]{What is LINQ?}}
  {\footnotesize
  Language Integrated Query enables querying collections with SQL-like syntax
  or fluent methods (\texttt{Where}, \texttt{Select}, etc.).
  }
\end{frame}
```

Four things to keep:

- **`\QuestionSlide[<badge>]<difficulty>{<question>}`** — the badge is optional,
  the difficulty goes in angle brackets, and the question is the last argument.
- **`\AnswerTitle[<badge>]{<short title>}` inside `\frametitle`** — never a
  hand-rolled `tikzpicture` overlay. The badge geometry is defined once, in
  `mybeamer.sty`; it used to be written out in all 270 answer frames and had
  drifted into three variants.
- **`[fragile]` on the frame**, always. It costs nothing on a frame without code
  and is required by any frame with `minted`, `lstlisting` or `\verb`.
- **The answer title is deliberately shorter than the question.** `What is RAG?`
  answers `What is RAG (Retrieval-Augmented Generation)?`. That is the design,
  not drift — do not "fix" it by copying the question.

### Adding a code listing

```latex
  \begin{minted}{csharp}
  var names = context.Customers
                     .Select(c => c.CustomerName)
                     .ToList();
  \end{minted}
```

The frame must be `[fragile]`, and the listing must be in the file rather than
inside a macro argument. Verbatim depends on line structure, and a macro argument
has none.

### Escaping

`#`, `%`, `_` and `&` are LaTeX special characters. Write `\#`, `\%`, `\_`, `\&`
— **`C\#` in particular**, which appears in nearly every card.

---

## Difficulty

One dot to three, rendered beside the category badge.

| | Means |
|---|---|
| `<1>` | **Recall.** You either know the term or you do not; no reasoning needed. |
| `<2>` | **Working knowledge.** You have used this and can explain what it does and when to reach for it. |
| `<3>` | **Depth.** Needs the trade-off, the failure mode, or the mechanism underneath — the kind of answer an interviewer follows up on. |

Every card carries one, and CI fails without it. Anything outside 1–3 is a build
error rather than a silent miscount.

Do not write the rating as asterisks in the question text. It used to be done
that way, LaTeX typeset the asterisks, and the reader saw
`12. ** What is a Service Mesh?` on the card and again in the outline.

---

## Adding a whole area

**Seven coordinated edits across three files.** Miss one and the deck either
fails to build or quietly renders wrong — there is no partial state that looks
correct.

Say you are adding area 25, "gRPC":

**1. The card file** — `areas/25-grpc.tex`, cards only, no preamble.

**2–5. `main.tex`**, four edits.

The Table of Contents is a **two-column `tabular`**, so where the new button goes
depends on whether your area number is odd or even. Getting this wrong is a build
error — `Extra alignment tab has been changed to \cr` — and it is the mistake this
checklist was written by making:

```latex
% ODD area number: starts a new row, and ends it with \\
    \TOCButtonTall{sec24}{sec24}{Tooling \& Agile} \\[0.6em]
    \TOCButtonTall{sec25}{sec25}{gRPC} \\[0.6em]

% EVEN area number: completes the previous row, so the entry BEFORE it
% gains a trailing &
    \TOCButtonTall{sec25}{sec25}{gRPC} &
    \TOCButtonTall{sec26}{sec26}{Kafka} \\[0.6em]
```

Then, at the end of the file with the other sections:

```latex
\hypertarget{sec25}{}
\section{gRPC}
\input{areas/25-grpc}
```

**6–7. `mybeamer.cls`**, two edits, both next to their numbered siblings:

```latex
\definecolor{sec25bg}{HTML}{00897B}   % pick a colour not already used
\setbeamercolor{sec25}{fg=white,bg=sec25bg}
```

Then build. A missing `secNbg` is an undefined colour and fails loudly; a missing
`\TOCButtonTall` fails silently, and the area simply cannot be reached from the
contents page.

**Also update `docs/index.html`.** The landing page states the area count in four
places and lists every area with its card count, and CI compares all of it
against the deck. It will tell you exactly which number is wrong.

---

## What CI checks

Two workflows run on every pull request.

**Card conventions** (~4 seconds) — `scripts/lint-cards.py`. Runs first and gates
the compile, so a convention mistake costs seconds rather than a three-minute
LaTeX run. It checks:

- no question title begins with a literal `*`
- every question slide has a difficulty of 1, 2 or 3
- no hand-rolled badge overlays
- every frame containing verbatim is `[fragile]`
- cards and answer titles pair up
- the landing page's counts match the deck

**Compile main.tex** (~3 minutes) — builds the deck and uploads the PDF, and
reports the page count and byte size to the run summary. If it fails, the summary
names the two commonest causes and the log's first line beginning with `!` is the
real error.

A third, **gitleaks**, scans full history on every push and weekly.

Every one of those checks was verified by introducing the defect and watching it
fail. If you add a check, do the same — a check nobody has watched fail is not
known to be checking anything.

---

## Opening a pull request

Fork, branch, and open a PR. The template asks for the card count before and
after, a green run, and — for a change to `mybeamer.cls`, `mybeamer.sty` or
`main.tex` — what you checked in the rendered PDF. A style change is invisible in
the diff and obvious on the page.

Those three files plus `.github/workflows/`, `scripts/` and `.gitleaks.toml` are
**protected paths**: breaking one breaks every later pull request, not only your
own. `ROADMAP.md` §5 says why, and `.github/CODEOWNERS` names them.
