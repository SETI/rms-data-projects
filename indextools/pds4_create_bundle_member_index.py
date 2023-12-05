"""Create a csv file of a bundle's members and their information.

This module creates an index file containing the LIDs, Reference Types, Member Statuses,
and filepaths of the bundle member entries in the bundle.xml file. There are two
command-line arguments.

Usage:

python pds4_create_bundle_member_index.py <bundle_dir> [--filesuffix (xml|lblx)]

<bundle_dir> is the root directory of the bundle.
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
                        help='The path to the directory containing the bundle '
                             'you wish to scrape.')
    
    parser.add_argument('--filesuffix', type=str, default='xml',
                        help='The type of label file present within the collection')

    args = parser.parse_args()

    basedir, bundle_name = os.path.split(tools.clean_directory_path(args.directorypath))
    # In get_member_files, nlevels is set to 1 so that the search does not go below
    # the top level of subdirectories. This ensures that only the bundle product is
    # caught.
    regex = r'[\w-]+\.(?:'+re.escape(args.filesuffix)+')'
    label_paths = tools.get_member_files(args.directorypath, 1, basedir,
                                         r'bundle\.(xml|lblx)')
    if len(label_paths) == 0:
        print(f'No label files ending in "{args.filesuffix}" '
              f'exist within this directory: {args.directorypath}')
        sys.exit(1)
        
    if len(label_paths) > 1:
        print(f'Chosen directory {args.directorypath} contains '
              f'too many toplevel label files: {label_paths}')
        sys.exit(1)
    member_index = {}

    bunprod_root = tools.get_index_root(basedir, label_paths[0])
    namespaces = tools.get_namespaces(bunprod_root)
    bundle_member_entries = tools.get_bundle_member_entries(bunprod_root, namespaces)
    tools.add_bundle_data(bundle_member_entries, member_index)
    # Here we are using 2 for the nlevels parameter to specify that only the files in
    # the first two levels of subdirectories are required. This relies on the assumption
    # that all the collection product files are within these subdirectories. If set to
    # None, it will iterate through all of the data products, making the runtime much
    # longer.
    dataprod_paths = tools.get_member_files(args.directorypath, 2, basedir, regex)
    # crossmatching filepaths to LIDs in member_index
    tools.dataprod_crossmatch(dataprod_paths,
                              basedir,
                              bundle_name,  member_index)
    for key in member_index:
        if member_index[key]['Path'] is None:
            lid = member_index[key]['LID']
            print(f'Data product with LID {lid} has no attributed filepath.')
            sys.exit(1)
    tools.create_results_file(args.directorypath, 'bundle', member_index)


if __name__ == '__main__':
    main()
