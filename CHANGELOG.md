# Change Log

## 1.2.1

- use uv tool as dependencies manager
- update github workflow
- fix few code style issue


## 1.2.0

- Remove python 3.8 support


## 1.1.5

Security Fix:

- inja vulnerable to HTML attribute injection when passing user input as keys to xmlattr filter

Build System:

  - update poetry declaration
  - use poe plugin (simplify makefile)
  - use pyright for analysis (remove mypi)


## 1.1.4

Build System:

- update dependabot pipeline
- update security dependencies


## 1.1.3

Bug Fix:

- bad docs on installation

## 1.1.2

Bug Fix:

- registry name when generate .terraformrc 

## 1.1.1 (2023-10-07)

Security fix (dev tools):

- Removal of e-Tugra root certificate
- `Cookie` HTTP header isn't stripped on cross-origin redirects

## 1.1.0 (2023-06-27)

Feat:

- Check if module ever exists before publishing or release.
- Add 'unpublish' command

Test:

- Add blob api experimental api to expose released terraform module into dedicated bucket.

## 1.0.0 (2023-06-21)

Feat:

- Generate project structure from [geronimo-iia/python-module-template](https://github.com/geronimo-iia/python-module-template)
- Check github action
- Add ApplicationConfiguration and load from yaml files, environment variable
- Add client utility and parser
- Add token management command
- add publish command
- add release command
- initiate documentation site
- add user documentation and usage into readme
- add basic test unit


