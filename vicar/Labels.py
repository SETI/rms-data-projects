"""
Syntax for VICAR files.
"""

from typing import TYPE_CHECKING

from Value import *
from VicarSyntax import maybe_bs

if TYPE_CHECKING:
    from typing import Optional
    from HistoryLabels import HistoryLabels
    from PropertyLabels import PropertyLabels
    from SystemLabels import SystemLabels

    SL = SystemLabels


class Labels(VicarSyntax):
    """A series of keyword-value pairs divided into three sections."""

    def __init__(self, system_labels, property_labels, history_labels,
                 padding):
        # type: (SL, PropertyLabels, HistoryLabels, Optional[str]) -> None
        assert system_labels is not None
        assert property_labels is not None
        assert history_labels is not None

        assert system_labels.get_int_value('LBLSIZE') > 0, \
            'LBLSIZE zero or missing'

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
        Return the value of LBLSIZE.  It must exist by construction.
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
