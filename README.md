# Termius CLI utility

[![Build status](https://travis-ci.org/termius/termius-cli.svg?branch=master)](https://travis-ci.org/termius/termius-cli)
[![Code Climate](https://codeclimate.com/github/termius/termius-cli/badges/gpa.svg)](https://codeclimate.com/github/termius/termius-cli)
[![Test Coverage](https://codeclimate.com/github/termius/termius-cli/badges/coverage.svg)](https://codeclimate.com/github/termius/termius-cli/coverage)

Provides command line interface for cross-platform terminal Termius.

[this project used to be named serverauditor-sshconfig in the past]

## Demo

[![asciicast](https://asciinema.org/a/6ilu50dbofnkufy2hux3ghhx4.svg)](https://asciinema.org/a/6ilu50dbofnkufy2hux3ghhx4?speed=2)

## Installation

For macOS users, there is a [Homebrew](http://brew.sh/) formula. Usage:

```bash
$ brew install termius
```

**Note**: By default, the command above installs Bash and zsh completions.

For Linux users, there is a `bootstrap.sh` script. Usage:

```bash
$ curl -sSL https://raw.githubusercontent.com/Crystalnix/termius-cli/master/bootstrap.sh | bash
```

Termius CLI utility can be installed via [pip](http://www.pip-installer.org/en/latest/index.html):

```bash
pip install -U termius
```
or [easy_install](http://pythonhosted.org/distribute/):

```bash
easy_install -U termius
```

## Usage

Init (login, pull, import-ssh-config, push)

```bash
termius init
```

Login to termius.com

```bash
termius login
```

Pull data from termius.com

```bash
termius pull
```

Create host
```bash
termius host --address localhost --label myhost
```

Connect to host
```
termius connect myhost
```

Push data to termius.com
```bash
termius push
```

Import hosts from ssh config
```bash
termius import-ssh-config
```

Export hosts from local storage to ./termius/sshconfig
```bash
termius export-ssh-config
```

### `termius` vs `serverauditor`

#### Import
A `serverauditor` user used to enter:

```bash
$ serverauditor export
```

Instead of it, a `termius` user enters:

```bash
$ termius import-ssh-config  # Not required password, or login
$ termius push  # Send all data to the cloud
```

To prevent import of some super secure host a `termius` user
should write special `# termius:ignore` annotation:

```bash
Host super-secure
    # termius:ignore
    HostName example.com
    User secret_user
```

If a client are not logged in, the next command logs it in:
```bash
$ termius login  # One time
```

#### Export

A `serverauditor` user used to enter:

```bash
$ serverauditor import
```

Instead of it, a `termius` user enters:

```bash
$ termius export-ssh-config  # Export to ./termius/sshconfig
```

## License

Please see [LICENSE](https://github.com/termius/termius-cli/blob/master/LICENSE).
