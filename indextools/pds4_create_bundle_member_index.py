"""Create a csv file of a bundle's members and their information.

This module creates an index file containing the LIDs, Reference Types, Member
Statuses, and filepaths of each bundle.xml file. There is a single
command-line argument, the path to the bundle.
"""
import argparse
import pds4_index_tools as tools


parser = argparse.ArgumentParser()
parser.add_argument('directorypath', type=str,
                    help='The path to the directory containing the bundles '
                         'you wish to scrape.')

args = parser.parse_args()


def main():
    bundle_name = args.directorypath.split('/')[-2]
    bundlexml_paths = tools.get_member_filepaths(
        args.directorypath, 3, 'bundle')
    namespaces = tools.get_schema(bundlexml_paths)
    member_index = {}
    bundle_root = tools.get_index_root(bundlexml_paths[0])
    # Get the bundle member entries for the bundle
    bundle_member_entries = tools.get_bundle_entries(bundle_root, namespaces)
    # Create and fill member_index with info, excluding filepaths
    tools.add_bundle_data(bundle_member_entries, member_index)
    fullpaths = tools.fullpaths_populate(args.directorypath, 2)
    # crossmatching filepaths to LIDs in member_index
    tools.bundle_crossmatch(fullpaths, member_index, args.directorypath,
                            bundle_name)
    tools.file_creator(args.directorypath, 'bundle', member_index)


if __name__ == '__main__':
    main()
