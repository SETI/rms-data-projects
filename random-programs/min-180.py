import sys
import os

for filepath in sys.argv[1:]:
    if not filepath.endswith('_ring_summary.tab'): continue
    print filepath

    if 'NH' in filepath:
        starts = (274, 283)
    elif 'VGISS' in filepath:
        starts = (284, 293)
    elif 'COISS' in filepath:
        starts = (266, 275)
    elif 'COVIMS' in filepath:
        starts = (287, 296)
    elif 'COUVIS' in filepath:
        starts = (269, 278)
    else:
        print 'Unrecognized filename'
        continue

    with open(filepath) as f:
        recs = f.readlines()

    for row in range(len(recs)):
        rec = recs[row]

        angles = []
        illegal = False
        for k in starts:
            angle = float(rec[k-1:k+7])
            angles.append(angle)

            if (angle < 0 or angle > 360) and angle != -999:
                print 'Illegal angle value: ', angle
                illegal = True

        if illegal:
            print 'processing aborted'
            break

        if angles == [0., 360.]:
            k = starts[0]
            rec = rec[:k-1] + ('%8.3f' % -180.) + rec[k+7:]

            k = starts[1]
            rec = rec[:k-1] + ('%8.3f' % 180.) + rec[k+7:]

        else:
            for k in starts:
                angle = float(rec[k-1:k+7])
                if angle >= 180:
                    rec = rec[:k-1] + ('%8.3f' % (angle - 360.)) + rec[k+7:]

        recs[row] = rec

    with open(filepath, 'w') as f:
        f.writelines(recs)

    print 'processing completed'

