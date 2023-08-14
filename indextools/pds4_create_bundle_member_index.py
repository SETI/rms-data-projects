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
    label_paths = tools.get_member_filepaths(
        args.directorypath, 3, 'bundle', bundle_name)
    namespaces = tools.get_schema(args.directorypath.replace(bundle_name, ''),
                                  label_paths)
    member_index = {}
    bunprod_root = tools.get_index_root(args.directorypath.replace(bundle_name,
                                                                   ''),
                                        label_paths[0])
    # Get the bundle member entries for the bundle
    bundle_member_entries = tools.get_bundle_entries(bunprod_root, namespaces)
    # Create and fill member_index with info, excluding filepaths
    tools.add_bundle_data(bundle_member_entries, member_index)
    dataprod_paths = tools.find_all_data_products(args.directorypath, 2,
                                                  bundle_name)
    # crossmatching filepaths to LIDs in member_index
    tools.dataprod_crossmatch(dataprod_paths, member_index,
                              args.directorypath,
                              bundle_name)
    tools.file_creator(args.directorypath, 'bundle', member_index)


if __name__ == '__main__':
    main()
