#!/usr/bin/env python3
"""Compile the deck into an ab-ovo content bundle.

WHY THIS LIVES HERE AND NOT IN THE PLATFORM
===========================================

ab-ovo (github.com/konradcinkusz/ab-ove) owns one content schema and never parses
LaTeX: "the external dialect is normalised once, at the boundary, in the repository
that knows the dialect."  This deck is the repository that knows this dialect, so the
normalisation is this script, and what crosses the boundary is JSON.

That also settles what ab-ovo may do with the result.  It renders the bundle.  It does
not read `areas/*.tex`, and a change to a card reaches a reader by being recompiled
here and re-pinned there -- never by being edited on the other side.

WHAT A CARD BECOMES
===================

The deck's mechanic is a question slide followed by an answer slide.  ab-ovo's is a
chain: a step asks, says `cue: true`, and the NEXT step opens with the answer to it.
The two are the same mechanic offset by one, so a card does not need a step of its own
for the answer -- it needs the answer to ride on the step that follows:

    card 1 Q  ->  step 1  { body: Q1,            cue: true }
    card 2 Q  ->  step 2  { answer: A1, body: Q2, cue: true }
    card 3 Q  ->  step 3  { answer: A2, body: Q3, cue: true }
                  ...
                  step N+1 { answer: AN, body: <the closing line below> }

So an area of N cards is N+1 steps, and the last one exists to carry the last answer.
Its body is the one string in the bundle that is not in the deck; it is named as a
constant below rather than buried in a format string, because a reader will meet it.

WHAT IS DROPPED, AND SAID OUT LOUD
==================================

A compiler that quietly emits less than it was given is the failure ab-ovo's own
contract names first: "the compiler REFUSES rather than degrades."  This one therefore
knows exactly three categories and treats them differently:

  carried   prose, `\\item` lists, and `minted` listings (the schema's `code`)
  dropped   `tikzpicture`, `tabular` and the `center`/`resizebox` wrappers around them,
            because the schema has no figure and no table.  Every card that loses one
            is COUNTED AND NAMED in the report, never silently trimmed.
  refused   anything else.  A LaTeX command this script does not know survives
            normalisation and fails the run with its file and line, so the next macro
            somebody adds to the deck is discovered here and not by a reader looking at
            a backslash on a web page.

The deck's difficulty rating (1, 2 or 3) is dropped too, and that is a schema gap
rather than a normalisation choice: ab-ovo has nowhere to put it.  It is recorded in
that repository's ADR-0037 rather than worked around here.

USAGE
=====

    python3 scripts/compile-bundle.py                 write bundle/csharp-flashcards.bundle.json
    python3 scripts/compile-bundle.py --check         recompile and diff; write nothing
    python3 scripts/compile-bundle.py --schema PATH   also validate against ab-ovo's schema

--check is what CI runs.  It is the check that makes the committed bundle a derived
artefact rather than a second copy of the deck: if the two disagree, somebody edited a
card without recompiling, or edited the bundle by hand, and both are findings.
"""
from __future__ import annotations

import argparse
import glob
import hashlib
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, 'bundle', 'csharp-flashcards.bundle.json')

TRACK_ID = 'csharp-flashcards'
TRACK_TITLE = 'C# Flashcards'
LANGUAGE = 'en'          # the deck has one edition; ab-ovo's switch hides itself below two
CODE_LANGUAGE = 'csharp'

# The body of the step that carries an area's last answer, and the only sentence in the
# bundle that no card wrote.  See the header: the chain needs a step after the last
# question, and a reader arriving at it has to be told why it is there.
CLOSING_BODY = 'That was the last card in this area.'


# ──────────────────────────────────────────────────────────────────────────────────────
# Reading the deck
# ──────────────────────────────────────────────────────────────────────────────────────

# main.tex is the order, the titles AND the membership: an area file that no \section
# includes is not in the deck, and inferring the list from `ls areas/` instead would put
# it in the bundle. One source, read once.
SECTION = re.compile(r'\\section\{((?:[^{}]|\{[^{}]*\})*)\}\s*\n\s*\\input\{areas/([^}]+)\}')

