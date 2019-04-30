"""
Syntax for VICAR files.
"""

from typing import TYPE_CHECKING

from LabelItem import LabelItem
from Value import *
from VicarSyntax import maybe_bs

if TYPE_CHECKING:
    from typing import Optional
    from HistoryLabels import HistoryLabels
    from PropertyLabels import PropertyLabels
    from SystemLabels import SystemLabels

    HL = HistoryLabels
    PL = PropertyLabels
    SL = SystemLabels


class Labels(VicarSyntax):
    """A series of keyword-value pairs divided into three sections."""

    def __init__(self, system_labels, property_labels, history_labels,
                 padding):
        # type: (SL, PL, HL, Optional[str]) -> None
        assert system_labels is not None
        assert property_labels is not None
        assert history_labels is not None

        lblsize = system_labels.get_int_value('LBLSIZE')
        assert lblsize > 0, 'LBLSIZE zero or missing'

        # make sure LBLSIZE is correct
        size_of_labels = sum([system_labels.to_byte_length(),
                              property_labels.to_byte_length(),
                              history_labels.to_byte_length(),
                              len(maybe_bs(padding))])
        assert size_of_labels == lblsize, \
            'size of labels (%d) != lblsize (%d)' % (size_of_labels, lblsize)

        self.system_labels = system_labels
        self.property_labels = property_labels
        self.history_labels = history_labels
        self.padding = padding

    def __eq__(self, other):
        return [self.system_labels,
                self.property_labels,
                self.history_labels,
                maybe_bs(self.padding)] == [other.system_labels,
                                            other.property_labels,
                                            other.history_labels,
                                            maybe_bs(other.padding)]

    def __repr__(self):
        items_str = ', '.join([repr(item)
                               for item in [self.system_labels,
                                            self.property_labels,
                                            self.history_labels,
                                            self.padding]])
        return 'Labels(%s)' % items_str

    def to_byte_length(self):
        return sum([self.system_labels.to_byte_length(),
                    self.property_labels.to_byte_length(),
                    self.history_labels.to_byte_length(),
                    len(maybe_bs(self.padding))])

    def to_byte_string(self):
        return ''.join([self.system_labels.to_byte_string(),
                        self.property_labels.to_byte_string(),
                        self.history_labels.to_byte_string(),
                        maybe_bs(self.padding)])

    def get_int_value(self, keyword, default=0):
        # type: (str, int) -> int
        """
        Look up a keyword in the system LabelItems and return the
        corresponding integer value as an int.  If there are no
        matching LabelItems, return the default value.  If there are
        more than one, or if the value is not an IntegerValue, raise
        an exception.
        """
        return self.system_labels.get_int_value(keyword, default)

    def get_lblsize(self):
        # type: () -> int
        """
        Return the value of LBLSIZE.  It must exist, by construction.
        """
        return self.get_int_value('LBLSIZE')

    def has_migration_task(self):
        # type: () -> bool
        """
        Return True if the last task in the HistoryLabels is s a
        migration task.  It has to be the last task because we don't
        guarantee we can backmigrate the file if it's been further
        processed.
        """
        return self.history_labels.has_migration_task()

    @staticmethod
    def create_labels_with_adjusted_lblsize(system_labels,
                                            property_labels,
                                            history_labels,
                                            padding):
        # type: (SL, PL, HL, Optional[str]) -> Labels
        """
        Create a Labels from the pieces, adjusting the LBLSIZE and
        adding padding as necessary.
        """
        recsize = system_labels.get_int_value('RECSIZE', 0)
        assert recsize > 0
        return _create_labels(recsize,
                              system_labels,
                              property_labels,
                              history_labels,
                              padding)

    @staticmethod
    def create_eol_labels_with_adjusted_lblsize(recsize,
                                                system_labels,
                                                property_labels,
                                                history_labels,
                                                padding):
        # type: (int, SL, PL, HL, Optional[str]) -> Labels
        """
        Create a Labels from the pieces, adjusting the LBLSIZE and
        adding padding as necessary.
        """
        return _create_labels(recsize,
                              system_labels,
                              property_labels,
                              history_labels,
                              padding)


def _create_labels(recsize, system_labels, property_labels, history_labels,
                   padding):
    # type: (int, SL, PL, HL, Optional[str]) -> Labels
    """
    Create a Labels from the pieces, adjusting the LBLSIZE and
    adding padding as necessary.
    """
    assert recsize > 0

    def make_lblsize_item(n):
        # type: (int) -> LabelItem
        """Create a LBLSIZE LabelItem with a fixed width."""
        int_str = '%10d' % n
        return LabelItem.create('LBLSIZE', IntegerValue(int_str))

    # Substitute a dummy LBLSIZE item of fixed width into the
    # SystemLabels and figure out its size.
    adjusted_system_labels_length = system_labels.replace_label_items(
        [make_lblsize_item(0)]).to_byte_length()
    property_labels_length = property_labels.to_byte_length()
    history_labels_length = history_labels.to_byte_length()
    padding_length = len(maybe_bs(padding))

    adjusted_labels_length = sum([adjusted_system_labels_length,
                                  property_labels_length,
                                  history_labels_length,
                                  padding_length])

    # Find the padding needed to bring the LBLSIZE up to a multiple of
    # RECSIZE.
    final_labels_length = round_to_multiple_of(adjusted_labels_length, recsize)
    new_padding_length = final_labels_length - adjusted_labels_length
    final_padding = maybe_bs(padding) + new_padding_length * '\0'

    # Substitute the actual LBLSIZE into the SystemLabels.
    final_system_labels = system_labels.replace_label_items(
        [make_lblsize_item(final_labels_length)])

    # Create the result with the right LBLSIZE.
    result = Labels(final_system_labels,
                    property_labels,
                    history_labels,
                    final_padding)

    assert final_labels_length == result.to_byte_length()
    return result


def round_to_multiple_of(n, m):
    assert m > 0
    excess = n % m
    if excess == 0:
        return n
    else:
        return n + m - excess
