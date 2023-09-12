"""Create a csv file of a bundleset's members and their information.

This module creates an index file containing the LIDs and filepaths of each
bundle.xml file. There are two command-line arguments: the path to the
bundleset, and the file type of the label files. The currently supported label file types
are xml and lblx. If no file type argument is given, it will default to xml.
"""
import argparse
import os
import sys

import pds4_index_tools as tools


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('directorypath', type=str,
                        help='The path to the directory containing the bundleset '
                             'you wish to scrape.')
    parser.add_argument('--filesuffix', nargs='?',  const=1, type=str, default='xml',
                        help='The type of label file present within the collection')

    args = parser.parse_args()
    
    basedir, bundleset_name = os.path.split(args.directorypath)
    label_paths = tools.get_member_files(args.directorypath, 2, bundleset_name,
                                         args.filesuffix)
    if len(label_paths) == 0:
        try:
            raise tools.NoLabelsFound(f'No label files ending in "{args.filesuffix}"'
                                       'exist within this directory:'
                                      f'{args.directorypath}')
        except tools.NoLabelsFound as e:
            print(e)
            sys.exit(1)

    member_index = {}
    for label_path in label_paths:
        # Change get_index_root so that it only parses the XML file
        bunprod_root = tools.get_index_root(args.directorypath
                                                .replace(bundleset_name, ''),
                                            label_path)
        # Create get_bundle_lid using two lines currently in get_index_root
        bunprod_lid = tools.get_bundle_lid(bunprod_root)
        # Change add_lid_to_member_index so that it accepts only these three
        # arguments, creates the dictionary containing all labels and filling
        # in values for lid and path, and then *returns* member_index
        tools.add_lid_to_member_index(['LID', 'Path'],
                                      label_path, bunprod_lid, member_index)
        for key in member_index:
            try:
                if member_index[key]['Path'] == None:
                    lid = member_index[key]['LID']
                    raise tools.MissingLabel(f'Data product with LID {lid} has no '
                                              'attributed filepath.')
            except tools.MissingLabel as e:
                print(e)
                sys.exit(1)
                
        tools.create_results_file(args.directorypath, 'bundleset', member_index)


if __name__ == '__main__':
    main()
