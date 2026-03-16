cat NHLALO_1001/NH????_????_index.tab \
    NHJULO_1001/NH????_????_index.tab \
    NHPCLO_1001/NH????_????_index.tab \
    NHPELO_1001/NH????_????_index.tab \
    NHKCLO_1001/NH????_????_index.tab \
    NHKELO_1001/NH????_????_index.tab \
    NHK2LO_1001/NH????_????_index.tab > NHxxLO_1999/NHxxLO_1999_index.tab

cat NHLALO_2001/NH????_????_index.tab \
    NHJULO_2001/NH????_????_index.tab \
    NHPCLO_2001/NH????_????_index.tab \
    NHPELO_2001/NH????_????_index.tab \
    NHKCLO_2001/NH????_????_index.tab \
    NHKELO_2001/NH????_????_index.tab \
    NHK2LO_2001/NH????_????_index.tab > NHxxLO_2999/NHxxLO_2999_index.tab

cat NHLALO_1001/NH????_????_supplemental_index.tab \
    NHJULO_1001/NH????_????_supplemental_index.tab \
    NHPCLO_1001/NH????_????_supplemental_index.tab \
    NHPELO_1001/NH????_????_supplemental_index.tab \
    NHKCLO_1001/NH????_????_supplemental_index.tab \
    NHKELO_1001/NH????_????_supplemental_index.tab \
    NHK2LO_1001/NH????_????_supplemental_index.tab \
    > NHxxLO_1999/NHxxLO_1999_supplemental_index.tab

cat NHLALO_2001/NH????_????_supplemental_index.tab \
    NHJULO_2001/NH????_????_supplemental_index.tab \
    NHPCLO_2001/NH????_????_supplemental_index.tab \
    NHPELO_2001/NH????_????_supplemental_index.tab \
    NHKCLO_2001/NH????_????_supplemental_index.tab \
    NHKELO_2001/NH????_????_supplemental_index.tab \
    NHK2LO_2001/NH????_????_supplemental_index.tab \
    > NHxxLO_2999/NHxxLO_2999_supplemental_index.tab

grep NHLALO_1001 NHxxLO_1999/NHxxLO_1999_index.tab > NHLALO_1001/NHLALO_1001_index.tab
grep NHJULO_1001 NHxxLO_1999/NHxxLO_1999_index.tab > NHJULO_1001/NHJULO_1001_index.tab
grep NHPCLO_1001 NHxxLO_1999/NHxxLO_1999_index.tab > NHPCLO_1001/NHPCLO_1001_index.tab
grep NHPELO_1001 NHxxLO_1999/NHxxLO_1999_index.tab > NHPELO_1001/NHPELO_1001_index.tab
grep NHKCLO_1001 NHxxLO_1999/NHxxLO_1999_index.tab > NHKCLO_1001/NHKCLO_1001_index.tab
grep NHKELO_1001 NHxxLO_1999/NHxxLO_1999_index.tab > NHKELO_1001/NHKELO_1001_index.tab
grep NHK2LO_1001 NHxxLO_1999/NHxxLO_1999_index.tab > NHK2LO_1001/NHK2LO_1001_index.tab

grep NHLALO_2001 NHxxLO_2999/NHxxLO_2999_index.tab > NHLALO_2001/NHLALO_2001_index.tab
grep NHJULO_2001 NHxxLO_2999/NHxxLO_2999_index.tab > NHJULO_2001/NHJULO_2001_index.tab
grep NHPCLO_2001 NHxxLO_2999/NHxxLO_2999_index.tab > NHPCLO_2001/NHPCLO_2001_index.tab
grep NHPELO_2001 NHxxLO_2999/NHxxLO_2999_index.tab > NHPELO_2001/NHPELO_2001_index.tab
grep NHKCLO_2001 NHxxLO_2999/NHxxLO_2999_index.tab > NHKCLO_2001/NHKCLO_2001_index.tab
grep NHKELO_2001 NHxxLO_2999/NHxxLO_2999_index.tab > NHKELO_2001/NHKELO_2001_index.tab
grep NHK2LO_2001 NHxxLO_2999/NHxxLO_2999_index.tab > NHK2LO_2001/NHK2LO_2001_index.tab

