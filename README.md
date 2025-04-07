# llm-templates-fabric

[![PyPI](https://img.shields.io/pypi/v/llm-templates-fabric.svg)](https://pypi.org/project/llm-templates-fabric/)
[![Changelog](https://img.shields.io/github/v/release/simonw/llm-templates-fabric?include_prereleases&label=changelog)](https://github.com/simonw/llm-templates-fabric/releases)
[![Tests](https://github.com/simonw/llm-templates-fabric/actions/workflows/test.yml/badge.svg)](https://github.com/simonw/llm-templates-fabric/actions/workflows/test.yml)
[![License](https://img.shields.io/badge/license-Apache%202.0-blue.svg)](https://github.com/simonw/llm-templates-fabric/blob/main/LICENSE)

Load LLM templates from Fabric

## Installation

Install this plugin in the same environment as [LLM](https://llm.datasette.io/).
```bash
llm install llm-templates-fabric
```
## Usage

This plugin adds a template loader with the `f:` prefix that loads templates from the [Fabric repository](https://github.com/danielmiessler/fabric).

```bash
# Use a Fabric template with LLM
llm -t f:explain explain_code
```

The plugin looks for templates in the Fabric repository's `patterns/` directory. For example, the command above will load from:
- System prompt: https://github.com/danielmiessler/fabric/blob/main/patterns/explain_code/system.md
- User prompt: https://github.com/danielmiessler/fabric/blob/main/patterns/explain_code/user.md

Both files are optional - if at least one of them exists, the template will load successfully.

## Development

To set up this plugin locally, first checkout the code. Then create a new virtual environment:
```bash
cd llm-templates-fabric
python -m venv venv
source venv/bin/activate
```
Now install the dependencies and test dependencies:
```bash
llm install -e '.[test]'
```
To run the tests:
```bash
python -m pytest
```
