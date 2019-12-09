import numpy as np
import textkernel
import tabulation
import cspyce

ROOT = '/Users/mark/GitHub/pds-migration/COUVIS/'
LSK = '/Volumes/Data-SSD/Resources/SPICE/leapseconds.ker'
EOM = '2017-09-16/00:00:00'

cspyce.furnsh(LSK)

tk = textkernel.from_file(ROOT + 'cas00172.tsc')
coeffts = np.array(tk['SCLK'][1]['COEFFICIENTS_82']).reshape(-1,3)
sclk = (coeffts[:,0] + tk['SCLK_PARTITION_START_82']) / 256.
tdt = coeffts[:,1]
tdb = [cspyce.unitim(t,'TDT','TDB') for t in tdt]

tdb_end = cspyce.utc2et(EOM)
tdt_end = cspyce.unitim(tdb_end,'TDB','TDT')
rate_end = coeffts[-1,2]
sclk_end = sclk[-1] + (tdt_end - tdt[-1]) / rate_end

sclk = np.array(list(sclk) + [sclk_end])
tdb  = np.array(list(tdb)  + [tdb_end])
cas00172 = tabulation.Tabulation(tdb, sclk)

tk = textkernel.from_file(ROOT + 'cas00171.tsc')
coeffts = np.array(tk['SCLK'][1]['COEFFICIENTS_82']).reshape(-1,3)
sclk = (coeffts[:,0] + tk['SCLK_PARTITION_START_82']) / 256.
tdt = coeffts[:,1]
tdb = [cspyce.unitim(t,'TDT','TDB') for t in tdt]

tdb_end = cspyce.utc2et(EOM)
tdt_end = cspyce.unitim(tdb_end,'TDB','TDT')
rate_end = coeffts[-1,2]
sclk_end = sclk[-1] + (tdt_end - tdt[-1]) / rate_end

sclk = np.array(list(sclk) + [sclk_end])
tdb  = np.array(list(tdb)  + [tdb_end])
cas00171 = tabulation.Tabulation(tdb, sclk)

correction = cas00172 - cas00171

print '# TDT, UTC, DOY, new-SCLK, old-SCLK, difference'

for et in np.arange(0.,cspyce.utc2et(EOM), 20000.):
    print '%9.0f' % et,
    print cspyce.et2utc(et, 'ISOC', 6),
    print cspyce.et2utc(et, 'ISOD', 6)[5:8],
    print '%17.6f' % cas00172(et),
    print '%17.6f' % cas00171(et),
    print '%9.6f' % correction(et)

pylab.plot(x[x>0]/86400./365.25 + 2000,y[x>0])
