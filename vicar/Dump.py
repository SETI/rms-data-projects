import contextlib

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Optional
    from ImageArea import ImageArea
    IA = ImageArea
    from Labels import Labels
    from Tail import Tail
    from VicarFile import VicarFile
    

class Dumper(object):
    def __init__(self):
        self.indent_level = 0

    def print_line(self, str):
        print '**** %s %s' % ((self.indent_level * 2) * ' ', str)

    def indent(self):
        self.indent_level += 1

    def outdent(self):
        self.indent_level -= 1


@contextlib.contextmanager
def indentation(dumper):
    dumper.indent()
    try:
        yield
    finally:
        dumper.outdent()


def dump_vicar_file(vicar_file, msg='', dumper=None):
    # type: (VicarFile, str, Optional[Dumper]) -> None
    if dumper is None:
        dumper = Dumper()

    dumper.print_line('== %s ==' % msg)
    dumper.print_line('VicarFile (%d):' % vicar_file.to_byte_length())
    with indentation(dumper):
        dump_labels(vicar_file.labels, dumper)
        dump_image_area(vicar_file.image_area, dumper)
        dump_eol_labels(vicar_file.eol_labels, dumper)
        dump_tail(vicar_file.tail, dumper)

def dump_vicar_file_parts(labels, image_area, eol_labels, tail, msg='', dumper=None):
    # type: (Labels, IA, Optional[Labels], Tail, str, Optional[Dumper]) -> None
    if dumper is None:
        dumper = Dumper()
    
    dumper.print_line('== %s ==' % msg)
    dumper.print_line('VicarFile parts:')
    with indentation(dumper):
        dump_labels(labels, dumper)
        dump_image_area(image_area, dumper)
        dump_eol_labels(eol_labels, dumper)
        dump_tail(tail, dumper)


def dump_labels(labels, dumper=None):
    # type: (Labels, Optional[Dumper]) -> None
    if dumper is None:
        dumper = Dumper()

    dumper.print_line('Labels (%d):' % labels.to_byte_length())
    with indentation(dumper):
        dumper.print_line('LBLSIZE = %d' % \
                              labels.system_labels.get_int_value('LBLSIZE'))
        dumper.print_line('RECSIZE = %d' % \
                              labels.system_labels.get_int_value('RECSIZE'))
        dumper.print_line('NBB = %d' % \
                              labels.system_labels.get_int_value('NBB'))
        dumper.print_line('NLB = %d' % \
                              labels.system_labels.get_int_value('NLB'))


def dump_image_area(image_area, dumper=None):
    # type: (ImageArea, Optional[Dumper]) -> None
    if dumper is None:
        dumper = Dumper()

    dumper.print_line('ImageArea (%d):' % image_area.to_byte_length())
    with indentation(dumper):
        if image_area.binary_header is None:
            dumper.print_line('Binary header: None')
        else:
            dumper.print_line('Binary header (%d):' %
                              (len(image_area.binary_header),))
        if image_area.binary_prefixes is None:
            dumper.print_line('Binary prefixes: None')
        else:
            dumper.print_line('Binary prefixes (%d x %d):' %
                              (len(image_area.binary_prefixes[0]),
                               len(image_area.binary_prefixes)))
        dumper.print_line('Binary image lines (%d x %d):' %
                          (len(image_area.binary_image_lines[0]),
                           len(image_area.binary_image_lines)))



def dump_eol_labels(labels, dumper=None):
    # type: (Optional[Labels], Optional[Dumper]) -> None
    if dumper is None:
        dumper = Dumper()

    if labels is None:
        dumper.print_line('EOL Labels: None')
    else:
        dumper.print_line('EOL Labels (%d):' % labels.to_byte_length())


def dump_tail(tail, dumper=None):
    # type: (Tail, Optional[Dumper]) -> None
    if dumper is None:
        dumper = Dumper()

    dumper.print_line('Tail (%d):' % tail.to_byte_length())
    with indentation(dumper):
        if tail.binary_prefixes_at_tail is None:
            dumper.print_line('Binary prefixes at tail: None')
        else:
            dumper.print_line('Binary prefixes at tail (%d x %d):' % 
                              (len(tail.binary_prefixes_at_tail[0]),
                               len(tail.binary_prefixes_at_tail)))
        if tail.tail_bytes is None:
            dumper.print_line('Tail bytes: None')
        else:
            dumper.print_line('Tail bytes (%d):' % 
                              len(tail.tail_bytes))