grep NHLALO_1001 NHxxLO_1999/NHxxLO_1999_supplemental_index.tab > NHLALO_1001/NHLALO_1001_supplemental_index.tab
grep NHJULO_1001 NHxxLO_1999/NHxxLO_1999_supplemental_index.tab > NHJULO_1001/NHJULO_1001_supplemental_index.tab
grep NHPCLO_1001 NHxxLO_1999/NHxxLO_1999_supplemental_index.tab > NHPCLO_1001/NHPCLO_1001_supplemental_index.tab
grep NHPELO_1001 NHxxLO_1999/NHxxLO_1999_supplemental_index.tab > NHPELO_1001/NHPELO_1001_supplemental_index.tab
grep NHKCLO_1001 NHxxLO_1999/NHxxLO_1999_supplemental_index.tab > NHKCLO_1001/NHKCLO_1001_supplemental_index.tab
grep NHKELO_1001 NHxxLO_1999/NHxxLO_1999_supplemental_index.tab > NHKELO_1001/NHKELO_1001_supplemental_index.tab
grep NHK2LO_1001 NHxxLO_1999/NHxxLO_1999_supplemental_index.tab > NHK2LO_1001/NHK2LO_1001_supplemental_index.tab

grep NHLALO_2001 NHxxLO_2999/NHxxLO_2999_supplemental_index.tab > NHLALO_2001/NHLALO_2001_supplemental_index.tab
grep NHJULO_2001 NHxxLO_2999/NHxxLO_2999_supplemental_index.tab > NHJULO_2001/NHJULO_2001_supplemental_index.tab
grep NHPCLO_2001 NHxxLO_2999/NHxxLO_2999_supplemental_index.tab > NHPCLO_2001/NHPCLO_2001_supplemental_index.tab
grep NHPELO_2001 NHxxLO_2999/NHxxLO_2999_supplemental_index.tab > NHPELO_2001/NHPELO_2001_supplemental_index.tab
grep NHKCLO_2001 NHxxLO_2999/NHxxLO_2999_supplemental_index.tab > NHKCLO_2001/NHKCLO_2001_supplemental_index.tab
grep NHKELO_2001 NHxxLO_2999/NHxxLO_2999_supplemental_index.tab > NHKELO_2001/NHKELO_2001_supplemental_index.tab
grep NHK2LO_2001 NHxxLO_2999/NHxxLO_2999_supplemental_index.tab > NHK2LO_2001/NHK2LO_2001_supplemental_index.tab

grep NHLALO_1001 NHxxLO_1999/NHxxLO_1999_inventory.csv > NHLALO_1001/NHLALO_1001_inventory.csv
grep NHJULO_1001 NHxxLO_1999/NHxxLO_1999_inventory.csv > NHJULO_1001/NHJULO_1001_inventory.csv
grep NHPCLO_1001 NHxxLO_1999/NHxxLO_1999_inventory.csv > NHPCLO_1001/NHPCLO_1001_inventory.csv
grep NHPELO_1001 NHxxLO_1999/NHxxLO_1999_inventory.csv > NHPELO_1001/NHPELO_1001_inventory.csv
grep NHKCLO_1001 NHxxLO_1999/NHxxLO_1999_inventory.csv > NHKCLO_1001/NHKCLO_1001_inventory.csv
grep NHKELO_1001 NHxxLO_1999/NHxxLO_1999_inventory.csv > NHKELO_1001/NHKELO_1001_inventory.csv
grep NHK2LO_1001 NHxxLO_1999/NHxxLO_1999_inventory.csv > NHK2LO_1001/NHK2LO_1001_inventory.csv

