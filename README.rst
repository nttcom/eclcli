Enterprise Cloud CLI
======================

Enterprise Cloud CLI (a.k.a eclcli) is an `OpenStackClient <https://github.com/openstack/python-openstackclient>`_ based command-line client for NTT Communications' Enterprise Cloud 2.0 that brings the command set for Baremetal, Compute, SSS, Image, Network, Block Storage and various other APIs together in a single shell with a uniform command structure.

The primary goal is to provide a unified user experience for various services provide in ECL2.0 through a uniform command structure.

Getting Started
------------------

Enterprise Cloud CLI can be installed from PyPI using pip.

.. code-block:: bash

   $ pip install eclcli

Yet it is strongly advised to use `virtualenv <https://virtualenv.pypa.io/en/stable/>`_ to avoid conflicts with system packages, in short:

.. code-block:: bash

   $ virtualenv .venv
   $ source .venv/bin/activate
   $ pip install --upgrade eclcli

For experienced users we suggest using `pyenv <https://github.com/pyenv/pyenv>`_ with pyenv-virtualenv plugin:

Configuration
--------------

Before you are able to use CLI you must configure it.

The CLI is configured via command-line, environment variables and `~/.config/ecl/clouds.yaml` file.

Authentication using username/password is most commonly used.

.. code-block:: bash

   $ export OS_USERNAME=<username>
   $ export OS_PASSWORD=<password>
   $ export OS_TENANT_ID=<tenant_id>
   $ export OS_AUTH_URL=<auth_url>
   $ export OS_PROJECT_DOMAIN_ID=default
   $ export OS_USER_DOMAIN_ID=default


In certain cases it may be more convenient to use file based configuration using file `~/.config/ecl/clouds.yaml`.

For more information see `ECL tutorial page <https://ecl.ntt.com/en/documents/tutorials/eclc/rsts/installation.html>`_.
Notice, though, that you may need to use `--os-cloud` option parameter to specify which credentials to use from the file.

Listing command references
--------------------------

There are a few variants on getting help.
A list of global options are supported with ``--help``.

.. code-block:: bash

   $ ecl --help

There is also a ``help`` command that can be used to get help text for a specific command.

.. code-block:: bash

   $ ecl help baremetal server create

Usage
--------

.. code-block:: bash

   $ ecl command list
   # Returns all available commands

   $ ecl baremetal server list
   # Returns list of baremetal servers

   $ ecl help baremetal
   # Returns help for any command

Documentation
----------------
Please find more usage documentation on `official site <https://ecl.ntt.com/en/>`_.

Support
-----------
ECL2.0 users can raise requests via NTT Communications' ticket portal.

Contact
-----------
* ecl-cli-sdk@ntt.com

Contributing
-------------

Please contribute using `Github Flow <https://guides.github.com/introduction/flow/>`_ Create a branch, add commits, and `open a pull request <https://github.com/nttcom/eclcli/compare/>`_.

License
-----------
* Apache 2.0
