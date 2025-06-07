tablelabel --save -t NHxxMV_supplemental_index_template.txt \
NH??MV_1001/NH??MV_1001_supplemental_index.tab

tablelabel --save -t NHxxMV_supplemental_index_template.txt \
NH??MV_2001/NH??MV_2001_supplemental_index.tab

cat NHLAMV_1001/NH????_????_supplemental_index.tab \
    NHJUMV_1001/NH????_????_supplemental_index.tab \
    NHPCMV_1001/NH????_????_supplemental_index.tab \
    NHPEMV_1001/NH????_????_supplemental_index.tab \
    NHKCMV_1001/NH????_????_supplemental_index.tab \
    NHKEMV_1001/NH????_????_supplemental_index.tab \
  > NHxxMV_1999/NHxxMV_1999_supplemental_index.tab

cat NHLAMV_2001/NH????_????_supplemental_index.tab \
    NHJUMV_2001/NH????_????_supplemental_index.tab \
    NHPCMV_2001/NH????_????_supplemental_index.tab \
    NHPEMV_2001/NH????_????_supplemental_index.tab \
    NHKCMV_2001/NH????_????_supplemental_index.tab \
    NHKEMV_2001/NH????_????_supplemental_index.tab \
  > NHxxMV_2999/NHxxMV_2999_supplemental_index.tab

tablelabel --save -t NHxxMV_supplemental_index_template.txt \
NHxxMV_1999/NHxxMV_1999_supplemental_index.tab

tablelabel --save -t NHxxMV_supplemental_index_template.txt \
NHxxMV_2999/NHxxMV_2999_supplemental_index.tab
