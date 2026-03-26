<!--
<img src="images/logo.png?raw=True" align="right" width="20%"/>
# CoverUp: Automatically Generating Higher-Coverage Test Suites with AI !
-->
<img src="images/logo-with-title.png?raw=True" align="right" width="100%"/>

by [Juan Altmayer Pizzorno](https://jaltmayerpizzorno.github.io) and [Emery Berger](https://emeryberger.com)
at UMass Amherst's [PLASMA lab](https://plasma-umass.org/).

[![pypi](https://img.shields.io/pypi/v/coverup?color=blue)](https://pypi.org/project/coverup/)
![pyversions](https://img.shields.io/pypi/pyversions/coverup)
[![Downloads](https://static.pepy.tech/badge/coverup)](https://pepy.tech/project/coverup)
[![Downloads](https://static.pepy.tech/badge/coverup/month)](https://pepy.tech/project/coverup)
![tests](https://github.com/plasma-umass/coverup/workflows/tests/badge.svg)


## About CoverUp
CoverUp automatically generates tests that ensure that more of your code is tested
(that is, it increases its [code coverage](https://en.wikipedia.org/wiki/Code_coverage)).
CoverUp can also create a test suite from scratch if you don't yet have one.
The new tests are based on your code, making them useful for [regression testing](https://en.wikipedia.org/wiki/Regression_testing).

CoverUp is designed to work closely with the [pytest](https://docs.pytest.org/en/latest/) test framework.
To generate tests, it first measures your suite's coverage using [SlipCover](https://github.com/plasma-umass/slipcover).
It then selects portions of the code that need more testing (that is, code that is uncovered).
CoverUp then engages in a conversation with an [LLM](https://en.wikipedia.org/wiki/Large_language_model),
prompting for tests, checking the results to verify that they run and increase coverage (again using SlipCover), and re-prompting for adjustments as necessary.
Finally, CoverUp optionally checks that the new tests integrate well, attempting to resolve any issues it finds.

For technical details and a complete evaluation, see our arXiv paper, [_CoverUp: Coverage-Guided LLM-Based Test Generation_](https://arxiv.org/abs/2403.16218) ([PDF](https://arxiv.org/pdf/2403.16218)), to appear at FSE 2025.


## Installing CoverUp
CoverUp is available from PyPI, so you can install simply with
```shell
$ python3 -m pip install coverup
```

### LLM model access
CoverUp can be used with OpenAI, Anthropic or AWS Bedrock models; it requires that the
access details be defined as shell environment variables: `OPENAI_API_KEY`,
`ANTHROPIC_API_KEY` or `AWS_ACCESS_KEY_ID`/`AWS_SECRET_ACCESS_KEY`/`AWS_REGION_NAME`, respectively.

For example, for OpenAI you would create an [account](https://platform.openai.com/signup), ensure
it has a [positive balance](https://platform.openai.com/account/usage) and then create an
an [API key](https://platform.openai.com/api-keys), storing its "secret key" (usually a
string starting with `sk-`) in an environment variable named `OPENAI_API_KEY`:
```shell
$ export OPENAI_API_KEY=<...your-api-key...>
```

## Using CoverUp
If your module is named `mymod`, its sources are under `src` and the tests under `tests`, you can run CoverUp as
```shell
$ coverup --package src/mymod --tests tests
```
CoverUp then creates tests named `test_coverup_N.py`, where `N` is a number, under the `tests` directory.

### Web Console
CoverUp also includes a lightweight web console for uploading a repository archive, launching a run, monitoring the job, and downloading the newly generated valid tests:

```shell
$ python3 -m pip install .[web]
$ coverup-web --host 127.0.0.1 --port 8000
```

Then open `http://127.0.0.1:8000` in your browser.
The console accepts `.zip`, `.tar`, `.tar.gz`, and `.tgz` repository archives and stores run artifacts under `.coverup-web/` by default.

### Example
Here we have CoverUp create additional tests for the popular package [Flask](https://flask.palletsprojects.com/):
```
$ coverup --package src/flask --tests tests
Measuring coverage...  90.9%
Prompting gpt-4o-2024-05-13 for tests to increase coverage...
(in the following, G=good, F=failed, U=useless and R=retry)
100%|███████████████████████████████████████| 92/92 [01:01<00:00,  1.50it/s, G=55, F=122, U=20, R=0, cost=~$4.19]
Measuring coverage...  94.4%

$
```
In just over a minute, CoverUp increases Flask's test coverage from 90.9% to 94.4%.

### Avoiding flaky tests
While evaluating each newly generated test, CoverUp executes it a number of times in an
attempt to detect any flaky tests; that can be adjusted with the `--repeat-tests` and
`--no-repeat-tests` options.
If CoverUp detects that a newly generated test is flaky, it prompts the LLM for a correction.

### Test pollution and isolation
CoverUp only adds tests to the suite that, when run by themselves, pass and increase coverage.
However, it is possible tests to "pollute" the state, changing it in a way that causes other tests to fail.
By default, CoverUp uses the [pytest-cleanslate](https://github.com/plasma-umass/pytest-cleanslate)
plugin to isolate tests, working around any (in-memory) test pollution; that can be disabled by
passing in the `--no-isolate-tests` option.
CoverUp can also be asked to find and disable the polluting test module or function (`--disable-polluting`)
or simply disable any failing tests (`--disable-failing`).

### Running CoverUp with Docker
To evaluate the tests generated by the LLM, CoverUp must execute them.
For best security and to minimize the risk of damage to your system, we recommend
running CoverUp with [Docker](https://www.docker.com/).

## Evaluation

<img src="images/comparison.png?raw=True" align="right" width="65%"/>

The graph shows CoverUp in comparison to [CodaMosa](https://www.carolemieux.com/codamosa_icse23.pdf),
a state-of-the-art search-based test generator based on [Pynguin](https://github.com/se2p/pynguin) test generator.
For this experiment, both CoverUp and CodaMosa created tests "from scratch", that is, ignoring any existing test suite.
The bars show the difference in coverage percentage between CoverUp and CodaMosa for various Python modules;
green bars, above 0, indicate that CoverUp achieved a higher coverage.

As the graph shows, CoverUp achieves higher coverage than CodaMosa for most modules.

<br/>

## Go Language Support

CoverUp now supports generating tests for **Go** projects. The Go backend provides:

- **Static analysis** via tree-sitter: symbol lookup (`get_info`), branch inference, receiver context extraction
- **Branch coverage guidance**: infers logical branches from `if/else`, `switch/case`, `select` and feeds them into prompts
- **Dynamic prompt hints**: automatically detects patterns (interface, error handling, goroutine, context, file I/O, etc.) and adds Go-specific testing guidance
- **LLM tool function**: exposes `get_info` so the LLM can query Go type definitions, function signatures and methods during generation

### Using CoverUp for Go

```shell
$ coverup --language go --package-dir /path/to/your/go/module --model gpt-4o
```

Example with the [Cobra](https://github.com/spf13/cobra) CLI framework:
```shell
$ coverup --language go --package-dir src/cobra --model gpt-4o --prompt gpt-go-v1
```

### Go Requirements
- Go 1.20+ installed and in PATH
- Python 3.10+ with `tree-sitter` and `tree-sitter-languages` packages
- LLM API key (same as Python usage)

For detailed testing instructions, see [docs/testing-guide.md](docs/testing-guide.md).
For technical details on Go support improvements, see [docs/go_generation_updates.md](docs/go_generation_updates.md).

<br/>

## Work In Progress

This is an early release of CoverUp.
Please enjoy it, and pardon any disruptions as we work to improve it. We welcome bug reports, experience reports, and feature requests (please [open an issue](https://github.com/plasma-umass/coverup/issues/new)).
