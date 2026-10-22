# RETROSPECTIVE.md

## What went well?

- Clear module ownership (M1–M5) let everyone work in parallel.
- Branch → PR → review → CI workflow was followed consistently.
- FR-03 validation rules and boundary tests were designed early and caught several edge cases.
- CI (Ruff + pytest) stayed green on main after the mid-project stabilisation.

## What caused difficulties?

- Initial merge conflicts when several people edited main.py and templates at the same time.
- Getting the overlap check and “starts exactly when previous ends” rule correct took extra test iterations.
- Coordinating seed data and image filenames across machines.

## What would your group do differently next time?

- Agree on a single source of truth for models earlier and protect main.py with smaller, more frequent PRs.
- Write the FR-03 test cases before implementing the validation function (TDD style).
- Keep the project board updated daily instead of only before evaluations.

## Metrics

| Metric | Value |
|--------|-------|
| Issues completed | 9 (FR-00–FR-04 + DOC-01–DOC-04) |
| Pull requests merged | ~41 |
| Peer reviews performed | 4 |
| Final test coverage | 85%|
