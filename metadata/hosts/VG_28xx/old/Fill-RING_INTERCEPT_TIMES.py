import datetime
import numpy as np

REFERENCE_TIMES = {
    'PS': '1981-08-25T00:00:00',
    'US': '1981-08-25T00:00:00',
    'RS': '1980-11-13T00:00:00',
    'PU': '1986-01-24T00:00:00',
    'UU': '1986-01-24T00:00:00',
    'RU': '1986-01-24T00:00:00',
    'PN': '1989-08-24T00:00:00',
    'UN': '1989-08-24T00:00:00',
}

ROOT_ = '/Volumes/pdsdata-mark/holdings/metadata/VG_28xx/'

FILENAMES = [
    'VG_2801/VG_2801_supplemental_index.tab',
    'VG_2802/VG_2802_supplemental_index.tab',
    'VG_2803/VG_2803_supplemental_index.tab',
]

GFILES = {
    'PS1G01'  : 'PS1G02',
    'PS2G01'  : 'SKIP!',
    'PU1G01XE': 'PU1G01',
    'PU1G01XI': 'PU1G01',
    'PU2G01XE': 'PU2G01',
    'PU2G01XI': 'PU2G01',
    'PN1G01'  : 'PN1G02',
    'US1G01'  : 'US1G02',
    'UU1G01XE': 'UU1G01',
    'UU1G01XI': 'UU1G01',
    'UU2G01XE': 'UU2G01',
    'UU2G01XI': 'UU2G01',
}

BADKEYS = {'PN1G01', 'PS1G01', 'PS2G01',
}

groot_ = ROOT_.replace('metadata', 'volumes')

