# Elmo

[![CircleCI](https://circleci.com/gh/palazzem/elmo-alerting/tree/master.svg?style=svg)](https://circleci.com/gh/palazzem/elmo-alerting/tree/master)
[![codecov](https://codecov.io/gh/palazzem/elmo-alerting/branch/master/graph/badge.svg)](https://codecov.io/gh/palazzem/elmo-alerting)

Elmo is an API adapter used to control programmatically an Elmo alarm system.
Through a generic configuration, the client allows:

* Retrieving access tokens to make API calls
* Obtaining/releasing the system `Lock()` to have exclusive control of the system
* Arm/disarm all the alarms registered in the system

This project is a **Work in Progress** and the following functionalities are part
of the roadmap:

* Retrieve alarm status (armed/disarmed) via read-only API
* Arm/disarm a single alarm or a subset
* REST stateless API on top of the `ElmoClient` to expose these functionalities
  via [Google Cloud Functions](https://cloud.google.com/functions/)

## Requirements

* Python 3.5+
* `requests`

## Getting Started

Elmo is not available on PyPI so installation from this repository is required:

```bash
$ pip install git+https://github.com/palazzem/elmo-alerting.git
```

### Arm/disarm the System

```python
from elmo.api.client import ElmoClient

# Initialize the client with an API endpoint and a vendor and
# authenticate your connection to retrieve the access token
client = ElmoClient("https://example.com", "vendor")
client.auth("username", "password")

# To arm/disarm the system you must gain the exclusive Lock()
with client.lock("secret-code") as c:
    c.arm()     # Arms all alarms
    c.disarm()  # Disarms all alarms
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

We use [flake8][1] as a style guide enforcement. Said that, we also use [black][2] to
reformat our code, keeping a well defined style even for quotes, multi-lines blocks and other.
Before submitting your code, be sure to launch `black` to reformat your PR.

[1]: https://pypi.org/project/flake8/
[2]: https://github.com/ambv/black

### Testing

`tox` is used to execute the following test matrix:
* `lint`: launches `flake8` and `black --check` to be sure the code honors our style guideline
* `py{35,36,37}`: launches `py.test` to execute all tests under Python 3.5, 3.6 and 3.7.

To launch the full test matrix, just:

```bash
$ tox
```
