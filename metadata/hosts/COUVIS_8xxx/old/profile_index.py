import os,sys
import pdsparser
import pdstable

HOLDINGS = '/Volumes/pdsdata-offsite/holdings/'

ROOT = HOLDINGS + 'volumes/COUVIS_8xxx/COUVIS_8001/data/'
INDEX = HOLDINGS + 'metadata/COUVIS_8xxx/COUVIS_8001/COUVIS_8001_profile_index.tab'

f = open(INDEX, 'w', encoding='latin-1')

filenames = os.listdir(ROOT)
for filename in filenames:
    if not filename.endswith('01KM.LBL'): continue

    label = pdsparser.PdsLabel.from_file(ROOT + filename).as_dict()
    reclist = []

    reclist.append('"%-46s"' % ('data/' + filename))
    reclist.append('"%-41s"' % label['PRODUCT_ID'])
    reclist.append('"%-3s"'  % label['ORBIT_NUMBER'])
    reclist.append('"%-21s"' % label['START_TIME'])
    reclist.append('"%-21s"' % label['STOP_TIME'])
    reclist.append('"%1s"'   % label['RING_PROFILE_DIRECTION'][0])
    reclist.append('"%1s"'   % label['PLANETARY_OCCULTATION_FLAG'])
    reclist.append('"%-10s"' % label['STAR_NAME'])
    reclist.append('0.110')
    reclist.append('0.190')
    reclist.append('"%-16s"' % label['SPACECRAFT_CLOCK_START_COUNT'])
    reclist.append('"%-16s"' % label['SPACECRAFT_CLOCK_STOP_COUNT'])
    reclist.append('"%-16s"' % label['RING_EVENT_START_TIME'])
    reclist.append('"%-16s"' % label['RING_EVENT_STOP_TIME'])
    reclist.append('%5.1f'   % label['OBSERVED_RING_ELEVATION'])
    reclist.append('%5.1f'   % label['LIGHT_SOURCE_INCIDENCE_ANGLE'])
    reclist.append('%2d'     % label['RADIAL_RESOLUTION'])
    reclist.append('%9.2f'   % label['MINIMUM_RING_RADIUS'])
    reclist.append('%10.2f'  % label['MAXIMUM_RING_RADIUS'])
    reclist.append('%8.4f'   % label['MINIMUM_RING_LONGITUDE'])
    reclist.append('%8.4f'   % label['MAXIMUM_RING_LONGITUDE'])
    reclist.append('%5.1f'   % label['MINIMUM_OBSERVED_RING_AZIMUTH'])
    reclist.append('%5.1f'   % label['MAXIMUM_OBSERVED_RING_AZIMUTH'])

    rec = ','.join(reclist)
    f.write(rec + '\r\n')

f.close()
