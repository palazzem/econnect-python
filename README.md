# E-connect Python API

[![PyPI version](https://badge.fury.io/py/econnect-python.svg)](https://badge.fury.io/py/econnect-python)

`econnect-python` is an API adapter used to control programmatically an Elmo alarm system.
Through a generic configuration, the client allows:

* Retrieving access tokens to make API calls
* Obtaining/releasing the system `Lock()` to have exclusive control of the system
* Arm/disarm all the alarms registered in the system
* Query the system and get the status of your sectors and inputs

## Requirements

* Python 3.8+
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

# Initialize a new client to authenticate your connection
# and retrieve an access token used for the entire session.
client = ElmoClient()
client.auth("username", "password")

# To arm/disarm the system you must gain the exclusive Lock()
with client.lock("secret-code") as c:
    c.arm()                # Arm all alarms
    c.disarm()             # Disarm all alarms
    c.arm(sectors=[3, 4])  # Arm only sectors 3 and 4
    c.disarm(sectors=[3])  # Disarm only sector 3

# Query the system
sectors_armed, sectors_disarmed = client.query(query.SECTORS)
inputs_alerted, inputs_wait = client.query(query.INPUTS)
```

The access token is valid for 10 minutes, after which, you need to authenticate again to
refresh the token. Obtaining the lock via `client.lock("secret-code")` is mandatory to arm or
disarm the system, otherwise the API returns `403`. `secret-code` is the numeric code you
use to arm/disarm the system from the alarm panel.

Once the lock is obtained, other clients cannot connect to the alarm system and only a
manual override on the terminal is allowed. Outside the context manager, the lock is
automatically released.

### Client Configuration

If `https://connect.elmospa.com` is your authentication page, no configuration is needed
and you can skip this section.

On the other hand, if your authentication page is something similar to
`https://connect3.elmospa.com/nwd`, you must configure your client as follows:

```python
# Override the default URL and domain
client = ElmoClient(base_url="https://connect3.elmospa.com", domain="nwd")
client.auth("username", "password")
```

If your `base_url` or `domain` are not properly set, your credentials will not work
and you will get a `403 Client Error` as your username and password are wrong.

## Contributing

We are very open to the community's contributions - be it a quick fix of a typo, or a completely new feature!
You don't need to be a Python expert to provide meaningful improvements. To learn how to get started, check
out our [Contributor Guidelines](https://github.com/palazzem/econnect-python/blob/main/CONTRIBUTING.md) first,
and ask for help in our [Discord channel](https://discord.gg/NSmAPWw8tE) if you have questions.

## Development

We welcome external contributions, even though the project was initially intended for personal use. If you think some
parts could be exposed with a more generic interface, please open a [GitHub issue](https://github.com/palazzem/econnect-python/issues)
to discuss your suggestion.

### Dev Environment

To create a virtual environment and install the project and its dependencies, execute the following commands in your
terminal:

```bash
# Create and activate a new virtual environment
python3 -m venv venv
source venv/bin/activate

# Upgrade pip and install all projects and their dependencies
pip install --upgrade pip
pip install -e '.[all]'

# Install pre-commit hooks
pre-commit install
```

### Coding Guidelines

To maintain a consistent codebase, we utilize [flake8][1] and [black][2]. Consistency is crucial as it
helps readability, reduces errors, and facilitates collaboration among developers.

To ensure that every commit adheres to our coding standards, we've integrated [pre-commit hooks][3].
These hooks automatically run `flake8` and `black` before each commit, ensuring that all code changes
are automatically checked and formatted.

For details on how to set up your development environment to make use of these hooks, please refer to the
[Development][4] section of our documentation.

[1]: https://pypi.org/project/flake8/
[2]: https://github.com/ambv/black
[3]: https://pre-commit.com/
[4]: https://github.com/palazzem/econnect-python#development

### Testing

Ensuring the robustness and reliability of our code is paramount. Therefore, all contributions must include
at least one test to verify the intended behavior.

To run tests locally, execute the test suite using `pytest` with the following command:
```bash
pytest tests/ --cov elmo -s -v
```

For a comprehensive test that mirrors the Continuous Integration (CI) environment across all supported Python
versions, use `tox`:
```bash
tox
```

**Note**: To use `tox` effectively, ensure you have all the necessary Python versions installed. If any
versions are missing, `tox` will provide relevant warnings.
