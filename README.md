# CSharp FlashCards 2025

[![PDF download](https://img.shields.io/badge/PDF-download-blue)](https://github.com/konradcinkusz/csharp-flashcards/releases/latest/download/CSharp_FlashCards.pdf)
[![CI](https://github.com/konradcinkusz/csharp-flashcards/actions/workflows/ci.yml/badge.svg)](https://github.com/konradcinkusz/csharp-flashcards/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

A Beamer slide deck of **Q-and-A flash-cards** that cover C# language basics, LINQ, async/await, Entity Framework, design principles and patterns, plus advanced cloud and leadership topics.
Use it for live classes, self-study, interview prep, or conference lightning talks.

---

## Features

* **“Flip-card” layout** – each question slide is followed by an answer slide.
* **Section colour-coding** for quick visual orientation.
* **One-click PDF** built automatically by GitHub Actions on every tagged release.
* **Easily extensible** – drop a new `areas/*.tex` file and include it in `main.tex`.

---

## Quick start

```bash
git clone https://github.com/konradcinkusz/csharp-flashcards.git
cd csharp-flashcards
latexmk -xelatex -shell-escape main.tex   # or just `pdflatex` twice
```

The compiled `main.pdf` will appear in the repository root.  
Prefer a browser? Import the repo into Overleaf and press *Re-compile* – Overleaf’s built-in Git sync keeps both copies up-to-date.

---

## Repository structure

```
.
├── areas/
│   ├── 1-csharp-language-beginner.tex
│   ├── 2-csharp-language-middle.tex
│   ├── 3-csharp-language-advance.tex
│   ├── 4-LINQ.tex
│   ├── 5-threading-async-await.tex
│   ├── 6-entity-framework.tex
│   ├── 7-design-principles.tex
│   ├── 8-design-patterns.tex
│   ├── 9-OAuth.tex
│   └── 10-microservices.tex
├── main.tex
├── mybeamer.cls / mybeamer.sty
└── .github/workflows/ci.yml
```

---

## Contributing

1. **Fork** → create a feature branch.
2. Add or edit an `areas/*.tex` file, or improve the Beamer style.
3. Open a **Pull Request** – automated checks will compile the PDF and comment with any LaTeX errors.

---

## License

This project is released under the **MIT License**.  
See [LICENSE](LICENSE)

---

*Created with ♥ for anyone learning C# in 2025!*