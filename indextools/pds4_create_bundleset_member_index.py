"""Create a csv file of a bundleset's members and their information.

This module creates an index file containing the LIDs and filepaths of each 
bundle.xml file. There is a single command-line argument, the path to the 
bundleset.
"""
import argparse
import csv
from lxml import objectify
import os

def get_bundle_filepaths(bundleset_directory):
    """Find and store paths to all bundle.xml files in bundleset.
    
    Inputs:
        bundleset_directory    The path to the bundleset directory.
        
    Returns:
        bundlexml_paths         The list of paths to all bundle.xml files within 
                               the bundle.
    """
    bundlexml_paths = []
    for path, subdirs, files in os.walk(bundleset_directory):
        for file in files:
            if file == 'bundle.xml':
                bundlexml_paths.append(os.path.join(path, file))

    return bundlexml_paths


def get_member_lid(bundlexml_path):
    """Scrape the LID from the bundle.xml file.
    
    Inputs:
        bundlexml_path    The path to the bundle.xml file of a bundle.
        
    Returns:
        bundle_lid        The LID of the bundle.xml file.
    """
    bundle_root = (objectify.parse(bundlexml_path,
                                   objectify.makeparser(
                                       remove_blank_text=True))
                            .getroot())

    bundle_lid = str(bundle_root.Identification_Area.logical_identifier.text)
    
    return bundle_lid
    
    
def get_shortpath(bundleset_name, bundle_directory): 
    """Create shortened path from the full filepath.
    
    Inputs:
        bundleset_name      The name of the bundleset.
        
        bundle_directory    The path to a bundle within the bundleset.
        
    Returns:
        shortpath           A shortened version of the filepath. First part now
                            begins with the bundleset directory.
    """
    shortpath = bundleset_name + bundle_directory.split(bundleset_name)[-1]
    return shortpath
    
    
def add_to_index(bundle_lid, bundleset_member_index, shortpath):
    """Add bundle information to index dictionary.
    
    Inputs:
        bundle_lid    The LID of the bundle.xml file.
        
        bundleset_member_index    The dictionary of bundle.xml information that
                                  will have the following added to it:
                                      
            "LID"                     The LID of the bundle.xml file.
            
            "Path"                    The path to the bundle.xml file. 
            
        shortpath                 The path to the bundle.xml file, starting from
                                  the bundleset directory.
    """
    bundleset_member_index[bundle_lid] = ({
        'LID': bundle_lid,
        'Path': shortpath})


def file_creator(bundle_directory, bundleset_member_index):
    """Create a index file in the bundleset directory.
    
    Inputs:
        bundle_directory    The path to the bundle directory.
        
        bundleset_member_index    The dictionary of all bundle.xml LIDs and
                                  filepaths within a bundleset.
    """
    with open(os.path.join(bundle_directory, 'bundleset_member_index.csv'),
              mode='w', encoding='utf8') as index_csv:
        bundle_member_index_writer = csv.DictWriter(
            index_csv,
            fieldnames=('LID',
                        'Path'))
        bundle_member_index_writer.writeheader()
        for index in sorted(bundleset_member_index):
            bundle_member_index_writer.writerow(bundleset_member_index[index])


def main():
    bundleset_member_index = {}
    bundleset_name = args.directorypath.split('/')[-1]
    bundlexml_paths = get_bundle_filepaths(args.directorypath)
    for bundlexml_path in bundlexml_paths:
        bundle_lid = get_member_lid(bundlexml_path)
        shortpath = get_shortpath(bundleset_name, bundlexml_path)
        add_to_index(bundle_lid, bundleset_member_index, shortpath)
    file_creator(args.directorypath, bundleset_member_index)


parser = argparse.ArgumentParser()
parser.add_argument('directorypath', type=str,
                    help='The path to the directory containing the bundles '
                         'you wish to scrape.')

args = parser.parse_args()

if __name__ == '__main__':
    main()
