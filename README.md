# CSharp FlashCards 2026

[![Build deck](https://github.com/konradcinkusz/csharp-flashcards/actions/workflows/build.yml/badge.svg?branch=main)](https://github.com/konradcinkusz/csharp-flashcards/actions/workflows/build.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

**Get the PDF:** no release has been cut yet, so the deck is built on demand —
[run the *Build & Release PDF* workflow](https://github.com/konradcinkusz/csharp-flashcards/actions/workflows/ci.yml)
and download `CSharp_FlashCards` from the run's Artifacts. Once a `v*` tag is
pushed the same workflow publishes a release, and this line is replaced by a
direct download link.

A Beamer slide deck of **Q-and-A flash-cards** that cover C# language basics, LINQ, async/await, Entity Framework, design principles and patterns, OAuth, microservices, cloud and leadership topics, AI & .NET, ASP.NET Core, Blazor, .NET Aspire, databases, Docker & Kubernetes, CI/CD & IaC, Azure, DDD & CQRS, REST & SignalR, AI tools/LLMs, and tooling & agile practices.
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
│   ├── 10-microservices.tex
│   ├── 11-advanced-cloud-leadership.tex
│   ├── 12-azure-serverless.tex
│   ├── 13-csharp-ai.tex
│   ├── 14-aspnetcore.tex
│   ├── 15-blazor-server.tex
│   ├── 16-dotnet-aspire.tex
│   ├── 17-databases.tex
│   ├── 18-docker-kubernetes.tex
│   ├── 19-cicd-terraform.tex
│   ├── 20-azure.tex
│   ├── 21-ddd-cqrs.tex
│   ├── 22-rest-signalr.tex
│   ├── 23-ai-tools-llms.tex
│   └── 24-tooling-agile.tex
├── main.tex
├── mybeamer.cls / mybeamer.sty
└── .github/workflows/
    ├── build.yml      # compiles main.tex on every push and PR
    ├── ci.yml         # builds and publishes the release PDF
    └── pages.yml      # deploys docs/ to GitHub Pages
```

---

## Roadmap

Planned work lives in [`ROADMAP.md`](ROADMAP.md): what "complete" means for this
deck, the four phases and their sequencing, the dependency list, and the paths
that must not break. Progress is tracked on
[issue #30](https://github.com/konradcinkusz/csharp-flashcards/issues/30).

---

## Contributing

Read [`CONTRIBUTING.md`](CONTRIBUTING.md) — it has the anatomy of a card, what the
three difficulty levels mean, the seven coordinated edits that adding a whole
area takes, and what CI checks.

The short version:

1. **Fork** → create a feature branch, and run `./scripts/install-hooks.sh` once.
2. Add or edit an `areas/*.tex` file, or improve the Beamer style.
3. Run `python3 scripts/lint-cards.py` — the same command CI runs.
4. Open a **Pull Request**. CI compiles `main.tex` on every pull request; if the
   deck fails to build, the run's summary names the LaTeX error and the file it is in.

---

## License

This project is released under the **MIT License**.  
See [LICENSE](LICENSE)

---

*Created with ♥ for anyone learning C# in 2026!*