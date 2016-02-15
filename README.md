# Serverauditor ssh config utility

[![Build status](https://travis-ci.org/Crystalnix/serverauditor-sshconfig.svg?branch=master)](https://travis-ci.org/Crystalnix/serverauditor-sshconfig)
[![Code Climate](https://codeclimate.com/github/Crystalnix/serverauditor-sshconfig/badges/gpa.svg)](https://codeclimate.com/github/Crystalnix/serverauditor-sshconfig)
[![Test Coverage](https://codeclimate.com/github/Crystalnix/serverauditor-sshconfig/badges/coverage.svg)](https://codeclimate.com/github/Crystalnix/serverauditor-sshconfig/coverage)


## Installation

Serverauditor ssh config utility can be installed via [pip](http://www.pip-installer.org/en/latest/index.html):

```bash
$ pip install -U serverauditor-sshconfig
```
or [easy_install](http://pythonhosted.org/distribute/):

```bash
$ easy_install -U serverauditor-sshconfig
```

## Usage


If you want to *export* connections from your computer to your Serverauditor's account:

```bash
$ serverauditor export
```
If you want to *import* connections from your Serverauditor's account to your computer:

```bash
$ serverauditor import
```

## License


Please see [LICENSE](https://github.com/Crystalnix/serverauditor-sshconfig/blob/master/LICENSE).


## Notes


* Some stages of utility's work may last for several seconds (depends on amount of the connections and your computer's performance).

* If installation failed with gcc error, you must install Python Development Libraries, for example:

```bash
$ sudo apt-get install python-dev
```
or

```bash
$ sudo yum  install python-devel.x86_64
```