QUESTION = re.compile(
    r'\\QuestionSlide'
    r'(?:\[(?P<badge>(?:[^\[\]]|\[[^\]]*\])*)\])?'
    r'(?:<(?P<difficulty>[^>]*)>)?'
    r'\s*\{'
)
BADGE = re.compile(r'\\CategoryBadge(?:\[[^\]]*\])?\{((?:[^{}]|\{[^{}]*\})*)\}')
FRAME = re.compile(r'\\begin\{frame\}(?:\[[^\]]*\])?(.*?)\\end\{frame\}', re.S)
MINTED = re.compile(r'\\begin\{minted\}(?:\[[^\]]*\])?\{[^}]*\}\n?(.*?)\\end\{minted\}', re.S)

# A PICTURE IS THE ONLY THING DROPPED WHOLE.  A `tabular` is text in a grid and its
# cells survive as prose (see `flatten_table`); a `tikzpicture` is a drawing, and there
# is no sentence inside it to carry.  `center` and `resizebox` are layout around one of
# the two and are unwrapped rather than dropped.
DROPPED_ENVIRONMENTS = ('tikzpicture',)
UNWRAPPED_ENVIRONMENTS = ('center',)

TABULAR = re.compile(
    r'\\begin\{tabular\}(?:\[[^\]]*\])?'
    # The column spec NESTS -- `{p{2.8cm}p{2.8cm}}` -- and a `[^}]*` stops at the first
    # inner brace, which leaks "p 2.8cm p 2.8cm" into the reader's answer. Measured.
    r'\{(?:[^{}]|\{[^{}]*\})*\}'
    r'(.*?)\\end\{tabular\}', re.S)

# A row becomes a sentence and a cell becomes a clause.  The separator is a middle dot
# rather than a pipe or a comma: a comma is already inside cells, and a pipe reads as a
# shell.  Alignment is the one thing lost, and alignment is not the content.
CELL = ' · '

# The cards that cannot cross at all, named rather than counted, with the reason each
# one is here.  The key is the file and the question AS THIS SCRIPT PRINTS IT, trailing
# full stop included, so the line the failure tells you to add is the line you add.
#
# The compiler FAILS both ways -- a card on this list that now compiles is as much a
# finding as a card that stops compiling and is not on it -- because a list of exceptions
# nobody re-checks is how one of them becomes thirty.
CANNOT_CROSS = {
    ('areas/9-OAuth.tex', 'Authorization Code Flow Diagram.'):
        'the answer is a tikzpicture and nothing else; ab-ovo has no figure',
}


def lineno(text: str, index: int) -> int:
    return text[:index].count('\n') + 1


def braced(text: str, open_index: int) -> tuple[str, int]:
    """Read a brace group whose `{` is at `open_index`; return its contents and the index
    just past the closing `}`.  Regex cannot do this and the deck nests braces three deep
    inside `\\frametitle{\\AnswerTitle[...]{...}}`."""
    depth = 0
    for i in range(open_index, len(text)):
        if text[i] == '{':
            depth += 1
        elif text[i] == '}':
            depth -= 1
            if depth == 0:
                return text[open_index + 1:i], i + 1
    raise ValueError(f'unbalanced {{ at offset {open_index}')


def strip_environment(text: str, name: str) -> str:
    pattern = re.compile(r'\\begin\{' + name + r'\}.*?\\end\{' + name + r'\}', re.S)
    return pattern.sub(' ', text)


def unwrap_environment(text: str, name: str) -> str:
    return re.sub(r'\\(?:begin|end)\{' + name + r'\}', ' ', text)


def flatten_table(match: re.Match) -> str:
    """A LaTeX table as lines of prose.

    The cells are already text; what a `tabular` adds is a grid, and the grid is exactly
    what does not survive a schema whose body is one paragraph.  Rather than drop eight
    comparison cards -- which is what dropping the environment did, and three of them had
    nothing else in the answer -- each row becomes a line and each cell a clause.
    `normalise` turns the lines into sentences afterwards, as it does for a bullet list.
    """
    body = match.group(1)
    body = re.sub(r'\\multicolumn\{[^}]*\}\{[^}]*\}\{((?:[^{}]|\{[^{}]*\})*)\}', r'\1', body)
    body = re.sub(r'(?<!\\)&', CELL, body)
    return body


