"""Create a csv file of a bundleset's members and their information.

This module creates an index file containing the LIDs and filepaths of each
bundle.xml file. There are two command-line arguments.

Usage:

python pds4_create_bundleset_member_index.py <bundleset_dir> [--filesuffix (xml|lblx)]

<bundleset_dir> is the root directory of the bundleset.
If given, --filesuffix specifies the type of label file; if not given, the default is xml
"""
import argparse
import os
import re
import sys

import pds4_index_tools as tools


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('directorypath', type=str,
                        help='The path to the directory containing the bundleset '
                             'you wish to scrape.')
    parser.add_argument('--filesuffix', type=str, default='xml',
                        help='The type of label file present within the collection')

    args = parser.parse_args()
    
    regex = r'[\w-]+\.(?:'+re.escape(args.filesuffix)+')'
    basedir, bundleset_name = os.path.split(args.directorypath)
    # In get_member_files, nlevels is set to 2 here to limit the search to the
    # bundle product files of the bundles within the bundleset.
    label_paths = tools.get_member_files(args.directorypath, 2, basedir, regex)
    if len(label_paths) == 0:
        print(f'No label files ending in "{args.filesuffix}" exist within this '
              f'directory: {args.directorypath}')
        sys.exit(1)

    member_index = {}
    for label_path in label_paths:
        bunprod_root = tools.get_index_root(basedir, label_path)
        bunprod_lid = tools.get_bundle_lid(bunprod_root)
        tools.add_lid_to_member_index(['LID', 'Path'],
                                      label_path, bunprod_lid, member_index)
        for key in member_index:
            if member_index[key]['Path'] is None:
                lid = member_index[key]['LID']
                print(f'Data product with LID {lid} has no attributed filepath.')
                sys.exit(1)
                
        tools.create_results_file(args.directorypath, 'bundleset', member_index)


if __name__ == '__main__':
    main()
