# VICAR migration tools

This software uses the
[Conda](https://docs.conda.io/en/latest/index.html) system to manage
packages, dependencies, and environments.

Miniconda is sufficient if you don't want to use the full Anaconda
system.  Installers may be downloaded from
[here](https://docs.conda.io/en/latest/miniconda.html).

This software was developed on Mac OS.  While Python and Miniconda are
platform-independent, the software has not (yet) been tested on other
platforms.

# Installing the proper environment

Once Miniconda (or full Anaconda) is installed, run

```bash
cd vicar
./set-up-environment
```

This will download the necessary packages and install them into a
Conda environment called `pds-migration-vicar`.  To use that
environment, in `bash`, type `source activate pds-migration-vicar` and
that environment will be active until you deactivate it.

# Removing the environment

If you want to remove the environment, in bash run

```bash
cd vicar
./tear-down-environment
```

