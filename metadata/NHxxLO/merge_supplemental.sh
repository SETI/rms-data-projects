tablelabel --save -t NHxxLO_supplemental_index_template.txt \
NH??LO_1001/NH??LO_1001_supplemental_index.tab

tablelabel --save -t NHxxLO_supplemental_index_template.txt \
NH??LO_2001/NH??LO_2001_supplemental_index.tab

cat NHLALO_1001/NH??LO_1001_supplemental_index.tab \
    NHJULO_1001/NH??LO_1001_supplemental_index.tab \
    NHPCLO_1001/NH??LO_1001_supplemental_index.tab \
    NHPELO_1001/NH??LO_1001_supplemental_index.tab \
    NHKCLO_1001/NH??LO_1001_supplemental_index.tab \
    NHKELO_1001/NH??LO_1001_supplemental_index.tab \
    NHK2LO_1001/NH??LO_1001_supplemental_index.tab \
  > NHxxLO_1999/NHxxLO_1999_supplemental_index.tab

cat NHLALO_2001/NH??LO_2001_supplemental_index.tab \
    NHJULO_2001/NH??LO_2001_supplemental_index.tab \
    NHPCLO_2001/NH??LO_2001_supplemental_index.tab \
    NHPELO_2001/NH??LO_2001_supplemental_index.tab \
    NHKCLO_2001/NH??LO_2001_supplemental_index.tab \
    NHKELO_2001/NH??LO_2001_supplemental_index.tab \
    NHK2LO_2001/NH??LO_2001_supplemental_index.tab \
  > NHxxLO_2999/NHxxLO_2999_supplemental_index.tab

tablelabel --save -t NHxxLO_supplemental_index_template.txt \
NHxxLO_1999/NHxxLO_1999_supplemental_index.tab

tablelabel --save -t NHxxLO_supplemental_index_template.txt \
NHxxLO_2999/NHxxLO_2999_supplemental_index.tab
