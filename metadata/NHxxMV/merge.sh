cat NHLAMV_1001/NH????_????_index.tab \
    NHJUMV_1001/NH????_????_index.tab \
    NHPCMV_1001/NH????_????_index.tab \
    NHPEMV_1001/NH????_????_index.tab \
    NHKCMV_1001/NH????_????_index.tab \
    NHKEMV_1001/NH????_????_index.tab \
  > NHxxMV_1999/NHxxMV_1999_index.tab

cat NHLAMV_2001/NH????_????_index.tab \
    NHJUMV_2001/NH????_????_index.tab \
    NHPCMV_2001/NH????_????_index.tab \
    NHPEMV_2001/NH????_????_index.tab \
    NHKCMV_2001/NH????_????_index.tab \
    NHKEMV_2001/NH????_????_index.tab \
  > NHxxMV_2999/NHxxMV_1999_index.tab

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
  > NHxxMV_2999/NHxxMV_1999_supplemental_index.tab


grep NHLAMV_1001 NHxxMV_1999/NHxxMV_1999_index.tab > NHLAMV_1001/NHLAMV_1001_index.tab
grep NHJUMV_1001 NHxxMV_1999/NHxxMV_1999_index.tab > NHJUMV_1001/NHJUMV_1001_index.tab
grep NHPCMV_1001 NHxxMV_1999/NHxxMV_1999_index.tab > NHPCMV_1001/NHPCMV_1001_index.tab
grep NHPEMV_1001 NHxxMV_1999/NHxxMV_1999_index.tab > NHPEMV_1001/NHPEMV_1001_index.tab
grep NHKCMV_1001 NHxxMV_1999/NHxxMV_1999_index.tab > NHKCMV_1001/NHKCMV_1001_index.tab
grep NHKEMV_1001 NHxxMV_1999/NHxxMV_1999_index.tab > NHKEMV_1001/NHKEMV_1001_index.tab

grep NHLAMV_2001 NHxxMV_2999/NHxxMV_2999_index.tab > NHLAMV_2001/NHLAMV_2001_index.tab
grep NHJUMV_2001 NHxxMV_2999/NHxxMV_2999_index.tab > NHJUMV_2001/NHJUMV_2001_index.tab
grep NHPCMV_2001 NHxxMV_2999/NHxxMV_2999_index.tab > NHPCMV_2001/NHPCMV_2001_index.tab
grep NHPEMV_2001 NHxxMV_2999/NHxxMV_2999_index.tab > NHPEMV_2001/NHPEMV_2001_index.tab
grep NHKCMV_2001 NHxxMV_2999/NHxxMV_2999_index.tab > NHKCMV_2001/NHKCMV_2001_index.tab
grep NHKEMV_2001 NHxxMV_2999/NHxxMV_2999_index.tab > NHKEMV_2001/NHKEMV_2001_index.tab


grep NHLAMV_1001 NHxxMV_1999/NHxxMV_1999_supplemental_index.tab > NHLAMV_1001/NHLAMV_1001_supplemental_index.tab
grep NHJUMV_1001 NHxxMV_1999/NHxxMV_1999_supplemental_index.tab > NHJUMV_1001/NHJUMV_1001_supplemental_index.tab
grep NHPCMV_1001 NHxxMV_1999/NHxxMV_1999_supplemental_index.tab > NHPCMV_1001/NHPCMV_1001_supplemental_index.tab
grep NHPEMV_1001 NHxxMV_1999/NHxxMV_1999_supplemental_index.tab > NHPEMV_1001/NHPEMV_1001_supplemental_index.tab
grep NHKCMV_1001 NHxxMV_1999/NHxxMV_1999_supplemental_index.tab > NHKCMV_1001/NHKCMV_1001_supplemental_index.tab
grep NHKEMV_1001 NHxxMV_1999/NHxxMV_1999_supplemental_index.tab > NHKEMV_1001/NHKEMV_1001_supplemental_index.tab

grep NHLAMV_2001 NHxxMV_2999/NHxxMV_2999_supplemental_index.tab > NHLAMV_2001/NHLAMV_2001_supplemental_index.tab
grep NHJUMV_2001 NHxxMV_2999/NHxxMV_2999_supplemental_index.tab > NHJUMV_2001/NHJUMV_2001_supplemental_index.tab
grep NHPCMV_2001 NHxxMV_2999/NHxxMV_2999_supplemental_index.tab > NHPCMV_2001/NHPCMV_2001_supplemental_index.tab
grep NHPEMV_2001 NHxxMV_2999/NHxxMV_2999_supplemental_index.tab > NHPEMV_2001/NHPEMV_2001_supplemental_index.tab
grep NHKCMV_2001 NHxxMV_2999/NHxxMV_2999_supplemental_index.tab > NHKCMV_2001/NHKCMV_2001_supplemental_index.tab
grep NHKEMV_2001 NHxxMV_2999/NHxxMV_2999_supplemental_index.tab > NHKEMV_2001/NHKEMV_2001_supplemental_index.tab



FILES = [
    'NHJUMV_1001/NHJUMV_1001_index.lbl',
    'NHJUMV_1001/NHJUMV_1001_supplemental_index.lbl',
    'NHJUMV_2001/NHJUMV_2001_index.lbl',
    'NHJUMV_2001/NHJUMV_2001_supplemental_index.lbl',
    'NHKCMV_1001/NHKCMV_1001_index.lbl',
    'NHKCMV_1001/NHKCMV_1001_supplemental_index.lbl',
    'NHKCMV_2001/NHKCMV_2001_index.lbl',
    'NHKCMV_2001/NHKCMV_2001_supplemental_index.lbl',
    'NHKEMV_1001/NHKEMV_1001_index.lbl',
    'NHKEMV_1001/NHKEMV_1001_supplemental_index.lbl',
    'NHKEMV_2001/NHKEMV_2001_index.lbl',
    'NHKEMV_2001/NHKEMV_2001_supplemental_index.lbl',
    'NHLAMV_1001/NHLAMV_1001_index.lbl',
    'NHLAMV_1001/NHLAMV_1001_supplemental_index.lbl',
    'NHLAMV_2001/NHLAMV_2001_index.lbl',
    'NHLAMV_2001/NHLAMV_2001_supplemental_index.lbl',
    'NHPCMV_1001/NHPCMV_1001_index.lbl',
    'NHPCMV_1001/NHPCMV_1001_supplemental_index.lbl',
    'NHPCMV_2001/NHPCMV_2001_index.lbl',
    'NHPCMV_2001/NHPCMV_2001_supplemental_index.lbl',
    'NHPEMV_1001/NHPEMV_1001_index.lbl',
    'NHPEMV_1001/NHPEMV_1001_supplemental_index.lbl',
    'NHPEMV_2001/NHPEMV_2001_index.lbl',
    'NHPEMV_2001/NHPEMV_2001_supplemental_index.lbl',
    'NHxxMV_1999/NHxxMV_1999_index.lbl',
    'NHxxMV_1999/NHxxMV_1999_supplemental_index.lbl',
    'NHxxMV_2999/NHxxMV_2999_index.lbl',
    'NHxxMV_2999/NHxxMV_2999_supplemental_index.lbl',
]

from pdstable import PdsTable

for f in FILES:
     print(f)
     x = PdsTable(f)
