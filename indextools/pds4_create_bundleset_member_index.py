"""Create a csv file of a bundleset's members and their information.

This module creates an index file containing the LIDs and filepaths of each 
bundle.xml file. There is a single command-line argument, the path to the 
bundleset.
"""
import argparse
import csv
from lxml import objectify
import os

def get_bundle_filepaths(bundleset_path):
    """Find and store paths to all bundle.xml files in bundleset.

    Generates the paths to bundle.xml files for each bundle within the
    bundleset, then appends them to a list to be iterated through. The
    bundle_path is the path to the bundleset.
    """
    bundlepaths = []
    for path, subdirs, files in os.walk(bundleset_path):
        for file in files:
            if file == 'bundle.xml':
                bundlepaths.append(os.path.join(path, file))

    return bundlepaths


def get_member_lid(bundle_path):
    """Scrape the LID from the bundle.xml file."""
    bundle_root = (objectify.parse(bundle_path,
                                   objectify.makeparser(
                                       remove_blank_text=True))
                            .getroot())

    bundle_lid = str(bundle_root.Identification_Area.logical_identifier.text)
    
    return bundle_lid
    
    
def get_shortpath(bundleset_name, bundle_path): 
    """Create shortened path from full filepath."""
    shortpath = bundleset_name + bundle_path.split(bundleset_name)[-1]
    return shortpath
    
    
def add_to_index(bundle_lid, bundleset_member_index, shortpath):
    """Add bundle information to index dictionary."""
    bundleset_member_index[bundle_lid] = ({
        'LID': bundle_lid,
        'Path': shortpath})


def file_creator(bundle_location, bundle_member_index):
    """Create a index file in the bundleset directory.

    This takes bbundleset_member_index and creates a csv file at the location
    of bundle_location. The bundle_location is the path leading to the 
    bundle.
    """
    with open(bundle_location + '/bundleset_member_index.csv',
              mode='w', encoding='utf8') as index_csv:
        bundle_member_index_writer = csv.DictWriter(
            index_csv,
            fieldnames=('LID',
                        'Path'))
        bundle_member_index_writer.writeheader()
        for index in sorted(bundle_member_index):
            bundle_member_index_writer.writerow(bundle_member_index[index])


def main():
    bundleset_member_index = {}
    bundleset_name = args.directorypath.split('/')[-1]
    bundlepaths = get_bundle_filepaths(args.directorypath)
    for bundlepath in bundlepaths:
        bundle_lid = get_member_lid(bundlepath)
        shortpath = get_shortpath(bundleset_name, bundlepath)
        add_to_index(bundle_lid, bundleset_member_index, shortpath)
    file_creator(args.directorypath, bundleset_member_index)


parser = argparse.ArgumentParser()
parser.add_argument('directorypath', type=str,
                    help='The path to the directory containing the bundles '
                         'you wish to scrape.')

args = parser.parse_args()

if __name__ == '__main__':
    main()
