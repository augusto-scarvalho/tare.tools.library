# Stack Specs

> Scope: section index for adopting-project specs; this file is an index, not a specification.

Use this folder for language, framework, runtime, toolchain, package manager, formatting, linting, testing, and build conventions for the adopted project.

The universal harness does not assume a stack. This folder is where a real project records stack-specific rules after adoption.

## What to document

- Supported languages and versions.
- Frameworks and runtime constraints.
- Package managers and lockfile policy.
- Formatting, linting, typechecking, and code-generation commands.
- Test framework and fixture conventions.
- Build and release commands.
- Directory conventions for source, tests, config, assets, generated code, and migrations.
- Rules for generated files and vendored artifacts.

## How this relates to `.harness/project.json`

- Human-readable conventions belong in stack specs.
- Executable commands belong in `.harness/project.json` under `validation` and `coverage`.
- If a command is expensive, document when to run it rather than forcing every task to execute it.

## Agent guidance

Agents should read stack specs before editing stack-sensitive files. If no stack spec exists yet, agents may inspect the repository and propose one, but should not assume a framework from unrelated examples.
