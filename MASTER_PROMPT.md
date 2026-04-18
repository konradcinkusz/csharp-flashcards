# Generic Content Repository — Master Prompt

> **How to use this file**
> 1. Fill in the **Metadata** block below with your project details.
> 2. Paste your raw content (Markdown, plain text, or outline) into the **Content** block at the bottom.
> 3. Give the entire file to Claude in a new session.
> 4. Claude will output every repo file as a fenced code block. Copy each file into a fresh directory.
> 5. Run `latexmk -xelatex -shell-escape main.tex` locally to verify, then push and tag to trigger the CI release.

---

## METADATA (fill this in before sending to Claude)

```yaml
title:        "My Book Title"
author:       "Author Name"
github_user:  "username"
repo_name:    "my-repo"
content_type: "book"        # book | article | flashcards | slides
pdf_name:     "My_Book"     # filename without extension, underscores instead of spaces
year:         "2025"
use_code:     false         # set true if your content contains code listings
engine:       "xelatex"    # xelatex (recommended) | pdflatex | lualatex
```

---

## INSTRUCTIONS FOR CLAUDE

You are a LaTeX document and GitHub repository generator. Your task is to produce a **complete, working repository** from the metadata and content provided above.

### Output format

Output every file as a fenced code block preceded by its exact relative path:

```
### FILE: path/to/file.ext
```

Use the correct language identifier for each code block (e.g., `latex`, `yaml`, `markdown`, `gitignore`). Do not output prose between files except a brief one-line transition such as `Generating chapter files...`. After all files, output a **SETUP** section with exact shell commands to compile locally and push the first release tag.

**Rules:**
- Generate ALL files listed in the manifest below. No partial files.
- Every `\input{...}` in `main.tex` must have a corresponding generated file.
- Do not leave placeholder comments like `% add content here`. Fill every file completely from the user's content.
- Do not carry over topic-specific strings from one content type to structural files (e.g., do not mention "C#" in `.gitignore`).

---

### Content-type branching

Read `content_type` from the metadata and follow the matching branch:

| `content_type` | LaTeX class | Structure unit | TOC style |
|---|---|---|---|
| `book` | `memoir` (12pt, a4paper) | `\chapter{}` per top-level heading | Full TOC + running headers |
| `article` | `article` (12pt, a4paper) | `\section{}` per top-level heading | `\tableofcontents` at top |
| `flashcards` | custom `mybeamer` (Beamer) | one `areas/` file per section | Grid of `\TOCButtonTall` |
| `slides` | `beamer` (aspectratio=169) | one `areas/` file per section | Right-sidebar TOC |

**Primary content types for this prompt: `book` and `article`.** The flashcards/slides branches are documented below for completeness.

---

### File generation manifest

Generate files in this exact order:

```
1.  .gitignore
2.  README.md
3.  main.tex
4.  chapters/01-<slug>.tex          (book / article — one per detected section)
    ...
    chapters/NN-<slug>.tex
    — OR —
    areas/01-<slug>.tex             (flashcards / slides — one per section)
    ...
    areas/NN-<slug>.tex
5.  (flashcards only) mycontent.cls
6.  (flashcards only) mycontent.sty
7.  (slides only)     theme/beamerthemedeepdiveinto.sty
8.  .github/workflows/ci.yml
9.  LICENSE
```

---

### Per-file detailed instructions

#### FILE 1 — `.gitignore`

Reproduce this list verbatim. Do not add or remove entries.

```
# LaTeX build artifacts
*.aux
*.log
*.toc
*.out
*.fls
*.synctex.gz
*.lof
*.lot
*.lol
*.bbl
*.blg
*.run.xml
*-blx.aux
*.fdb_latexmk
.latexmk/
latexmkrc.*
*.nav
*.snm
*.vrb
*.glo
*.glg
*.gls
*.ist
*.idx
*.ilg
*.ind
*.acn
*.acr
*.maf
*.mtc
*.mtc0
*.xdy
*.pyg
*.tdo
*.brf
*.dvi
*.ps
*.synctex.gz

# Generated output (delivered via GitHub Releases only)
*.pdf

# Temporary and editor junk
.DS_Store
Thumbs.db
ehthumbs.db
.vscode/
.idea/
*.sublime-*
*~
~$*
.ipynb_checkpoints/

# Build directories
build/
_build/
out/
```

#### FILE 2 — `README.md`

Include:
- Two shield badges at the top:
  - CI status: `https://github.com/{github_user}/{repo_name}/actions/workflows/ci.yml/badge.svg`
  - Latest PDF download: `https://img.shields.io/github/v/release/{github_user}/{repo_name}?label=PDF`
