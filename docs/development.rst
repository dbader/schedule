Development
===========

These instructions are geared towards people who want to help develop this library.

Preparing for development
-------------------------
All required tooling and libraries can be installed using the ``requirements-dev.txt`` file:

.. code-block:: bash

    pip install -r requirements-dev.txt


Running tests
-------------

``pytest`` is used to run tests. Run all tests with coverage and formatting checks:

.. code-block:: bash

    py.test test_schedule.py --flake8 schedule -v --cov schedule --cov-report term-missing

Platform requirements for timezone tests
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Tests involving timezone manipulation rely on ``time.tzset()``, which is only available on Unix-like systems.
On Windows, ``time.tzset()`` is not implemented, and some timezone-related tests may fail or be skipped.

If you are developing on Windows, consider the following alternatives:

- **WSL (Windows Subsystem for Linux)**: Run the test suite inside a WSL distribution.
- **Docker**: Use a Linux-based container to execute the tests.
- **CI with Linux runners**: Rely on continuous integration pipelines configured with Linux environments.

Formatting the code
-------------------
This project uses `black formatter <https://black.readthedocs.io/en/stable/>`_.
To format the code, run:

.. code-block:: bash

    black .

Make sure you use version 20.8b1 of black.

Compiling documentation
-----------------------

The documentation is written in `reStructuredText <https://docutils.sourceforge.io/rst.html>`_.
It is processed using `Sphinx <http://www.sphinx-doc.org/en/1.4.8/tutorial.html>`_ using the `alabaster <https://alabaster.readthedocs.io/en/latest/>`_ theme.
After installing the development requirements it is just a matter of running:

.. code-block:: bash

    cd docs
    make html

The resulting html can be found in ``docs/_build/html``

Publish a new version
---------------------

Update the ``HISTORY.rst`` and ``AUTHORS.rst`` files.
Bump the version in ``setup.py`` and ``docs/conf.py``.
Merge these changes into master. Finally:

.. code-block:: bash

    git tag X.Y.Z -m "Release X.Y.Z"
    git push --tags

    pip install --upgrade setuptools twine wheel
    python3 -m build --wheel
    # For https://test.pypi.org/project/schedule/
    twine upload --repository schedule-test dist/*
    # For https://pypi.org/project/schedule/
    twine upload --repository schedule dist/*

This project follows `semantic versioning <https://semver.org/>`_.`
