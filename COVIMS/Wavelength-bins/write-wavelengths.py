import pickle
import numpy as np
import os, sys

f = open('BINS352.pickle', 'rb')
BINS352 = pickle.load(f)
f.close()

INTERVALS = {
    5.09762: '1999.6000',
    5.09862: '2000.3500',
    5.10062: '2000.6950',
    5.10762: '2000.8680',
    5.10862: '2000.8780',
    5.10962: '2000.8840',
    5.11062: '2000.8940',
    5.11162: '2000.9030',
    5.11262: '2000.9110',
    5.11362: '2000.9180',
    5.11462: '2000.9250',
    5.11562: '2000.9310',
    5.11662: '2000.9360',
    5.11762: '2000.9420',
    5.11862: '2000.9470',
    5.11962: '2000.9520',
    5.12062: '2000.9560',
    5.12162: '2000.9610',
    5.12262: '2001.1200',
    5.12462: '2001.5000',
    5.12342: '2002.0000',
    5.12382: '2005.5000',
    5.12452: '2006.0000',
    5.12532: '2006.5000',
    5.12602: '2007.0000',
    5.12682: '2007.5000',
    5.12752: '2008.0000',
    5.12832: '2008.5000',
    5.12902: '2009.0000',
    5.12942: '2009.5000',
    5.13042: '2011.5000',
    5.13072: '2012.0000',
    5.13112: '2012.5000',
    5.13142: '2013.0000',
    5.13182: '2013.5000',
    5.13212: '2014.0000',
    5.13252: '2014.3000',
    5.13262: '2014.5000',
    5.13272: '2015.5000',
    5.13282: '2016.0000',
    5.13292: '2016.5000',
    5.13302: '2017.0000',
    5.13312: '2017.5000',
}

def write_wavelengths(key, values, id):
    centers = [np.array(values[:96]), np.array(values[96:])]
#     print(key, id, np.shape(centers[0]), np.shape(centers[1]))

    halfdiffs = [0.5 * np.diff(c) for c in centers]

    halfdiffs_above = [np.hstack((d, [d[-1]])) for d in halfdiffs]
    halfdiffs_below = [np.hstack(([d[0]], d )) for d in halfdiffs]

    fwhm = [halfdiffs_above[k] + halfdiffs_below[k] for k in (0,1)]
    fwhm = np.hstack(fwhm)

    outfile = 'wavelength-bins-%s.tab' % id.replace('.','-')
    f = open(outfile, 'w')
    f.write('Bin Number, Bin Center Wavelength (microns), FWHM (microns)\r\n')
    for k in range(352):
        f.write('%3d %8.6f %8.6f\r\n' % (k+1, values[k], fwhm[k]))
    f.close()

for (key, values) in BINS352.items():
    write_wavelengths(key, values, INTERVALS[key])


