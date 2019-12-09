import numpy as np
import textkernel
import tabulation
import cspyce

ROOT = '/Users/mark/GitHub/pds-migration/COUVIS/'
LSK = '/Volumes/Data-HD/Resources/SPICE/leapseconds.ker'
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



x = correction.x
y = correction.y
pylab.plot(x[x>0]/86400./365.25 + 2000,y[x>0])
