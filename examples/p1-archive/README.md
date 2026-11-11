# P1 archive: the original study's responses

`runs.csv` holds the 60 responses (20 questions x 3 models) collected by the
original single-script harness (committed 5 July 2026) in
[ai-pm-portfolio P1](https://github.com/rohanjindal-pm/ai-pm-portfolio/tree/main/p1-hello-llm),
run at temperature 0 with the default system prompt in `bondbench.runner`.

Two things to know:

- The original script cut each response to 300 characters before saving it.
  Every answer that matters for grading fits inside that limit, and the old
  checks reproduce the old grades exactly on this file, but new checks that
  look past character 300 can't be applied to it.
- The `keyword_eval`, `refusal_eval`, `json_eval` and `passed_all` columns are
  the original, buggy grades. Re-grade with the current checks:

```bash
bondbench score examples/p1-archive/runs.csv --markdown
```

`tests/test_runner.py::test_score_reproduces_the_corrected_p1_results` pins
the re-graded numbers, so any change to a check that moves them shows up in CI.