- One paragraph describing the publication (infer from the user's content).
- **Quick start** section:
  ```bash
  git clone https://github.com/{github_user}/{repo_name}.git
  cd {repo_name}
  latexmk -xelatex -shell-escape main.tex
  ```
  (Omit `-shell-escape` if `use_code: false` and no code blocks were detected.)
- **Repository structure** tree (generated from the files you are producing).
- **Releasing** section: explain that pushing a `v*` tag triggers the GitHub Actions build and publishes the PDF to GitHub Releases.
- **Contributing** and **License** sections.

#### FILE 3 — `main.tex`

**For `book`:**
```latex
\documentclass[12pt,a4paper,openany]{memoir}
\usepackage[T1]{fontenc}
\usepackage[utf8]{inputenc}
\usepackage{microtype}
\usepackage[margin=2.5cm]{geometry}
\usepackage{hyperref}
\usepackage{xcolor}
\usepackage{booktabs}
% Include minted only when use_code is true or code blocks were detected:
% \usepackage{minted}

\hypersetup{
  colorlinks=true,
  linkcolor=blue!60!black,
  urlcolor=blue!60!black
}

\title{{title}}
\author{{author}}
\date{{year}}

\begin{document}
\frontmatter
\maketitle
\tableofcontents
\mainmatter

\input{chapters/01-<first-chapter-slug>}
% \input{chapters/02-...}  (repeat for each chapter)

\backmatter
\end{document}
```

**For `article`:**
```latex
\documentclass[12pt,a4paper]{article}
\usepackage[T1]{fontenc}
\usepackage[utf8]{inputenc}
\usepackage{microtype}
\usepackage[margin=2.5cm]{geometry}
\usepackage{hyperref}
\usepackage{xcolor}
\usepackage{abstract}
% \usepackage{minted}  (include only when use_code: true or code detected)

\hypersetup{
  colorlinks=true,
  linkcolor=blue!60!black,
  urlcolor=blue!60!black
}

\title{{title}}
\author{{author}}
\date{{year}}

\begin{document}
\maketitle
\tableofcontents
\bigskip

\input{chapters/01-<first-section-slug>}
% \input{chapters/02-...}

\end{document}
```

Replace `{title}`, `{author}`, `{year}` with the actual metadata values. Replace each `\input{}` argument with the real filenames you generate.

#### FILE 4 — `chapters/NN-<slug>.tex` (book / article)

One file per top-level section detected in the user's content.

Filename slugging rule: lowercase, spaces → hyphens, remove punctuation. Examples:
- `# Introduction` → `chapters/01-introduction.tex`
- `# Design Patterns in Go` → `chapters/02-design-patterns-in-go.tex`

Content rules:
- **book**: wrap each file in `\chapter{Section Title}` then use `\section{}`, `\subsection{}` for sub-headings.
- **article**: start each file directly with `\section{Section Title}` and use `\subsection{}` for sub-headings.
- Prose paragraphs: plain LaTeX text, separated by blank lines.
- `**bold**` → `\textbf{bold}`
- `*italic*` → `\textit{italic}`
- `` `inline code` `` → `\texttt{inline code}`
- `- item` or `* item` → `\begin{itemize}\item...\end{itemize}`
- `1. item` → `\begin{enumerate}\item...\end{enumerate}`
- Fenced code block (if `use_code: true` or code detected):
  ````
  \begin{minted}{language}
  ...code...
  \end{minted}
  ````
  If `use_code: false` and no code was detected, use `\begin{verbatim}...\end{verbatim}` as fallback.
- `> blockquote` → `\begin{quote}...\end{quote}`
- `---` (horizontal rule) → `\bigskip\noindent\rule{\linewidth}{0.4pt}\bigskip`
- No headings detected: split at ~600-word boundaries, name sections "Part 1", "Part 2", etc.

#### FILE 4 (alt) — `areas/NN-<slug>.tex` (flashcards / slides)

One file per section. For flashcards, each Q&A pair uses:
```latex
\QuestionSlide[badge]{Question text here?}
\AnswerSlide[badge]{Short Title}{
  Answer body — prose, lists, or minted code.
}
```

If the user's content has prose rather than explicit Q&A pairs, synthesise question slides from headings and answer slides from the body text under each heading.

#### FILE 5 — `mycontent.cls` (flashcards only)

Produce a generic Beamer class file equivalent to the one in the `csharp-flashcards` repo but with:
- `\newcommand{\RepoURL}{https://github.com/{github_user}/{repo_name}}` replacing all hardcoded URLs.
- Section colors defined as `sec1bg` through `sec{N}bg` where N is the number of detected sections. Use this rotating 8-color palette by index: `#6BAED6`, `#FD8D3C`, `#9C27B0`, `#388E3C`, `#0288D1`, `#795548`, `#8BC34A`, `#D81B60`.
- All other class features (portrait 1080×1920 geometry, navigation symbols, footline, `minted`/`listings` setup, `\AtBeginSection` outline frame) reproduced as-is.

#### FILE 6 — `mycontent.sty` (flashcards only)

Reproduce the `mybeamer.sty` macros verbatim (`\qcounter`, `\CategoryBadge`, `\TOCButtonTall`, `\QuestionSlide`, `\AnswerSlide`, `\ChunkedTOC`). These are already fully generic.

#### FILE 7 — `theme/beamerthemedeepdiveinto.sty` (slides only)

Reproduce the existing `beamerthemedeepdiveinto.sty` theme verbatim. Replace any hardcoded step labels in `\implprogress` with stage names derived from the user's section headings.

#### FILE 8 — `.github/workflows/ci.yml`

```yaml
name: Build & Release PDF

on:
  push:
    tags:
      - 'v*'

permissions:
  contents: write

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: xu-cheng/latex-action@v4
        with:
          root_file: main.tex
          latexmk_use_xelatex: true        # set false if engine: pdflatex
          latexmk_shell_escape: true       # required for minted; omit if use_code: false and no code detected
      - name: Rename PDF
        run: mv main.pdf {pdf_name}.pdf
      - uses: actions/upload-artifact@v4
        with:
          name: {pdf_name}
          path: {pdf_name}.pdf

  release:
    runs-on: ubuntu-latest
    needs: build
    steps:
      - uses: actions/download-artifact@v4
        with:
          name: {pdf_name}
      - uses: softprops/action-gh-release@v2
        with:
          files: {pdf_name}.pdf
```

Replace `{pdf_name}` with the metadata value. Set `latexmk_use_xelatex: false` if `engine: pdflatex`. Remove `latexmk_shell_escape: true` if `use_code: false` and no code blocks were found in the content.

#### FILE 9 — `LICENSE`

```
MIT No Attribution

Copyright {year} {author}

Permission is hereby granted, free of charge, to any person obtaining a copy of this
software and associated documentation files (the "Software"), to deal in the Software
without restriction, including without limitation the rights to use, copy, modify,
merge, publish, distribute, sublicense, and/or sell copies of the Software, and to
permit persons to whom the Software is furnished to do so.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED,
INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A
PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
```

Replace `{year}` and `{author}` with the metadata values.

---

### Content parsing rules

**Markdown input:**

| Markdown | LaTeX output |
|---|---|
| `# Heading` | New chapter/section file + `\chapter{}`/`\section{}` |
| `## Heading` | `\subsection{}` |
| `### Heading` | `\subsubsection{}` |
| `**bold**` | `\textbf{bold}` |
| `*italic*` | `\textit{italic}` |
| `` `code` `` | `\texttt{code}` |
| ` ```lang\n...\n``` ` | `\begin{minted}{lang}...\end{minted}` |
| `- item` / `* item` | `\item` inside `itemize` |
| `1. item` | `\item` inside `enumerate` |
| `> quote` | `\begin{quote}...\end{quote}` |

**Plain text / outline input:**

- ALL-CAPS lines, numbered lines (`1.`, `I.`), or lines followed by `===`/`---` → section boundaries.
- Lines ending with `?` in a Q&A context → question slide (flashcards) or callout box (article/book).
- Subsequent paragraph → answer / body.
- No detectable structure → split at ~600-word boundaries.

---

### Self-check before outputting

Verify all of the following before generating output:

1. Every `\input{chapters/NN-...}` or `\input{areas/NN-...}` in `main.tex` has a matching generated file.
2. `{pdf_name}` in `ci.yml` matches the metadata exactly (character-for-character).
3. No topic-specific content from the user's text has leaked into structural files (`.gitignore`, `ci.yml`, `LICENSE`).
4. `\usepackage{minted}` and `latexmk_shell_escape: true` are present **only** if `use_code: true` OR code blocks were detected in the content.
5. `*.pdf` is present in `.gitignore`.
6. README badge URLs use the correct `{github_user}` and `{repo_name}` from metadata.
7. The `\title{}`, `\author{}`, `\date{}` in `main.tex` use the actual metadata values, not placeholder text.
8. All chapter/area filenames are valid LaTeX `\input` paths (no spaces, no special characters).

---

### SETUP section (output after all files)

After generating all files, output a `## SETUP` section containing:

```bash
# 1. Copy all generated files into a fresh directory and enter it
mkdir {repo_name} && cd {repo_name}
git init

# 2. Compile locally to verify
latexmk -xelatex -shell-escape main.tex   # produces main.pdf

# 3. Commit and connect to GitHub
git add .
git commit -m "Initial content commit"
git remote add origin https://github.com/{github_user}/{repo_name}.git
git push -u origin main

# 4. Tag to trigger the CI release
git tag v1.0.0
git push origin v1.0.0
# GitHub Actions builds the PDF and creates a GitHub Release automatically.
```

---

## CONTENT (paste your raw content below this line)

<!-- ================================================================
     Paste your content here.
     Accepted formats: Markdown, plain text, outline, Q&A pairs.
     Claude will infer section structure, headings, and formatting.
     ================================================================ -->
