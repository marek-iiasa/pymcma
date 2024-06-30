# What is `pymcma`?
PyMCMA is a Python package for generation of uniformly distributed
Pareto-efficient representation for the provided core-model.

You can read more about the project in the
[online documentation](https://pymcma.readthedocs.io/).

# Installation

Below you can find a short description of how to install `pymcma` software.
For extended information see the documentation available under
the [link](https://pymcma.readthedocs.io/).

1. Creating and/or activating the Conda environment

    In order to avoid possible conflicts with already installed packages,
    we recommend to install and use the pyMCMA within a dedicated and regularly
    updated conda environment created for Python version 3.11.

    To be sure that everything will work as intended we highly recommend to use
    the following `.condarc` configuration file:

    ```yaml
        ssl_verify: true
        channels:
          - conda-forge
          - defaults
        channel_priority: flexible
        auto_activate_base: false
    ```

    1. Update of the conda version.
    ```bash
        $ conda update -n base -c conda-forge conda
    ```
    2. Create a dedicated conda environment for pyMCMA.
    ```bash
        $ conda create --name pymcma -c conda-forge python=3.11
    ```
    The dedicated conda environment should be activated whenever the
    ``pymcma`` is executed by the command-line.

2. Installation of the `pymcma`

    The installation shall be done by executing at the terminal prompt the following
    two commands (the first one should be skipped, if the conda pymcma environment
    is active in the currently used terminal window):

    ```bash
        $ conda activate pymcma
        $ conda install pymcma
    ```
	 Installation shall be tested by running:
    ```bash
        $ pymcma -h
    ```
	 which displays the command-line options.

3. Copying the examples and templates

    The following command copies to the current directory the files organized
	 into three directories:

    ```bash
        $ pymcma --install
    ```

    The copied files are needed for running the example analysis on the model
	 shipped with the package using; this can be done by the following command:

    ```bash
        $ pymcma --anaDir anaTst
    ```

    More details about the ``pymcma`` installation and testing is available
    [documentation](https://pymcma.readthedocs.io/).

# Basic usage

To make your own analysis with the our example model you need to change the
configuration in the `anaTst/cfg.yml` in your work directory. Then, you need to
run the following command to start analysis:

```bash
    $ pymcma --anaDir anaTst
```

To make analysis for your own model you need to create a core model in
Pyomo and export it in the `dill` format, as well as adapt the ``pymcma`` configuration file for
your desired analysis.
Please refer to the [User Guide](https://pymcma.readthedocs.io/user_guide.html)
section in the documentation for comprehensive guidelines.