# ──────────────────────────────────────────────────────────────────────────────────────
# LaTeX -> text.  P11's normalisation, and the whole of it is here.
# ──────────────────────────────────────────────────────────────────────────────────────

# Commands whose ARGUMENT is the text and whose name is presentation: \texttt{Task} is
# the word Task. Applied repeatedly because they nest.
UNWRAP = ('texttt', 'textbf', 'textit', 'emph', 'textsf', 'underline', 'mbox', 'text')

# Commands that take an argument that is NOT text to keep.
DISCARD_WITH_ARGUMENT = ('vspace', 'hspace', 'setlength', 'label', 'hypertarget', 'phantom')

# Commands with no argument, which is all they are: a size, a space, a rule.
DISCARD_BARE = (
    'footnotesize', 'scriptsize', 'tiny', 'small', 'normalsize', 'large', 'Large',
    'centering', 'hline', 'noindent', 'par', 'bigskip', 'medskip', 'smallskip',
    'linewidth', 'textwidth', 'columnwidth', 'arraystretch', 'tabcolsep', 'hfill',
    'quad', 'qquad', 'strut',
)

SYMBOLS = {
    r'\ldots': '…', r'\dots': '…', r'\textasciitilde': '~', r'\textbackslash': '\\',
    r'\approx': '≈', r'\geq': '≥', r'\leq': '≤', r'\times': '×', r'\rightarrow': '→',
    r'\to': '→', r'\&': '&', r'\#': '#', r'\%': '%', r'\_': '_', r'\$': '$',
    r'\{': '{', r'\}': '}',
    # TYPOGRAPHY THE DECK USES AND A READER MUST NOT SEE. Each one was found by the
    # leftover-backslash guard below rather than by reading the deck: `e.g.\ ` forces a
    # sentence space, `N\,+\,1` sets thin spaces, and `ASP\.NET` stops LaTeX widening the
    # full stop. All three are spacing instructions, and none of them is text.
    '\\ ': ' ', r'\,': ' ', r'\;': ' ', r'\:': ' ', r'\!': '', r'\-': '',
    r'\.': '.',
}


def normalise(latex: str, *, sentences: bool = True) -> str:
    """One card's LaTeX to one paragraph of text.

    THE OUTPUT IS A PARAGRAPH, and that is a constraint from the other side rather than a
    preference: ab-ovo renders a body as a single `<p>`, so a line break or a bullet does
    not survive the journey. Rather than ship text whose shape depends on markup the
    renderer collapses, this turns every `\\\\` break and every `\\item` into a sentence and
    joins them with a space -- adding a full stop where a line has no closing punctuation,
    because two statements run together without one read as one broken sentence.
    """
    text = latex

    # \href{url}{label} -> label. Before UNWRAP, which would otherwise take the url.
    text = re.sub(r'\\href\{[^}]*\}\{((?:[^{}]|\{[^{}]*\})*)\}', r'\1', text)
    # \resizebox{a}{b}{ ... } -> the group's contents; the two measurements are layout.
    text = re.sub(r'\\resizebox\{[^}]*\}\{[^}]*\}\{%?', ' ', text)
    text = re.sub(r'\\(?:multicolumn|renewcommand)\{[^}]*\}(?:\{[^}]*\})+', ' ', text)

    for name in DISCARD_WITH_ARGUMENT:
        text = re.sub(r'\\' + name + r'\*?\{[^{}]*\}', ' ', text)

    for _ in range(4):                       # \textbf{\texttt{x}} is two rounds
        before = text
        for name in UNWRAP:
            text = re.sub(r'\\' + name + r'\{((?:[^{}]|\{[^{}]*\})*)\}', r'\1', text)
        if text == before:
            break

    # Lists become sentences. `\item` is the separator; the environment itself is gone by
    # the time this runs for the dropped ones, and itemize/enumerate are unwrapped here.
    text = re.sub(r'\\(?:begin|end)\{(?:itemize|enumerate|description)\}', '\n', text)
    text = re.sub(r'\\item(?:\[[^\]]*\])?', '\n', text)
    text = text.replace('\\\\', '\n')

    for symbol, replacement in SYMBOLS.items():
        text = text.replace(symbol, replacement)
    # After the escapes, so `\#` is not mistaken for a comment.
    text = re.sub(r'(?<!\\)%.*', '', text)

    for name in DISCARD_BARE:
        text = re.sub(r'\\' + name + r'\b', ' ', text)

    text = text.replace('~', ' ').replace('``', '“').replace("''", '”')
    # Inline maths, in both spellings the deck uses. `\(O(1)\)` is prose about complexity
    # here rather than typeset mathematics, and the delimiters are all that has to go.
    text = re.sub(r'\$([^$]*)\$', r'\1', text)
    text = re.sub(r'\\[()\[\]]', '', text)
    text = text.replace('---', '—').replace('--', '–')
    text = re.sub(r'[{}]', ' ', text)

    lines = [re.sub(r'\s+', ' ', line).strip(' &|') for line in text.split('\n')]
    lines = [line.strip() for line in lines if line.strip()]

    # A BODY IS SENTENCES AND A TITLE IS NOT. Without the distinction a heading reads
    # "Databases." and a unit reads "C# Language: Beginner.", which is a full stop this
    # deck never wrote and no reader can remove.
    if not sentences:
        return ' '.join(lines).strip()

    return ' '.join(
        line if line[-1] in '.!?:;,' else line + '.'
        for line in lines
    ).strip()


