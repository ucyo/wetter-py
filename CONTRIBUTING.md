# Contributing to `wetter`

Welcome! And thank you for planning on contributing to `wetter` :wave:

## Development Environment

It is highly recommended to use the provided [Makefile](./Makefile) and
with that the provided [Dockerfile](./Dockerfile) environment for
interactive development. The Dockerfile is set up in such a way that
your currently edited folder is mounted into the container and started
in the [wetter](./wetter/) folder. That way any change in the codebase
is automatically reflected in the container. You can start the development
environment with the following command.

```bash
make bash
```

## Static Analysis and Testing during development

The Makefile also includes an environment for automatically checking for code
styling. It uses [`black`](https://black.readthedocs.io/en/stable/),
[`flake8`](https://flake8.pycqa.org/en/latest/) and
[`test`](https://docs.pytest.org/en/7.1.x/contents.html) in the background.
Simply start a new terminal window and execute the following command

```bash
make watch
```

## Packaging

You can create an installable Python wheel at any time.
This can be done using the [`poetry`](https://python-poetry.org/) package.
But don't worry if you don't have `poetry` installed on your system.
It is packaged in the Dockerfile.
Additionally, the Makefile provides a handy shortcut for building the command.

```bash
make package  # make wheel
```
