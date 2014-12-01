ServerAuditor ssh config utility
================================



Prerequisites
-------------

Our package requires `cryptolibrary <https://pypi.python.org/pypi/pycrypto>`_, so please install Python Development Libraries for it. If you're on Ubuntu/Debian:

.. code-block:: bash

    $ sudo apt-get install python-dev

or if you use Fedora/RedHat

.. code-block:: bash

    $ sudo yum  install python-devel.x86_64


Installation
------------

ServerAuditor ssh config utility can be installed via `pip <http://www.pip-installer.org/en/latest/index.html>`_:

.. code-block:: bash

    $ pip install -U serverauditor-sshconfig

or `easy_install <http://pythonhosted.org/distribute/>`_:

.. code-block:: bash

    $ easy_install -U serverauditor-sshconfig


Usage
-----

If you want to *export* connections from your computer to your ServerAuditor's account:

.. code-block:: bash

    $ serverauditor export

If you want to *import* connections from your ServerAuditor's account to your computer:

.. code-block:: bash

    $ serverauditor import


License
-------

Please see `LICENSE <https://github.com/Crystalnix/serverauditor-sshconfig/blob/master/LICENSE>`_.

Notes
-----

* Some stages of utility's work may last for several seconds (depends on amount of the connections and your computer's performance).