# ANY surviving backslash, not just a `\word`: the deck's maths is written `\(O(1)\)`
# and a guard that only looked for letters after the backslash let every one of them
# through to a reader. Measured on the first full compile.
LEFTOVER_COMMAND = re.compile(r'\\[^\s]*')


# ──────────────────────────────────────────────────────────────────────────────────────
# Cards
# ──────────────────────────────────────────────────────────────────────────────────────

class Card:
    __slots__ = ('question', 'answer', 'code', 'category', 'line', 'dropped')

    def __init__(self, question, answer, code, category, line, dropped):
        self.question = question
        self.answer = answer
        self.code = code
        self.category = category
        self.line = line
        self.dropped = dropped


def read_cards(path: str, source: str, problems: list[str],
               omitted: list[tuple[str, str, str]]) -> list[Card]:
    cards: list[Card] = []

    for match in QUESTION.finditer(source):
        line = lineno(source, match.start())
        where = f'{path}:{line}'
        question_latex, after = braced(source, match.end() - 1)

        badge = BADGE.search(match.group('badge') or '')
        category = normalise(badge.group(1), sentences=False) if badge else ''

        frame = FRAME.search(source, after)
        if frame is None:
            problems.append(f'{where}: question slide with no answer frame after it')
            continue

        body = frame.group(1)

        # The title is the question again; the deck repeats it so the answer slide can be
        # read on its own. Dropping it here is not a loss -- the question is already the
        # step's body, and keeping it would print every question twice.
        title = body.find('\\frametitle')
        if title != -1:
            open_brace = body.index('{', title)
            _, end = braced(body, open_brace)
            body = body[:title] + body[end:]

        code = '\n\n'.join(listing(block.group(1)) for block in MINTED.finditer(body))
        body = MINTED.sub(' ', body)

        dropped = [name for name in DROPPED_ENVIRONMENTS if f'\\begin{{{name}}}' in body]
        for name in DROPPED_ENVIRONMENTS:
            body = strip_environment(body, name)
        body = TABULAR.sub(flatten_table, body)
        for name in UNWRAPPED_ENVIRONMENTS:
            body = unwrap_environment(body, name)

        question = normalise(question_latex)
        answer = normalise(body)

        excused = CANNOT_CROSS.get((path, question))
        empty = not answer and not code

        # BOTH DIRECTIONS. A card that stops compiling and is not on the list is a defect
        # in this script; a card on the list that has started compiling is a stale excuse,
        # and the entry has to go in the same commit as whatever fixed it.
        if excused and not empty:
            problems.append(
                f'{where}: CANNOT_CROSS excuses this card ("{excused}") and it now '
                f'compiles. Remove the entry.'
            )
        if empty and not excused:
            problems.append(
                f'{where}: the answer normalises to nothing and carries no code. Either '
                f'this script dropped something it should have kept, or the card is a '
                f'picture and nothing else -- in which case add, with the reason:\n'
                f"        ('{path}', {question!r}): '...'," 
            )
        if excused:
            omitted.append((where, question, excused))
            continue

        for label, text in (('question', question), ('answer', answer)):
            leftover = LEFTOVER_COMMAND.search(text)
            if leftover:
                problems.append(
                    f'{where}: the {label} still holds "{leftover.group(0)}" after '
                    f'normalisation. Teach scripts/compile-bundle.py what it means '
                    f'rather than letting a reader meet a backslash.'
                )
        if not question:
            problems.append(f'{where}: the question normalises to nothing')

        cards.append(Card(question, answer, code, category, line, dropped))

    return cards


