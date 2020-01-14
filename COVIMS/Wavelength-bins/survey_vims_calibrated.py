import pdsparser
import numpy as np
import os, sys

IR_FLATS = set()
VIS_FLATS = set()
SPECIFIC_ENERGIES = set()
RM_SOLARS = set()

MIN_TIMES = {}
MAX_TIMES = {}
BINS352 = {}

SKIP = 5
count = 0
prev_sclk = ''
for (root, dirs, files) in os.walk('/Volumes/Untitled/uncompressed/'):
  if '/geo' in root: continue
  if '/S' in root: continue
  for basename in files:
    if not basename.endswith('.cub'): continue

    sclk = basename[:13]
    if sclk == prev_sclk: continue
    prev_sclk = sclk

    count += 1
    if count % SKIP != 0:
        continue

    filepath = os.path.join(root, basename)
    label = pdsparser.PdsLabel.from_file(filepath)
    bins = tuple(float(x) for x in (label['QUBE']['BAND_BIN']['BAND_BIN_CENTER']))
    time = str(label['QUBE']['START_TIME'])

    key = bins[-1]
    if len(bins) > 256:
        if key in BINS352:
            if bins != BINS352[key]:
                raise ValueError('value of last bin is not unique!')
        else:
            BINS352[key] = bins

    if key not in MIN_TIMES:
        MIN_TIMES[key] = (time, filepath)
        MAX_TIMES[key] = (time, filepath)
    else:
        if time < MIN_TIMES[key][0]:
            MIN_TIMES[key] = (time, filepath)
        if time > MAX_TIMES[key][0]:
            MAX_TIMES[key] = (time, filepath)

    print(len(MIN_TIMES), filepath)

    IR_FLATS.add(str(label['QUBE']['CALIBRATION']['IR_FLAT']))
    VIS_FLATS.add(str(label['QUBE']['CALIBRATION']['VIS_FLAT']))
    SPECIFIC_ENERGIES.add(str(label['QUBE']['CALIBRATION']['SPECIFIC_ENERGY']))
    RM_SOLARS.add(str(label['QUBE']['CALIBRATION']['RM_SOLAR']))

min_tuples = list(MIN_TIMES.values())
max_tuples = list(MAX_TIMES.values())
min_tuples.sort()
max_tuples.sort()
min_tuples = [(x[0],os.path.basename(x[1])) for x in min_tuples]
max_tuples = [(x[0],os.path.basename(x[1])) for x in max_tuples]

gaps = [(max_tuples[k],min_tuples[k+1]) for k in range(len(min_tuples)-1)]

SKIP = 1
count = 0
for (root, dirs, files) in os.walk('/Volumes/Untitled/uncompressed/'):
  if '/geo' in root: continue
  if '/S' in root: continue
  for basename in files:
    if not basename.endswith('.cub'): continue

    for (below,above) in gaps:
      if basename <= below[1] or basename >= above[1]: continue

      count += 1
      if count % SKIP != 0:
        continue

      filepath = os.path.join(root, basename)
      label = pdsparser.PdsLabel.from_file(filepath)
      bins = tuple(float(x) for x in (label['QUBE']['BAND_BIN']['BAND_BIN_CENTER']))
      time = str(label['QUBE']['START_TIME'])
      key = bins[-1]
      print(time, key, filepath)

      if time < MIN_TIMES[key][0]:
            MIN_TIMES[key] = (time, filepath)
      if time > MAX_TIMES[key][0]:
            MAX_TIMES[key] = (time, filepath)

min_tuples = list(MIN_TIMES.values())
max_tuples = list(MAX_TIMES.values())
min_tuples.sort()
max_tuples.sort()
min_tuples = [(x[0],os.path.basename(x[1])) for x in min_tuples]
max_tuples = [(x[0],os.path.basename(x[1])) for x in max_tuples]

gaps = [(max_tuples[k],min_tuples[k+1]) for k in range(len(min_tuples)-1)]

SKIP = 1
count = 0
for (root, dirs, files) in os.walk('/Volumes/Untitled/uncompressed/'):
  if '/geo' in root: continue
  if '/S' in root: continue
  for basename in files:
    if not basename.endswith('.cub'): continue

    for (below,above) in gaps:
      if basename <= below[1] or basename >= above[1]: continue

      count += 1
      if count % SKIP != 0:
        continue

      filepath = os.path.join(root, basename)
      label = pdsparser.PdsLabel.from_file(filepath)
      bins = tuple(float(x) for x in (label['QUBE']['BAND_BIN']['BAND_BIN_CENTER']))
      time = str(label['QUBE']['START_TIME'])
      key = bins[-1]
      print(time, key, filepath)

      if time < MIN_TIMES[key][0]:
            MIN_TIMES[key] = (time, filepath)
      if time > MAX_TIMES[key][0]:
            MAX_TIMES[key] = (time, filepath)

min_tuples = list(MIN_TIMES.values())
max_tuples = list(MAX_TIMES.values())
min_tuples.sort()
max_tuples.sort()
min_tuples = [(x[0],os.path.basename(x[1])) for x in min_tuples]
max_tuples = [(x[0],os.path.basename(x[1])) for x in max_tuples]

gaps = [(max_tuples[k],min_tuples[k+1]) for k in range(len(min_tuples)-1)]




keys = list(MIN_TIMES.keys())
intervals = [(MIN_TIMES[k][0], MAX_TIMES[k][0], k) for k in keys]                                                     
intervals.sort()                                                                                             

