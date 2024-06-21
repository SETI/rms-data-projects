#!/usr/bin/env python
##########################################################################################
"""sphinxify.py

From the command line:
    sphinxify.py path-to-python-file, ...

Each listed file will have its function docstrings converted to Google style. Each
original file will be saved with "-backup.py" appended to its name. File paths ending in
"-backup.py" will not be processed.

File and class docstrings are not modified.

Within the modified file, "xxx" identifies missing information that must be replaced.
"""
##########################################################################################

import os
import re
import sys

# Pattern to match a def or class plus a docstring, with five capture patterns
PATTERN = re.compile(r'(?s)(def +\w+ *\( *)'        # 1: "def", name, "("
                     r'([^)]*?)'                    # 2: everything inside parens
                     r'(\) *: *(?:|#[^\n]*)\n)'     # 3: "):", comment, newline
                     r'( *)'                        # 4: indent
                     r'(""")'                       # 5: '"""'
                     r'(.*?)'                       # 6: entire docstring
                     r'(""" *\n)')                  # 7: '"""', newline


def _format_arg(name, default, definition):
    """The formatted docstring, returned as a list of strings with proper relative
    indentation.
    """

    # Attempt to infer the type from the default, if any; otherwise, use "xxx"
    type_ = 'xxx'
    if default not in ('', 'None'):
        try:
            value = eval(default)
        except Exception:
            pass
        else:
            type_ = type(value).__name__

    # Begin the docstring
    optional = ', optional' if default else ''
    docstring = [f'    {name} ({type_}{optional}):']

    # If the definition fits on the first line, append it; otherwise, indent all text
    if len(definition) == 1 and len(definition[0]) <= 89 - len(docstring[0]):
        docstring[0] += ' ' + definition[0]
    else:
        docstring += ['        ' + line.strip() for line in definition]

    return docstring


