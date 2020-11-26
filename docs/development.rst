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


Compiling documentation
-----------------------

The documentation is written in `reStructuredText <https://docutils.sourceforge.io/rst.html>`_.
It is processed using `Sphinx <http://www.sphinx-doc.org/en/1.4.8/tutorial.html>`_ using the `alabaster <https://alabaster.readthedocs.io/en/latest/>`_ theme.
After installing the development requirements it is just a matter of running:

.. code-block:: bash

    cd docs
    make html

The resulting html can be found in ``docs/_build/html``
