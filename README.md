# PDF

## 📄 Download Latest PDF

[![Download PDF](https://img.shields.io/badge/PDF-download-blue)](https://github.com/konradcinkusz/CSharp-FlashCards-2025/releases/latest/download/main.pdf)

## 📄 PDF Downloads

| Version | Download Link | Date       | Notes             |
|---------|---------------|------------|-------------------|
| v1.1.0  | [PDF](https://github.com/konradcinkusz/CSharp-FlashCards-2025/releases/download/v1.1.0/main.pdf) | 2025-08-04 | Updated abstract |
| v1.0.0  | [PDF](https://github.com/konradcinkusz/CSharp-FlashCards-2025/releases/download/v1.0.0/main.pdf) | 2025-07-28 | Initial release  |

# CSharp FlashCards 2025

A set of Beamer-based flash-card slides for C\#/.NET topics, designed for live classroom or self-study presentations.  
Each “area” (beginner, intermediate, threading, design, LINQ, etc.) is a Beamer **section** whose first slide shows a mini-table-of-contents of that area, followed by question/answer slides as **subsections**.

---

## Purpose

- **Learn & teach C\#**: turn core concepts into bite-sized Q&A slides.
- **Reusable slide deck**: easily add/remove topics by dropping in `areas/*.tex`.
- **Auto-generated TOCs**:
  - **Global TOC** at the start, chunked into multiple pages.
  - **Per-section TOC** slide(s) showing only that area’s questions.

---

## Repository Structure

```text
.
├── areas/                       # One .tex per topic-area
│   ├── csharp-language-beginner.tex
│   ├── csharp-language-middle.tex
│   ├── csharp-language-advanced.tex
│   ├── threading-async-await.tex
│   ├── design-principles.tex
│   ├── design-patterns.tex
│   ├── entity-framework.tex
│   └── linq.tex
├── main.tex                     # Minimal driver: loads class, style, and inputs areas
├── mybeamer.cls                 # Custom Beamer class (packages, slide hooks)
├── mybeamer.sty                 # Macros: Q/A slides, chunked TOC helper
└── README.md                    # (You are here!)
````

---

## Getting Started

### 1. Clone the repo

```bash
git clone https://github.com/your-org/CSharp-FlashCards-2025.git
cd CSharp-FlashCards-2025
```

### 2. Build locally

You only need a modern TeX distribution with Beamer support. For example:

```bash
pdflatex main.tex
# or, for multiple passes (TOC links):
pdflatex main.tex && bibtex main && pdflatex main.tex
```

### 3. Online editing

Import the project into Overleaf (or any other online LaTeX editor) by pointing it to this repo.

---

## ➕ Adding or Modifying Content

1. **New topic area**

   * Create `areas/your-topic.tex`.
   * At the top of `main.tex`, add:

     ```latex
     \section{Your Topic Title}
     \input{areas/your-topic}
     ```
2. **Add Q\&A**

   * In your `.tex` file, use:

     ```latex
     \QuestionSlide{Your question text?}
     \AnswerSlide{Your question text?}{%
       Your full answer here…
     }
     ```
   * Questions automatically number and become subsections.
3. **Recompile**

   * The global and per-section TOCs will update automatically.

---

## Contributing

1. **Fork** the repository.
2. Create your **feature branch** (`git checkout -b feat/my-topic`).
3. Make your changes in `areas/...` or adjust styling in `mybeamer.*`.
4. Commit & **push** (`git push origin feat/my-topic`).
5. Open a **Pull Request**.

   * Describe your topic or styling changes.
   * Reference any related issues.

We welcome:

* New topic areas
* Enhancements to macros or styling
* Bug reports & typos fixes

---

## License

Distributed under the **MIT License**. See [LICENSE](LICENSE) for details.

---

*Created with ♥ for anyone learning C# in 2025!*