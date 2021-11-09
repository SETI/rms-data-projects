import numpy as np
import sys, os
from vims2pds4 import read_pds4
from VERSIONS_WITH_MATCHING_DATA import VERSIONS_WITH_MATCHING_DATA

PREFIX = '/Volumes/Migration2/COVIMS_0xxx/'

LAST_FILEPATHS = {}
for (pds4_filename, version, pds3_filepath) in VERSIONS_PDS4_VS_PDS3:
    if '-v' in pds4_filename: continue
    LAST_FILEPATHS[pds4_filename] = pds3_filepath

prev_shortname = ''
for (pds4_filename, version, pds3_filepath) in VERSIONS_WITH_MATCHING_DATA:
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

    print ('*** ' + pds4_filename)

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

    if np.any(core1     != core0)    : print ('    core differs')
    if np.any(splane1   != splane0)  : print ('    splane differs')
    if np.any(bplane1   != bplane0)  : print ('    bplane differs')
    if np.any(corner1   != corner0)  : print ('    corner differs')
    if np.any(padding1  != padding0) : print ('    padding differs')

# *** 1405644685-v1.qub
# *** 1405644685-v2.qub
# *** 1405644892-v1.qub
# *** 1405644892-v2.qub
# *** 1405645066-v1.qub
# *** 1405645066-v2.qub
# *** 1405645273-v1.qub
# *** 1405645273-v2.qub
# *** 1405645447-v1.qub
# *** 1405645447-v2.qub
# *** 1405645654-v1.qub
# *** 1405645654-v2.qub
# *** 1405645984-v1.qub
# *** 1405645984-v2.qub
# *** 1405646098-v1.qub
# *** 1405646098-v2.qub
# *** 1405646212-v1.qub
# *** 1405646212-v2.qub
# *** 1405646326-v1.qub
# *** 1405646326-v2.qub
# *** 1405646440-v1.qub
# *** 1405646440-v2.qub
# *** 1405646554-v1.qub
# *** 1405646554-v2.qub
# *** 1405646667-v1.qub
# *** 1405646667-v2.qub
# *** 1405646781-v1.qub
# *** 1405646781-v2.qub
# *** 1405646895-v1.qub
# *** 1405646895-v2.qub
# *** 1405647009-v1.qub
# *** 1405647009-v2.qub
# *** 1405647123-v1.qub
# *** 1405647123-v2.qub
# *** 1405647237-v1.qub
# *** 1405647237-v2.qub
# *** 1405647351-v1.qub
# *** 1405647351-v2.qub
# *** 1405647465-v1.qub
# *** 1405647465-v2.qub
# *** 1405647579-v1.qub
# *** 1405647579-v2.qub
# *** 1405647692-v1.qub
# *** 1405647692-v2.qub
# *** 1405647806-v1.qub
# *** 1405647806-v2.qub
# *** 1405647920-v1.qub
# *** 1405647920-v2.qub
# *** 1405648034-v1.qub
# *** 1405648034-v2.qub
# *** 1405648148-v1.qub
# *** 1405648148-v2.qub
# *** 1405648262-v1.qub
# *** 1405648262-v2.qub
# *** 1405648376-v1.qub
# *** 1405648376-v2.qub
# *** 1405648490-v1.qub
# *** 1405648490-v2.qub
# *** 1405648604-v1.qub
# *** 1405648604-v2.qub
# *** 1405648717-v1.qub
# *** 1405648717-v2.qub
# *** 1405648831-v1.qub
# *** 1405648831-v2.qub
# *** 1405648945-v1.qub
# *** 1405648945-v2.qub
# *** 1405649059-v1.qub
# *** 1405649059-v2.qub
# *** 1405649173-v1.qub
# *** 1405649173-v2.qub
# *** 1405649287-v1.qub
# *** 1405649287-v2.qub
# *** 1405649401-v1.qub
# *** 1405649401-v2.qub
# *** 1405649515-v1.qub
# *** 1405649515-v2.qub
# *** 1405649629-v1.qub
# *** 1405649629-v2.qub
# *** 1405649742-v1.qub
# *** 1405649742-v2.qub
# *** 1405649856-v1.qub
# *** 1405649856-v2.qub
# *** 1405649970-v1.qub
# *** 1405649970-v2.qub
# *** 1405650084-v1.qub
# *** 1405650084-v2.qub
# *** 1405650198-v1.qub
# *** 1405650198-v2.qub
# *** 1405650312-v1.qub
# *** 1405650312-v2.qub
# *** 1405650426-v1.qub
# *** 1405650426-v2.qub
# *** 1405652446-v1.qub
# *** 1405652446-v2.qub
# *** 1405652560-v1.qub
# *** 1405652560-v2.qub
# *** 1405652674-v1.qub
# *** 1405652674-v2.qub
# *** 1405652787-v1.qub
# *** 1405652787-v2.qub
# *** 1405652901-v1.qub
# *** 1405652901-v2.qub
# *** 1405653015-v1.qub
# *** 1405653015-v2.qub
# *** 1405653129-v1.qub
# *** 1405653129-v2.qub
# *** 1405653243-v1.qub
# *** 1405653243-v2.qub
# *** 1405653357-v1.qub
# *** 1405653357-v2.qub
# *** 1405653471-v1.qub
# *** 1405653471-v2.qub
# *** 1405653585-v1.qub
# *** 1405653585-v2.qub
# *** 1405653699-v1.qub
# *** 1405653699-v2.qub
# *** 1405653812-v1.qub
# *** 1405653812-v2.qub
# *** 1405653926-v1.qub
# *** 1405653926-v2.qub
# *** 1405654040-v1.qub
# *** 1405654040-v2.qub
# *** 1405654154-v1.qub
# *** 1405654154-v2.qub
# *** 1405654268-v1.qub
# *** 1405654268-v2.qub
# *** 1405654382-v1.qub
# *** 1405654382-v2.qub
# *** 1405654496-v1.qub
# *** 1405654496-v2.qub
# *** 1405654610-v1.qub
# *** 1405654610-v2.qub
# *** 1405654724-v1.qub
# *** 1405654724-v2.qub
# *** 1405654837-v1.qub
# *** 1405654837-v2.qub
# *** 1405654951-v1.qub
# *** 1405654951-v2.qub
# *** 1405655065-v1.qub
# *** 1405655065-v2.qub
# *** 1405655179-v1.qub
# *** 1405655179-v2.qub
# *** 1405655293-v1.qub
# *** 1405655293-v2.qub
# *** 1405655407-v1.qub
# *** 1405655407-v2.qub
# *** 1405655521-v1.qub
# *** 1405655521-v2.qub
# *** 1405655635-v1.qub
# *** 1405655635-v2.qub
# *** 1405655749-v1.qub
# *** 1405655749-v2.qub
# *** 1405655862-v1.qub
# *** 1405655862-v2.qub
# *** 1405655976-v1.qub
# *** 1405655976-v2.qub
# *** 1405656090-v1.qub
# *** 1405656090-v2.qub
# *** 1405656204-v1.qub
# *** 1405656204-v2.qub
# *** 1405656318-v1.qub
# *** 1405656318-v2.qub
# *** 1405656432-v1.qub
# *** 1405656432-v2.qub
# *** 1405670305-v1.qub
# *** 1405670305-v2.qub
# *** 1405670512-v1.qub
# *** 1405670512-v2.qub
# *** 1405670686-v1.qub
# *** 1405670686-v2.qub
# *** 1405670893-v1.qub
# *** 1405670893-v2.qub
# *** 1405671067-v1.qub
# *** 1405671067-v2.qub
# *** 1405671274-v1.qub
# *** 1405671274-v2.qub
# *** 1405673305-v1.qub
# *** 1405673305-v2.qub
# *** 1405673512-v1.qub
# *** 1405673512-v2.qub
# *** 1405673686-v1.qub
# *** 1405673686-v2.qub
# *** 1405673893-v1.qub
# *** 1405673893-v2.qub
# *** 1405674067-v1.qub
# *** 1405674067-v2.qub
# *** 1405679046-v1.qub
# *** 1405679046-v2.qub
# *** 1405680724-v1.qub
# *** 1405680724-v2.qub
# *** 1405680838-v1.qub
# *** 1405680838-v2.qub
# *** 1405680952-v1.qub
# *** 1405680952-v2.qub
# *** 1405681066-v1.qub
# *** 1405681066-v2.qub
# *** 1405681180-v1.qub
# *** 1405681180-v2.qub
# *** 1405681294-v1.qub
# *** 1405681294-v2.qub
# *** 1405681407-v1.qub
# *** 1405681407-v2.qub
# *** 1405681521-v1.qub
# *** 1405681521-v2.qub
# *** 1405681635-v1.qub
# *** 1405681635-v2.qub
# *** 1405681749-v1.qub
# *** 1405681749-v2.qub
# *** 1405681863-v1.qub
# *** 1405681863-v2.qub
# *** 1405681977-v1.qub
# *** 1405681977-v2.qub
# *** 1405682091-v1.qub
# *** 1405682091-v2.qub
# *** 1405682205-v1.qub
# *** 1405682205-v2.qub
# *** 1405682319-v1.qub
# *** 1405682319-v2.qub
# *** 1405682432-v1.qub
# *** 1405682432-v2.qub
# *** 1405682546-v1.qub
# *** 1405682546-v2.qub
# *** 1405682660-v1.qub
# *** 1405682660-v2.qub
# *** 1405682774-v1.qub
# *** 1405682774-v2.qub
# *** 1405682888-v1.qub
# *** 1405682888-v2.qub
# *** 1405683002-v1.qub
# *** 1405683002-v2.qub
# *** 1405683116-v1.qub
# *** 1405683116-v2.qub
# *** 1405683230-v1.qub
# *** 1405683230-v2.qub
# *** 1405683344-v1.qub
# *** 1405683344-v2.qub
# *** 1405683457-v1.qub
# *** 1405683457-v2.qub
# *** 1405683571-v1.qub
# *** 1405683571-v2.qub
# *** 1405683685-v1.qub
# *** 1405683685-v2.qub
# *** 1405683799-v1.qub
# *** 1405683799-v2.qub
# *** 1405683913-v1.qub
# *** 1405683913-v2.qub
# *** 1405684027-v1.qub
# *** 1405684027-v2.qub
# *** 1405684141-v1.qub
# *** 1405684141-v2.qub
# *** 1405684255-v1.qub
# *** 1405684255-v2.qub
# *** 1405684369-v1.qub
# *** 1405684369-v2.qub
# *** 1405684482-v1.qub
# *** 1405684482-v2.qub
# *** 1405684596-v1.qub
# *** 1405684596-v2.qub
# *** 1405684710-v1.qub
# *** 1405684710-v2.qub
# *** 1405684824-v1.qub
# *** 1405684824-v2.qub
# *** 1405684938-v1.qub
# *** 1405684938-v2.qub
# *** 1405685052-v1.qub
# *** 1405685052-v2.qub
# *** 1405685166-v1.qub
# *** 1405685166-v2.qub
# *** 1405699105-v1.qub
# *** 1405699105-v2.qub
# *** 1405699312-v1.qub
# *** 1405699312-v2.qub
# *** 1405699486-v1.qub
# *** 1405699486-v2.qub
# *** 1405699693-v1.qub
# *** 1405699693-v2.qub
# *** 1405699867-v1.qub
# *** 1405699867-v2.qub
# *** 1405700074-v1.qub
# *** 1405700074-v2.qub
# *** 1405702106-v1.qub
# *** 1405702106-v2.qub
# *** 1405702313-v1.qub
# *** 1405702313-v2.qub
# *** 1405702487-v1.qub
# *** 1405702487-v2.qub
# *** 1405702694-v1.qub
# *** 1405702694-v2.qub
# *** 1405702868-v1.qub
# *** 1405702868-v2.qub
# *** 1405703075-v1.qub
# *** 1405703075-v2.qub
# *** 1405703405-v1.qub
# *** 1405703405-v2.qub
# *** 1405703519-v1.qub
# *** 1405703519-v2.qub
# *** 1405703633-v1.qub
# *** 1405703633-v2.qub
# *** 1405703747-v1.qub
# *** 1405703747-v2.qub
# *** 1405703861-v1.qub
# *** 1405703861-v2.qub
# *** 1405703975-v1.qub
# *** 1405703975-v2.qub
# *** 1405704088-v1.qub
# *** 1405704088-v2.qub
# *** 1405704202-v1.qub
# *** 1405704202-v2.qub
# *** 1405704316-v1.qub
# *** 1405704316-v2.qub
# *** 1405704430-v1.qub
# *** 1405704430-v2.qub
# *** 1405704544-v1.qub
# *** 1405704544-v2.qub
# *** 1405704658-v1.qub
# *** 1405704658-v2.qub
# *** 1405704772-v1.qub
# *** 1405704772-v2.qub
# *** 1405704886-v1.qub
# *** 1405704886-v2.qub
# *** 1405705000-v1.qub
# *** 1405705000-v2.qub
# *** 1405705113-v1.qub
# *** 1405705113-v2.qub
# *** 1405705227-v1.qub
# *** 1405705227-v2.qub
# *** 1405705341-v1.qub
# *** 1405705341-v2.qub
# *** 1405705455-v1.qub
# *** 1405705455-v2.qub
# *** 1405705569-v1.qub
# *** 1405705569-v2.qub
# *** 1405705683-v1.qub
# *** 1405705683-v2.qub
# *** 1405705797-v1.qub
# *** 1405705797-v2.qub
# *** 1405705911-v1.qub
# *** 1405705911-v2.qub
# *** 1405706025-v1.qub
# *** 1405706025-v2.qub
# *** 1405706138-v1.qub
# *** 1405706138-v2.qub
# *** 1405706252-v1.qub
# *** 1405706252-v2.qub
# *** 1405706366-v1.qub
# *** 1405706366-v2.qub
# *** 1405706480-v1.qub
# *** 1405706480-v2.qub
# *** 1405706594-v1.qub
# *** 1405706594-v2.qub
# *** 1405706708-v1.qub
# *** 1405706708-v2.qub
# *** 1405706822-v1.qub
# *** 1405706822-v2.qub
# *** 1405706936-v1.qub
# *** 1405706936-v2.qub
# *** 1405707050-v1.qub
# *** 1405707050-v2.qub
# *** 1405707163-v1.qub
# *** 1405707163-v2.qub
# *** 1405707277-v1.qub
# *** 1405707277-v2.qub
# *** 1405707391-v1.qub
# *** 1405707391-v2.qub
# *** 1405707505-v1.qub
# *** 1405707505-v2.qub
# *** 1405707619-v1.qub
# *** 1405707619-v2.qub
# *** 1405707733-v1.qub
# *** 1405707733-v2.qub
# *** 1405707847-v1.qub
# *** 1405707847-v2.qub
# *** 1405709525-v1.qub
# *** 1405709525-v2.qub
# *** 1405709639-v1.qub
# *** 1405709639-v2.qub
# *** 1405709753-v1.qub
# *** 1405709753-v2.qub
# *** 1405709867-v1.qub
# *** 1405709867-v2.qub
# *** 1405709981-v1.qub
# *** 1405709981-v2.qub
# *** 1405710095-v1.qub
# *** 1405710095-v2.qub
# *** 1405710208-v1.qub
# *** 1405710208-v2.qub
# *** 1405710322-v1.qub
# *** 1405710322-v2.qub
# *** 1405710436-v1.qub
# *** 1405710436-v2.qub
# *** 1405710550-v1.qub
# *** 1405710550-v2.qub
# *** 1405710664-v1.qub
# *** 1405710664-v2.qub
# *** 1405710778-v1.qub
# *** 1405710778-v2.qub
# *** 1405710892-v1.qub
# *** 1405710892-v2.qub
# *** 1405711006-v1.qub
# *** 1405711006-v2.qub
# *** 1405711120-v1.qub
# *** 1405711120-v2.qub
# *** 1405711233-v1.qub
# *** 1405711233-v2.qub
# *** 1405711347-v1.qub
# *** 1405711347-v2.qub
# *** 1405711461-v1.qub
# *** 1405711461-v2.qub
# *** 1405711575-v1.qub
# *** 1405711575-v2.qub
# *** 1405711689-v1.qub
# *** 1405711689-v2.qub
# *** 1405711803-v1.qub
# *** 1405711803-v2.qub
# *** 1405711917-v1.qub
# *** 1405711917-v2.qub
# *** 1405712031-v1.qub
# *** 1405712031-v2.qub
# *** 1405712145-v1.qub
# *** 1405712145-v2.qub
# *** 1405712258-v1.qub
# *** 1405712258-v2.qub
# *** 1405712372-v1.qub
# *** 1405712372-v2.qub
# *** 1405712486-v1.qub
# *** 1405712486-v2.qub
# *** 1405712600-v1.qub
# *** 1405712600-v2.qub
# *** 1405712714-v1.qub
# *** 1405712714-v2.qub
# *** 1405712828-v1.qub
# *** 1405712828-v2.qub
# *** 1405712942-v1.qub
# *** 1405712942-v2.qub
# *** 1405713056-v1.qub
# *** 1405713056-v2.qub
# *** 1405713170-v1.qub
# *** 1405713170-v2.qub
# *** 1405713283-v1.qub
# *** 1405713283-v2.qub
# *** 1405713397-v1.qub
# *** 1405713397-v2.qub
# *** 1405713511-v1.qub
# *** 1405713511-v2.qub
# *** 1405713625-v1.qub
# *** 1405713625-v2.qub
# *** 1405713739-v1.qub
# *** 1405713739-v2.qub
# *** 1405713853-v1.qub
# *** 1405713853-v2.qub
# *** 1405713967-v1.qub
# *** 1405713967-v2.qub
# *** 1405727906-v1.qub
# *** 1405727906-v2.qub
# *** 1405728113-v1.qub
# *** 1405728113-v2.qub
# *** 1405728287-v1.qub
# *** 1405728287-v2.qub
# *** 1405728494-v1.qub
# *** 1405728494-v2.qub
# *** 1405728668-v1.qub
# *** 1405728668-v2.qub
# *** 1405728875-v1.qub
# *** 1405728875-v2.qub
# *** 1405730906-v1.qub
# *** 1405730906-v2.qub
# *** 1405731113-v1.qub
# *** 1405731113-v2.qub
# *** 1405731287-v1.qub
# *** 1405731287-v2.qub
# *** 1405731494-v1.qub
# *** 1405731494-v2.qub
# *** 1405731668-v1.qub
# *** 1405731668-v2.qub
# *** 1405731875-v1.qub
# *** 1405731875-v2.qub
# *** 1405732205-v1.qub
# *** 1405732205-v2.qub
# *** 1405732319-v1.qub
# *** 1405732319-v2.qub
# *** 1405732433-v1.qub
# *** 1405732433-v2.qub
# *** 1405732547-v1.qub
# *** 1405732547-v2.qub
# *** 1405732661-v1.qub
# *** 1405732661-v2.qub
# *** 1405732775-v1.qub
# *** 1405732775-v2.qub
# *** 1405732888-v1.qub
# *** 1405732888-v2.qub
# *** 1405733002-v1.qub
# *** 1405733002-v2.qub
# *** 1405733116-v1.qub
# *** 1405733116-v2.qub
# *** 1405733230-v1.qub
# *** 1405733230-v2.qub
# *** 1405733344-v1.qub
# *** 1405733344-v2.qub
# *** 1405733458-v1.qub
# *** 1405733458-v2.qub
# *** 1405733572-v1.qub
# *** 1405733572-v2.qub
# *** 1405733686-v1.qub
# *** 1405733686-v2.qub
# *** 1405733800-v1.qub
# *** 1405733800-v2.qub
# *** 1405733913-v1.qub
# *** 1405733913-v2.qub
# *** 1405734027-v1.qub
# *** 1405734027-v2.qub
# *** 1405734141-v1.qub
# *** 1405734141-v2.qub
# *** 1405734255-v1.qub
# *** 1405734255-v2.qub
# *** 1405734369-v1.qub
# *** 1405734369-v2.qub
# *** 1405734483-v1.qub
# *** 1405734483-v2.qub
# *** 1405734597-v1.qub
# *** 1405734597-v2.qub
# *** 1405734711-v1.qub
# *** 1405734711-v2.qub
# *** 1405734825-v1.qub
# *** 1405734825-v2.qub
# *** 1405734938-v1.qub
# *** 1405734938-v2.qub
# *** 1405735052-v1.qub
# *** 1405735052-v2.qub
# *** 1405735166-v1.qub
# *** 1405735166-v2.qub
# *** 1405735280-v1.qub
# *** 1405735280-v2.qub
# *** 1405735394-v1.qub
# *** 1405735394-v2.qub
# *** 1405735508-v1.qub
# *** 1405735508-v2.qub
# *** 1405735622-v1.qub
# *** 1405735622-v2.qub
# *** 1405735736-v1.qub
# *** 1405735736-v2.qub
# *** 1405735850-v1.qub
# *** 1405735850-v2.qub
# *** 1405735963-v1.qub
# *** 1405735963-v2.qub
# *** 1405736077-v1.qub
# *** 1405736077-v2.qub
# *** 1405736191-v1.qub
# *** 1405736191-v2.qub
# *** 1405736305-v1.qub
# *** 1405736305-v2.qub
# *** 1405736419-v1.qub
# *** 1405736419-v2.qub
# *** 1405736533-v1.qub
# *** 1405736533-v2.qub
# *** 1405736647-v1.qub
# *** 1405736647-v2.qub
# *** 1405738325-v1.qub
# *** 1405738325-v2.qub
# *** 1405738439-v1.qub
# *** 1405738439-v2.qub
# *** 1405738553-v1.qub
# *** 1405738553-v2.qub
# *** 1405738667-v1.qub
# *** 1405738667-v2.qub
# *** 1405738781-v1.qub
# *** 1405738781-v2.qub
# *** 1405738895-v1.qub
# *** 1405738895-v2.qub
# *** 1405739008-v1.qub
# *** 1405739008-v2.qub
# *** 1405739122-v1.qub
# *** 1405739122-v2.qub
# *** 1405739236-v1.qub
# *** 1405739236-v2.qub
# *** 1405739350-v1.qub
# *** 1405739350-v2.qub
# *** 1405739464-v1.qub
# *** 1405739464-v2.qub
# *** 1405739578-v1.qub
# *** 1405739578-v2.qub
# *** 1405739692-v1.qub
# *** 1405739692-v2.qub
# *** 1405739806-v1.qub
# *** 1405739806-v2.qub
# *** 1405739920-v1.qub
# *** 1405739920-v2.qub
# *** 1405740033-v1.qub
# *** 1405740033-v2.qub
# *** 1405740147-v1.qub
# *** 1405740147-v2.qub
# *** 1405740261-v1.qub
# *** 1405740261-v2.qub
# *** 1405740375-v1.qub
# *** 1405740375-v2.qub
# *** 1405740489-v1.qub
# *** 1405740489-v2.qub
# *** 1405740603-v1.qub
# *** 1405740603-v2.qub
# *** 1405740717-v1.qub
# *** 1405740717-v2.qub
# *** 1405740831-v1.qub
# *** 1405740831-v2.qub
# *** 1405740945-v1.qub
# *** 1405740945-v2.qub
# *** 1405741058-v1.qub
# *** 1405741058-v2.qub
# *** 1405741172-v1.qub
# *** 1405741172-v2.qub
# *** 1405741286-v1.qub
# *** 1405741286-v2.qub
# *** 1405741400-v1.qub
# *** 1405741400-v2.qub
# *** 1405741514-v1.qub
# *** 1405741514-v2.qub
# *** 1405741628-v1.qub
# *** 1405741628-v2.qub
# *** 1405741742-v1.qub
# *** 1405741742-v2.qub
# *** 1405741856-v1.qub
# *** 1405741856-v2.qub
# *** 1405741970-v1.qub
# *** 1405741970-v2.qub
# *** 1405742083-v1.qub
# *** 1405742083-v2.qub
# *** 1405742197-v1.qub
# *** 1405742197-v2.qub
# *** 1405742311-v1.qub
# *** 1405742311-v2.qub
# *** 1405742425-v1.qub
# *** 1405742425-v2.qub
# *** 1405742539-v1.qub
# *** 1405742539-v2.qub
# *** 1405742653-v1.qub
# *** 1405742653-v2.qub
# *** 1405742767-v1.qub
# *** 1405742767-v2.qub
# *** 1405756706-v1.qub
# *** 1405756706-v2.qub
# *** 1405756913-v1.qub
# *** 1405756913-v2.qub
# *** 1405757087-v1.qub
# *** 1405757087-v2.qub
# *** 1405757294-v1.qub
# *** 1405757294-v2.qub
# *** 1405757468-v1.qub
# *** 1405757468-v2.qub
# *** 1405757675-v1.qub
# *** 1405757675-v2.qub
# *** 1405759706-v1.qub
# *** 1405759706-v2.qub
# *** 1405759913-v1.qub
# *** 1405759913-v2.qub
# *** 1405760087-v1.qub
# *** 1405760087-v2.qub
# *** 1405760294-v1.qub
# *** 1405760294-v2.qub
# *** 1405760468-v1.qub
# *** 1405760468-v2.qub
# *** 1405760675-v1.qub
# *** 1405760675-v2.qub
# *** 1405761005-v1.qub
# *** 1405761005-v2.qub
# *** 1405761119-v1.qub
# *** 1405761119-v2.qub
# *** 1405761233-v1.qub
# *** 1405761233-v2.qub
# *** 1405761347-v1.qub
# *** 1405761347-v2.qub
# *** 1405761461-v1.qub
# *** 1405761461-v2.qub
# *** 1405761575-v1.qub
# *** 1405761575-v2.qub
# *** 1405761688-v1.qub
# *** 1405761688-v2.qub
# *** 1405761802-v1.qub
# *** 1405761802-v2.qub
# *** 1405761916-v1.qub
# *** 1405761916-v2.qub
# *** 1405762030-v1.qub
# *** 1405762030-v2.qub
# *** 1405762144-v1.qub
# *** 1405762144-v2.qub
# *** 1405762258-v1.qub
# *** 1405762258-v2.qub
# *** 1405762372-v1.qub
# *** 1405762372-v2.qub
# *** 1405762486-v1.qub
# *** 1405762486-v2.qub
# *** 1405762600-v1.qub
# *** 1405762600-v2.qub
# *** 1405762713-v1.qub
# *** 1405762713-v2.qub
# *** 1405762827-v1.qub
# *** 1405762827-v2.qub
# *** 1405762941-v1.qub
# *** 1405762941-v2.qub
# *** 1405763055-v1.qub
# *** 1405763055-v2.qub
# *** 1405763169-v1.qub
# *** 1405763169-v2.qub
# *** 1405763283-v1.qub
# *** 1405763283-v2.qub
# *** 1405763397-v1.qub
# *** 1405763397-v2.qub
# *** 1405763511-v1.qub
# *** 1405763511-v2.qub
# *** 1405763625-v1.qub
# *** 1405763625-v2.qub
# *** 1405763738-v1.qub
# *** 1405763738-v2.qub
# *** 1413246503-v1.qub
# *** 1431917388-v1.qub
# *** 1431917637-v1.qub
# *** 1432028818-v1.qub
# *** 1444713101-v1.qub
# *** 1467344835_001-v1.qub
# *** 1467344835_002-v1.qub
# *** 1467344835_003-v1.qub
# *** 1467344835_004-v1.qub
# *** 1467344835_005-v1.qub
# *** 1467345081_001-v1.qub
# *** 1467345081_002-v1.qub
# *** 1467345081_003-v1.qub
# *** 1467345081_004-v1.qub
# *** 1467345081_005-v1.qub
# *** 1467345081_006-v1.qub
# *** 1467345081_007-v1.qub
# *** 1467345081_008-v1.qub
# *** 1467345081_009-v1.qub
# *** 1467345081_010-v1.qub
# *** 1467345081_011-v1.qub
# *** 1467345081_012-v1.qub
# *** 1467345081_013-v1.qub
# *** 1467345081_014-v1.qub
# *** 1467345081_015-v1.qub
# *** 1467345081_016-v1.qub
# *** 1467345081_017-v1.qub
# *** 1467345081_018-v1.qub
# *** 1467345081_019-v1.qub
# *** 1467345081_020-v1.qub
# *** 1467345081_021-v1.qub
# *** 1467345081_022-v1.qub
# *** 1467345081_023-v1.qub
# *** 1467345081_024-v1.qub
# *** 1467345081_025-v1.qub
# *** 1467345081_026-v1.qub
# *** 1467345081_027-v1.qub
# *** 1467345081_028-v1.qub
# *** 1467345081_029-v1.qub
# *** 1467345081_030-v1.qub
# *** 1467345081_031-v1.qub
# *** 1467345081_032-v1.qub
# *** 1467345081_033-v1.qub
# *** 1467345081_034-v1.qub
# *** 1467345081_035-v1.qub
# *** 1467345081_036-v1.qub
# *** 1467345081_037-v1.qub
# *** 1467345081_038-v1.qub
# *** 1467345081_039-v1.qub
# *** 1467345081_040-v1.qub
# *** 1467345081_041-v1.qub
# *** 1467345081_042-v1.qub
# *** 1467345081_043-v1.qub
# *** 1467345081_044-v1.qub
# *** 1467345081_045-v1.qub
# *** 1467345081_046-v1.qub
# *** 1467345081_047-v1.qub
# *** 1467345081_048-v1.qub
# *** 1467345081_049-v1.qub
# *** 1467345081_050-v1.qub
# *** 1467345081_051-v1.qub
# *** 1467345081_052-v1.qub
# *** 1467345081_053-v1.qub
# *** 1467345081_054-v1.qub
# *** 1467345081_055-v1.qub
# *** 1467345081_056-v1.qub
# *** 1467345081_057-v1.qub
# *** 1467345081_058-v1.qub
# *** 1467345081_059-v1.qub
# *** 1467345081_060-v1.qub
# *** 1467345081_061-v1.qub
# *** 1467345081_062-v1.qub
# *** 1467345081_063-v1.qub
# *** 1467345081_064-v1.qub
# *** 1467345779_001-v1.qub
# *** 1467345779_002-v1.qub
# *** 1467345779_003-v1.qub
# *** 1467345779_004-v1.qub
# *** 1467345779_005-v1.qub
# *** 1467345779_006-v1.qub
# *** 1467345779_007-v1.qub
# *** 1467345779_008-v1.qub
# *** 1467345779_009-v1.qub
# *** 1467345779_010-v1.qub
# *** 1467345779_011-v1.qub
# *** 1467345779_012-v1.qub
# *** 1467345779_013-v1.qub
# *** 1467345779_014-v1.qub
# *** 1467345779_015-v1.qub
# *** 1467345779_016-v1.qub
# *** 1467345779_017-v1.qub
# *** 1467345779_018-v1.qub
# *** 1467345779_019-v1.qub
# *** 1467345779_020-v1.qub
# *** 1467345779_021-v1.qub
# *** 1467345779_022-v1.qub
# *** 1467345779_023-v1.qub
# *** 1467345779_024-v1.qub
# *** 1467345779_025-v1.qub
# *** 1467345779_026-v1.qub
# *** 1467345779_027-v1.qub
# *** 1467345779_028-v1.qub
# *** 1467345779_029-v1.qub
# *** 1467345779_030-v1.qub
# *** 1467345779_031-v1.qub
# *** 1467345779_032-v1.qub
# *** 1467345779_033-v1.qub
# *** 1467345779_034-v1.qub
# *** 1467345779_035-v1.qub
# *** 1467345779_036-v1.qub
# *** 1467345779_037-v1.qub
# *** 1467345779_038-v1.qub
# *** 1467345779_039-v1.qub
# *** 1467345779_040-v1.qub
# *** 1467345779_041-v1.qub
# *** 1467345779_042-v1.qub
# *** 1467345779_043-v1.qub
# *** 1467345779_044-v1.qub
# *** 1467345779_045-v1.qub
# *** 1467345779_046-v1.qub
# *** 1467345779_047-v1.qub
# *** 1467345779_048-v1.qub
# *** 1467345779_049-v1.qub
# *** 1467345779_050-v1.qub
# *** 1467345779_051-v1.qub
# *** 1467345779_052-v1.qub
# *** 1467345779_053-v1.qub
# *** 1467345779_054-v1.qub
# *** 1467345779_055-v1.qub
# *** 1467345779_056-v1.qub
# *** 1467345779_057-v1.qub
# *** 1467345779_058-v1.qub
# *** 1467345779_059-v1.qub
# *** 1467345779_060-v1.qub
# *** 1467345779_061-v1.qub
# *** 1467345779_062-v1.qub
# *** 1467345779_063-v1.qub
# *** 1467345779_064-v1.qub
# *** 1467346477_001-v1.qub
# *** 1467346477_001-v2.qub
# *** 1467346477_001-v3.qub
# *** 1467346477_002-v1.qub
# *** 1467346477_002-v2.qub
# *** 1467346477_002-v3.qub
# *** 1467346477_003-v1.qub
# *** 1467346477_003-v2.qub
# *** 1467346477_003-v3.qub
# *** 1467346477_004-v1.qub
# *** 1467346477_004-v2.qub
# *** 1467346477_004-v3.qub
# *** 1467346477_005-v1.qub
# *** 1467346477_005-v2.qub
# *** 1467346477_005-v3.qub
# *** 1467346477_006-v1.qub
# *** 1467346477_006-v2.qub
# *** 1467346477_006-v3.qub
# *** 1467346477_007-v1.qub
# *** 1467346477_007-v2.qub
# *** 1467346477_007-v3.qub
# *** 1467346477_008-v1.qub
# *** 1467346477_008-v2.qub
# *** 1467346477_008-v3.qub
# *** 1467346477_009-v1.qub
# *** 1467346477_009-v2.qub
# *** 1467346477_009-v3.qub
# *** 1467346477_010-v1.qub
# *** 1467346477_010-v2.qub
# *** 1467346477_010-v3.qub
# *** 1467346477_011-v1.qub
# *** 1467346477_011-v2.qub
# *** 1467346477_011-v3.qub
# *** 1467346477_012-v1.qub
# *** 1467346477_012-v2.qub
# *** 1467346477_012-v3.qub
# *** 1467346477_013-v1.qub
# *** 1467346477_013-v2.qub
# *** 1467346477_013-v3.qub
# *** 1467346477_014-v1.qub
# *** 1467346477_014-v2.qub
# *** 1467346477_014-v3.qub
# *** 1467346477_015-v1.qub
# *** 1467346477_015-v2.qub
# *** 1467346477_015-v3.qub
# *** 1467346477_016-v1.qub
# *** 1467346477_016-v2.qub
# *** 1467346477_016-v3.qub
# *** 1467346477_017-v1.qub
# *** 1467346477_017-v2.qub
# *** 1467346477_017-v3.qub
# *** 1467346477_018-v1.qub
# *** 1467346477_018-v2.qub
# *** 1467346477_018-v3.qub
# *** 1467346477_019-v1.qub
# *** 1467346477_019-v2.qub
# *** 1467346477_019-v3.qub
# *** 1467346477_020-v1.qub
# *** 1467346477_020-v2.qub
# *** 1467346477_020-v3.qub
# *** 1467346477_021-v1.qub
# *** 1467346477_021-v2.qub
# *** 1467346477_021-v3.qub
# *** 1467346477_022-v1.qub
# *** 1467346477_022-v2.qub
# *** 1467346477_022-v3.qub
# *** 1467347131_001-v1.qub
# *** 1467347131_001-v2.qub
# *** 1467347131_002-v1.qub
# *** 1467347131_002-v2.qub
# *** 1467347131_003-v1.qub
# *** 1467347131_003-v2.qub
# *** 1467347131_004-v1.qub
# *** 1467347131_004-v2.qub
# *** 1467347131_005-v1.qub
# *** 1467347131_005-v2.qub
# *** 1467347131_006-v1.qub
# *** 1467347131_006-v2.qub
# *** 1467347131_007-v1.qub
# *** 1467347131_007-v2.qub
# *** 1467347131_008-v1.qub
# *** 1467347131_008-v2.qub
# *** 1467347131_009-v1.qub
# *** 1467347131_009-v2.qub
# *** 1467347131_010-v1.qub
# *** 1467347131_010-v2.qub
# *** 1467347131_011-v1.qub
# *** 1467347131_011-v2.qub
# *** 1467347131_012-v1.qub
# *** 1467347131_012-v2.qub
# *** 1467347131_013-v1.qub
# *** 1467347131_013-v2.qub
# *** 1467347131_014-v1.qub
# *** 1467347131_014-v2.qub
# *** 1467347131_015-v1.qub
# *** 1467347131_015-v2.qub
# *** 1467347131_016-v1.qub
# *** 1467347131_016-v2.qub
# *** 1467347131_017-v1.qub
# *** 1467347131_017-v2.qub
# *** 1467347131_018-v1.qub
# *** 1467347131_018-v2.qub
# *** 1467347131_019-v1.qub
# *** 1467347131_019-v2.qub
# *** 1467347131_020-v1.qub
# *** 1467347131_020-v2.qub
# *** 1467347131_021-v1.qub
# *** 1467347131_021-v2.qub
# *** 1467347131_022-v1.qub
# *** 1467347131_022-v2.qub
# *** 1467347131_023-v1.qub
# *** 1467347131_023-v2.qub
# *** 1467347131_024-v1.qub
# *** 1467347131_024-v2.qub
# *** 1467347131_025-v1.qub
# *** 1467347131_025-v2.qub
# *** 1467347131_026-v1.qub
# *** 1467347131_026-v2.qub
# *** 1467347131_027-v1.qub
# *** 1467347131_027-v2.qub
# *** 1467347131_028-v1.qub
# *** 1467347131_028-v2.qub
# *** 1467347131_029-v1.qub
# *** 1467347131_029-v2.qub
# *** 1467347131_030-v1.qub
# *** 1467347131_030-v2.qub
# *** 1467347131_031-v1.qub
# *** 1467347131_031-v2.qub
# *** 1467347131_032-v1.qub
# *** 1467347131_032-v2.qub
# *** 1467347131_033-v1.qub
# *** 1467347131_033-v2.qub
# *** 1467347131_034-v1.qub
# *** 1467347131_034-v2.qub
# *** 1467347131_035-v1.qub
# *** 1467347131_035-v2.qub
# *** 1467347131_036-v1.qub
# *** 1467347131_036-v2.qub
# *** 1467347131_037-v1.qub
# *** 1467347131_037-v2.qub
# *** 1467347131_038-v1.qub
# *** 1467347131_038-v2.qub
# *** 1467347131_039-v1.qub
# *** 1467347131_039-v2.qub
# *** 1467347131_040-v1.qub
# *** 1467347131_040-v2.qub
# *** 1467347131_041-v1.qub
# *** 1467347131_041-v2.qub
# *** 1467347131_042-v1.qub
# *** 1467347131_042-v2.qub
# *** 1477473027-v1.qub
# *** 1487124681-v1.qub
# *** 1487124708-v1.qub
# *** 1487124942-v1.qub
# *** 1487124969-v1.qub
# *** 1490874598_001-v1.qub
# *** 1490874654_001-v1.qub
# *** 1490874707_001-v1.qub
# *** 1490874775_001-v1.qub
# *** 1490874823_001-v1.qub
# *** 1490874878_001-v1.qub
# *** 1490874946_001-v1.qub
# *** 1490874999_001-v1.qub
# *** 1490875052_001-v1.qub
# *** 1492259003_001-v1.qub
# *** 1787305664_001-v1.qub
# *** 1787305664_002-v1.qub
# *** 1787305664_003-v1.qub
# *** 1787305664_004-v1.qub
# *** 1787305664_005-v1.qub
# *** 1787305664_006-v1.qub
# *** 1787305664_007-v1.qub
# *** 1787305664_008-v1.qub
# *** 1787305664_009-v1.qub
# *** 1787305664_010-v1.qub
# *** 1787305664_011-v1.qub
# *** 1787305664_012-v1.qub
# *** 1787305664_013-v1.qub
# *** 1787305664_014-v1.qub
# *** 1787305664_015-v1.qub
# *** 1787305664_016-v1.qub
# *** 1787305664_017-v1.qub
# *** 1787305664_018-v1.qub
# *** 1787305664_019-v1.qub
# *** 1787305664_020-v1.qub
# *** 1787305664_021-v1.qub
# *** 1787305664_022-v1.qub
# *** 1787305664_023-v1.qub
# *** 1787305664_024-v1.qub
# *** 1787305664_025-v1.qub
# *** 1787305664_026-v1.qub
# *** 1787305664_027-v1.qub
# *** 1787305664_028-v1.qub
# *** 1787305664_029-v1.qub
# *** 1787305664_030-v1.qub
# *** 1787305664_031-v1.qub
# *** 1787305664_032-v1.qub
# *** 1787305664_033-v1.qub
# *** 1787305664_034-v1.qub
# *** 1787305664_035-v1.qub
# *** 1787305664_036-v1.qub
# *** 1787305664_037-v1.qub
# *** 1787305664_038-v1.qub
# *** 1787305664_039-v1.qub
# *** 1787305664_040-v1.qub
# *** 1787305664_041-v1.qub
# *** 1787305664_042-v1.qub
# *** 1787305664_043-v1.qub
# *** 1787305664_044-v1.qub
# *** 1787305664_045-v1.qub
# *** 1787305664_046-v1.qub
# *** 1787305664_047-v1.qub
# *** 1787305664_048-v1.qub
# *** 1787305664_049-v1.qub
# *** 1787305664_050-v1.qub
# *** 1787305664_051-v1.qub
# *** 1787305664_052-v1.qub
# *** 1787305664_053-v1.qub
# *** 1787305664_054-v1.qub
# *** 1787305664_055-v1.qub
# *** 1787305664_056-v1.qub
# *** 1787305664_057-v1.qub
# *** 1787305664_058-v1.qub
# *** 1787305664_059-v1.qub
# *** 1787305664_060-v1.qub
# *** 1787305664_061-v1.qub
# *** 1787305664_062-v1.qub
# *** 1787305664_063-v1.qub
# *** 1787305664_064-v1.qub
# *** 1787305849_001-v1.qub
# *** 1787305849_002-v1.qub
# *** 1787305849_003-v1.qub
# *** 1787305849_004-v1.qub
# *** 1787305849_005-v1.qub
# *** 1787305849_006-v1.qub
# *** 1787305849_007-v1.qub
# *** 1787305849_008-v1.qub
# *** 1787305849_009-v1.qub
# *** 1787305849_010-v1.qub
# *** 1787305849_011-v1.qub
# *** 1787305849_012-v1.qub
# *** 1787305849_013-v1.qub
# *** 1787305849_014-v1.qub
# *** 1787305849_015-v1.qub
# *** 1787305849_016-v1.qub
# *** 1787305849_017-v1.qub
# *** 1787305849_018-v1.qub
# *** 1787305849_019-v1.qub
# *** 1787305849_020-v1.qub
# *** 1787305849_021-v1.qub
# *** 1787305849_022-v1.qub
# *** 1787305849_023-v1.qub
# *** 1787305849_024-v1.qub
# *** 1787305849_025-v1.qub
# *** 1787305849_026-v1.qub
# *** 1787305849_027-v1.qub
# *** 1787305849_028-v1.qub
# *** 1787305849_029-v1.qub
# *** 1787305849_030-v1.qub
# *** 1787305849_031-v1.qub
# *** 1787305849_032-v1.qub
# *** 1787305849_033-v1.qub
# *** 1787305849_034-v1.qub
# *** 1787305849_035-v1.qub
# *** 1787305849_036-v1.qub
# *** 1787305849_037-v1.qub
# *** 1787305849_038-v1.qub
# *** 1787305849_039-v1.qub
# *** 1787305849_040-v1.qub
# *** 1787305849_041-v1.qub
# *** 1787305849_042-v1.qub
# *** 1787305849_043-v1.qub
# *** 1787305849_044-v1.qub
# *** 1787305849_045-v1.qub
# *** 1787305849_046-v1.qub
# *** 1787305849_047-v1.qub
# *** 1787305849_048-v1.qub
# *** 1787305849_049-v1.qub
# *** 1787305849_050-v1.qub
# *** 1787305849_051-v1.qub
# *** 1787305849_052-v1.qub
# *** 1787305849_053-v1.qub
# *** 1787305849_054-v1.qub
# *** 1787305849_055-v1.qub
# *** 1787305849_056-v1.qub
# *** 1787305849_057-v1.qub
# *** 1787305849_058-v1.qub
# *** 1787305849_059-v1.qub
# *** 1787305849_060-v1.qub
# *** 1787305849_061-v1.qub
# *** 1787305849_062-v1.qub
# *** 1787305849_063-v1.qub
# *** 1787305849_064-v1.qub
# *** 1787306033_001-v1.qub
# *** 1787306033_002-v1.qub
# *** 1787306033_003-v1.qub
# *** 1787306033_004-v1.qub
# *** 1787306033_005-v1.qub
# *** 1787306033_006-v1.qub
# *** 1787306033_007-v1.qub
# *** 1787306033_008-v1.qub
# *** 1787306033_009-v1.qub
# *** 1787306033_010-v1.qub
# *** 1787306033_011-v1.qub
# *** 1787306033_012-v1.qub
# *** 1787306033_013-v1.qub
# *** 1787306033_014-v1.qub
# *** 1787306033_015-v1.qub
# *** 1787306033_016-v1.qub
# *** 1787306033_017-v1.qub
# *** 1787306033_018-v1.qub
# *** 1787306033_019-v1.qub
# *** 1787306033_020-v1.qub
# *** 1787306033_021-v1.qub
# *** 1787306033_022-v1.qub
# *** 1787306033_023-v1.qub
# *** 1787306033_024-v1.qub
# *** 1787306033_025-v1.qub
# *** 1787306033_026-v1.qub
# *** 1787306033_027-v1.qub
# *** 1787306033_028-v1.qub
# *** 1787306033_029-v1.qub
# *** 1787306033_030-v1.qub
# *** 1787306033_031-v1.qub
# *** 1787306033_032-v1.qub
# *** 1787306033_033-v1.qub
# *** 1787306033_034-v1.qub
# *** 1787306033_035-v1.qub
# *** 1787306033_036-v1.qub
# *** 1787306033_037-v1.qub
# *** 1787306033_038-v1.qub
# *** 1787306033_039-v1.qub
# *** 1787306033_040-v1.qub
# *** 1787306033_041-v1.qub
# *** 1787306033_042-v1.qub
# *** 1787306033_043-v1.qub
# *** 1787306033_044-v1.qub
# *** 1787306033_045-v1.qub
# *** 1787306033_046-v1.qub
# *** 1787306033_047-v1.qub
# *** 1787306033_048-v1.qub
# *** 1787306033_049-v1.qub
# *** 1787306033_050-v1.qub
# *** 1787306033_051-v1.qub
# *** 1787306033_052-v1.qub
# *** 1787306033_053-v1.qub
# *** 1787306033_054-v1.qub
# *** 1787306033_055-v1.qub
# *** 1787306033_056-v1.qub
# *** 1787306033_057-v1.qub
# *** 1787306033_058-v1.qub
# *** 1787306033_059-v1.qub
# *** 1787306033_060-v1.qub
# *** 1787306033_061-v1.qub
# *** 1787306033_062-v1.qub
# *** 1787306033_063-v1.qub
# *** 1787306033_064-v1.qub
# *** 1787306217_001-v1.qub
# *** 1787306217_002-v1.qub
# *** 1787306217_003-v1.qub
# *** 1787306217_004-v1.qub
# *** 1787306217_005-v1.qub
# *** 1787306217_006-v1.qub
# *** 1787306217_007-v1.qub
# *** 1787306217_008-v1.qub
# *** 1787306217_009-v1.qub
# *** 1787306217_010-v1.qub
# *** 1787306217_011-v1.qub
# *** 1787306217_012-v1.qub
# *** 1787306217_013-v1.qub
# *** 1787306217_014-v1.qub
# *** 1787306217_015-v1.qub
# *** 1787306217_016-v1.qub
# *** 1787306217_017-v1.qub
# *** 1787306217_018-v1.qub
# *** 1787306217_019-v1.qub
# *** 1787306217_020-v1.qub
# *** 1787306217_021-v1.qub
# *** 1787306217_022-v1.qub
# *** 1787306217_023-v1.qub
# *** 1787306217_024-v1.qub
# *** 1787306217_025-v1.qub
# *** 1787306217_026-v1.qub
# *** 1787306217_027-v1.qub
# *** 1787306217_028-v1.qub
# *** 1787306217_029-v1.qub
# *** 1787306217_030-v1.qub
# *** 1787306217_031-v1.qub
# *** 1787306217_032-v1.qub
# *** 1787306217_033-v1.qub
# *** 1787306217_034-v1.qub
# *** 1787306217_035-v1.qub
# *** 1787306217_036-v1.qub
# *** 1787306217_037-v1.qub
# *** 1787306217_038-v1.qub
# *** 1787306217_039-v1.qub
# *** 1787306217_040-v1.qub
# *** 1787306217_041-v1.qub
# *** 1787306217_042-v1.qub
# *** 1787306217_043-v1.qub
# *** 1787306217_044-v1.qub
# *** 1787306217_045-v1.qub
# *** 1787306217_046-v1.qub
# *** 1787306217_047-v1.qub
# *** 1787306217_048-v1.qub
# *** 1787306217_049-v1.qub
# *** 1787306217_050-v1.qub
# *** 1787306217_051-v1.qub
# *** 1787306217_052-v1.qub
# *** 1787306217_053-v1.qub
# *** 1787306217_054-v1.qub
# *** 1787306217_055-v1.qub
# *** 1787306217_056-v1.qub
# *** 1787306217_057-v1.qub
# *** 1787306217_058-v1.qub
# *** 1787306217_059-v1.qub
# *** 1787306217_060-v1.qub
# *** 1787306217_061-v1.qub
# *** 1787306217_062-v1.qub
# *** 1787306217_063-v1.qub
# *** 1787306217_064-v1.qub
# *** 1787306401_001-v1.qub
# *** 1787306401_002-v1.qub
# *** 1787306401_003-v1.qub
# *** 1787306401_004-v1.qub
# *** 1787306401_005-v1.qub
# *** 1787306401_006-v1.qub
# *** 1787306401_007-v1.qub
# *** 1787306401_008-v1.qub
# *** 1787306401_009-v1.qub
# *** 1787306401_010-v1.qub
# *** 1787306401_011-v1.qub
# *** 1787306401_012-v1.qub
# *** 1787306401_013-v1.qub
# *** 1787306401_014-v1.qub
# *** 1787306401_015-v1.qub
# *** 1787306401_016-v1.qub
# *** 1787306401_017-v1.qub
# *** 1787306401_018-v1.qub
# *** 1787306401_019-v1.qub
# *** 1787306401_020-v1.qub
# *** 1787306401_021-v1.qub
# *** 1787306401_022-v1.qub
# *** 1787306401_023-v1.qub
# *** 1787306401_024-v1.qub
# *** 1787306401_025-v1.qub
# *** 1787306401_026-v1.qub
# *** 1787306401_027-v1.qub
# *** 1787306401_028-v1.qub
# *** 1787306401_029-v1.qub
# *** 1787306401_030-v1.qub
# *** 1787306401_031-v1.qub
# *** 1787306401_032-v1.qub
# *** 1787306401_033-v1.qub
# *** 1787306401_034-v1.qub
# *** 1787306401_035-v1.qub
# *** 1787306401_036-v1.qub
# *** 1787306401_037-v1.qub
# *** 1787306401_038-v1.qub
# *** 1787306401_039-v1.qub
# *** 1787306401_040-v1.qub
# *** 1787306401_041-v1.qub
# *** 1787306401_042-v1.qub
# *** 1787306401_043-v1.qub
# *** 1787306401_044-v1.qub
# *** 1787306401_045-v1.qub
# *** 1787306401_046-v1.qub
# *** 1787306401_047-v1.qub
# *** 1787306401_048-v1.qub
# *** 1787306401_049-v1.qub
# *** 1787306401_050-v1.qub
# *** 1787306401_051-v1.qub
# *** 1787306401_052-v1.qub
# *** 1787306401_053-v1.qub
# *** 1787306401_054-v1.qub
# *** 1787306401_055-v1.qub
# *** 1787306401_056-v1.qub
# *** 1787306401_057-v1.qub
# *** 1787306401_058-v1.qub
# *** 1787306401_059-v1.qub
# *** 1787306401_060-v1.qub
# *** 1787306401_061-v1.qub
# *** 1787306401_062-v1.qub
# *** 1787306401_063-v1.qub
# *** 1787306401_064-v1.qub
# *** 1787306586_001-v1.qub
# *** 1787306586_002-v1.qub
# *** 1787306586_003-v1.qub
# *** 1787306586_004-v1.qub
# *** 1787306586_005-v1.qub
# *** 1787306586_006-v1.qub
# *** 1787306586_007-v1.qub
# *** 1787306586_008-v1.qub
# *** 1787306586_009-v1.qub
# *** 1787306586_010-v1.qub
# *** 1787306586_011-v1.qub
# *** 1787306586_012-v1.qub
# *** 1787306586_013-v1.qub
# *** 1787306586_014-v1.qub
# *** 1787306586_015-v1.qub
# *** 1787306586_016-v1.qub
# *** 1787306586_017-v1.qub
# *** 1787306586_018-v1.qub
# *** 1787306586_019-v1.qub
# *** 1787306586_020-v1.qub
# *** 1787306586_021-v1.qub
# *** 1787306586_022-v1.qub
# *** 1787306586_023-v1.qub
# *** 1787306586_024-v1.qub
# *** 1787306586_025-v1.qub
# *** 1787306586_026-v1.qub
# *** 1787306586_027-v1.qub
# *** 1787306586_028-v1.qub
# *** 1787306586_029-v1.qub
# *** 1787306586_030-v1.qub
# *** 1787306586_031-v1.qub
# *** 1787306586_032-v1.qub
# *** 1787306586_033-v1.qub
# *** 1787306586_034-v1.qub
# *** 1787306586_035-v1.qub
# *** 1787306586_036-v1.qub
# *** 1787306586_037-v1.qub
# *** 1787306586_038-v1.qub
# *** 1787306586_039-v1.qub
# *** 1787306586_040-v1.qub
# *** 1787306586_041-v1.qub
# *** 1787306586_042-v1.qub
# *** 1787306586_043-v1.qub
# *** 1787306586_044-v1.qub
# *** 1787306586_045-v1.qub
# *** 1787306586_046-v1.qub
# *** 1787306586_047-v1.qub
# *** 1787306586_048-v1.qub
# *** 1787306586_049-v1.qub
# *** 1787306586_050-v1.qub
# *** 1787306586_051-v1.qub
# *** 1787306586_052-v1.qub
# *** 1787306586_053-v1.qub
# *** 1787306586_054-v1.qub
# *** 1787306586_055-v1.qub
# *** 1787306586_056-v1.qub
# *** 1787306586_057-v1.qub
# *** 1787306586_058-v1.qub
# *** 1787306586_059-v1.qub
# *** 1787306586_060-v1.qub
# *** 1787306586_061-v1.qub
# *** 1787306586_062-v1.qub
# *** 1787306586_063-v1.qub
# *** 1787306586_064-v1.qub
# *** 1787306770_001-v1.qub
# *** 1787306770_002-v1.qub
# *** 1787306770_003-v1.qub
# *** 1787306770_004-v1.qub
# *** 1787306770_005-v1.qub
# *** 1787306770_006-v1.qub
# *** 1787306770_007-v1.qub
# *** 1787306770_008-v1.qub
# *** 1787306770_009-v1.qub
# *** 1787306770_010-v1.qub
# *** 1787306770_011-v1.qub
# *** 1787306770_012-v1.qub
# *** 1787306770_013-v1.qub
# *** 1787306770_014-v1.qub
# *** 1787306770_015-v1.qub
# *** 1787306770_016-v1.qub
# *** 1787306770_017-v1.qub
# *** 1787306770_018-v1.qub
# *** 1787306770_019-v1.qub
# *** 1787306770_020-v1.qub
# *** 1787306770_021-v1.qub
# *** 1787306770_022-v1.qub
# *** 1787306770_023-v1.qub
# *** 1787306770_024-v1.qub
# *** 1787306770_025-v1.qub
# *** 1787306770_026-v1.qub
# *** 1787306770_027-v1.qub
# *** 1787306770_028-v1.qub
# *** 1787306770_029-v1.qub
# *** 1787306770_030-v1.qub
# *** 1787306770_031-v1.qub
# *** 1787306770_032-v1.qub
# *** 1787306770_033-v1.qub
# *** 1787306770_034-v1.qub
# *** 1787306770_035-v1.qub
# *** 1787306770_036-v1.qub
# *** 1787306770_037-v1.qub
# *** 1787306770_038-v1.qub
# *** 1787306770_039-v1.qub
# *** 1787306770_040-v1.qub
# *** 1787306770_041-v1.qub
# *** 1787306770_042-v1.qub
# *** 1787306770_043-v1.qub
# *** 1787306770_044-v1.qub
# *** 1825945979-v1.qub