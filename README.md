explaining the use, installation, and purpose of your proposed software.
file should be well-written,

# What is `pymcma`?
PyMCMA is a Python package for generation of uniformly distributed
Pareto-efficient representation for the provided core-mode.

You can read more about the project in the
[online documentation](https://pymcma.readthedocs.io/).

# Installation

Below you can find a short description of how to install `pymcma` software.
For extended information see the documentation available under the [link](https://pymcma.readthedocs.io/).

1. Creating and/or activating the Conda environment

    In order to avoid possible conflicts with already installed packages,
    we recommend to install and use the pyMCMA within a dedicated and regularly updated
    conda environment created for Python version 3.11.

    To be sure that everything will work as intended we highly recommend to use
    the following `.condarc` configuration file:

    ```yaml
        ssl_verify: true
        channels:
          - conda-forge
          - defauklts
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

3. Creation of the workspace
    The workspace for initial analysis can be created by running:

    ```bash
        $ pymcma --install
    ```

    This command creates in the current directory the initial workspace
    and run analysis on the example model shipped with the software.
    You can find more detail about working directory in the
    [documentation](https://pymcma.readthedocs.io/).

# Basic usage

To make your own analysis with the our example model you need to change the
configuration in the `anaTst/cfg.yml` in your work directory. Then, you need to
run the following command to start analysis:

```bash
    $ pymcma --anaDir anaTst
```

To make analysis for your own model you need to create you own core model in
Pyomo and export it in `dill` format and adapt the configuration file for
this model.
Please refer to the [User Guide](https://pymcma.readthedocs.io/user_guide.html)
section in the documentation to comprehensive instruction about how to do it.
