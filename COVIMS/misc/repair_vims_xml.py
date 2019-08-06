import os, sys

def repair_xml(path):

    with open(path) as f:
        recs = f.readlines()

    for k,rec in enumerate(recs):
        if not rec.startswith('        <logical_identifier>'):
            continue
        if '.qub</logical_identifier>' not in rec:
            break

        recs[k] = rec.replace('.qub','')
        print 'a',
        break

    for k,rec in enumerate(recs):
        if '<!-- Descriptions of the individual objects in the file  -->' not in rec:
            continue

        if rec[0] == ' ':
            recs[k] = rec[1:]

        print 'b',
        break

    shifted = 0
    if '</Local_ID_Relation>' in recs[k-2]:
        recs = recs[:k-1] + ['        </Composite_Structure>' + recs[k][-2:]] + recs[k-1:]
        print 'c',

        for kk in range(k+1,len(recs)-2):
            rec = recs[kk]
            if rec.startswith('    '):
                recs[kk] = rec[4:]
                shifted += 1

    print shifted,

    if '</Composite_Structure>' in recs[-3]:
        recs = recs[:-3] + recs[-2:]
        print 'd',

    shifted = 0
    for k,rec in enumerate(recs):
        if rec.startswith(' <!'):
            rec = rec[2:]

        if rec.startswith('<!'):
            while ('  ') in rec:
                rec = rec.replace('  ', ' ')
                shifted += 1

            rec = rec.replace('.', '')

        recs[k] = rec

    print shifted,

    with open(path, 'w') as f:
        f.writelines(recs)

for arg in sys.argv[1:]:
  for (root, dirs, files) in os.walk(arg):
    for file in files:
      if not file.endswith('.xml'): continue
      path = os.path.join(root, file)
      repair_xml(path)
      print file
