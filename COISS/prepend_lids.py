import sys, os, re

pattern = re.compile('([NW])(1[0-9]{9})[^0-9]')

bundle_name = 'cassini_iss_cruise'
infile = '/Volumes/Marks-Migration-HD/pds4/COISS_xxxx/COISS_2xxx/COISS_2999/COISS_2999_inventory.tab'
outfile = '/Volumes/Marks-Migration-HD/pds4/COISS_xxxx/cassini_iss_saturn/metadata/body-inventory.tab'

with open(infile) as f:
    recs = f.readlines()

newrecs = []
for k,rec in enumerate(recs):
    match = pattern.search(rec)
    nw = match.group(1).lower()
    sclk = match.group(2)

    newrecs.append('urn:nasa:pds:%s:data_raw:%s%s,%sxxxxx/%s%s.img,' %
                   (bundle_name, sclk, nw, sclk[:5], sclk, nw) +
                   rec)

with open(outfile, 'w') as f:
    f.writelines(newrecs)


