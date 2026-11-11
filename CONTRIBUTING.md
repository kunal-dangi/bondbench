# Contributing to bondbench

Thanks for helping. Small, focused pull requests are the easiest to review and
merge. If you're unsure whether something is wanted, open an issue first and
ask.

## Ways to help

1. **Add gold-set questions.** This is the most valuable contribution,
   especially from people who work in fixed income, structured credit or fund
   operations. See the rules below.
2. **Improve a check.** The known limitations in the README are all open
   issues.
3. **Add a provider**, such as Gemini or Bedrock.
4. **Improve the docs**: tutorials, examples, clearer error messages.

Issues labelled
[good first issue](https://github.com/rohanjindal-pm/bondbench/labels/good%20first%20issue)
are scoped so you can finish them in an evening without knowing the codebase.

## Development setup

```bash
git clone https://github.com/rohanjindal-pm/bondbench
cd bondbench
python -m venv .venv && source .venv/bin/activate   # or: uv venv && source .venv/bin/activate
pip install -e ".[dev]"

pytest                 # tests make no network calls and need no API keys
ruff check .           # lint
ruff format .          # format
bondbench validate     # check the built-in gold set
```

CI runs all of these on Python 3.10 to 3.13 for every pull request.

## Adding gold-set questions

Questions live in `src/bondbench/data/fixed_income_ops_v1.csv`. The column
format is in the README.

- **One topic per pull request.** Five questions on CLO coverage tests is a
  good PR; twenty questions on everything is hard to review.
- **Explain the answer in the PR description.** For keyword questions, say why
  those keywords are the right test. For numeric questions, show the
  calculation, and give the tolerance a reason (for example, "answers rounded
  to two decimals").
- **Prefer checks a reviewer can verify.** A calculation with one right number
  beats an open-ended question graded by keywords.
- **No proprietary or client data**, and nothing copied from paid exam or
  training material (CFA, FRM and similar). Write questions in your own words.
- **Use the next free id** (`q21`, `q22`, ...) and never renumber or edit an
  existing question in place. A changed question makes old results
  meaningless; add a new one instead.
- Run `bondbench validate` before you push.

The issue template "New gold-set question" walks through all of this.

## Changing a check

- Add a test that fails before your change and passes after it.
- Run `bondbench score examples/p1-archive/runs.csv` and say in the PR whether
  the re-graded results changed. `tests/test_runner.py` pins them, so if they
  move you'll need to update that test and explain why the new numbers are
  more correct.

## Adding a provider

- Import the SDK lazily inside the provider, so bondbench still works without
  it, and add it as an optional extra in `pyproject.toml`.
- Tests must not call the network. Use a scripted provider like the one in
  `tests/test_runner.py`.
- Document the environment variables it reads.

## Pull request checklist

- [ ] Tests added or updated, and `pytest` passes
- [ ] `ruff check .` and `ruff format --check .` pass
- [ ] `bondbench validate` passes if you touched the gold set
- [ ] `CHANGELOG.md` has a line under "Unreleased" for user-visible changes

I aim to give every pull request a first review within a week. If you've heard
nothing after that, a polite ping on the PR is welcome.

## Releasing (maintainers)

1. Update `version` in `pyproject.toml` and move the "Unreleased" notes in
   `CHANGELOG.md` under the new version.
2. Merge to `main`, then tag: `git tag v0.2.0 && git push origin v0.2.0`, and
   create a GitHub release from the tag.
3. Run the **Publish to PyPI** workflow from the Actions tab.

One-time PyPI setup: on pypi.org, go to *Your account > Publishing* and add a
pending trusted publisher with owner `rohanjindal-pm`, repository `bondbench`,
workflow `publish.yml` and environment `pypi`. No API token is needed.

## Code of conduct

Everyone taking part is expected to follow the
[code of conduct](CODE_OF_CONDUCT.md).