for filename in FILENAMES:

    with open(ROOT_ + filename) as f:
        recs = f.readlines()

    prev_gkey = ''
    new_recs = []
    for rec in recs:
        new_rec = rec[:393] + '-99.000,-99.000,' + rec[393:]

        r0 = float(rec[312:324])
        r1 = float(rec[325:337])
        iso0 = rec[261:284].rstrip()
        iso1 = rec[287:310].rstrip()
        has_iso = (iso0 not in ('N/A', 'UNK') and
                   iso1 not in ('N/A', 'UNK'))

        path = rec[11:65].rstrip()
        parts = path.split('/')
        key = parts[-1].replace('.LBL','')

        dirname = parts[1] if key[0] == 'R' else parts[0]
        if (dirname[:3] in ('CAL', 'FOV', 'IMA', 'JIT', 'NOI', 'SOR', 'SPI', 'TRA', 'VEC')
                    or rad0 == -99 or rad1 == -99 or key in BADKEYS):
            new_recs.append(new_rec)
            continue

        shortkey = key
        if key[6:] in ('04', '05', '06', '07', '08', '09', '10', '11',
                       '12', '13', '14'):
            shortkey = key[:6]

        if shortkey[0] == 'R':
            gkey = shortkey[:2] + '0G' + shortkey[4] + 'B' + shortkey[6:]
        else:
            gkey = shortkey[:3] + 'G0' + shortkey[5:]

        if 'EASYDATA/' in path and key[4:6] == '01' and key[1] in 'SN' and key[2] == '1' and key[3] != 'G':
            gkey = gkey[:4] + '02' + gkey[6:]

        if 'EDITDATA/U' in path or 'RAWDATA/U' in path:
            gkey = gkey[:6]     # strip 'I', 'D', 'V', etc.

        if 'S_RINGS/LOWDATA/R' in path and gkey[-2:] in ('1T', '2T'):
            gkey = 'SKIP!'      # simulation files
        elif 'S_RINGS/EDITDATA/R' in path or 'S_RINGS/LOWDATA/R' in path:
            gkey = gkey[:6]     # strip 'I', 'D', 'V', etc.

        gkey = GFILES.get(gkey, gkey)

        if gkey == 'SKIP!' or (gkey[2] >= '3' and gkey[2] <= '9'):
            new_recs.append(new_rec)
            continue

        if gkey != prev_gkey:
            volname_ = filename[:8]
            if key[0] == 'R':
                parts = path.split('/')
                gfile = groot_ + volname_ + parts[0] + '/GEOMETRY/' + gkey + '.TAB'
            else:
                gfile = groot_ + volname_ + 'GEOMETRY/' + gkey + '.TAB'

            try:
                with open(gfile, 'r') as g:
                    grecs = g.readlines()
            except IOError:
                print('**** Geometry not found for ' + path)
                raise

            secs = []
            rads = []
            lons = []
            for grec in grecs:
                parts = grec.split(',')
                secs.append(float(parts[1]))
                rads.append(float(parts[2]))
                lons.append(float(parts[3]))

            secs = np.array(secs)
            rads = np.array(rads)
            lons = np.array(lons)

            ref_iso = REFERENCE_TIMES[key[:2]]
            ref_dt = datetime.datetime.fromisoformat(ref_iso)
            ref_timestamp = datetime.datetime.timestamp(ref_dt)

            prev_gkey = gkey

        new_isos = []
        new_lons = []
        new_rads = []

        if has_iso and ('EASYDATA/KM000_2/P' not in path and
                        'EASYDATA/KM000_5/P' not in path):
          for iso in (iso0, iso1):
            dt = datetime.datetime.fromisoformat(iso)
            ts = datetime.datetime.timestamp(dt)
            sec = ts - ref_timestamp
            dsec = sec - secs
            products = dsec[:-1] * dsec[1:]
            kvals = np.where(products <= 0)[0]
            if len(kvals) == 0:
                if abs(dsec[0]) < abs(dsec[1])/2:
                    k = 0
                elif abs(dsec[-1]) < abs(dsec[-2])/2:
                    k = len(dsec) - 2
                else:
                    x0 = abs(dsec[0] / (dsec[1] - dsec[0]))
                    x1 = abs(dsec[-1] / (dsec[-2] - dsec[-1]))
                    x = min(x0,x1)
                    print(f'**** INTERPOLATION FAILURE: {path} {gkey} {x}')
                    break
            else:
                k = np.where(products <= 0)[0][0]

            frac = (sec - secs[k]) / (secs[k+1] - secs[k])
            lon = lons[k] + frac * (lons[k+1] - lons[k])
            new_lons.append(lon)

            rad = rads[k] + frac * (rads[k+1] - rads[k])
            new_rads.append(rad)

          lon0 = min(new_lons)
          lon1 = max(new_lons)

          new_r0 = min(new_rads)
          new_r1 = max(new_rads)

          index_r0 = new_r0
          index_r1 = new_r1
          if r0 != -99.:
            if abs(new_r0 - r0) > 0.07:
                print(f'**** RADIUS MISMATCH: {r0}, {new_r0}, {path}')
            index_r0 = r0

          if r1 != -99.:
            if abs(new_r1 - r1) > 0.07:
                print(f'**** RADIUS MISMATCH: {r1}, {new_r1}, {path}')
            index_r1 = r1

          new_rec = (rec[:312] + f'{index_r0:12.5f},{index_r1:12.5f},' + rec[338:393] +
                   f'{lon0:7.3f},{lon1:7.3f},' + rec[393:])
          new_recs.append(new_rec)

        else:
          for r in (r0, r1):
            dr = r - rads
            products = dr[:-1] * dr[1:]
            kvals = np.where(products <= 0)[0]
            if len(kvals) == 0:
                if abs(dr[0]) < abs(dr[1])/2:
                    k = 0
                elif abs(dr[-1]) < abs(dr[-2])/2:
                    k = len(dr) - 2
                else:
                    x0 = abs(dr[0] / (dr[1] - dr[0]))
                    x1 = abs(dr[-1] / (dr[-2] - dr[-1]))
                    x = min(x0,x1)
                    print(f'**** INTERPOLATION FAILURE: {path} {gkey} {x}')
                    break
            elif len(kvals) == 2 and key.endswith('E'):
                k = kvals[1]
            else:
                k = kvals[0]

            frac = (r - rads[k]) / (rads[k+1] - rads[k])
            lon = lons[k] + frac * (lons[k+1] - lons[k])
            new_lons.append(lon)

            sec = secs[k] + frac * (secs[k+1] - secs[k])
            dt = datetime.datetime.fromtimestamp(ref_timestamp + sec)
            iso = datetime.datetime.isoformat(dt, timespec='milliseconds')
            new_isos.append(iso)

          if len(new_lons) == 2:
            lon0 = min(new_lons)
            lon1 = max(new_lons)

            new_iso0 = min(new_isos)
            new_iso1 = max(new_isos)

            index_iso0 = new_iso0
            index_iso1 = new_iso1
            if iso0 not in ('N/A', 'UNK'):
                if iso0[:-2] != new_iso0[:-2]:
                    dt = datetime.datetime.fromisoformat(iso0)
                    ts0 = datetime.datetime.timestamp(dt)
                    dt = datetime.datetime.fromisoformat(new_iso0)
                    ts1 = datetime.datetime.timestamp(dt)
                    print(f'**** TIME MISMATCH: {iso0}, {new_iso0}, {ts1-ts0}, {path}')
                    index_iso0 = iso0

            if iso1 not in ('N/A', 'UNK'):
                if iso1[:-2] != new_iso1[:-2]:
                    dt = datetime.datetime.fromisoformat(iso1)
                    ts0 = datetime.datetime.timestamp(dt)
                    dt = datetime.datetime.fromisoformat(new_iso1)
                    ts1 = datetime.datetime.timestamp(dt)
                    print(f'**** TIME MISMATCH: {iso1}, {new_iso1}, {ts1-ts0}, {path}')
                    index_iso1 = iso1

            if 'EASYDATA/KM000_2/PS' in path or 'EASYDATA/KM000_5/PS' in path:
                index_iso0 = new_iso0       # correct small time errors in table
                index_iso1 = new_iso1
                print(f'**** OVERRIDING TIME IN INDEX: {iso0}, {new_iso0}, {path}')
                print(f'**** OVERRIDING TIME IN INDEX: {iso1}, {new_iso1}, {path}')

          else:
            lon0 = -99.
            lon1 = -99.
            index_iso0 = iso0.ljust(23)
            index_iso1 = iso1.ljust(23)

          new_rec = (rec[:260] + f'"{index_iso0}","{index_iso1}",' + rec[312:393] +
                     f'{lon0:7.3f},{lon1:7.3f},' + rec[393:])
          new_recs.append(new_rec)

    with open(ROOT_ + filename[:-4] + '-new.tab', 'wb') as f:
        for rec in new_recs:
            f.write(rec.rstrip().encode('latin-1') + b'\r\n')

