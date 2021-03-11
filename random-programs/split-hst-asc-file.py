import os, sys, re

HEADER = re.compile(r"(/\*+\n/\*+\nfitsfile= ')(.*?)(\.FITS' /.*\nheaderno= +1 /)")

for (root, dirs, files) in os.walk('/Volumes/pdsdata-server2/holdings/volumes/HSTOx_xxxx copy'):
    for fname in files:
        fpath = os.path.join(root, fname)
        if fname.endswith('.ASC'):
            print('***', fpath)
            with open(fpath, encoding='latin-1') as f:
                contents = f.read()

            parts = HEADER.split(contents)
            for k in range(1, len(parts), 4):
                new_fpath = os.path.join(root, parts[k+1]) + '.txt'
                print('******', new_fpath)
                with open(new_fpath, 'w', encoding='latin-1') as f:
                    f.write(parts[k])
                    f.write(parts[k+1])
                    f.write(parts[k+2])
                    f.write(parts[k+3])

        else:
            print('xxx', fpath)
            os.remove(fpath)

