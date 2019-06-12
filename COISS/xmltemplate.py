################################################################################
# Class XmlTemplate
################################################################################

import os
import time, datetime, pytz
import hashlib
from xml.sax.saxutils import escape

class XmlTemplate(object):
    """Class to generate PDS4 labels based on XML templates.

    Inside the template file, everything in between "$" is interpreted as an
    expression to be evaluated in Python that will replace this value. For
    example, if INSTRUMENT_ID = 'ISSWA', then
        description>$INSTRUMENT_ID$</description>
    in the template will become
        description>ISSNA</description>
    in the label. The expression between "$" can include indexes, function
    calls, or anything else that is defined inside the Python program that
    imports this module.

    The expression can also be of the form "name=expression", where the name is
    a valid Python variable name. In this case, the variable becomes defined,
    and it can be subsequently re-used further down in the template. For
    example, if this appears as an expression,
        $cruise_or_saturn=('cruise' if START_TIME < 2004 else 'saturn')$
    then later in the template, one can write:
        <lid_reference>
        urn:nasa:pds:cassini_iss_$cruise_or_saturn$:data_raw:cum-index
        </lid_reference>

    The template may also contain any number of "Section" headers. These
    begin with "$" in the first character, and they apply to the section of
    the file starting immediately below and continuing to the next section
    header or the end of the file. For example, this is a one-line section of
    the template, with a "$FOR_EACH" header:

    $FOR_EACH(target_alt)
            <alternate_designation>$VALUE$</alternate_designation>
    $ONCE
            ...

    These types of section headers are supported:
    $ONCE:          every line of XML in this section is used exactly once.
    $IF(e):         this section is included only if the expression e is nonzero
                    when evaluated within the scope of the Python program.
    $FOR_EACH(e):   this section is repeated zero or more times, once for each
                    value of the Python expression e. Within each iteration of
                    this section,
                        VALUE  is replaced by each value in the list;
                        INDEX  is replaced by each list index (0-based);
                        LENGTH is replaced by the number of values.

    It is not necessary to start the template file with a header; "$ONCE" is
    implied.

    The following pre-defined functions can be used anywhere in a template:

        REPLACE_NA(value, if_na):
            return the second argument if the value is a string "N/A";
            otherwise, return the value.

        CURRENT_ZULU():
            return the current time UTC as a string "yyyy-mm-ddThh:mm:ssZ".

        DATETIME(string):
            convert the given date/time string to a year-month-day format with a
            trailing "Z"

        BASENAME(filename):
            return the basename of a file, with leading directory paths removed.

        FILE_ZULU(filename):
            return the modification time of a file as a UTC string
            "yyyy-mm-ddThh:mm:ss.sssZ".

        FILE_BYTES(filename):
            return the size of a file in bytes.

        FILE_MD5(filepath):
            return the MD5 checksum of the file at the specified filepath.

    Note that these functions can be called from the user's Python program by
    importing them from XmlTemplate.
    """

    TIMEZONE = 'America/Los_Angeles'    # convert to the name of the local
                                        # timezone as recognized by pytz. Needed
                                        # by FILE_ZULU().

    def __init__(self, filename):
        """Construct a PDS4 template object from the contents of a file."""

        # Read the template
        with open(filename) as f:
            recs = f.readlines()

        # Remove Mitch's comments; strip trailing whitespace
        for k,rec in enumerate(recs):
            parts = rec.split('<!-- [mkg]')
            assert len(parts) <= 2
            recs[k] = parts[0].rstrip() + '\r\n'

        # Break up into sections, header_types, header_expressions
        sections = [[]]
        header_types = ['$ONCE']
        header_expressions = ['']
        for rec in recs:

            # Handle headers
            if rec.startswith('$'):
                sections.append([])     # start a new section

                header = rec.rstrip()
                parts = header.partition('(')
                assert parts[0] in ('$ONCE', '$IF', '$FOR_EACH')
                header_types.append(parts[0])

                if parts[0] == '$ONCE':
                    assert parts[1:] == ('','')
                    header_expressions.append(None)
                else:
                    assert parts[2].endswith(')')
                    header_expressions.append(parts[2][:-1])

            # Otherwise it's the next line of this section
            else:
                sections[-1].append(rec)

        # Within each section, identify expressions to be evaluated
        expressions = []
        for k,section in enumerate(sections):
            expressions.append([])
            new_recs = []
            for rec in section:
                parts = rec.split('$')
                assert len(parts) % 2 == 1

                # List the index of every part that needs to be evaluated
                for j in range(1,len(parts),2):
                    expressions[-1].append(len(new_recs) + j)

                new_recs += parts
            sections[k] = new_recs

        # Identify assignments among the expressions
        assignments = []
        for k,section in enumerate(sections):
            assignments.append(len(expressions[k]) * [None])
            for jndex,j in enumerate(expressions[k]):
                expr = section[j].strip()
                while expr.startswith('(') and expr.endswith(')'):
                    expr = expr[1:-1]

                (varname, equals, right) = expr.partition('=')
                if equals != '=':         continue      # no equal sign
                if right.startswith('='): continue      # "==" is not assignment

                varname = varname.strip()
                right = right.strip()

                wo_underscores = varname.replace('_','')
                if len(wo_underscores) == 0:     continue   # no varname
                if not wo_underscores.isalnum(): continue   # invalid varname
                if not varname[0].isalpha():     continue   # invalid varname

                # It's an assignment!
                assignments[-1][jndex] = varname
                section[j] = right

        self.sections = sections
        self.expressions = expressions
        self.assignments = assignments

        self.header_types = header_types
        self.header_expressions = header_expressions

    ############################################################################

    def stringlist(self, lookup):
        """Return a list of strings such that ''.join(stringlist) is the
        filled-out template.

        Input:
            lookup      a dictionary containing all the variable names and
                        values that will be needed to fill in the template.
        """

        # Function to fill out one section of the template.
        def fill_out_one_section(section, expressions, assignments,
                                 lookup, **more):
            """Fill out one section of the template and return a list of
            strings.

            Inputs:
                section         one section of the XML label as a list of
                                strings.
                expressions     a list of indices identifying the expressions to
                                be evaluated in this section.
                assignments     a list of variable names to assign to the value
                                of associated expressions.
                lookup          a dictionary of variable names and their values.
                more            a "local" dictionary of overrides.
            """

            recs = list(section)    # Copy the section so we can update in-place
            for jndex,j in enumerate(expressions):
                rec = recs[j]

                # Evaluate within the namespaces
                result = eval(rec, lookup, more)

                # Apply assignment if necessary
                varname = assignments[jndex]
                if varname:
                    lookup[varname] = result

                # Format a float without unnecessary trailing zeros
                if isinstance(result, float):
                    result = str(result)
                    if result.endswith('.0'):
                        result = result[:-1]

                # Otherwise, convert to string and escape
                result = escape(str(result))

                recs[j] = result

            return recs

        ### Begin active code

        # Add the predefined functions to the lookup unless they were overridden
        # or are there already
        for key in PREDEFINED_FUNCTIONS:
            if key not in lookup:
                lookup[key] = PREDEFINED_FUNCTIONS[key]

        # Fill out the template
        filled_out = []
        for k in range(len(self.sections)):
            header_type = self.header_types[k]
            header_expr = self.header_expressions[k]

            # For a $ONCE section, just perform evaluations
            if header_type == '$ONCE':
                filled_out += fill_out_one_section(self.sections[k],
                                                   self.expressions[k],
                                                   self.assignments[k],
                                                   lookup)

            # For an $IF section, first decide whether to include it
            elif header_type == '$IF':
                result = eval(header_expr, lookup)
                if results:
                    filled_out += fill_out_one_section(self.sections[k],
                                                       self.expressions[k],
                                                       self.assignments[k],
                                                       lookup)

            # For a $FOR_EACH, make a list of the values that will be inserted
            # and repeat for each one.
            else:
                results = list(eval(header_expr, lookup))

                # Repeat for each result
                for j,result in enumerate(results):
                    # The variables VALUE, INDEX, and LENGTH are local overrides
                    # for this iteration of the loop
                    filled_out += fill_out_one_section(self.sections[k],
                                                       self.expressions[k],
                                                       self.assignments[k],
                                                       lookup,
                                                       VALUE=result,
                                                       INDEX=j,
                                                       LENGTH=len(result))

        return filled_out

    ############################################################################

    def write(self, lookup, outfile):
        """Write one XML label based on the template, lookup dictionary, and
        output filename."""

        # Write the label
        with open(outfile, 'w') as f:
            for part in self.stringlist(lookup):
                f.write(part)

    ############################################################################
    # Utility functions
    ############################################################################

    @staticmethod
    def REPLACE_NA(value, na_value, flag='N/A'):
        """Replace a string with the value 'N/A' with a numeric."""

        if value == flag:
            return na_value
        elif type(value) == str:
            raise ValueError('Illegal number! ' + value)
        else:
            return value

    @staticmethod
    def CURRENT_ZULU():
        """Return the current time UTC as a formatted string."""

        return time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())

    @staticmethod
    def DATETIME(value):
        """Convert the given date/time string to a year-month-day format with a
        trailing "Z". The date can be in year-month-day or year-dayofyear
        format. The time component (following a capital 'T') is unchanged."""

        (date,hms) = value.split('T')     # fails if not exactly two parts

        # Convert the date to ymd if necessary
        parts = date.split('-')
        if len(parts) == 2:
            day = time.strptime(date, '%Y-%j')
            date = time.strftime('%Y-%m-%d', day)

        # Reassemble
        return date + 'T' + hms + ('Z' if not hms.endswith('Z') else '')

    ############################################################################
    # Info about a file
    ############################################################################

    @staticmethod
    def BASENAME(filename):
        """Return the basename of a file path."""

        return os.path.basename(filename)

    @staticmethod
    def FILE_ZULU(filename):
        """Return the modification time of a file as a formatted string."""

        timestamp = os.path.getmtime(filename)
        creation_dt = datetime.datetime.fromtimestamp(timestamp)
        local = pytz.timezone(XmlTemplate.TIMEZONE)
        local_dt = local.localize(creation_dt, is_dst=None)
        utc_dt = local_dt.astimezone(pytz.utc)
        return utc_dt.strftime('%Y-%m-%dT%H:%M:%SZ')

    @staticmethod
    def FILE_BYTES(filename):
        """Return the number of bytes in a file."""

        return os.path.getsize(filename)

    # From http://stackoverflow.com/questions/3431825/-
    @staticmethod
    def FILE_MD5(filename, blocksize=65536):
        """Return the MD5 checksum of the file at the specified path."""

        f = open(filename, 'rb')
        hasher = hashlib.md5()
        buf = f.read(blocksize)
        while len(buf) > 0:
            hasher.update(buf)
            buf = f.read(blocksize)

        return hasher.hexdigest()

################################################################################

PREDEFINED_FUNCTIONS = {}
PREDEFINED_FUNCTIONS['REPLACE_NA'  ] = XmlTemplate.REPLACE_NA
PREDEFINED_FUNCTIONS['CURRENT_ZULU'] = XmlTemplate.CURRENT_ZULU
PREDEFINED_FUNCTIONS['DATETIME'    ] = XmlTemplate.DATETIME
PREDEFINED_FUNCTIONS['BASENAME'    ] = XmlTemplate.BASENAME
PREDEFINED_FUNCTIONS['FILE_ZULU'   ] = XmlTemplate.FILE_ZULU
PREDEFINED_FUNCTIONS['FILE_BYTES'  ] = XmlTemplate.FILE_BYTES
PREDEFINED_FUNCTIONS['FILE_MD5'    ] = XmlTemplate.FILE_MD5

################################################################################
