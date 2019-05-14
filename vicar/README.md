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

If you want to completely remove the environment, in `bash` run

```bash
cd vicar
./tear-down-environment
```

# Using the software

At this point, it consists of building blocks; wrapper functions are
yet to be written, but in the meantime you can easily write your own
wrapper using the information below.

# Migration entry points

The key function for migration is `migrate_vicar_file()` in
`Migration.py`.  It takes the original filepath (optional), a properly
formatted `DAT_TIM` string which will go into the migration task, and
a parsed VICAR file object.  It returns a VICAR file object with any
binary labels pushed into the tail of the file and a migration task in
the history labels with proper information to reconstruct the original
file.  This resulting object will be compliant with PDS4.

The `DAT_TIM` string is passed in so that when doing bulk migration,
all migrated files can be stamped with the same date-time, even if it
takes a while to parse the full archive.  To get a properly formatted
string in Python, this code snippet will work:

```python
import datetime
now = datetime.datetime.utcnow()
dat_tim_value = now.strftime('%a %b %d %H:%M:%S %Y')
```

The key function for back-migration is `back_migrate_vicar_file()` in
`BackMigration.py`.  It takes a parsed VICAR file object, and returns
a 2-tuple of the original filepath given (may be `None`) and a parsed
VICAR file object representing the original file, byte for byte.

# I/O

To read a VICAR file, read its bytes and then pass them to
`parse_vicar_file()` in `VicarFile.py`.  It will return a 2-tuple of
any unparsed bytes (should be empty), and a `VicarFile` object.
(Equivalently, running `parse_all(parse_vicar_file, input_bytes)` will
enforce all bytes were consumed and return only the `VicarFile`
object.)  Attempting to parse malformed files will raise an exception.

To write a VICAR file `vf`, call `vf.to_byte_string()` then write the
bytes to a file.


# Example usage

See the bottom of `Migration.py` for example usage of the software.

We read in a VICAR file, parse it into a `VicarFile` object.  We
migrate it and write the PDS4 version out to an output file.  We then
back-migrate and verify that the results are byte-for-byte equivalent
to the original file.