"""Create a csv file of a bundleset's members and their information.

This module creates an index file containing the LIDs and filepaths of each 
bundle.xml file. There is a single command-line argument, the path to the 
bundleset.
"""
import argparse
from lxml import objectify 
import pds4_index_tools as tools


def create_member_index(member_index, lid, labels, path, directory):
    bundle_name = directory.split('/')[-2]
    temp_dict = {'Path': '__'}
    for label in labels:
        if label == 'LID':
            temp_dict.update({label: lid})
        elif label == 'Path':
            temp_dict.update({label: path})
        else:
            temp_dict.update({label: '__'})
        temp_dict = dict(sorted(temp_dict.items()))
        member_index[lid] = temp_dict
    
    tools.shortpaths(directory, bundle_name, member_index)
    return member_index


def get_index_root(bundlexml_paths, directory, labels):
    member_index = {}
    for path in bundlexml_paths:
        bundle_root = (objectify.parse(path,
                                       objectify.makeparser(
                                           remove_blank_text=True))
                       .getroot())
        bundle_lid = str(
            bundle_root.Identification_Area.logical_identifier.text)
        create_member_index(member_index, bundle_lid, labels, path, directory)
    return member_index


def main():
    bundlexml_paths = tools.get_member_filepaths(
        args.directorypath, 2, 'bundle')
    member_index = get_index_root(bundlexml_paths, args.directorypath, ['LID', 'Path'])
    tools.file_creator(args.directorypath, 'bundleset', member_index)


parser = argparse.ArgumentParser()
parser.add_argument('directorypath', type=str,
                    help='The path to the directory containing the bundles '
                         'you wish to scrape.')

args = parser.parse_args()

if __name__ == '__main__':
    main()