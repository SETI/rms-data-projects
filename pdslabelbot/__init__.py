#!/usr/bin/python
################################################################################
# pdslabelbot.py
#
# Methods to generate PDS labels for arbitrary CSV tables.
#
# Joe Spitale, SETI Institute, November 2024
#
################################################################################
import pdsparser
import pdslogger

from pdstemplate    import PdsTemplate
from pathlib        import Path


#===============================================================================
def read_txt_file(filename):           ### move to utilities
    """Utility shortcut to read a text file.
    Args:
        filename (str): Name of file to read.

    Returns:
        list: Lines comprising the file.
    """
    f = open(filename)
    lines = f.readlines()
    f.close()
    return lines

#===============================================================================
def write_txt_file(filename, lines, append=False):        ### move to utilities
    """Utility shortcut to write a text file.
    Args:
        filename (str): Name of file to write.
        lines (list): Lines comprising the file.
        append (bool, optional): 
            If True the lines are appended to the existing file.

    Returns: 
        None.
    """
    mode = 'a' if append else 'w'
    f = open(filename, mode)
    for line in lines:
        f.write(line)
    f.close()

#===============================================================================
def clean(s):
    """Remove leading and trailing whitespace and double quotes.

    Args:
        s (str): String to clean.

    Returns:
        str: Cleaned string.
    """
    s = s.strip()
    if s[0] == '"':
        s = s[1:-1]
    return s.strip()

##########################################################################################
# PdsLabelBot class
##########################################################################################

