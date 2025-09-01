# wheely-bucket

[![Python Version from PEP 621 TOML](https://img.shields.io/python/required-version-toml?tomlFilePath=https%3A%2F%2Fraw.githubusercontent.com%2Fsco1%2Fwheely-bucket%2Frefs%2Fheads%2Fmain%2Fpyproject.toml&logo=python&logoColor=FFD43B)](https://github.com/sco1/wheely-bucket/blob/main/pyproject.toml)
[![GitHub Release](https://img.shields.io/github/v/release/sco1/wheely-bucket)](https://github.com/sco1/wheely-bucket/releases)
[![GitHub License](https://img.shields.io/github/license/sco1/wheely-bucket?color=magenta)](https://github.com/sco1/wheely-bucket/blob/main/LICENSE)
[![pre-commit.ci status](https://results.pre-commit.ci/badge/github/sco1/wheely-bucket/main.svg)](https://results.pre-commit.ci/latest/github/sco1/wheely-bucket/main)

Cache wheels for your locked dependencies.

## Installation

Wheels are built in CI for each released version; the latest release can be found at: <https://github.com/sco1/wheely-bucket/releases/latest>

You can confirm proper installation via the `wheely_bucket` CLI:
<!-- [[[cog
import cog
from subprocess import PIPE, run
out = run(["wheely_bucket", "--help"], stdout=PIPE, encoding="ascii")
cog.out(
    f"\n```text\n$ wheely_bucket --help\n{out.stdout.rstrip()}\n```\n\n"
)
]]] -->

```text
$ wheely_bucket --help
Usage: wheely_bucket [OPTIONS] COMMAND [ARGS]...

  Cache wheels for your locked dependencies.

Options:
  --help  Show this message and exit.

Commands:
  package  Download wheels for the the specified package(s).
  project  Download wheels specified by the project's uv lockfile.
```

<!-- [[[end]]] -->

## Usage

`wheely-bucket` provides two mechanisms for package specification: manual specification & project lockfile specification.

### Manual Package Specification

Manual package specification is accomplished via the `wheely_bucket package` command:
<!-- [[[cog
import cog
from subprocess import PIPE, run
out = run(["wheely_bucket", "package", "--help"], stdout=PIPE, encoding="ascii")
cog.out(
    f"\n```text\n$ wheely_bucket package --help\n{out.stdout.rstrip()}\n```\n\n"
)
]]] -->

```text
$ wheely_bucket package --help
Usage: wheely_bucket package [OPTIONS] PACKAGES...

  Download wheels for the the specified package(s).

  Package specifiers are expected in a form understood by pip, e.g. "black" or
  "black==25.1.0".

  python_version and platform are expected in a form understood by 'pip
  download'; if not specified pip will default to matching the currently
  running interpreter.

Arguments:
  PACKAGES...  [required]

Options:
  --dest PATH            [default: .]
  --python-version TEXT
  --platform TEXT
  --help                 Show this message and exit.
```

<!-- [[[end]]] -->

### Project Lockfile Specification

Project lockfile specification is accomplished via the `wheely_bucket project` command:
<!-- [[[cog
import cog
from subprocess import PIPE, run
out = run(["wheely_bucket", "project", "--help"], stdout=PIPE, encoding="ascii")
cog.out(
    f"\n```text\n$ wheely_bucket project --help\n{out.stdout.rstrip()}\n```\n\n"
)
]]] -->

```text
$ wheely_bucket project --help
Usage: wheely_bucket project [OPTIONS] TOPDIR

  Download wheels specified by the project's uv lockfile.

  python_version and platform are expected in a form understood by 'pip
  download'; if not specified pip will default to matching the currently
  running interpreter.

  If recurse is True, the specified topdir is assumed to contain one or more
  projects managed by uv, and will recursively parse all contained lockfiles
  for locked dependencies.

Arguments:
  TOPDIR  [required]

Options:
  --dest PATH               [default: .]
  --recurse / --no-recurse  [default: no-recurse]
  --python-version TEXT
  --platform TEXT
  --help                    Show this message and exit.
```

<!-- [[[end]]] -->
