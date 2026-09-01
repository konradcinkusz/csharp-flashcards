#!/usr/bin/env python3
"""Move the difficulty rating out of the question string and into markup.

Cards encoded difficulty by prefixing the question with asterisks. LaTeX
typesets those, so the reader saw "12. ** What is a Service Mesh?" on the
card and again in every outline frame. This rewrites

    \\QuestionSlide[<badge>]{** What is a Service Mesh?}
    \\AnswerTitle[<badge>]{** What is a Service Mesh?}

to

    \\QuestionSlide[<badge>]<2>{What is a Service Mesh?}
    \\AnswerTitle[<badge>]{What is a Service Mesh?}

The rating renders on the question slide only. It is a signal for deciding
whether to attempt a card, so it belongs before the reveal and is noise
after it -- and the deck was already inconsistent here, with only 88 of 267
answer titles carrying the marker at all.

Eight cards carried no rating. They are listed in UNRATED below with the
rating assigned and why, because "decide them explicitly" is the whole point
and a silent default would put the deck back where it started.
"""
from __future__ import annotations

import argparse
import glob
import re
import sys

STARS = {'*': 1, '**': 2, '***': 3}

# Cards with no marker in the source. Each rating here is an editorial
# judgement made during this migration, not the original author's -- flagged
# in the pull request so it can be overruled cheaply.
UNRATED = {
    'When would you use the \\texttt{ref}, \\texttt{out} and \\texttt{in} modifiers?': (2,
        'working knowledge: you have used them and can say which copies'),
    'What are the main roles in OAuth 2.0?': (1,
        'recall: naming the four roles'),
    'What is the Authorization Code Flow?': (2,
        'working knowledge, and the opener of the six-slide walkthrough below'),
    'Authorization Code Flow — Step 1': (2, 'part of that walkthrough'),
    'Authorization Code Flow — Step 2': (2, 'part of that walkthrough'),
    'Authorization Code Flow — Step 3': (2, 'part of that walkthrough'),
    'Authorization Code Flow — Step 4': (2, 'part of that walkthrough'),
    'Authorization Code Flow Diagram': (2, 'part of that walkthrough'),
}


def split_marker(text: str) -> tuple[int | None, str]:
    """Return (rating, text-without-marker)."""
    # The rating form: leading asterisks followed by a space.
    m = re.match(r'\s*(\*{1,3})\s+(.*)$', text, re.S)
    if m:
        return STARS[m.group(1)], m.group(2).strip()

    # One card is Markdown bold rather than a rating -- **text** with
    # asterisks at BOTH ends and no space. It renders literally on the slide.
    # Strip both and let UNRATED assign the rating.
    m = re.match(r'\s*\*{2}(.*?)\*{2}\s*$', text, re.S)
    if m:
        return None, m.group(1).strip()

    return None, text.strip()


def find_calls(s: str, macro: str):
    """Yield (start, arg_start, arg_end, badge_text) for each call."""
    for m in re.finditer(re.escape(macro) + r'(?![A-Za-z])', s):
        i = m.end()
        badge = None
        if i < len(s) and s[i] == '[':
            d, j = 1, i + 1
            while j < len(s) and d:
                if s[j] == '[': d += 1
                elif s[j] == ']': d -= 1
                j += 1
            badge = s[i + 1:j - 1]
            i = j
        # skip whitespace AND LaTeX comments between the arguments
        while i < len(s):
            if s[i] in ' \n\t':
                i += 1
            elif s[i] == '%':
                i = s.index('\n', i) + 1
            else:
                break
        if i >= len(s) or s[i] != '{':
            continue
        d, j = 1, i + 1
        while j < len(s) and d:
            if s[j] == '{': d += 1
            elif s[j] == '}': d -= 1
            j += 1
        yield m.start(), i, j, badge


def convert(s: str, macro: str, keep_rating: bool) -> tuple[str, int, list[str]]:
    out, last, n, undecided = [], 0, 0, []
    for start, a, b, badge in find_calls(s, macro):
        body = s[a + 1:b - 1]
        rating, text = split_marker(body)
        if rating is None:
            hit = UNRATED.get(text)
            if hit:
                rating = hit[0]
            elif keep_rating:
                undecided.append(text[:70])
        if body == text and rating is None:
            continue                       # nothing to do for this call
        head = macro + (f'[{badge}]' if badge is not None else '')
        if keep_rating and rating is not None:
            head += f'<{rating}>'
        out.append(s[last:start]); out.append(head + '{' + text + '}')
        last = b
        n += 1
    out.append(s[last:])
    return ''.join(out), n, undecided


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('--check', action='store_true')
    args = ap.parse_args()

    total_q = total_a = 0
    problems: list[str] = []
    for path in sorted(glob.glob('areas/*.tex')):
        s = open(path, encoding='utf-8').read()
        s, nq, undecided = convert(s, '\\QuestionSlide', keep_rating=True)
        s, na, _ = convert(s, '\\AnswerTitle', keep_rating=False)
        total_q += nq
        total_a += na
        problems += [f'  {path}: no rating and not in UNRATED: {u}' for u in undecided]
        if not args.check:
            open(path, 'w', encoding='utf-8').write(s)

    print(f'question slides rated: {total_q}')
    print(f'answer titles cleaned: {total_a}')
    if problems:
        print('\n'.join(problems), file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
