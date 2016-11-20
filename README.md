# Termius CLI utility

[![Build status](https://travis-ci.org/Crystalnix/serverauditor-sshconfig.svg?branch=master)](https://travis-ci.org/Crystalnix/serverauditor-sshconfig)
[![Code Climate](https://codeclimate.com/github/Crystalnix/serverauditor-sshconfig/badges/gpa.svg)](https://codeclimate.com/github/Crystalnix/serverauditor-sshconfig)
[![Test Coverage](https://codeclimate.com/github/Crystalnix/serverauditor-sshconfig/badges/coverage.svg)](https://codeclimate.com/github/Crystalnix/serverauditor-sshconfig/coverage)

## Demo

[![demo](https://asciinema.org/a/9w1l0zgyiax6u3nqkd4qrpg5p.png)](https://asciinema.org/a/9w1l0zgyiax6u3nqkd4qrpg5p?autoplay=1)

## Installation

Termius CLI utility can be installed via [pip](http://www.pip-installer.org/en/latest/index.html):

```bash
pip install -U termius
```
or [easy_install](http://pythonhosted.org/distribute/):

```bash
easy_install -U termius
```


## Usage

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

Create hosts from ssh config
```bash
termius sync ssh
```

## License


Please see [LICENSE](https://github.com/Crystalnix/serverauditor-sshconfig/blob/master/LICENSE).


## Notes


* Some stages of utility's work may last for several seconds (depends on amount of the connections and your computer's performance).

* If installation failed with gcc error, you must install Python Development Libraries, for example:

```bash
sudo apt-get install python-dev
```
or

```bash
sudo yum  install python-devel.x86_64
```
