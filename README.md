# E-connect Python API

[![PyPI version](https://badge.fury.io/py/econnect-python.svg)](https://badge.fury.io/py/econnect-python)
[![CircleCI](https://circleci.com/gh/palazzem/elmo-alerting/tree/master.svg?style=svg)](https://circleci.com/gh/palazzem/elmo-alerting/tree/master)
[![codecov](https://codecov.io/gh/palazzem/elmo-alerting/branch/master/graph/badge.svg)](https://codecov.io/gh/palazzem/elmo-alerting)

`econnect-python` is an API adapter used to control programmatically an Elmo alarm system.
Through a generic configuration, the client allows:

* Retrieving access tokens to make API calls
* Obtaining/releasing the system `Lock()` to have exclusive control of the system
* Arm/disarm all the alarms registered in the system
* Query the system and get the status of your sectors and inputs

## Requirements

* Python 3.5+
* `requests`

## Getting Started

This package is available on PyPI:

```bash
$ pip install econnect-python
```

### Usage

```python
from elmo import query
from elmo.api.client import ElmoClient

# Initialize the client with an API endpoint and a vendor and
# authenticate your connection to retrieve the access token
client = ElmoClient("https://example.com", "vendor")
client.auth("username", "password")

# To arm/disarm the system you must gain the exclusive Lock()
with client.lock("secret-code") as c:
    c.arm()        # Arms all alarms
    c.disarm()     # Disarms all alarms
    c.arm(sectors=[3, 4])  # Arms only sectors 3 and 4
    c.disarm(sectors=[3])  # Disarm only sector 3

# Query the system
sectors_armed, sectors_disarmed = client.query(query.SECTORS)
inputs_alerted, inputs_wait = client.query(query.INPUTS)

# Or use the shortcut
status = client.check()

# Returns:
# {
#   "sectors_armed": [{"id": 0, "name": "Entryway", "element": 1, "index": 0}, ...],
#   "sectors_disarmed": [{"id": 1, "name": "Kitchen", "element": 2, "index": 1}, ...],
#   "inputs_alerted": [{"id": 0, "name": "Door", "element": 3, "index": 0}, ...],
#   "inputs_wait": [{"id": 1, "name": "Window", "element": 4, "index": 1}, ...],
# }
```

The access token is valid for 10 minutes after that you need to authenticate again to
refresh the token. Obtaining the lock via `client.lock("code")` is mandatory to arm or
disarm the alert, otherwise the API returns `403`.

Once the lock is obtained, other clients cannot connect to the alarm system and only a
manual override on the terminal is allowed. Outside the context manager, the lock is
automatically released.

## Development

We accept external contributions even though the project is mostly designed for personal
needs. If you think some parts can be exposed with a more generic interface, feel free
to open a GitHub issue and to discuss your suggestion.

### Coding Guidelines

We use [flake8][1] as a style guide enforcement. That said, we also use [black][2] to
reformat our code, keeping a well defined style even for quotes, multi-lines blocks and
other.

Before submitting your code, be sure to launch `black` to reformat your PR.

[1]: https://pypi.org/project/flake8/
[2]: https://github.com/ambv/black

### Testing

`tox` is used to execute the following test matrix:
* `lint`: launches `flake8` and `black --check` to be sure the code honors our style
  guideline
* `py{35,36,37,38}`: launches `py.test` to execute all tests under Python 3.5, 3.6, 3.7
  and 3.8.

To launch the full test matrix, just:

```bash
$ tox
```
