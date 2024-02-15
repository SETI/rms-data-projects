import datetime
import numpy as np

SPACECRAFT_CLOCK_START_COUNT   =  0
MISSION_NAME                   =  1
INSTRUMENT_ID                  =  2
DATA_SET_ID                    =  3
IMAGE_ID                       =  4
OBSERVATION_ID                 =  5
PRODUCT_TYPE                   =  6
TARGET_NAME                    =  7
IMAGE_TIME                     =  8
FILTER_NAME                    =  9
FILTER_NUMBER                  = 10
EXPOSURE_DURATION              = 11
GAIN_MODE_ID                   = 12
FRAME_DURATION                 = 13
OBSTRUCTION_ID                 = 14
ORBIT_NUMBER                   = 15
NTV_TIME_FROM_CLOSEST_APPROACH = 16
NTV_SAT_TIME_FROM_CLOSEST_APR  = 17
PHASE_ANGLE                    = 18
EMISSION_ANGLE                 = 19
INCIDENCE_ANGLE                = 20
LOCAL_HOUR_ANGLE               = 21
TWIST_ANGLE                    = 22
CONE_ANGLE                     = 23
RIGHT_ASCENSION                = 24
DECLINATION                    = 25
NORTH_AZIMUTH                  = 26
SMEAR_AZIMUTH                  = 27
SMEAR_MAGNITUDE                = 28
HORIZONTAL_PIXEL_SCALE         = 29
VERTICAL_PIXEL_SCALE           = 30
SLANT_DISTANCE                 = 31
LIGHT_SOURCE_LATITUDE          = 32
LIGHT_SOURCE_LONGITUDE         = 33
TARGET_CENTER_DISTANCE         = 34
CENTRAL_BODY_DISTANCE          = 35
SUB_SPACECRAFT_LATITUDE        = 36
SUB_SPACECRAFT_LONGITUDE       = 37
SUB_SOLAR_AZIMUTH              = 38
SUB_SOLAR_LATITUDE             = 39
SUB_SOLAR_LONGITUDE            = 40
SOLAR_DISTANCE                 = 41
SUB_SPACECRAFT_LINE            = 42
SUB_SPACECRAFT_LINE_SAMPLE     = 43
CENTER_RING_RADIUS             = 44
VOLUME_ID                      = 45
FILE_SPECIFICATION_NAME        = 46
COMPRESSION_TYPE               = 47
ENCODING_MIN_COMPRESSION_RATIO = 48
ENCODING_MAX_COMPRESSION_RATIO = 49
ENCODING_COMPRESSION_RATIO     = 50
PROCESSING_HISTORY_TEXT        = 51

FILEPATH = '/Volumes/pdsdata-mark/holdings/metadata/GO_0xxx/GO_0016/GO_0016_index.tab'

with open(FILEPATH) as f:
    recs = f.readlines()

recs = [rec for rec in recs if 'SL9/' in rec]

rows = []
for rec in recs:
    parts = rec.rstrip().split(',')
    parts[PROCESSING_HISTORY_TEXT] = ','.join(parts[PROCESSING_HISTORY_TEXT:])
    parts = parts[:PROCESSING_HISTORY_TEXT+1]

#     if parts[EXPOSURE_DURATION] == '    8.33':
#         parts[EXPOSURE_DURATION] ='   8.333'

    rows.append(parts)

# Group items by image and then by column
new_rows = []
filespec = ''
cols = len(rows[0])
for row in rows:
    if filespec != row[FILE_SPECIFICATION_NAME]:
        merged = []
        for k in range(cols):
            merged.append([])

        new_rows.append(merged)
        filespec = row[FILE_SPECIFICATION_NAME]

    merged = new_rows[-1]
    for k in range(cols):
        merged[k].append(row[k])

# Omit "UNKs" unless they are all UNKs
for row in new_rows:
    for k,values in enumerate(row):
        selected = [v for v in values if not 'UNK' in v and not '-99' in v]
        if selected:
            row[k] = selected

# Merge values...
out_recs = []
for row in new_rows:
    columns = []
    new_columns = []
    for k,values in enumerate(row):

        if k in (SPACECRAFT_CLOCK_START_COUNT,
                 IMAGE_ID,
                 IMAGE_TIME):
            columns.append(min(values))
            new_columns.append(max(values))

        elif k == NTV_TIME_FROM_CLOSEST_APPROACH: # negative sorts backward!
            columns.append(max(values))
            new_columns.append(min(values))

        elif values[0][0] == '"':
            unique = list(set(values))
            if len(unique) == 1:
                columns.append(values[0])
            elif len(unique) > 2:
                print('too many unique strings',
                      row[FILE_SPECIFICATION_NAME][0], k, values)
                columns.append(values[0])
            else:       # one of two strings can be unique; use the other
                counts = [sum([v == u for v in values]) for u in unique]
                if counts[0] == 1:
                    columns.append(unique[1])
                elif counts[1] == 1:
                    columns.append(unique[0])
                else:
                    print('too many unique strings',
                          row[FILE_SPECIFICATION_NAME][0], k, values)
                    columns.append(values[0])

        elif '-99' in values[0]:
            columns.append(values[0])

        elif '.' in values[0]:
            # deal with weird exposure durations
            values = [('   8.333' if v == '    8.33' else v) for v in values]
            width = len(values[0])
            (mantissa, _, exp) = values[0].partition('e')
            (before, _, after) = mantissa.partition('.')
            fmt = f'%{width}.{len(after)}' + ('e' if exp else 'f')

            floats = [float(v) for v in values]
            floats = [(8.333 if v == 8.33 else v) for v in floats] # weird texp
            columns.append(fmt % np.mean(floats))

        else:
            ints = [int(v) for v in values]
            ints.sort()
            if ints[0] != ints[-1]:
                print('int value is not unique',
                      row[FILE_SPECIFICATION_NAME][0], k, ints)
            columns.append(values[0])

    out_recs.append(','.join(columns + new_columns))

outfile = FILEPATH.replace('_index', '_sl9_index')
with open(outfile, 'wb') as f:
    for rec in out_recs:
        f.write(rec.encode('latin-1') + b'\r\n')