def listing(source: str) -> str:
    """A `minted` block as source: its own indentation kept, the frame's removed.

    The closing `\\end{minted}` sits indented inside the frame, so the raw capture ends
    with the two spaces in front of it -- trailing whitespace that would reach a reader
    inside a `<pre>`. Blank edges go, every line is right-trimmed, and a listing that is
    uniformly indented is dedented so the code starts at column zero rather than wherever
    the slide put it.
    """
    lines = [line.rstrip() for line in source.split('\n')]
    while lines and not lines[0].strip():
        lines.pop(0)
    while lines and not lines[-1].strip():
        lines.pop()
    if not lines:
        return ''
    indent = min((len(line) - len(line.lstrip()) for line in lines if line.strip()), default=0)
    return '\n'.join(line[indent:] for line in lines)


def slug(text: str) -> str:
    out = re.sub(r'[^a-z0-9]+', '-', text.lower()).strip('-')
    return out or 'cards'


def unit_for(number: int, title: str, cards: list[Card]) -> dict:
    """One area as a unit: N cards, N+1 steps, headings from the category badges."""
    steps: list[dict] = []
    for index, card in enumerate(cards):
        step: dict = {'n': index + 1, 'kind': 'frame'}
        if index > 0:
            step['answer'] = {LANGUAGE: cards[index - 1].answer}
            if cards[index - 1].code:
                step['code'] = {'language': CODE_LANGUAGE, 'source': cards[index - 1].code}
        step['body'] = {LANGUAGE: card.question}
        step['cue'] = True
        steps.append(step)

    last = cards[-1]
    closing: dict = {
        'n': len(cards) + 1,
        'kind': 'prose',
        'answer': {LANGUAGE: last.answer},
        'body': {LANGUAGE: CLOSING_BODY},
    }
    if last.code:
        closing['code'] = {'language': CODE_LANGUAGE, 'source': last.code}
    steps.append(closing)

    # A heading per RUN of one badge, not per distinct badge: the deck returns to a
    # category later in an area, and a section's span in ab-ovo ends where the next one
    # begins. Two spans cannot share an id, so a repeat is numbered.
    sections: list[dict] = []
    seen: dict[str, int] = {}
    for index, card in enumerate(cards):
        if not card.category or (index > 0 and card.category == cards[index - 1].category):
            continue
        base = slug(card.category)
        seen[base] = seen.get(base, 0) + 1
        identifier = base if seen[base] == 1 else f'{base}-{seen[base]}'
        sections.append({
            'id': identifier,
            'titles': {LANGUAGE: card.category},
            'firstStep': index + 1,
        })

    # Every step belongs to the heading it opens under, INCLUDING the closing one, which
    # belongs to the last card's heading because it carries that card's answer.
    if sections:
        boundaries = [section['firstStep'] for section in sections] + [len(steps) + 1]
        for position, section in enumerate(sections):
            for n in range(boundaries[position], boundaries[position + 1]):
                steps[n - 1]['section'] = section['id']
        for step in steps:
            step.setdefault('section', None)
        for step in steps:
            if step['section'] is None:
                del step['section']

    unit: dict = {'id': f'A{number:02d}', 'titles': {LANGUAGE: title}}
    if sections:
        unit['sections'] = sections
    unit['steps'] = [order_step(step) for step in steps]
    return unit


def order_step(step: dict) -> dict:
    """Schema order, so a diff of two compiles is a diff of content."""
    keys = ('n', 'kind', 'section', 'titles', 'answer', 'body', 'code', 'cue', 'check')
    return {key: step[key] for key in keys if key in step}