def sphinxify(source, verbose=False, save=False):
    """Convert Python source code using Mark's style of function docstrings to Google
    style.

    File and class docstrings are not modified.

    Args:
        source (str):
            Either an extended string of Python source code or a path to a Python file;
            if the latter, the file is read and its content is used.
        verbose (bool, optional):
            True to print out the name of each function as it is identified in the source.
        save (bool, optional):
            True to save the source code under the original file path. If this option is
            used, the original file will be saved under the same path but ending in
            "-backup.py". This option is ignored if `source` contains source code rather
            than a file path.

    Return:
        str: The complete source code with docstrings converted to Google style.

    Raises:
        IOError: If the backup file already exists.
    """

    if source.endswith('.py'):
        filepath = source
        with open(filepath) as f:
            source = f.read()
    else:
        filepath = ''
        save = False

    if save:
        backup = filepath[:-3] + '-backup.py'
        if os.path.exists(backup):
            raise IOError('Backup file already exists')

    # Split entire text of file
    substrings = PATTERN.split(source)

    new_substrings = []
    for indx, substring in enumerate(substrings):
        mod8 = indx % 8
        if mod8 != 6:       # don't send args direct to the output file
            new_substrings.append(substring)

        if mod8 == 0:
            star_missing = False
            unknown_format = False
            unknown_names = []
            out_of_order = ''

        if mod8 == 1 and verbose:
            print(indx, substring)

        if mod8 == 2:
            star_missing = True
            args = substring.split(',')
            names = []
            defaults = {}
            for arg in args:
                name, _, default = arg.partition('=')
                name = name.strip()
                if name in ('self', 'cls'):
                    continue
                if name == '*':
                    star_missing = False
                    continue

                names.append(name)
                defaults[name] = default.strip()

            if len(names) < 4:
                star_missing = False

        if mod8 == 4:
            indent = substring
            continue

        if mod8 == 7:
            if star_missing:
                new_substrings.append('#xxx Insert "*"?\n')
            if unknown_format:
                new_substrings.append('#xxx Unknown docstring format\n')
            for name in unknown_names:
                new_substrings.append(f'#xxx Unknown arg name: {name}\n')
            if out_of_order:
                new_substrings.append(f'#xxx Arg defined out of order: {out_of_order}\n')

        # Everything has been handled except the docstring
        if mod8 != 6:
            continue

        # Locate the source code, which falls two substrings after this one
        code = substrings[indx+2]

        # Break the docstring into individual lines without indentation
        lines = substring.split('\n')
        if lines[0].strip() == '':
            lines = lines[1:]
        if lines[-1].strip() == '':
            lines = lines[:-1]

        k_args = -1
        k_returns = -1
        for k,line in enumerate(lines):
            line = line.rstrip()
            if line.startswith(indent):
                line = line[len(indent):]
            else:
                line = line.lstrip()

            if line in {'Input:', 'Inputs:', 'Args:'}:
                line = 'Args:'
                k_args = k

            if line in {'Return:', 'Returns:'}:     # either is OK
                k_returns = k

            lines[k] = line

        # Insert the docstring up to and including "Args:"
        kstop = k_args + 1 if k_args >= 0 else len(lines)
        docstring = lines[:kstop]

        # If there's an undefined input argument, "Args:" might be missing
        if k_args < 0 and names:
            if docstring[-1] != '':
                docstring.append('')
            docstring.append('Args:')

        # Format the args
        if k_args >= 0:
            k_stop = k_returns if k_returns > 0 else len(lines)
            name = ''
            definition = []
            for line in lines[k_args+1:k_stop]:
                if unknown_format:
                    break

                if not line:        # remove blank lines
                    continue

                if not line.startswith('    '):
                    unknown_format = True
                    continue

                new_name, _, extra = line[4:].partition(' ')
                if new_name:
                    if name:
                        docstring += _format_arg(name, defaults.get(name, ''), definition)

                    name = new_name
                    extra = extra.strip()
                    definition = [extra] if extra else []

                    if name not in names:
                        unknown_names.append(name)
                    else:
                        if name != names[0]:
                            out_of_order = name
                        names.remove(name)
                else:
                    definition.append(line.strip())

            if name:
                docstring += _format_arg(name,  defaults.get(name, ''), definition)

            if unknown_format:
                new_substrings.append(substring)
                continue

        # Handle any missing args
        if names:
            for name in names:
                docstring += _format_arg(name, defaults[name], ['xxx'])

        # Format the returns
        if k_returns >= 0:

            # Always a blank line before "Return:" or "Returns:"
            if docstring[-1] != '':
                docstring.append('')

            # Move anything after "Return:" to the next line
            return_, _, extra = line[k_returns].partition(':')
            docstring.append(return_ + ':')

            extra = extra.strip()
            if extra:
                docstring.append('    xxx: ' + extra)   # type is unknown

            for line in lines[k_returns+1:]:
                # If this is a named return value, insert a colon after the name
                name, blanks, extra = line.partition('  ')
                if blanks:
                    line = name + ': ' + extra.strip()

                docstring.append(line)

        # Handle a missing "Returns:" section
        elif k_returns < 0:
            # Check the source code to see if the function returns something
            has_returns = False
            parts = code.split(' return ')
            for part in parts[1:]:
                if part.lstrip(' ')[0] not in ('#', '\n'):
                    has_returns = True
                    break

            if has_returns:
                docstring += ['', 'Returns:', '    xxx: xxx']

        # Insert a "Raises:" section
        excepts = set()
        parts = code.split(' raise ')
        for part in parts[1:]:
            part = part.lstrip(' ')
            if part[0] not in ('#', '\n'):
                excepts.add(part.partition('(')[0])

        if excepts:
            docstring += ['', 'Raises:']
            excepts = list(excepts)
            excepts.sort()
            for except_ in excepts:
                docstring.append('    ' + except_ + ': xxx')

        # Add the indent but not for blank lines
        docstring = [(indent if line else '') + line for line in docstring]
        docstring[0] = docstring[0][len(indent):]           # no indent in first line
        docstring = '\n'.join(docstring) + '\n' + indent    # trailing indent before """
        new_substrings.append(docstring)

    new_source = ''.join(new_substrings)

    if save:
        os.rename(filepath, backup)
        with open(filepath, 'w') as f:
            f.write(new_source)

    return new_source

##########################################################################################

if __name__ == '__main__':

    for arg in sys.argv[1:]:

        if len(sys.argv) > 1:
            if arg.endswith('-backup.py'):
                print(arg, '**skipped**')
                continue
            print(arg)

        try:
            sphinxify(arg, verbose=False, save=True)
        except IOError as e:
            print(e)

##########################################################################################