#===============================================================================
class PdsLabelBot(object):
    """Class to create PDS3 labels using a template.

    The general procedure is as follows.

    1. Create a template file according to the rules below.
    2. Create a PdsLabelBot object to read the template and corresponding 
       CSV table:
            bot = PdsLabelBot(table_path, template_path)
    3. Generate and write the newlabel file as:
            bot.write(label_file)

    TEMPLATE RULES

        The PdsLabelBot template is an augmented PdsTemplate template, so all
        PdsTemplate rules apply. In addition, directives and substitutions, as 
        described below, are implemented.

        PdsLabelBot uses multiple PdsTemplate passes to build the pds3
        column descriptions. A typical column description looks like:

          OBJECT                        = COLUMN
          $ONCE(COLUMN_NAME                                  = 'VOLUME_ID')
            NAME                        = $COLUMN_NAME$
            COLUMN_NUMBER               = $COUNTER('COLUMN')$
            START_BYTE                  = $$$COLUMN_NAME$_START_BYTE$$
            DATA_TYPE                   = $$$COLUMN_NAME$_DATA_TYPE$$
            BYTES                       = $$$COLUMN_NAME$_BYTES$$
            FORMAT                      = $$$COLUMN_NAME$_FORMAT$$
            DESCRIPTION                 = "The volume ID provides a unique identifier
              for a PDS data volume."
          END_OBJECT                    = COLUMN

        On the first PdsTemplate pass, the NAME and COLUMN_NUMBER fields
        are filled in and the other fields become $VOLUME_ID_START_BYTE$,
        $VOLUME_ID_DATA_TYPE$, etc. Those quantites are computed from the 
        table file and then resolved in the second PdsTemplate pass.

    DIRECTIVES

        Directives must appear at the beginning of a line and are specified 
        as $<directive>{<arg>}.

    PRE-DEFINED DIRECTIVE FUNCTIONS

        INSERT(filepath):
            Replaces the directive with the contents of the filepath.

    SUBSTITUTIONS

        Column names appearing in curly brackets are substituted for their 
        corresponding value in the first row ofthe table file.

    LOGGING AND EXCEPTION HANDLING

    The pdslogger module is used to handle logging. By default, the 
    pdslogger.NullLogger class is used, meaning that no actions are logged. 
    To override, call:
        set_logger(logger)
    in your Python program to use the specified logger. For example,
        set_logger(pdslogger.EasyLogger())
    will log all messages to the terminal.

    By default, exceptions during a call to write() or generate() are handled as follows:
    1. They are written to the log.
    2. The template attribute ERROR_COUNT contains the number of exceptions raised.
    3. The expression that triggered the exception is replaced by the error text in the
       label, surrounded by "[[[" and "]]]" to make it easier to find.
    4. The exception is otherwise suppressed.

    This behavior can be modified by calling method raise_exceptions(True). In this case,
    the call to write() or generate() raises the exception and then halts.
    """
    GLOBAL_LOGGER = pdslogger.NullLogger()     # default

    def __init__(self, table_path, template_path, 
                       table_type=None, terminator='\r\n', logger=None):
        """Construct a label bot.

        Args:
            table_path (str): Path to the table file.
            table_path (str): Path to the template file.
            terminator (str, optional): Line terminator.
            logger (pdslogger): 
                Pdslogger to use.  Default is pdslogger.NullLogger.
            table_type (str, optional): Table type to put in label.

        Returns:
            None.
        """
        self.logger = logger or PdsTemplate.GLOBAL_LOGGER

        self.table_path = Path(table_path)
        self.template_path = Path(template_path)
        self.table_type = table_type.upper()
        self.terminator = terminator

        self.table_lines = []
        self.template_lines = []

        self.table_dicts = []
        self.column_stubs = []

        # Read the template and table
        self.read()

        # List of accepted directives.  Define new directives by adding to this 
        # list and adding a directive function below.
        self.directives = ['INSERT']

    ######################################################################################
    # Utility functions
    ######################################################################################

    #---------------------------------------------------------------------------
    @staticmethod
    def set_logger(logger=None):
        """Define the pdslogger globally for this module."""

        if logger:
            self.logger = logger
        else:
            self.logger = pdslogger.NullLogger()

    #---------------------------------------------------------------------------
    def read(self, logger=None):
        """Read the table and template file.

        Args:
            logger (pdslogger): 
                logger to use; None for the global default logger.

        Return:
            None.
        """
        logger = logger or self.logger

        try:
            logger.info('Loading template', self.template_path.as_posix())
            self.template_lines = read_txt_file(self.template_path)

            logger.info('Loading table', self.table_path.as_posix())
            self.table_lines = read_txt_file(self.table_path)
        except Exception as e:
            logger.exception(e, filename)
            raise

    #---------------------------------------------------------------------------
    def write(self, filename, logger=None):
        """Generate and write the label file.

        Args:
            filename: Name of label file to write.
            logger (pdslogger): 
                logger to use; None for the global default logger.

        Return:
            None.
        """
        logger = logger or self.logger

        self.generate()

        try:
            logger.info('Writing label', self.template_path.as_posix())
            write_txt_file(filename, self.template_lines)
        except Exception as e:
            logger.exception(e, filename)
            raise

    #---------------------------------------------------------------------------
    def regenerate(self, fields):
        """Regenerate the template."""
        T = PdsTemplate('_', content=self.template_lines)
        template = T.generate(fields, terminator=self.terminator+'[[]]')
        self.template_lines = template.split('[[]]')

    #---------------------------------------------------------------------------
    def detect_format(self, val):
        """Detect the format of a table value."""
        l = len(val)

        # Char format
        if val[0] == '"':
            return 'A' + str(l-2)

        # Float format
        if '.' in val:
            p = val.find('.')
            if p != -1:
                return 'F' + str(l) + '.' + str(l-p-1)

        # Int format
        return 'I' + str(l)

    #---------------------------------------------------------------------------
    def generate(self, logger=None):
        """Fully process the template.

        Args:
            logger (pdslogger): 
                logger to use; None for the global default logger.

        Returns: 
            list: Processed template lines.
        """
        logger = logger or self.logger

        try:
            # Pass 1: Parse directives
            self.process_directives()

            # Pass 2: Global fields
            self.process_globals()

            # Pass 3: Column fields
            self.process_columns()

            # Pass 4: Table substitutions
            self.process_substitutions()
        except Exception as e:
            logger.exception(e, filename)
            raise

        # Handle output
        return self.template_lines

    ######################################################################################
    # Directive functions
    ######################################################################################

    #---------------------------------------------------------------------------
    def _directive_insert(self, lnum, filename):
        """Defines the INSERT directive, which replaces the directive with the
        contents of the named file.

        Args:
            lnum (int): Line number at which this directive was encountered.
            filename (str): Name of file containing the lines to insert.

        Returns:
            int: Line number in output label at which processing 
                 is to continue.
        """

        # Read file
        insert_lines = read_txt_file(filename)       

        # Insert into label
        self.template_lines = \
            self.template_lines[0:lnum] + insert_lines + self.template_lines[lnum+1:]
        lnum += len(insert_lines)-1

        return lnum

    ######################################################################################
    # Table functions
    ######################################################################################

    #---------------------------------------------------------------------------
    def parse_table(self):
        """Make row dictionaries from a table.

        Args:
            None.

        Returns:
            list: 
                Dictionaries containing tuples in which the first element gives
                the cleaned value(s) and the second gives the raw value(s).
        """
        self.table_dicts = []
        for line in self.table_lines:
            items = line.split(',')
            ii = 0
            dict = {}
            for stub in self.column_stubs:
                nitems = int(stub['ITEMS']) if 'ITEMS' in stub else 1
                raw = []
                cleaned = []
                for i in range(nitems):
                    raw.append(items[ii])
                    cleaned.append(clean(items[ii]))
                    ii += 1
                dict[stub['NAME']] = (cleaned, raw)
            self.table_dicts.append(dict)


    ######################################################################################
    # Column functions
    ######################################################################################

    #---------------------------------------------------------------------------
    def parse_columns(self):
        """Parse all label column descriptions into a list of stub dictionaries.

        Args:
            None.

        Returns:
            list: Column stub dictionaries.
        """

        #-----------------------------------------------------------------------
        def parse_block(lines, head=0, *,
                        start_token='OBJECT=COLUMN', end_token='END_OBJECT=COLUMN'):
            """Extract a block of lines between two tokens.

            Args:
                lines (list): List of strings.
                head (list, optional): Line at which to start search.  Default: 0.
                start_token (str, optional): Block start token.  Default: 'OBJECT=COLUMN'.
                end_token (str, optional): Block end token.  Default: END_OBJECT=COLUMN'.

            Returns:
                NamedTuple (block (list), head (int), tail (int)):
                    block (list): List of strings in the first detected block.
                    head (int): Line number of the start of the block.
                    tail (int): Line number of the end of the block.
            """   
            tail = -1
            block = []
            for i in range(head,len(lines)):
                line = lines[i]
                if line.replace(' ', '').startswith(start_token):
                    head = i
                    tail = head
                    for line in lines[i:]:
                        tail += 1
                        block.append(line)
                        if line.replace(' ', '').startswith(end_token):
                            break
                    if block:
                        break

            return (block, head, tail)

        #-----------------------------------------------------------------------
        def parse_column(lines):
            """Parse a label column description into a stub dictionary.

            Args:
                lines (list): Column description.

            Returns:
                dict: Column stub dictionary.
            """   
            column_dict = {}
            for line in lines:
                line = line.replace(' ', '')
                kv = line.split('=')
                if len(kv) == 2:
                    column_dict[kv[0]] = kv[1].strip()
            return column_dict


        self.column_stubs = []
        head = 0
        while(True):

            # Get the current block
            block, head, tail = parse_block(self.template_lines, head)
            if block == []:
                break

            # Append the column dictionary 
            self.column_stubs.append(parse_column(block))

            # Advance the read head
            head += len(block)

    ######################################################################################
    # Processing functions
    ######################################################################################

    #---------------------------------------------------------------------------
    def process_directives(self):
        """Process label directives of the form $<DIRECTIVE>{<arg>} and update
        template lines.  Directives must appear at the start of a line.

        Args: 
            None

        Returns: 
            None

        """
        lnum = 0
        for line in self.template_lines:
            for directive in self.directives:

                # test for directive pattern at start of line: $<directive>{
                pattern = '$' + directive + '{'
                if line.startswith(pattern):
                    try:
                        arg = line.split('{')[1].split('}')[0]
                    except:
                        raise SyntaxError(line)

                    # call directive function
                    fn = globals()['PdsLabelBot'].__dict__['_directive_' + directive.lower()]
                    lnum = fn(self, lnum, arg)
            lnum += 1

    #---------------------------------------------------------------------------
    def process_globals(self):
        """Process global template fields.  And update template lines.

        Args: 
            None.

        Returns: 
            None
        """

        # Set up global field valuess
        recs = len(self.table_lines)
        linelen = len(self.table_lines[0])
        self.parse_columns()
        fields = {'TABLE_TYPE'      : self.table_type,
                  'FILENAME'        : self.table_path.name,
                  'RECORD_BYTES'    : linelen+1,
                  'FILE_RECORDS'    : recs,
                  'ROWS'            : recs,
                  'COLUMNS'         : len(self.column_stubs),
                  'ROW_BYTES'       : linelen+1 }  

        # Process the template
        self.regenerate(fields)

    #---------------------------------------------------------------------------
    def process_columns(self):
        """Process all template columns and update template lines.

        Args: 
            None.

        Returns: 
            None
        """

        # Update column stub dictionaries
        self.parse_columns()

        # Determine column properties
        self.parse_table()
        table_dict = self.table_dicts[0]
        pos = 1
        fields = {}
        for name, stub in zip(table_dict, self.column_stubs):
            prefix = stub['NAME'] + '_'

            col = table_dict[name][0]
            raw = table_dict[name][1]
            item_width = len(raw[0])

            format = self.detect_format(raw[0])
            fields[prefix+'FORMAT'] = '"' + format + '"'

            data_type = 'CHARACTER' if format[0]=='A' \
                                    else 'ASCII_REAL' if format[0]=='F' \
                                    else 'ASCII_INTEGER'
            fields[prefix+'DATA_TYPE'] = data_type


            nbytes = item_width-2 if data_type == 'CHARACTER' else item_width
            item_bytes = nbytes

            fields[prefix+'START_BYTE'] = pos+1 if data_type == 'CHARACTER' else pos
            fields[prefix+'BYTES'] = item_bytes

            # Arrays
            total_width = item_width
            if 'ITEMS' in stub:
                count = int(stub['ITEMS'])

                total_width = nbytes*count + (count-1)
                bytes = total_width

                if data_type == 'CHARACTER':
                    total_width += 2*count
                    bytes = total_width - 2

                fields[prefix + 'BYTES'] = bytes
                fields[prefix + 'ITEM_BYTES'] = item_bytes
                fields[prefix + 'ITEM_OFFSET'] = nbytes + 1
                if data_type == 'CHARACTER':
                    fields[prefix + '_ITEM_OFFSET'] += 2

            pos = pos + total_width + 1

        # Process the template
        self.regenerate(fields)

    #---------------------------------------------------------------------------
    def process_substitutions(self, index=0):
        """Perform substitutions defined by column names enclosed in curly
        brackets, e.g., {VOLUME_ID}.  The expression is replaced by the 
        named table value from the 0th row.  The template is updated.

        Args:
            None.

        Returns:
            None.
        """

        #-----------------------------------------------------------------------
        def parse_substitution(line):
            """ Create valid pdsTemplate variables by replacing {} with $$"""
            line = line.replace('{', '$')
            line = line.replace('}', '$')
            return line


        # Update column stub dictionaries
        self.parse_columns()

        # Update the table dicts
        self.parse_table()

        # Parse substitutions
        for i in range(len(self.template_lines)):
            self.template_lines[i] = parse_substitution(self.template_lines[i])

        # Create substitution dict
        fields = {}
        for stub, dict in zip(self.column_stubs, self.table_dicts):
            fields[stub['NAME']] = dict[stub['NAME']][0][0]

        # Process the template
        self.regenerate(fields)





