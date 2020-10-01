import numpy as np
import sys, os
from vims2pds4 import read_pds4
from VERSIONS_WITH_DIFFERENT_DATA import VERSIONS_WITH_DIFFERENT_DATA

PREFIX = '/Volumes/Migration2/COVIMS_0xxx/'

LAST_FILEPATHS = {}
for (pds4_filename, version, pds3_filepath) in VERSIONS_WITH_DIFFERENT_DATA:
    if '-v' in pds4_filename: continue
    LAST_FILEPATHS[pds4_filename] = pds3_filepath

prev_shortname = ''
for (pds4_filename, version, pds3_filepath) in VERSIONS_WITH_DIFFERENT_DATA:
    shortname = pds4_filename.replace('-v1','')
    shortname = shortname.replace('-v2','')
    shortname = shortname.replace('-v3','')

    if shortname == pds4_filename: continue

    (header0, header_recs0, history0, core0,
     splane0, bplane0, corner0, padding0) = read_pds4(PREFIX + pds3_filepath)
#     recs0 = [rec.rstrip() for rec in header_recs0 + history0.split('\r\n')]

    if shortname != prev_shortname:
        (header1, header_recs1, history1, core1,
         splane1, bplane1, corner1, padding1) = read_pds4(PREFIX + LAST_FILEPATHS[shortname])
#         recs1 = [rec.rstrip() for rec in header_recs1 + history1.split('\r\n')]
        prev_shortname = shortname

    print ('# *** ' + pds4_filename)

#     for rec in header_recs0:
#         if '  SOFTWARE_VERSION_ID' in rec:
#             print ('old: ' + rec)
#             break
# 
#     for rec in header_recs1:
#         if '  SOFTWARE_VERSION_ID' in rec:
#             print ('new: ' + rec)
#             break

#     matched_lines = set()
#     for rec in recs0:
#         if rec in recs1:
#             matched_lines.add(rec)
# 
#     for rec in recs0:
#         if rec not in matched_lines:
#             print ('old: ' + rec)
# 
#     for rec in recs1:
#         if rec not in matched_lines:
#             print ('new: ' + rec)

    for (name, array0, array1) in [('core', core0, core1),
                                   ('splane', splane0, splane1),
                                   ('bplane', bplane0, bplane1),
                                   ('corner', corner0, corner1)]:
        test = (array0 == array1)
        mask0 = (array0 > -4095)
        mask1 = (array1 > -4095)
        if np.all(test):
            continue
        elif np.all(test[mask0]):
            print('#     ' + name + '0 has extra nulls')
        elif np.all(test[mask1]):
            print('#     ' + name + '1 has extra nulls')
        else:
            print('#     ' + name + 's differ')

    if np.any(padding1 != padding0) : print ('#     padding differs')

