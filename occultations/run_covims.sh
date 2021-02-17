#!/bin/bash
METADIR=$1/metadata/COVIMS_8xxx/COVIMS_8001
VOLROOT=$1/volumes/COVIMS_8xxx/COVIMS_8001
python covims.py $METADIR/COVIMS_8001_profile_index.lbl $VOLROOT $METADIR/COVIMS_8001_supplemental_index.lbl