# ──────────────────────────────────────────────────────────────────────────────────────
# The structural rules ab-ovo's validator applies, applied here first
# ──────────────────────────────────────────────────────────────────────────────────────

def verify(bundle: dict) -> list[str]:
    """What JSON Schema cannot say, checked by the producer rather than discovered by the
    consumer.  These are ab-ovo's `checkStructure` rules, and a bundle that fails one of
    them is refused there -- finding out here is the difference between a compiler with a
    contract and a compiler with a hope."""
    problems: list[str] = []
    languages = bundle['track']['languages']
    unit_ids: set[str] = set()

    for unit in bundle['units']:
        where = f'unit {unit["id"]}'
        if unit['id'] in unit_ids:
            problems.append(f'{where}: two units share this id')
        unit_ids.add(unit['id'])

        steps = unit['steps']
        section_ids = [section['id'] for section in unit.get('sections', [])]
        if len(section_ids) != len(set(section_ids)):
            problems.append(f'{where}: two sections share an id')

        firsts = [section['firstStep'] for section in unit.get('sections', [])]
        if any(b <= a for a, b in zip(firsts, firsts[1:])):
            problems.append(f'{where}: section firstStep must ascend strictly, and does not')
        for section in unit.get('sections', []):
            if not 1 <= section['firstStep'] <= len(steps):
                problems.append(f'{where}: section "{section["id"]}" anchors to a step that does not exist')

        for index, step in enumerate(steps):
            at = f'{where} step {step["n"]}'
            if step['n'] != index + 1:
                problems.append(f'{at}: steps must run 1..{len(steps)} in order')
            for field in ('titles', 'body', 'answer'):
                if field in step:
                    missing = [code for code in languages if code not in step[field]]
                    if missing:
                        problems.append(f'{at}: {field} is missing {missing}')
            if step.get('section') and step['section'] not in section_ids:
                problems.append(f'{at}: names a section this unit does not have')

            following = steps[index + 1] if index + 1 < len(steps) else None
            answered = following is not None and 'answer' in following
            if step.get('cue') is True and not answered:
                problems.append(f'{at}: says the next step answers it, and nothing does')
            if step.get('cue') is not True and answered:
                problems.append(f'{at}: the next step opens with an answer and nothing announces it')

    for text in (bundle['track']['titles'],):
        missing = [code for code in languages if code not in text]
        if missing:
            problems.append(f'track titles are missing {missing}')

    return problems


# ──────────────────────────────────────────────────────────────────────────────────────

def compile_bundle() -> tuple[dict, list[Card], list[tuple[str, str, str]], list[str]]:
    main = open(os.path.join(ROOT, 'main.tex'), encoding='utf-8').read()
    included = SECTION.findall(main)
    if not included:
        raise SystemExit('main.tex names no \\section{...}\\input{areas/...} pair; nothing to compile.')

    problems: list[str] = []
    omitted: list[tuple[str, str, str]] = []
    units: list[dict] = []
    every_card: list[Card] = []

    on_disk = {os.path.splitext(os.path.basename(p))[0] for p in glob.glob(os.path.join(ROOT, 'areas', '*.tex'))}
    listed = {name for _, name in included}
    for orphan in sorted(on_disk - listed):
        problems.append(f'areas/{orphan}.tex is in the tree and in no \\input{{}} in main.tex')

    for number, (title_latex, stem) in enumerate(included, start=1):
        path = f'areas/{stem}.tex'
        source = open(os.path.join(ROOT, path), encoding='utf-8').read()
        cards = read_cards(path, source, problems, omitted)
        if not cards:
            problems.append(f'{path}: no cards')
            continue
        every_card.extend(cards)
        units.append(unit_for(number, normalise(title_latex, sentences=False), cards))

    bundle = {
        'schemaVersion': 1,
        'tag': '',
        'track': {
            'id': TRACK_ID,
            'titles': {LANGUAGE: TRACK_TITLE},
            'languages': [LANGUAGE],
        },
        'units': units,
    }

    # THE TAG IS THE CONTENT'S OWN DIGEST, not a number somebody remembers to raise.
    # ab-ovo keys every tally on (track, tag) so that "a frame which was reworded is a
    # different frame for the instrument's purposes rather than the same frame with a
    # suspicious history". A hand-maintained tag makes that guarantee only as good as the
    # last person to edit a card; a digest makes it mechanical.
    material = json.dumps(
        {'track': bundle['track'], 'units': bundle['units']},
        ensure_ascii=False, sort_keys=True, separators=(',', ':'),
    )
    bundle['tag'] = 'deck-' + hashlib.sha256(material.encode('utf-8')).hexdigest()[:12]

    problems.extend(verify(bundle))
    return bundle, every_card, omitted, problems


