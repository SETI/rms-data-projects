#!/bin/bash
METADIR=$1/metadata/CORSS_8xxx/CORSS_8001
VOLROOT=$1/volumes/CORSS_8xxx/CORSS_8001
python corss.py $METADIR/CORSS_8001_profile_index.lbl $VOLROOT $METADIR/CORSS_8001_supplemental_index.lbl
