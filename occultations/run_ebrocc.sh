#!/bin/bash
METADIR=$1/metadata/EBROCC_xxxx/EBROCC_0001
VOLROOT=$1/volumes/EBROCC_xxxx/EBROCC_0001
python ebrocc.py $METADIR/ES1_profile_index.lbl $VOLROOT $METADIR/ES1_supplemental_index.lbl
python ebrocc.py $METADIR/ES2_profile_index.lbl $VOLROOT $METADIR/ES2_supplemental_index.lbl
python ebrocc.py $METADIR/IRT_profile_index.lbl $VOLROOT $METADIR/IRT_supplemental_index.lbl
python ebrocc.py $METADIR/LIC_profile_index.lbl $VOLROOT $METADIR/LIC_supplemental_index.lbl
python ebrocc.py $METADIR/MCD_profile_index.lbl $VOLROOT $METADIR/MCD_supplemental_index.lbl
python ebrocc.py $METADIR/PAL_profile_index.lbl $VOLROOT $METADIR/PAL_supplemental_index.lbl
