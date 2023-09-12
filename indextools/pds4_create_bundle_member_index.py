"""Create a csv file of a bundle's members and their information.

This module creates an index file containing the LIDs, Reference Types, Member Statuses,
and filepaths of each bundle.xml file. There is a two command-line arguments: the path
to the bundle, and the file type of the label files. The file type can be xml or lblx,
but if no argument is given, it will default to xml.
"""
import argparse
import os
import sys

import pds4_index_tools as tools


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('directorypath', type=str,
                        help='The path to the directory containing the bundle '
                             'you wish to scrape.')
    
    parser.add_argument('--filesuffix', nargs='?',  const=1, type=str, default='xml',
                        help='The type of label file present within the collection')

    args = parser.parse_args()

    basedir, bundle_name = os.path.split(args.directorypath)
    label_paths = tools.get_member_files(args.directorypath, 1, bundle_name,
                                         args.filesuffix)
    if len(label_paths) == 0:
        try:
            raise tools.NoLabelsFound(f'No label files ending in "{args.filesuffix}" '
                                       'exist within this directory: '
                                      f'{args.directorypath}')
        except tools.NoLabelsFound as e:
            print(e)
            sys.exit(1)
        
    if len(label_paths) > 1:
        try:
            raise tools.TooManyLabels(f'Chosen directory {args.directorypath} contains '
                                      f'too many toplevel label files: {label_paths}')
        except tools.TooManyLabels as e:
            print(e)
            sys.exit(1)
    namespaces = tools.get_namespaces(args.directorypath.replace(bundle_name, ''),
                                      label_paths)
    member_index = {}
    bunprod_root = tools.get_index_root(args.directorypath.replace(bundle_name,
                                                                   ''),
                                        label_paths[0])
    # Get the bundle member entries for the bundle
    bundle_member_entries = tools.get_bundle_entries(bunprod_root, namespaces)
    # Create and fill member_index with info, excluding filepaths
    tools.add_bundle_data(bundle_member_entries, member_index)
    dataprod_paths = tools.get_member_files(args.directorypath, 2, bundle_name,
                                            args.filesuffix)
    # crossmatching filepaths to LIDs in member_index
    tools.dataprod_crossmatch(dataprod_paths,
                              args.directorypath,
                              bundle_name,  member_index)
    for key in member_index:
        if member_index[key]['Path'] is None:
            lid = member_index[key]['LID']
            try:
                raise tools.MissingLabel(f'Data product with LID {lid} has no attributed '
                                          'filepath.')
            except tools.MissingLabel as e:
                print(e)
                sys.exit(1)
    tools.create_results_file(args.directorypath, 'bundle', member_index)


if __name__ == '__main__':
    main()