grep NHLALO_2001 NHxxLO_2999/NHxxLO_2999_inventory.csv > NHLALO_2001/NHLALO_2001_inventory.csv
grep NHJULO_2001 NHxxLO_2999/NHxxLO_2999_inventory.csv > NHJULO_2001/NHJULO_2001_inventory.csv
grep NHPCLO_2001 NHxxLO_2999/NHxxLO_2999_inventory.csv > NHPCLO_2001/NHPCLO_2001_inventory.csv
grep NHPELO_2001 NHxxLO_2999/NHxxLO_2999_inventory.csv > NHPELO_2001/NHPELO_2001_inventory.csv
grep NHKCLO_2001 NHxxLO_2999/NHxxLO_2999_inventory.csv > NHKCLO_2001/NHKCLO_2001_inventory.csv
grep NHKELO_2001 NHxxLO_2999/NHxxLO_2999_inventory.csv > NHKELO_2001/NHKELO_2001_inventory.csv
grep NHK2LO_2001 NHxxLO_2999/NHxxLO_2999_inventory.csv > NHK2LO_2001/NHK2LO_2001_inventory.csv

cat NHLALO_1001/NH????_????_inventory.csv \
    NHJULO_1001/NH????_????_inventory.csv \
    NHPCLO_1001/NH????_????_inventory.csv \
    NHPELO_1001/NH????_????_inventory.csv \
  > NHxxLO_1999/NHxxLO_1999_inventory.csv

cat NHLALO_2001/NH????_????_inventory.csv \
    NHJULO_2001/NH????_????_inventory.csv \
    NHPCLO_2001/NH????_????_inventory.csv \
    NHPELO_2001/NH????_????_inventory.csv \
  > NHxxLO_2999/NHxxLO_2999_inventory.csv

cat NHLALO_1001/NH????_????_jupiter_summary.tab \
    NHJULO_1001/NH????_????_jupiter_summary.tab \
  > NHxxLO_1999/NHxxLO_1999_jupiter_summary.tab

cat NHLALO_2001/NH????_????_jupiter_summary.tab \
    NHJULO_2001/NH????_????_jupiter_summary.tab \
  > NHxxLO_2999/NHxxLO_2999_jupiter_summary.tab

cat NHPCLO_1001/NH????_????_pluto_summary.tab \
    NHPELO_1001/NH????_????_pluto_summary.tab \
  > NHxxLO_1999/NHxxLO_1999_pluto_summary.tab

cat NHPCLO_2001/NH????_????_pluto_summary.tab \
    NHPELO_2001/NH????_????_pluto_summary.tab \
  > NHxxLO_2999/NHxxLO_2999_pluto_summary.tab

cat NHPCLO_1001/NH????_????_charon_summary.tab \
    NHPELO_1001/NH????_????_charon_summary.tab \
  > NHxxLO_1999/NHxxLO_1999_charon_summary.tab

cat NHPCLO_2001/NH????_????_charon_summary.tab \
    NHPELO_2001/NH????_????_charon_summary.tab \
  > NHxxLO_2999/NHxxLO_2999_charon_summary.tab

cat NHLALO_1001/NH????_????_moon_summary.tab \
    NHJULO_1001/NH????_????_moon_summary.tab \
    NHPCLO_1001/NH????_????_moon_summary.tab \
    NHPELO_1001/NH????_????_moon_summary.tab \
  > NHxxLO_1999/NHxxLO_1999_moon_summary.tab

cat NHLALO_2001/NH????_????_moon_summary.tab \
    NHJULO_2001/NH????_????_moon_summary.tab \
    NHPCLO_2001/NH????_????_moon_summary.tab \
    NHPELO_2001/NH????_????_moon_summary.tab \
  > NHxxLO_2999/NHxxLO_2999_moon_summary.tab

cat NHLALO_1001/NH????_????_ring_summary.tab \
    NHJULO_1001/NH????_????_ring_summary.tab \
    NHPCLO_1001/NH????_????_ring_summary.tab \
    NHPELO_1001/NH????_????_ring_summary.tab \
  > NHxxLO_1999/NHxxLO_1999_ring_summary.tab

cat NHLALO_2001/NH????_????_ring_summary.tab \
    NHJULO_2001/NH????_????_ring_summary.tab \
    NHPCLO_2001/NH????_????_ring_summary.tab \
    NHPELO_2001/NH????_????_ring_summary.tab \
  > NHxxLO_2999/NHxxLO_2999_ring_summary.tab

