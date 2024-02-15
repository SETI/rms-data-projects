#!/usr/bin/env python

import sys

for arg in sys.argv[1:]:

    with open(arg, 'r') as f:
        recs = f.readlines()

    print arg

    if len(recs[0]) != 712:
        print 'Record length is incorrect, aborted'
        continue

    newrecs = []
    for rec in recs:
        min_solar_elevation = float(rec[409:][:8])
        max_solar_elevation = float(rec[418:][:8])

        min_observer_elevation = float(rec[427:][:8])
        max_observer_elevation = float(rec[436:][:8])

        if min_solar_elevation == -999.:
            min_solar_elevation_unsigned = -999.
            max_solar_elevation_unsigned = -999.
        elif min_solar_elevation > 0.:
            min_solar_elevation_unsigned = min_solar_elevation
            max_solar_elevation_unsigned = max_solar_elevation
        else:
            min_solar_elevation_unsigned = -max_solar_elevation
            max_solar_elevation_unsigned = -min_solar_elevation

        if min_observer_elevation == -999.:
            min_observer_elevation_unsigned = -999.
            max_observer_elevation_unsigned = -999.
        elif min_observer_elevation > 0.:
            min_observer_elevation_unsigned = min_observer_elevation
            max_observer_elevation_unsigned = max_observer_elevation
        else:
            min_observer_elevation_unsigned = -max_observer_elevation
            max_observer_elevation_unsigned = -min_observer_elevation

        rec = rec[:445] + \
              '%8.3f,%8.3f,%8.3f,%8.3f,' % (min_solar_elevation_unsigned,
                                            max_solar_elevation_unsigned,
                                            min_observer_elevation_unsigned,
                                            max_observer_elevation_unsigned) + \
              rec[445:]

        newrecs.append(rec)

    with open(arg, 'w') as f:
        f.writelines(newrecs)

