#!/usr/bin/env python3
"""Check the card conventions this deck settled on in Phase 2.

Every check here corresponds to a defect this repository actually had.
None is hypothetical, and each one is listed with the issue that found it:

  #18  a question string beginning with a literal asterisk, which LaTeX
       typesets on the card and in the outline frame
  #17  a hand-rolled badge overlay, which is how the badge geometry came to
       exist in 270 places and drift into three variants
  #16  a frame containing verbatim without [fragile], which is a build error
  #18  a card with no difficulty rating
  --   a question slide with no answer frame after it, or two

and the counts it reports feed #22, where the landing page's card claim has
to stop drifting.

Run from the repository root:

    python3 scripts/lint-cards.py

Exits non-zero on any finding, printing file:line for each. This is the same
command CI runs -- REPO-BASELINE.md §4 asks for CI jobs to be reproducible
locally so that "it passed locally" means something.
"""
from __future__ import annotations

import glob
import re
import sys

# Two cards keep a hand-rolled overlay on purpose. The reasons live in
# scripts/migrate-answer-titles.py, which is imported rather than copied:
# two lists of exceptions that can disagree is the failure this deck already
# had once, when the badge geometry existed in 270 places.
sys.path.insert(0, 'scripts')
try:
    from importlib import util as _util
    _spec = _util.spec_from_file_location('_mig', 'scripts/migrate-answer-titles.py')
    _mig = _util.module_from_spec(_spec)
    _spec.loader.exec_module(_mig)
    OVERLAY_EXCEPTIONS = dict(_mig.KNOWN_EXCEPTIONS)
except Exception as exc:                                  # pragma: no cover
    print(f'cannot read the overlay exceptions: {exc}', file=sys.stderr)
    raise SystemExit(2)

VERBATIM = ('\\begin{minted}', '\\begin{lstlisting}', '\\verb')


def lineno(s: str, i: int) -> int:
    return s[:i].count('\n') + 1


def check_file(path: str, s: str) -> list[str]:
    out: list[str] = []

    # --- a rating must not be a substring of the question (#18) ------------
    for m in re.finditer(r'\\(QuestionSlide|AnswerTitle)'
                         r'(?:\[(?:[^\[\]]|\[[^\]]*\])*\])?'
                         r'(?:<[^>]*>)?\s*\{\s*(\*+)', s):
        out.append(f'{path}:{lineno(s, m.start())}: '
                   f'title begins with a literal "{m.group(2)}" -- '
                   f'use <1|2|3> rather than asterisks (#18)')

    # --- every question slide carries a rating (#18) -----------------------
    for m in re.finditer(r'\\QuestionSlide'
                         r'(?:\[(?:[^\[\]]|\[[^\]]*\])*\])?'
                         r'(?P<rating><[^>]*>)?', s):
        r = m.group('rating')
        if r is None:
            out.append(f'{path}:{lineno(s, m.start())}: '
                       f'question slide has no difficulty rating (#18)')
        elif r[1:-1] not in ('1', '2', '3'):
            out.append(f'{path}:{lineno(s, m.start())}: '
                       f'difficulty {r} is not 1, 2 or 3 (#18)')

    # --- no hand-rolled badge overlays (#17) -------------------------------
    allowed = 1 if path in OVERLAY_EXCEPTIONS else 0
    found = len(re.findall(r'\\begin\{tikzpicture\}\[remember picture', s))
    if found > allowed:
        note = f' ({allowed} documented exception)' if allowed else ''
        out.append(f'{path}: {found} hand-rolled badge overlay(s){note} -- '
                   f'use \\AnswerTitle (#17)')

    # --- verbatim needs [fragile] (#16) ------------------------------------
    for m in re.finditer(r'\\begin\{frame\}(\[[^\]]*\])?(.*?)\\end\{frame\}', s, re.S):
        opts, body = m.group(1) or '', m.group(2)
        if any(v in body for v in VERBATIM) and 'fragile' not in opts:
            out.append(f'{path}:{lineno(s, m.start())}: '
                       f'frame contains verbatim but is not [fragile] (#16)')

    return out


