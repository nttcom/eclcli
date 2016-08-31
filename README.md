# Enterprise Cloud CLI

Enterprise Cloud CLI (aka eclcli) is an [OpenStackClient](https://github.com/openstack/python-openstackclient) based command-line client for NTT Communications' Enterprise Cloud 2.0 that brings the command set for Baremetal, Compute, SSS, Image, Network, Block Storage and various other APIs together in a single shell with a uniform command structure.

The primary goal is to provide a unified user experience for various services provide in ECL2.0 through a uniform command structure.

# Getting Started

Enterprise Cloud CLI can be installed from PyPI using pip::

```sh
$~ pip install eclcli
```

There are a few variants on getting help.  A list of global options and supported
commands is shown with ``--help``::

```sh
ecl --help
```

There is also a ``help`` command that can be used to get help text for a specific
command::

```sh
ecl help
ecl help baremetal server create
```

## Configuration

The CLI is configured via environment variables and command-line

Authentication using username/password is most commonly used::

```sh
export OS_USERNAME=<username>
export OS_PASSWORD=<password>
export OS_TENANT_ID=<tenant_id>
export OS_AUTH_URL=<auth_url>
export OS_PROJECT_DOMAIN_ID=default
export OS_USER_DOMAIN_ID=default
```

## Usage
```sh
$~ ecl command list
#Returns all available commands

$~ ecl baremetal server list
#Returns list of baremetal servers

$~ ecl help baremetal
#Returns help for any command
```

## Documentation
Please find more usage documentation [here](https://ecl.ntt.com)

## Support

ECL2.0 users can raise requests via NTT Communications' ticket portal

## Contact

## Contributing

Please contribute using [Github Flow](https://guides.github.com/introduction/flow/). Create a branch, add commits, and [open a pull request](https://github.com/nttcom/eclcli/compare/).
## License
* Apache 2.0
