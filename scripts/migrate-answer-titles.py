#!/usr/bin/env python3
"""Rewrite hand-rolled answer-frame titles to use \\AnswerTitle.

Every answer frame in this deck opened with the same eight lines: a
tikzpicture overlay positioning the category badge, then the frame's own
title. mybeamer.sty defines \\AnswerTitle for exactly that, so the eight
lines collapse to one and the badge geometry has a single definition
instead of one per card.

Why a script rather than an editor macro: 270 frames is past the point
where a by-hand pass is reviewable, and the transformation has to be
provably faithful. This refuses to touch anything it does not recognise
exactly, and reports what it skipped, so a frame that has drifted from
the common shape shows up as a number rather than as a silent mangling.

Run from the repository root:

    python3 scripts/migrate-answer-titles.py            # rewrite in place
    python3 scripts/migrate-answer-titles.py --check    # report only
"""
from __future__ import annotations

import argparse
import glob
import re
import sys

# The hand-rolled form. Two variants exist in the tree and both are matched
# here, because the difference between them is not a decision anybody made:
#
#   * The four oldest area files (1, 2, 3, 11 — 90 cards) write the node
#     without `text=black` and without spaces after the commas.
#   * Everything written later (170 cards) sets `text=black`.
#
# Whether the badge is legible therefore depended on which file a card
# happened to live in, since without `text=black` the badge text inherits
# beamer's frametitle colour. Normalising is the point of the migration, so
# this pattern accepts both and \AnswerTitle emits one.
#
# 52 overlays carry two badges rather than one; the payload between the node's
# braces is captured whole rather than assuming a single \CategoryBadge.
PATTERN = re.compile(
    r'\\frametitle\{%?\s*\n'
    r'\s*\\begin\{tikzpicture\}\[remember picture,\s*overlay\]\s*\n'
    r'\s*\\node\[\s*anchor=north east,\s*xshift=-0\.4cm,\s*yshift=-0\.4cm'
    r'(?:,\s*text=black)?\s*\]\s*'
    r'at \(current page\.north east\)\s*\{'
    r'(?P<badges>.*?)'
    r'\};\s*\n'
    r'\s*\\end\{tikzpicture\}\s*\n'
    r'\s*Answer \\theqcounter:\s*(?P<title>.*?)%?[ \t]*\n'
    r'\s*\}',
    re.S,
)

# A second shape, used only by areas/3-csharp-language-advance.tex (6 cards):
# the title is plain and the overlay sits in the frame BODY underneath it, at a
# 0.5cm inset rather than 0.4cm. That 0.5cm is the inset the deleted
# \AnswerSlide macro used, so this file was written against the macro nobody
# could actually call. Folding it in normalises the inset by 0.1cm — about
# 2.8pt on a 1080x1920pt page.
PATTERN_BODY = re.compile(
    r'\\frametitle\{Answer \\theqcounter:\s*(?P<title>[^\n]*?)\}\s*\n'
    r'\s*\n?'
    r'\s*\\begin\{tikzpicture\}\[remember picture,\s*overlay\]\s*\n'
    r'\s*\\node\[\s*anchor=north east,\s*xshift=-0\.5cm,\s*yshift=-0\.5cm\s*\]\s*\n?'
    r'\s*at \(current page\.north east\)\s*\n?'
    r'\s*\{(?P<badges>.*?)\};\s*\n'
    r'\s*\\end\{tikzpicture\}',
    re.S,
)

OVERLAY = re.compile(r'\\begin\{tikzpicture\}\[remember picture')

# Two cards keep their hand-rolled overlay on purpose. Both set a yshift that is
# not the deck's 0.4cm, which is a per-card decision rather than a file-level
# convention that drifted — unlike everything else this script rewrites. Moving
# a badge somebody deliberately pushed down the page is not a mechanical
# migration, so they are listed here instead, with what makes each one odd.
#
# If either turns out to be a typo, fix it in its own commit where the visual
# change is the subject rather than a side effect of a 258-card rewrite.
KNOWN_EXCEPTIONS = {
    'areas/12-azure-serverless.tex': 'yshift=-0.8cm, double the deck default',
    'areas/2-csharp-language-middle.tex': 'yshift=-3.45cm, pushed well down the page',
}


def rewrite(text: str) -> tuple[str, int]:
    def repl(m: re.Match) -> str:
        badges = ' '.join(m.group('badges').split())
        title = m.group('title').rstrip().rstrip('%').rstrip()
        return '\\frametitle{\\AnswerTitle[%s]{%s}}' % (badges, title)

    text, n1 = PATTERN.subn(repl, text)
    text, n2 = PATTERN_BODY.subn(repl, text)
    return text, n1 + n2


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('--check', action='store_true',
                    help='report what would change; write nothing')
    args = ap.parse_args()

    migrated = remaining = unexpected = 0
    for path in sorted(glob.glob('areas/*.tex')):
        before = open(path, encoding='utf-8').read()
        after, n = rewrite(before)
        left = len(OVERLAY.findall(after))
        migrated += n
        remaining += left
        known = path in KNOWN_EXCEPTIONS
        if left and not known:
            unexpected += left
        if n or left:
            note = f'  {path}: {n} migrated'
            if left:
                note += f', {left} left ('
                note += (KNOWN_EXCEPTIONS[path] if known else 'NOT RECOGNISED') + ')'
            print(note)
        if not args.check and after != before:
            open(path, 'w', encoding='utf-8').write(after)

    print(f'\ntotal migrated: {migrated}')
    print(f'overlay blocks still present: {remaining} '
          f'({remaining - unexpected} documented, {unexpected} unexpected)')
    if unexpected:
        print('\nThose frames differ from the common shape. Read each one before '
              'widening the pattern: an overlay that is genuinely different is a '
              'card doing something on purpose.', file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