"""
from pdslabelbot import PdsLabelBot
bot = PdsLabelBot('/home/spitale/SETI/RMS/metadata_test/GO_0xxx/GO_0017/GO_0017_sky_summary.tab', 
                  '/home/spitale/rms-/rms-data-projects/metadata/templates/labelbot/sky_summary.lbl',
                  table_type='SKY_GEOMETRY')
bot.write('/home/spitale/tmp/test.lbl')



from pdslabelbot import PdsLabelBot
bot = PdsLabelBot('/home/spitale/SETI/RMS/metadata_test/GO_0xxx/GO_0017/GO_0017_body_summary.tab', 
                  '/home/spitale/rms-/rms-data-projects/metadata/templates/labelbot/body_summary.lbl',
                  table_type='BODY_GEOMETRY')
bot.write('/home/spitale/tmp/test.lbl')



from pdslabelbot import PdsLabelBot
bot = PdsLabelBot('/home/spitale/SETI/RMS/metadata_test/GO_0xxx/GO_0017/GO_0017_ring_summary.tab', 
                  '/home/spitale/rms-/rms-data-projects/metadata/templates/labelbot/ring_summary.lbl',
                  table_type='RING_GEOMETRY')
bot.write('/home/spitale/tmp/test.lbl')



from pdslabelbot import PdsLabelBot
bot = PdsLabelBot('/home/spitale/SETI/RMS/metadata_test/GO_0xxx/GO_0017/GO_0017_supplemental_index.tab', 
                  '/home/spitale/rms-/rms-data-projects/metadata/hosts/GO_0xxx/templates/GO_0xxx_supplemental_index-labelbot.lbl',
                  table_type='SUPPLEMENTAL')
bot.write('/home/spitale/SETI/RMS/metadata_test/GO_0xxx/GO_0017/GO_0017_supplemental_index.lbl')
"""

