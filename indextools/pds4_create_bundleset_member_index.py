"""Create a csv file of a bundleset's members and their information.

This module creates an index of all .xml and .lblx files within a bundleset,
sorted alphabetically by LID, and then stores it in the attributed bundle
directory for each bundle within the bundleset. There is a single command-line
argument, the path to the bundleset.
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
    """Populate the bundleset_member_index dictionary with bundle information.

    The path to the bundle.xml file is parsed with lxml.objectify. The
    bundle member entries are found and scraped for their LID. This LID is
    put into the bundleset_member_index dictionary as a key with the same LID
    and the filepath to the bundle.xml file as values. The input bundle_path 
    is the path to the bundle, bundleset_member_index is the dictionary to be
    populated, and bundleset_name is the name of the bundleset.
    """
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
    """Create the bundleset_member_index.csv file for the bundleset."""
    bundleset_member_index = {}
    bundleset_name = args.directorypath.split('/')[-1]
    bundlepaths = get_bundle_filepaths(args.directorypath)
    for bundlepath in bundlepaths:
        bundle_lid = get_member_lid(bundlepath)
        shortpath = get_shortpath(bundleset_name, bundlepath)
        add_to_index(bundle_lid, bundleset_member_index, shortpath)
    file_creator(args.directorypath, bundleset_member_index)
        
    
ns = {'pds': 'http://pds.nasa.gov/pds4/pds/v1',
      'cassini': 'http://pds.nasa.gov/pds4/mission/cassini/v1'}

parser = argparse.ArgumentParser()
parser.add_argument('directorypath', type=str,
                    help='The path to the directory containing the bundles '
                         'you wish to scrape.')

args = parser.parse_args()

if __name__ == '__main__':
    main()
