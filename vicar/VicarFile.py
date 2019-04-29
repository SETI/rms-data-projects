from typing import TYPE_CHECKING

from ImageArea import ImageArea
from Labels import Labels
from Tail import Tail
from VicarSyntax import VicarSyntax

if TYPE_CHECKING:
    from typing import Optional


class VicarFile(VicarSyntax):
    def __init__(self,
                 labels,
                 image_area,
                 eol_labels,
                 tail):
        # type: (Labels, ImageArea, Optional[Labels], Tail) -> None
        assert labels is not None
        assert isinstance(labels, Labels)
        assert image_area is not None
        assert isinstance(image_area, ImageArea)
        assert eol_labels is None or isinstance(labels, Labels)
        assert tail is not None
        assert isinstance(tail, Tail)

        assert (labels.get_int_value('EOL') == 0) == (eol_labels is None), \
            'nonzero EOL keyword value exactly when eol_labels present'
        assert labels.get_int_value('RECSIZE') > 0, 'must have RECSIZE keyword'
        assert (labels.get_int_value('RECSIZE') ==
                image_area.implicit_recsize_value()), \
            ('RECSIZE value not correct for image; should be  %d' %
             image_area.implicit_recsize_value())
        assert (labels.get_int_value('NBB') ==
                image_area.implicit_nbb_value()), \
            ('NBB value not correct for image; should be %d' %
             image_area.implicit_nbb_value())

        assert (labels.get_int_value('NLB') ==
                image_area.implicit_nlb_value()), \
            ('NLB value not correct for image; should be %d' %
             image_area.implicit_nlb_value())

        self.labels = labels
        self.image_area = image_area
        self.eol_labels = eol_labels
        self.tail = tail

    def __eq__(self, other):
        return [self.labels,
                self.image_area,
                self.eol_labels,
                self.tail] == [other.labels,
                               other.image_area,
                               other.eol_labels,
                               other.tail]

    def __repr__(self):
        return 'VicarFile(%r, %r, %r, %r)' % (self.labels,
                                              self.image_area,
                                              self.eol_labels,
                                              self.tail)

    def to_byte_length(self):
        if self.eol_labels is None:
            eol_labels_byte_length = 0
        else:
            eol_labels_byte_length = self.eol_labels.to_byte_length()
        return sum([self.labels.to_byte_length(),
                    self.image_area.to_byte_length(),
                    eol_labels_byte_length,
                    self.tail.to_byte_length()])

    def to_byte_string(self):
        if self.eol_labels is None:
            eol_labels_byte_string = ''
        else:
            eol_labels_byte_string = self.eol_labels.to_byte_string()
        return ''.join([self.labels.to_byte_string(),
                        self.image_area.to_byte_string(),
                        eol_labels_byte_string,
                        self.tail.to_byte_string()])

    def get_recsize(self):
        # type: () -> int
        return self.labels.get_int_value('RECSIZE')
