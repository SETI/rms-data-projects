import os,sys
import pdsparser
import pdstable

HOLDINGS = '/Volumes/pdsdata-offsite/holdings/'

ROOT = HOLDINGS + 'volumes/COUVIS_8xxx/COUVIS_8001/data/'
INDEX = HOLDINGS + 'metadata/COUVIS_8xxx/COUVIS_8001/COUVIS_8001_supplemental_index.tab'

RAW_DICTS = pdstable.PdsTable(
    HOLDINGS + 'metadata/COUVIS_0xxx/COUVIS_0999/COUVIS_0999_index.lbl',
    columns = ['FILE_NAME', 'INTEGRATION_DURATION']).dicts_by_row()

DURATIONS_VS_LBL = {os.path.basename(d['FILE_NAME']):d['INTEGRATION_DURATION']
                    for d in RAW_DICTS if 'HSP' in d['FILE_NAME']}

SUPP_DICTS = pdstable.PdsTable(
    HOLDINGS + 'metadata/COUVIS_0xxx/COUVIS_0999/COUVIS_0999_supplemental_index.lbl',
    columns = ['FILE_SPECIFICATION_NAME', 'OBSERVATION_ID']).dicts_by_row()

DURATIONS_VS_OBSID = {}
for d in SUPP_DICTS:
    lbl = os.path.basename(d['FILE_SPECIFICATION_NAME'])
    if 'HSP' not in lbl:
        continue

    obsid = d['OBSERVATION_ID']
    duration = DURATIONS_VS_LBL[lbl]

    if obsid in DURATIONS_VS_OBSID:
        DURATIONS_VS_OBSID[obsid].append(duration)
    else:
        DURATIONS_VS_OBSID[obsid] = [duration]

f = open(INDEX, 'w', encoding='latin-1')

filenames = os.listdir(ROOT)
for filename in filenames:
    if not filename.endswith('.LBL'): continue

    label = pdsparser.PdsLabel.from_file(ROOT + filename).as_dict()
    reclist = []

    obs_ids = label['OBSERVATION_ID'].strip()
    obs_id_list = obs_ids.split(',')
    obs_id_list.sort()
    obs_id = obs_id_list[0]

    if obs_id in DURATIONS_VS_OBSID:
        durations = DURATIONS_VS_OBSID[obs_id]
        durations.sort()
        if durations[0] != durations[-1]:
            print('Ambiguous duration:', obs_id, durations, filename)
    else:
        print('Missing OBSID', obs_id, filename)
        durations = [1.]

    reclist.append('"COUVIS_8001"')
    reclist.append('"%-50s"' % ('data/' + filename))
    reclist.append('"%-21s"' % label['START_TIME'])
    reclist.append('"%-21s"' % label['STOP_TIME'])
    reclist.append('"%-16s"' % label['SPACECRAFT_CLOCK_START_COUNT'])
    reclist.append('"%-16s"' % label['SPACECRAFT_CLOCK_STOP_COUNT'])
    reclist.append('%10.6f'  % label['LOWEST_DETECTABLE_OPACITY'])
    reclist.append('%10.6f'  % label['HIGHEST_DETECTABLE_OPACITY'])
    reclist.append('"%-8s"'  % label['DATA_QUALITY_SCORE'])
    reclist.append('"%-32s"' % obs_id_list[0])
    reclist.append('"%-8s"'  % 'N/A')
    reclist.append('"%-6s"'  % 'SQRT_9')
    reclist.append('%10.4f'  % durations[0])
    reclist.append('"%-19s"' % label['PRODUCT_CREATION_TIME'].strip())

    rec = ','.join(reclist)
    f.write(rec + '\r\n')

f.close()
