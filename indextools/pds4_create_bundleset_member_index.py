"""Create a csv file of a bundleset's members and their information.

This module creates an index file containing the LIDs and filepaths of each 
bundle.xml file. There is a single command-line argument, the path to the 
bundleset.
"""
import argparse

import pds4_index_tools as tools


def main():
    bundlexml_paths = tools.get_member_filepaths(
        args.directorypath, 2, 'bundle')
    member_index = tools.add_to_index(
        args.directorypath, bundlexml_paths, 'bundle')
    tools.file_creator(args.directorypath, 'bundleset', member_index)


parser = argparse.ArgumentParser()
parser.add_argument('directorypath', type=str,
                    help='The path to the directory containing the bundles '
                         'you wish to scrape.')

args = parser.parse_args()

if __name__ == '__main__':
    main()
