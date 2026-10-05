# Contributing

BAA-Protocol is a research prototype for conditional guarantees and bounded action admission. Contributions should preserve the distinction between modeled properties, experimental evidence, and claims about real deployments.

## Before proposing a change

- State the behavior, assumption, or claim that the change affects.
- Keep guarantees conditional on their stated domain, interfaces, horizon, and evidence.
- Include reproducible tests or experiment evidence for changes to protocol behavior.
- Do not present compatibility with the pinned AIOS surface as production certification.

## Run the reference tests

From the repository root:

```powershell
python -m unittest discover -s tests -p "test_*.py" -v
python scripts/run_offboarding_experiment.py
```

The AIOS compatibility suite runs in `.github/workflows/tests.yml` against the pinned AIOS revision. Changes to that integration should preserve or explicitly update the pin and its compatibility evidence.

Open an issue for substantial protocol or experiment-design changes before investing in a large implementation. Pull requests should summarize the changed claim or behavior and the evidence used to evaluate it.
