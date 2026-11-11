## What and why

<!-- What does this change, and what problem does it solve? Link the issue: "Closes #12". -->

## For gold-set changes

<!-- Show the working for each expected answer, and say why the keywords or tolerance are the right test. -->

## Checklist

- [ ] Tests added or updated, and `pytest` passes
- [ ] `ruff check .` and `ruff format --check .` pass
- [ ] `bondbench validate` passes (if the gold set changed)
- [ ] If a check changed: I ran `bondbench score examples/p1-archive/runs.csv` and noted whether the results moved
- [ ] `CHANGELOG.md` updated for user-visible changes
- [ ] No proprietary or client data, and nothing copied from paid exam or training material
