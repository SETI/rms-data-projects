"""Create a csv file of a bundleset's members and their information.

This module creates an index file containing the LIDs and filepaths of each
bundle.xml file. There is a single command-line argument, the path to the
bundleset.
"""
import argparse
import os
import pds4_index_tools as tools


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('directorypath', type=str,
                        help='The path to the directory containing the bundles '
                             'you wish to scrape.')

    args = parser.parse_args()
    
    basedir, bundleset_name = os.path.split(args.directorypath)
    label_paths = tools.get_member_filepaths(
        args.directorypath, 'bundle', bundleset_name)
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
        tools.add_lid_to_member_index(member_index, ['LID', 'Path'],
                                      label_path, bunprod_lid)
        tools.create_results_file(args.directorypath, 'bundleset', member_index)


if __name__ == '__main__':
    main()
