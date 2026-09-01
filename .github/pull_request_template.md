<!--
  What a review of this repository actually needs. Delete what does not apply;
  do not delete the headings you are answering.
-->

## What changed

<!-- One or two sentences. If cards changed, say which areas. -->

## Card count

<!--
  Before → after. `python3 scripts/lint-cards.py` prints it, and CI puts it in
  the run summary along with the built page count.

  Leave this as "unchanged" for a change that touches no card.
-->

- Cards: <!-- e.g. 269 → 271, or unchanged -->

## Evidence

- [ ] CI is green on this branch (**not** "this would obviously pass" — the deck
      has 24 area files and 197 frames carrying code listings).
- [ ] `python3 scripts/lint-cards.py` passes locally.

## If this touches `mybeamer.cls`, `mybeamer.sty` or `main.tex`

A style change is invisible in the diff and obvious on the page, so say what you
checked in the rendered PDF. Download it from the run's Artifacts.

- Pages before → after: <!-- the run summary prints this -->
- What you looked at:

## If this touches a workflow

- [ ] The check was seen to **fail** on a deliberate defect, not only to pass.
      A check nobody has watched fail is not known to be checking anything.