# *** 1405674718-v1.qub
#     cores differ
#     splanes differ
#     bplane1 has extra nulls
#     corners differ
# *** 1405674718-v2.qub
#     cores differ
#     splanes differ
#     bplane1 has extra nulls
#     corners differ
# *** 1405674832-v1.qub
#     cores differ
#     splanes differ
# *** 1405674832-v2.qub
#     cores differ
#     splanes differ
# *** 1405674946-v1.qub
#     cores differ
#     splanes differ
# *** 1405674946-v2.qub
#     cores differ
#     splanes differ
# *** 1405675060-v1.qub
#     cores differ
#     splanes differ
# *** 1405675060-v2.qub
#     cores differ
#     splanes differ
# *** 1405675174-v1.qub
#     cores differ
#     splanes differ
# *** 1405675174-v2.qub
#     cores differ
#     splanes differ
# *** 1405675287-v1.qub
#     cores differ
#     splanes differ
# *** 1405675287-v2.qub
#     cores differ
#     splanes differ
# *** 1405675401-v1.qub
#     cores differ
#     splanes differ
# *** 1405675401-v2.qub
#     cores differ
#     splanes differ
# *** 1405675515-v1.qub
#     cores differ
#     splanes differ
# *** 1405675515-v2.qub
#     cores differ
#     splanes differ
# *** 1405675629-v1.qub
#     cores differ
#     splanes differ
# *** 1405675629-v2.qub
#     cores differ
#     splanes differ
# *** 1405675743-v1.qub
#     cores differ
#     splanes differ
# *** 1405675743-v2.qub
#     cores differ
#     splanes differ
# *** 1405675857-v1.qub
#     cores differ
#     splanes differ
# *** 1405675857-v2.qub
#     cores differ
#     splanes differ
# *** 1405675971-v1.qub
#     cores differ
#     splanes differ
# *** 1405675971-v2.qub
#     cores differ
#     splanes differ
# *** 1405676085-v1.qub
#     cores differ
#     splanes differ
# *** 1405676085-v2.qub
#     cores differ
#     splanes differ
# *** 1405676199-v1.qub
#     cores differ
#     splanes differ
# *** 1405676199-v2.qub
#     cores differ
#     splanes differ
# *** 1405676312-v1.qub
#     cores differ
#     splanes differ
# *** 1405676312-v2.qub
#     cores differ
#     splanes differ
# *** 1405676426-v1.qub
#     cores differ
#     splanes differ
# *** 1405676426-v2.qub
#     cores differ
#     splanes differ
# *** 1405676540-v1.qub
#     cores differ
#     splanes differ
# *** 1405676540-v2.qub
#     cores differ
#     splanes differ
# *** 1405676654-v1.qub
#     cores differ
#     splanes differ
# *** 1405676654-v2.qub
#     cores differ
#     splanes differ
# *** 1405676768-v1.qub
#     cores differ
#     splanes differ
# *** 1405676768-v2.qub
#     cores differ
#     splanes differ
# *** 1405676882-v1.qub
#     cores differ
#     splanes differ
# *** 1405676882-v2.qub
#     cores differ
#     splanes differ
# *** 1405676996-v1.qub
#     cores differ
#     splanes differ
# *** 1405676996-v2.qub
#     cores differ
#     splanes differ
# *** 1405677110-v1.qub
#     cores differ
#     splanes differ
# *** 1405677110-v2.qub
#     cores differ
#     splanes differ
# *** 1405677224-v1.qub
#     cores differ
#     splanes differ
# *** 1405677224-v2.qub
#     cores differ
#     splanes differ
# *** 1405677337-v1.qub
#     cores differ
#     splanes differ
# *** 1405677337-v2.qub
#     cores differ
#     splanes differ
# *** 1405677451-v1.qub
#     cores differ
#     splanes differ
# *** 1405677451-v2.qub
#     cores differ
#     splanes differ
# *** 1405677565-v1.qub
#     cores differ
#     splanes differ
# *** 1405677565-v2.qub
#     cores differ
#     splanes differ
# *** 1405677679-v1.qub
#     cores differ
#     splanes differ
# *** 1405677679-v2.qub
#     cores differ
#     splanes differ
# *** 1405677793-v1.qub
#     cores differ
#     splanes differ
# *** 1405677793-v2.qub
#     cores differ
#     splanes differ
# *** 1405677907-v1.qub
#     cores differ
#     splanes differ
# *** 1405677907-v2.qub
#     cores differ
#     splanes differ
# *** 1405678021-v1.qub
#     cores differ
#     splanes differ
# *** 1405678021-v2.qub
#     cores differ
#     splanes differ
# *** 1405678135-v1.qub
#     cores differ
#     splanes differ
# *** 1405678135-v2.qub
#     cores differ
#     splanes differ
# *** 1405678249-v1.qub
#     cores differ
#     splanes differ
# *** 1405678249-v2.qub
#     cores differ
#     splanes differ
# *** 1405678362-v1.qub
#     cores differ
#     splanes differ
# *** 1405678362-v2.qub
#     cores differ
#     splanes differ
# *** 1405678476-v1.qub
#     cores differ
#     splanes differ
# *** 1405678476-v2.qub
#     cores differ
#     splanes differ
# *** 1405678590-v1.qub
#     cores differ
#     splanes differ
# *** 1405678590-v2.qub
#     cores differ
#     splanes differ
# *** 1405678704-v1.qub
#     cores differ
#     splanes differ
# *** 1405678704-v2.qub
#     cores differ
#     splanes differ
# *** 1405678818-v1.qub
#     cores differ
#     splanes differ
# *** 1405678818-v2.qub
#     cores differ
#     splanes differ
# *** 1405678932-v1.qub
#     cores differ
#     splanes differ
# *** 1405678932-v2.qub
#     cores differ
#     splanes differ
# *** 1465673806-v1.qub
#     core1 has extra nulls
#     splanes differ
#     bplane1 has extra nulls
#     corners differ
# *** 1465680977-v1.qub
#     core1 has extra nulls
#     splanes differ
# *** 1465700253-v1.qub
#     core1 has extra nulls
#     splanes differ
#     bplane1 has extra nulls
#     corners differ
# *** 1465711602-v1.qub
#     core1 has extra nulls
#     splanes differ
#     bplane1 has extra nulls
#     corners differ
# *** 1471676803-v1.qub
#     core1 has extra nulls
#     splanes differ
#     bplane1 has extra nulls
#     corners differ
# *** 1472712701-v1.qub
#     core1 has extra nulls
#     splanes differ
# *** 1472969272-v1.qub
#     core1 has extra nulls
#     splanes differ
# *** 1473199707-v1.qub
#     core1 has extra nulls
#     splanes differ
# *** 1475048593-v1.qub
#     core1 has extra nulls
#     splanes differ
# *** 1476574898-v1.qub
#     core1 has extra nulls
#     splanes differ
# *** 1476944152-v1.qub
#     core1 has extra nulls
#     splanes differ
#     bplane1 has extra nulls
#     corners differ
# *** 1480707723-v1.qub
#     core1 has extra nulls
#     splanes differ
# *** 1484867611-v1.qub
#     core1 has extra nulls
#     splanes differ
# *** 1489039632-v1.qub
#     core1 has extra nulls
#     splanes differ
#     bplane1 has extra nulls
#     corners differ
# *** 1489040393-v1.qub
#     cores differ
#     splanes differ
#     bplane1 has extra nulls
#     corners differ
# *** 1489040893-v1.qub
#     cores differ
#     splanes differ
#     bplane1 has extra nulls
#     corners differ
# *** 1489041542-v1.qub
#     core1 has extra nulls
#     splanes differ
#     bplane1 has extra nulls
#     corners differ