def check_landing_page(cards: int, areas: int) -> list[str]:
    """The landing page's claims must be derived from the deck, not remembered.

    docs/index.html advertised "300+ Q&A flashcards" against 269, and "13 topic
    areas" against 24 -- it listed 13 and had never been updated for the eleven
    added in July 2026, so LINQ was missing and every number from 04 onward
    named the wrong section. Nothing reported any of it, because nothing
    compared the page against the deck.
    """
    path = 'docs/index.html'
    try:
        s = open(path, encoding='utf-8').read()
    except FileNotFoundError:
        return []

    out: list[str] = []

    # The deck-wide claim, in the hero line and the meta description.
    claimed = {int(m) for m in re.findall(r'(\d+)-card Q&amp;A deck', s)}
    claimed |= {int(m) for m in re.findall(r'(\d+) Q&amp;A flashcards', s)}
    for c in sorted(claimed - {cards}):
        out.append(f'{path}: claims {c} cards deck-wide; the deck has {cards}')

    claimed_areas = {int(m) for m in re.findall(r'(\d+) (?:topic areas|areas,)', s)}
    claimed_areas |= {int(m) for m in re.findall(r'badge/Topics-(\d+)-', s)}
    for a in sorted(claimed_areas - {areas}):
        out.append(f'{path}: claims {a} topic areas; the deck has {areas}')

    # Each topic tile carries its own count. Check every one against the file
    # it names, so a card added to one area cannot silently make the page wrong.
    tiles = re.findall(r'class="topic-num">(\d+)</div>.*?'
                       r'class="topic-count">(\d+) cards', s, re.S)
    if len(tiles) != areas:
        out.append(f'{path}: lists {len(tiles)} topic tiles with counts; '
                   f'the deck has {areas} areas')
    for num, claimed_n in tiles:
        hit = glob.glob(f'areas/{int(num)}-*.tex')
        if not hit:
            out.append(f'{path}: topic {num} names no area file')
            continue
        actual = len(re.findall(r'\\QuestionSlide',
                                open(hit[0], encoding='utf-8').read()))
        if int(claimed_n) != actual:
            out.append(f'{path}: topic {num} claims {claimed_n} cards; '
                       f'{hit[0]} has {actual}')

    # No release has ever been cut, so a releases/latest link is a 404. Delete
    # this check in the same commit that pushes the first v* tag.
    if 'releases/latest' in s:
        out.append(f'{path}: links to releases/latest, and no release exists')

    return out


def main() -> int:
    findings: list[str] = []
    cards = answers = 0

    for path in sorted(glob.glob('areas/*.tex')):
        s = open(path, encoding='utf-8').read()
        findings += check_file(path, s)
        cards += len(re.findall(r'\\QuestionSlide', s))
        answers += len(re.findall(r'\\AnswerTitle', s))

    # --- one answer per question -------------------------------------------
    # 267 rather than 269 because two cards keep a hand-rolled title, and one
    # \frametitle in 9-OAuth.tex belongs to a diagram frame rather than a card.
    expected_answers = cards - len(OVERLAY_EXCEPTIONS)
    if answers != expected_answers:
        findings.append(f'{answers} \\AnswerTitle for {cards} cards '
                        f'(expected {expected_answers}: one per card, less the '
                        f'{len(OVERLAY_EXCEPTIONS)} documented exceptions)')

    areas = len(glob.glob('areas/*.tex'))
    findings += check_landing_page(cards, areas)

    print(f'cards: {cards}')
    print(f'answer titles: {answers}')
    print(f'areas: {areas}')

    summary = __import__('os').environ.get('GITHUB_STEP_SUMMARY')
    if summary:
        with open(summary, 'a', encoding='utf-8') as fh:
            fh.write(f'\n## Cards\n\n**{cards}** question slides across '
                     f'**{areas}** areas, {answers} answer titles.\n')

    if findings:
        print('\n' + '\n'.join(findings), file=sys.stderr)
        print(f'\n{len(findings)} finding(s)', file=sys.stderr)
        return 1
    print('conventions OK')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
