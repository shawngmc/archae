<!-- start docs-include-index -->

# Building Archae

## Environment

Recommend using Conda with Python 3.14+

## Tooling

From [CookieCutter template](https://github.com/sgraaf/cookiecutter-python-cli-app):

- Beautiful and powerful command-line interfaces with [Click](https://click.palletsprojects.com/)
- Linting with autofix (i.e. removing unused imports, formatting and Python syntax upgrades) with [ruff](https://beta.ruff.rs/docs/)
- Code formatting with [ruff](https://beta.ruff.rs/docs/) and [Prettier](https://prettier.io/)
- Static type-checking with [mypy](http://www.mypy-lang.org/)
- Checks and fixes before every commit with [pre-commit](https://pre-commit.com/)
- Testing with [pytest](https://docs.pytest.org/en/stable/index.html)
- Project automation with [Nox](https://nox.thea.codes/en/stable/)
- Extremely fast Python package and project management with [uv](https://docs.astral.sh/uv/)
- Continuous Integration with [GitHub Actions](https://github.com/features/actions) and [pre-commit.ci](https://pre-commit.ci/)
- Automated version updates for GitHub Actions with [Dependabot](https://docs.github.com/en/code-security/dependabot/working-with-dependabot/keeping-your-actions-up-to-date-with-dependabot)
- Documentation with [Sphinx](https://www.sphinx-doc.org/en/master/), [MyST](https://myst-parser.readthedocs.io/en/latest/), and [Read the Docs](https://readthedocs.org/) using the [Furo](https://pradyunsg.me/furo/) theme
- Automated release builds and uploads to [PyPI](https://pypi.org/)

## Activities

### Running code cleanup checks manually

```
pre-commit run --all-files
```

### Running normal documentation tasks

```
nox
```

### Updating embedded help blocks

```
nox -s cog
```

### Pushing to PyPi

This is also done via GitHub Actions.

```
nox -s release-to-pypi
```