def render(bundle: dict) -> str:
    return json.dumps(bundle, ensure_ascii=False, indent=2) + '\n'


def report(bundle: dict, cards: list[Card],
           omitted: list[tuple[str, str, str]]) -> None:
    with_code = sum(1 for card in cards if card.code)
    lost = [card for card in cards if card.dropped]
    print(f'track      {bundle["track"]["id"]} @ {bundle["tag"]}')
    print(f'units      {len(bundle["units"])}')
    print(f'cards      {len(cards)}  ({with_code} carry a code listing)')
    print(f'steps      {sum(len(unit["steps"]) for unit in bundle["units"])}')

    if lost:
        print(f'\n{len(lost)} card(s) lose a diagram the schema cannot hold:')
        for card in lost:
            print(f'  {card.question[:74]}')

    if omitted:
        print(f'\n{len(omitted)} card(s) do not cross at all:')
        for where, question, reason in omitted:
            print(f'  {question[:52]:54s} {reason}')

    summary = os.environ.get('GITHUB_STEP_SUMMARY')
    if summary:
        with open(summary, 'a', encoding='utf-8') as handle:
            handle.write(
                f'\n## Bundle\n\n`{bundle["track"]["id"]}` at **{bundle["tag"]}** — '
                f'{len(cards)} cards in {len(bundle["units"])} units, '
                f'{with_code} with code, {len(lost)} losing a diagram, '
                f'{len(omitted)} not crossing at all.\n'
            )


def validate_against(schema_path: str, bundle: dict) -> list[str]:
    try:
        import jsonschema
    except ImportError:
        return ['--schema was given and the jsonschema package is not installed '
                '(pip install jsonschema). Refusing to report a pass nothing checked.']
    schema = json.load(open(schema_path, encoding='utf-8'))
    validator = jsonschema.Draft202012Validator(schema)
    return [
        '/' + '/'.join(str(part) for part in error.absolute_path) + ': ' + error.message
        for error in sorted(validator.iter_errors(bundle), key=lambda e: list(e.absolute_path))
    ]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    parser.add_argument('--check', action='store_true',
                        help='recompile and compare with the committed bundle; write nothing')
    parser.add_argument('--schema', metavar='PATH',
                        help="ab-ovo's content-schema.v1.json, to validate the result against")
    arguments = parser.parse_args()

    bundle, cards, omitted, problems = compile_bundle()

    if arguments.schema:
        problems.extend(validate_against(arguments.schema, bundle))

    report(bundle, cards, omitted)

    if problems:
        print(f'\n{len(problems)} problem(s):', file=sys.stderr)
        for problem in problems:
            print(f'  {problem}', file=sys.stderr)
        return 1

    rendered = render(bundle)
    if arguments.check:
        try:
            committed = open(OUT, encoding='utf-8').read()
        except FileNotFoundError:
            print(f'\n{os.path.relpath(OUT, ROOT)} does not exist. Run this script without '
                  f'--check and commit the result.', file=sys.stderr)
            return 1
        if committed != rendered:
            print(f'\n{os.path.relpath(OUT, ROOT)} is not what the deck compiles to.\n'
                  f'Either a card changed and the bundle was not rebuilt, or the bundle was\n'
                  f'edited by hand. Run:  python3 scripts/compile-bundle.py',
                  file=sys.stderr)
            return 1
        print('\nthe committed bundle matches the deck')
        return 0

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, 'w', encoding='utf-8') as handle:
        handle.write(rendered)
    print(f'\nwrote {os.path.relpath(OUT, ROOT)}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
