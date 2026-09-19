# `bundle/` — derived, never authored

`csharp-flashcards.bundle.json` is what `areas/*.tex` compiles to. It is written by
[`scripts/compile-bundle.py`](../scripts/compile-bundle.py) and by nothing else.

**Do not edit it.** A card is changed in its `areas/*.tex` file and the bundle is rebuilt;
editing the JSON puts a correction in a file the next compile overwrites, and leaves the deck
and the bundle saying different things in the meantime. `build.yml` runs
`compile-bundle.py --check` on every pull request precisely so that the two cannot disagree
without a red tick.

```bash
python3 scripts/compile-bundle.py            # rebuild after changing a card
python3 scripts/compile-bundle.py --check    # what CI runs; writes nothing
```

## What it is for

[ab-ovo](https://github.com/konradcinkusz/ab-ove) is a learning platform that reads content
bundles. It owns one schema, and it never parses LaTeX: the dialect is normalised once, at
the boundary, in the repository that knows the dialect — this one. So the deck crosses as
JSON, and ab-ovo pins it by `(track, tag)` and renders it.

That direction is the whole arrangement. ab-ovo does not read `areas/`, and a corrected card
reaches a reader there by being recompiled here and re-pinned there.

## The tag is the content's own digest

`tag` is `deck-` and twelve hex characters of a SHA-256 over the track and the units. It is
not a version somebody remembers to raise.

ab-ovo keys every tally on `(track, tag)` so that a reworded card is a *different* card for
measurement rather than the same card with a suspicious history. A hand-maintained tag makes
that guarantee only as good as the last person to edit one; a digest makes it mechanical. The
consequence is worth knowing before it surprises you: **any** change to any card moves the
tag, and moving the tag is what a consumer re-pins to.

## What does not cross, and why

The compiler carries prose, `\item` lists and `minted` listings. Three things it does not:

| Not carried | Why |
|---|---|
| The difficulty rating (`<1>`, `<2>`, `<3>`) | The schema has nowhere to put it. Recorded as a gap in ab-ovo's ADR-0037 rather than worked around here. |
| `tikzpicture` diagrams | A drawing has no sentence inside it to carry, and the schema has no figure. |
| The layout of a `tabular` | The cells survive as prose — a row becomes a sentence, a cell a clause. The alignment does not, and the alignment is not the content. |

One card is a diagram and nothing else, so it does not cross at all. It is named in
`CANNOT_CROSS` in the compiler, with its reason, and the compiler fails if that list stops
matching the deck — in *either* direction, because an exception nobody re-checks is how one
of them becomes thirty.

Everything else the compiler does not recognise **fails the run**, with the file and the
line. A LaTeX macro added to the deck is discovered there rather than by a reader meeting a
backslash on a web page.

## Validating against the platform's schema

The compiler applies ab-ovo's structural rules itself — steps contiguous from 1, a cue
matched by the answer that follows it, section anchors that exist, every declared language
present in every text — so a bundle that would be refused is refused here first.

It can also check the document shape against ab-ovo's schema directly:

```bash
pip install jsonschema
python3 scripts/compile-bundle.py --schema path/to/ab-ove/web/app/src/lib/content/content-schema.v1.json
```

This is not yet a CI gate, and the reason is specific rather than an omission: 196 of the
deck's cards carry a code listing, and schema v1 has no field for one. That single property
is the only thing the bundle fails on, and adding it is
[ab-ove#81](https://github.com/konradcinkusz/ab-ove/issues/81)'s other half. The gate lands
in the same change as the pin.
