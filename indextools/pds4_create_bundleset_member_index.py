"""Create a csv file of a bundleset's members and their information.

This module creates an index file containing the LIDs and filepaths of each
bundle.xml file. There is a single command-line argument, the path to the
bundleset.
"""
import argparse
import pds4_index_tools as tools


def main():
    bundleset_name = args.directorypath.split('/')[-2]
    bundlexml_paths = tools.get_member_filepaths(
        args.directorypath, 2, 'bundle', bundleset_name)
    member_index = {}
    for bundlexml_path in bundlexml_paths:
        # Change get_index_root so that it only parses the XML file
        bundle_root = tools.get_index_root(args.directorypath.replace(bundleset_name, ''),
                                           bundlexml_path)
        # Create get_bundle_lid using two lines currently in get_index_root
        bundle_lid = tools.get_bundle_lid(bundle_root)
        # Change create_member_index so that it accepts only these three
        # arguments, creates the dictionary containing all labels and filling
        # in values for lid and path, and then *returns* member_index
        tools.create_member_index(member_index, ['LID', 'Path'],
                                  bundlexml_path, bundle_lid)
        tools.file_creator(args.directorypath, 'bundleset', member_index)


parser = argparse.ArgumentParser()
parser.add_argument('directorypath', type=str,
                    help='The path to the directory containing the bundles '
                         'you wish to scrape.')

args = parser.parse_args()

if __name__ == '__main__':
    main()
