lammps-executor
=======

package to automate lammps  calculation using  using aiida

This package rely on  https://github.com/aiidateam/aiida-core and  https://github.com/aiidaplugins/aiida-lammps


Support and Documentation
-------------------------
see docs for documentation, reporting bugs, and getting support.



Installation
-------------------------

- Install poetry (https://github.com/python-poetry/poetry)

    + osx / linux / bashonwindows install instructions
        .. sourcecode:: bash

            recommended
            $ curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/install-poetry.py | python -

            other possibility
            $ pip install poetry

    + windows powershell install instructions
        .. sourcecode:: bash

            recommended
            $ (Invoke-WebRequest -Uri https://raw.githubusercontent.com/python-poetry/poetry/master/install-poetry.py -UseBasicParsing).Content | python -

other possibility
            $ pip install poetry

- Once Poetry is installed you can execute the following:

.. sourcecode:: bash

    $ poetry --version

    $ poetry self update

- Clone the repo

.. sourcecode:: bash

    $ git clone
    $ cd lammps-executor

- Create a Virtual Environment

    By default, Poetry create virtual environment in $HOME/.poetry/env or  $HOME/.cache/pypoetry/virtualenvs for cahcing/sharing purpose
        - to install install dependencies to current python interpreter/virtualenv
        .. sourcecode:: bash

            $poetry config virtualenvs.create false --local

        - create virtual environment in default location
        .. sourcecode:: bash

            $poetry config virtualenvs.create

        -   create virtual environment in th root directory of a Python project
        .. sourcecode:: bash

            $poetry config virtualenvs.in-project true



        -   To change or otherwise add a new configuration setting,
        .. sourcecode:: bash

            $poetry config virtualenvs.path /path/to/cache/directory/virtualenvs


- install the packages
.. sourcecode:: bash

    $poetry install
    $poetry check
    $pre-commit install
    $poetry run pytest
    $poetry build


+ Listing the current configuration

    .. sourcecode:: bash

        $poetry config --list


    which will give you something similar to this

    .. sourcecode:: bash

        cache-dir = "/path/to/cache/directory"
        virtualenvs.create = true
        virtualenvs.in-project = null
        virtualenvs.path = "{cache-dir}/virtualenvs"  # /path/to/cache/directory/virtualenvs

+ Show Information of the Vitual Environment

    .. sourcecode:: bash

        poetry env info


+ Activate Virtual Environment

.. sourcecode:: bash

    $poetry shell

Usage
-------------------------



Developing and Contributing
---------------------------
See contributing.md
for guidelines on running tests, adding features, coding style, and updating
documentation when developing in or contributing to lammps-executor

+ Install pre-commit

.. sourcecode:: bash

    $

+ Add a pre-commit configuration

.. sourcecode:: bash

    $

+ Install the git hook scripts

.. sourcecode:: bash

    $pre-commit install






Authors
-------

Conrard Tetsassi
