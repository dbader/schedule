Installation
============


Python version support
######################

We recommend using the latest version of Python.
Schedule is tested on Python 3.7, 3.8, 3.9, 3.10, 3.11 and 3.12

Want to use Schedule on earlier Python versions? See the History.


Dependencies
############

Schedule has 1 optional dependency:

Only when you use ``.at()`` with a timezone, you must have `pytz <https://pypi.org/project/pytz/>`_ installed.

Installation instructions
#########################

Problems? Check out :doc:`faq`.

PIP (preferred)
***************
The recommended way to install this package is to use pip.
Use the following command to install it:

.. code-block:: bash

    $ pip install schedule

Schedule is now installed.
Check out the :doc:`examples </examples>` or go to the :doc:`the documentation overview </index>`.


Using another package manager
*****************************
Schedule is available through some linux package managers.
These packages are not maintained by the maintainers of this project.
It cannot be guarantee that these packages are up-to-date (and will stay up-to-date) with the latest released version.
If you don't mind having an old version, you can use it.

Ubuntu
-------

**OUTDATED!** At the time of writing, the packages for 20.04LTS and below use version 0.3.2 (2015).

.. code-block:: bash

    $ apt-get install python3-schedule

See `package page <https://packages.ubuntu.com/search?keywords=python3-schedule>`__.

Debian
------

**OUTDATED!** At the time of writing, the packages for buster and below use version 0.3.2 (2015).

.. code-block:: bash

    $ apt-get install python3 schedule

See `package page <https://packages.debian.org/search?searchon=names&keywords=+python3-schedule>`__.

Arch
----

On the Arch Linux User repository (AUR) the package is available using the name `python-schedule`.
See the package page `here <https://aur.archlinux.org/packages/python-schedule/>`__.
For yay users, run:

.. code-block:: bash

    $ yay -S python-schedule

Conda (Anaconda)
----------------

Schedule is `published <https://anaconda.org/conda-forge/schedule>`__ in conda (the Anaconda package manager).

For installation instructions, visit `the conda-forge Schedule repo <https://github.com/conda-forge/schedule-feedstock#installing-schedule>`__.
The release of Schedule on conda is maintained by the `conda-forge project <https://conda-forge.org/>`__.

Install manually
**************************
If you don't have access to a package manager or need more control, you can manually copy the library into your project.
This is easy as the schedule library consists of a single sourcefile MIT licenced.
However, this method is highly discouraged as you won't receive automatic updates.

1. Go to the `Github repo <https://github.com/dbader/schedule>`_.
2. Open file `schedule/__init__.py` and copy the code.
3. In your project, create a packaged named `schedule` and paste the code in a file named `__init__.py`.
