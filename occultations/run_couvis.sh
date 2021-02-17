#!/bin/bash
METADIR=$1/metadata/COUVIS_8xxx/COUVIS_8001
VOLROOT=$1/volumes/COUVIS_8xxx/COUVIS_8001
python couvis.py $METADIR/COUVIS_8001_profile_index.lbl $VOLROOT $METADIR/COUVIS_8001_supplemental_index.lbl
