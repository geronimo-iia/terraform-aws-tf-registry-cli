# Contributing

This project is based on [Geronimo-iaa's Python Module Template](https://github.com/geronimo-iia/python-module-template).


## Setup

### Requirements

You will need:

* Python 3.11+
* [uv](https://docs.astral.sh/uv/getting-started/installation/)
* Make


### Make Installation

* macOS: `$ xcode-select --install`
* Linux: [https://www.gnu.org/software/make](https://www.gnu.org/software/make)
* Windows: [https://mingw.org/download/installer](https://mingw.org/download/installer)

### UV Installation

[https://docs.astral.sh/uv/getting-started/installation/](https://docs.astral.sh/uv/getting-started/installation/)

UV will manage dependencies and virtual environment.


## Development

Install the project:

```bash
make install
```

## Make Targets

| Name               | Comment                                    |
| ------------------ | ------------------------------------------ |
| make help          | Show available targets                     |
| make install       | Install project dependencies               |
| make lock          | Lock project dependencies                  |
| make lint          | Check format, linting and types            |
| make lint-fix      | Fix all auto-fixable issues                |
| make test          | Run unit tests                             |
| make check         | Run all checks (lint + test)               |
| make build         | Build module                               |
| make publish       | Publish module                             |
| make docs          | Build site documentation                   |
| make docs-serve    | Serve documentation locally with live reload |
| make docs-publish  | Publish site documentation                 |
| make clean         | Remove all generated and temporary files   |
| make requirements  | Generate requirements.txt                  |

Run `make help` to see the full list.
