# Contributing to pass

Wombat Core (`pass`) is the Python scanning engine used by the CLI, server and GitHub Action.

## Before you start

- Open an issue for larger changes so the approach can be agreed before implementation.
- Keep pull requests focused and include tests for behaviour changes.
- Sign off your commits with `git commit -s` (Developer Certificate of Origin, see `DCO`).

## Development checks

```bash
python -m pip install -e ".[dev]"
pytest
ruff check .
```


## Pull requests

- Describe the problem and the chosen approach.
- Link related issues.
- Update `CHANGELOG.md` when the change is user-visible.
- Keep documentation and examples in sync with the code.
