##########################################################################################
# fancyindex.py
##########################################################################################
"""Class FancyIndex for online file retrieval via URL from fancy indices."""

import datetime
import os
import pathlib
import re
import requests
import warnings


################################################################################
# From Mark:
# Take a look. Basically, create a FancyIndex object for a URL with 
# recursive=True, and then
# 
#     walk(pattern=r'.*\.lbl', dest=destination_dir)
#
# will copy all the label files into your local destination directory with the 
# same tree structure. We can discuss with Rob next week about where it 
# belongs on GitHub.
#
# FYI I just updated fancyindex.py on Dropbox. One notable change is that I 
# decided walk() should default to Unix-style patterns instead of regular 
# expressions, so now you need either
#
#     walk(pattern=r'.*\.lbl', regex=True, dest=destination_dir)
# or
#
#     walk(pattern='*.lbl', dest=destination_dir)
################################################################################



class FancyIndex:
    """Class representing the content of an online directory or directory tree."""

    _TABLE_CACHE = {}
    _DICT_CACHE = {}

    def __init__(self, url, recursive=False, *, local_dir=None):
        """Constructor for a fancy index.

        If the URL does not point to an online fancy index, this returns an object with
        attribute is_fancy = False and with no internal files.

        Args:
            url:        The URL of an online fancy index.
            recursive:  True to read the entire tree recursively; False for this directory
                        only.
            local_dir:  Optional local directory for any retrieved files as a string or
                        pathlib.Path object. This can also be specified after defining the
                        object using the local_dir setter.
        """

        self.url = url.rstrip('/') + '/'
        self.local_dir = local_dir
        self.recursive = recursive

        if (self.url, recursive) in FancyIndex._DICT_CACHE:
            self.info = FancyIndex._DICT_CACHE[self.url, recursive]
            self.is_fancy = bool(FancyIndex._TABLE_CACHE[self.url, recursive])
        else:
            table = FancyIndex._read(self.url, recursive=recursive)
            self.info = {name: (date, size, FancyIndex._int_size(size))
                         for (name, date, size) in table}
            self.is_fancy = bool(table)
            FancyIndex._DICT_CACHE[self.url, recursive] = self.info

        self.by_basename = {}
        for subpath in self.info.keys():
            basename = subpath.rpartition('/')[-1]
            if basename in self.info:
                self.by_basename[basename] = basename   # root-level files always dominate
            elif basename not in self.by_basename:
                self.by_basename[basename] = subpath

    def __contains__(self, subpath):
        return subpath in self.info

    def __str__(self):
        return f'FancyIndex("{self.url}", recursive={self.recursive})'

    def __repr__(self):
        return str(self)

    @property
    def local_dir(self):
        """The local directory associated with this FancyIndex as a pathlib.Path object.

        None if the local directory is undefined.
        """

        return self._local_dir

    @local_dir.setter
    def local_dir(self, path):
        """Set the local directory associated with this FancyIndex."""

        if isinstance(path, pathlib.Path):
            self._local_dir = path
        elif isinstance(path, str):
            self._local_dir = pathlib.Path(path)
        else:
            self._local_dir = None

    def date(self, subpath):
        """The date associated with the given subpath within this FancyIndex.

        Args:
            subpath:    The subpath or basename within this directory tree.

        Returns:
            date:       The date in "YYYY-MM-DD HH:MM" format.
        """

        if subpath not in self.info:
            subpath = self.by_basename[subpath]

        return self.info[subpath][0]

    def size_str(self, subpath):
        """The size string associated with the given subpath within this FancyIndex.

        Args:
            subpath:    The subpath or basename within this directory tree.

        Returns:
            size_str:   The size string, generally 2-3 digits followed by "K", "M", "G",
                        or "T".
        """

        if subpath not in self.info:
            subpath = self.by_basename[subpath]

        return self.info[subpath][1]

    def size(self, subpath):
        """The approximate size in bytes of the file at the given subpath within this
        FancyIndex.

        Args:
            subpath:    The subpath or basename within this directory tree.

        Returns:
            size:       Approximate size of the file in bytes, generally accurate to 2-3
                        significant digits.
        """

        if subpath not in self.info:
            subpath = self.by_basename[subpath]

        return self.info[subpath][2]

    def subpath(self, basename):
        """The subpath within the directory tree associated with this basename.

        Args:
            basename:   The basename (or full subpath) within this directory tree.

        Returns:
            subpath:    The full directory subpath within this directory tree.
        """

        if subpath in self.info:
            return subpath

        return self.by_basename[subpath]

    def file_url(self, subpath):
        """The full URL associated with the given subpath within this FancyIndex.

        Args:
            subpath:    The subpath or basename within this directory tree.

        Returns:
            url:        The full URL to the specified file.
        """

        if subpath in self.info:
            return self.url + subpath

        return self.url + self.by_basename[subpath]

    def search(self, pattern, fnmatch=False, flags=re.IGNORECASE):
        """The set of file subpaths matching a match pattern within a fancy index.

        Args:
            pattern:    The match pattern for file basenames.
            fnmatch:    True for Unix-style match patterns; False for regular expressions.
            flags:      Compile flags for the regular expression pattern.

        Returns:
            matches:    The set of file subpaths within the given URL with basenames that
                        match the specified regular expression.
        """

        if fnmatch:
            pattern = fnmatch.translate(pattern)

        if isinstance(pattern, str):
            pattern = re.compile(pattern, flags=flags)

        return {subpath for subpath in self.info
                if pattern.fullmatch(subpath.rpartition('/')[-1])}

    def retrieve(url, subpath, dest=None, *, labels=False, comments=False, dates=True,
                      subdirs=True):
        """Retrieve a file from a remote directory tree.

        The source can be specified using a FancyIndex object or URL string. You can use
        the latter option to retrieve a remote file that is not found inside a fancy
        index.

        Example using a FancyIndex:
            fancy_index = FancyIndex('https://domain.name/url', local_dir='images/')
            fancy_index.retrieve('path/to/filename.img')

        Example using a URL:
            FancyIndex.retrieve('https://domain.name/url', 'path/to/filename.img',
                                dest='images/')

        Args:
            url:        FancyIndex object or URL string.
            subpath:    The subpath or basename within this directory tree.
            dest:       The subdirectory where the file is to be saved, as a string or
                        pathlib.Path object. If not specified, the FancyIndex's local_dir
                        property is used.
            labels:     True to download any ".lbl" or ".xml" files as well.
            comments:   True to download any ".cmt" files as well.
            dates:      True to apply the remote dates to the downloaded file(s).
            subdirs:    If True, the saved file will retain the full directory subpath;
                        Otherwise, it will be saved into the destination directory using
                        only its basename.

        Returns:
            file_path:  The local path to the retrieved file as a pathlib.Path object.

        Exceptions:
            ConnectionError:    If the specified file could not be retrieved.

        """

        # Validate inputs
        if subpath.endswith('/'):
            raise ValueError('directory downloads are not supported')

        if isinstance(url, FancyIndex):
            file_url = url.file_url(subpath)
        else:
            file_url = url.rstrip('/') + '/' + subpath

        # Request the file
        request = requests.get(file_url, allow_redirects=True)
        if request.status_code != 200:
            from IPython import embed; print('+++++++++++++'); embed()
            raise ConnectionError(f'response {request.status_code} received from '
                                  f'{file_url}')

        # Save it to the destination
        local_dir = url.local_dir if dest is None else pathlib.Path(dest)
        (parent, _, basename) = subpath.rpartition('/')
        if subdirs:
            parent_path = local_dir / parent
        else:
            parent_path = local_dir

        parent_path.mkdir(parents=True, exist_ok=True)

        file_path = parent_path / basename
        with file_path.open('wb') as f:
            f.write(request.content)

        # Maybe we're done
        if not (labels or comments or dates):
            return file_path

        # Get the parent's FancyIndex if possible
        (parent_url, _, basename) = file_url.rpartition('/')
        parent_index = FancyIndex(parent_url, recursive=False)

        # Fix the file date if requested; note it's only good to the minute
        if dates and parent_index.is_fancy:
            date = parent_index.date(basename)
            timestamp = datetime.datetime.fromisoformat(date).timestamp()
            os.utime(file_path.resolve(), (timestamp, timestamp))

        # Download labels and comments if necessary
        stem = basename.partition('.')[0]
        options = []
        if labels:
            options += [stem + ext for ext in ('.lbl', '.LBL', '.xml', '.xlbl')]
            options += [basename + ext for ext in ('.lbl', '.LBL')]
        if comments:
            options += [stem + ext for ext in ('.cmt', '.CMT')]
            options += [basename + ext for ext in ('.cmt', '.CMT')]

        for name in options:
            if name == basename:
                continue

            if parent_index.is_fancy:
                if name in parent_index:
                    parent_index._retrieve(name, dest=parent_path, labels=False,
                                           comments=False, dates=dates, subdirs=False)
            else:   # without an index, try requests directly; ignore failure
                try:
                    FancyIndex._retrieve(parent_url, name, dest=parent_path, labels=False,
                                         comments=False, dates=dates, subdirs=False)
                except ConnectionError:
                    pass

        return file_path

    def walk(self, pattern, dest=None, *, labels=False, comments=False, dates=True,
                            fnmatch=False, flags=re.IGNORECASE, resume=False, warn=False):
        """Retrieve all of the files from a remote fancy index tree that match a given
        regular expression.

        Args:
            pattern:    The subpath within this directory tree.
            dest:       The subdirectory where the file is to be saved, as a string or
                        pathlib.Path object. If not specified, the FancyIndex's local_dir
                        property is used.
            labels:     True to download any ".lbl" or ".xml" files as well.
            comments:   True to download any ".cmt" files as well.
            dates:      True to apply the remote dates to the downloaded file(s).
            fnmatch:    True for Unix-style match patterns; False for regular expressions.
            flags:      Compile flags for the regular expression pattern.
            resume:     True to resume a walk task that did not complete. It will skip
                        over the files that already exist locally.
            warn:       True to warn about ConnectionErrors rather than stopping.

        Returns:
            subpaths:   The complete set of matching subpaths.

        Exceptions:
            ConnectionError: If the task did not complete.
        """

        subpaths = self.search(pattern, flags=flags)

        dest = self.local_dir if dest is None else pathlib.Path(dest)
        failures = set()
        for subpath in subpaths:
            if resume and (dest / subpath).exists():
                continue

            try:
                self.retrieve(subpath, dest=dest, labels=labels, comments=comments,
                              dates=dates, subdirs=True)
            except ConnectionError:
                if warn:
                    failures.add(subpath)
                    subpaths.remove(subpath)
                else:
                    raise

        if failures:
            if len(failures) == 1:
                warnings.warn('Failed to retrieve 1 file: ' + failures[0])
            else:
                failures = list(failures)
                failures.sort()
                warnings.warn(f'Failed to retrieve {len(failures)} files: '
                              + ', '.join(failures))

        return subpaths

    ######################################################################################
    # Utilities
    ######################################################################################

    _SIZE_FACTORS = {'K': 1024, 'M': 1024**2, 'G': 1024**3, 'T': 1024**4}

    @staticmethod
    def _int_size(size):
        """Internal method to convert a size string to a size in bytes."""

        if size == '-':
            return 0

        if size[-1] in FancyIndex._SIZE_FACTORS:
            return int(float(size[:-1]) * FancyIndex._SIZE_FACTORS[size[-1]] + 0.5)

        return int(size)

    _HTML_TAG = re.compile(r'<.*?>')
    _FIELDS = re.compile(r' *([^ ]+) +(\d{4}-\d\d-\d\d \d\d:\d\d(?:|:\d\d)) +([^ ]+) *')
    _END_OF_TABLE = re.compile('.*(</pre>|<hr>).*')

    @staticmethod
    def _read(url, recursive=False):
        """The content of a fancy index page as a list of tuples (subpath, date_string,
        size_string).

        If the URL does not point to a fancy index, this function returns an empty list.

        Args:
            url:        The URL of an online fancy index.
            recursive:  True to read the entire tree recursively; False for this directory
                        only.

        Returns:
            table:      A list of tuples (subpath, date_string, size_string).
        """

        # If we have already read this fancy index, return it
        url = url.rstrip('/') + '/'
        if (url, recursive) in FancyIndex._TABLE_CACHE:
            return FancyIndex._TABLE_CACHE[url, recursive]

        # If we have read this index but not recursively, start with what we've got
        if (url, False) in FancyIndex._TABLE_CACHE:
            row_tuples = list(FancyIndex._TABLE_CACHE[url, False])

        # Otherwise, retrieve and parse this fancy index
        else:
            request = requests.get(url, allow_redirects=True)
            if request.status_code != 200:
                raise ConnectionError(f'response {request.status_code} received from '
                                      f'{url}')

            text = request.content.decode('latin8')

            # The first line of the fancy index always contains "Parent Directory".
            parts = text.partition('Parent Directory')
            if not parts[-1]:
                FancyIndex._TABLE_CACHE[url, False] = []
                return []           # not a fancy index!

            # Rows are always split by "\n".
            recs = parts[-1].split('\n')

            # The record after the last table row always contains "</pre>" or "<hr>"
            last = [k for k, rec in enumerate(recs)
                    if FancyIndex._END_OF_TABLE.fullmatch(rec)]

            # Select the table rows
            recs = recs[1:last[0]]

            # Interpret each row
            row_tuples = []
            for rec in recs:

                # Remove anything inside quotes
                parts = rec.split('"')
                rec = ''.join(parts[::2])

                # Insert a space before "<td"
                rec = rec.replace('<td', ' <td')

                # Remove anything inside HTML tags
                parts = rec.split('<')
                parts = FancyIndex._HTML_TAG.split(rec)
                rec = ''.join(parts)

                # Interpret the fields
                row_tuples.append(FancyIndex._FIELDS.match(rec).groups())

            # Save the non-recursive result
            FancyIndex._TABLE_CACHE[url, False] = row_tuples
            row_tuples = list(row_tuples)   # don't append to the non-recursive list

        # Proceed recursively if necessary
        if recursive:
            new_row_tuples = []
            for (name, date, size) in row_tuples:
                if name.endswith('/') or size == '-':
                    name = name.rstrip('/') + '/'   # make sure name ends in a slash
                    new_tuples = FancyIndex._read(url + name, recursive=True)
                        # This call saves each subdirectory of the URL into the cache.
                        # This means that any future call referencing a URL's subdirectory
                        # will not trigger a new remote request.
                    new_tuples = [(name + n, d, s) for (n,d,s) in new_tuples]
                    new_row_tuples += new_tuples

            row_tuples += new_row_tuples
            FancyIndex._TABLE_CACHE[url, True] = row_tuples

        return row_tuples

##########################################################################################
