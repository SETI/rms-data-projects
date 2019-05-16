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

## Migration: PDS3 to PDS4

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

A VICAR file that does not have binary labels is already
PDS4-compliant.  Migrating such a file will add a harmless migration
task but otherwise not affect the file.  Depending on her needs, a
user might want to:

1. Do this harmless migration, or
1. Just copy the original file, or
1. Do nothing.

This software doesn't have an opinion on what to do and leaves it to
you.  To check whether a VICAR file has binary labels, call
`vf.has_binary_labels()` on the parsed `VicarFile` object.

Note that migration optionally stores the original filepath.  If this
is important for your back-migration needs, then you will want to
migrate, not copy, even if the VICAR file has no binary labels.

## Back-migration: PDS4 back to original

The key function for back-migration is `back_migrate_vicar_file()` in
`BackMigration.py`.  It takes a parsed VICAR file object, and returns
a 2-tuple of the original filepath given (may be `None`) and a parsed
VICAR file object representing the original file, byte for byte.

If the original file had no binary labels and was just copied instead
of migrated, you can't back-migrate it.  Any file that has been
migrated will have a migration task in its history labels.  You can
check whether it has a migration task by calling
`vf.has_migration_task()` on the parsed `VicarFile` object.

# I/O

To read a VICAR file, read its bytes and then pass them to
`parse_all(parse_vicar_file, input_bytes)` in `VicarFile.py`.  It will
return a `VicarFile` object.  Attempting to parse malformed files will
raise an exception.

To write a VICAR file `vf`, call `vf.to_byte_string()` then write the
bytes to a file.

# Example usage

See the bottom of `Migration.py` for example usage of the software,
using all of the functionality.

We read in a VICAR file, parse it into a `VicarFile` object.  We
migrate it and write the PDS4 version out to an output file.  We then
back-migrate and verify that the results are byte-for-byte equivalent
to the original file.

A limited but more realistic example is in `Migrate.py`, a script to
migrate a single VICAR file, taking its name from the command line,
then writing the migrated file into the same directory but with a
different name.

# Bugs and issues

 * This software uses [ply](https://www.dabeaz.com/ply/) to generate
parsers for the VICAR labels.  It may spew a lot of WARNING messages;
they are harmless and may be ignored.  Nevertheless, this should be
addressed in the future.