"""Create a csv file of a bundle's members and their information.

This module creates an index of all .xml and .lblx files within a bundle,
sorted alphabetically by LID, and then stores it in the attributed bundle
directory. There is a single command-line argument, the path to the bundle
directory.
"""
import argparse
import csv
from lxml import objectify
import os
import sys


def create_bundle_member_index(directory_path):
    """Generate a .csv file containing information about the bundle directory.

    This function derives the bundle member information by creating file paths
    to all known bundle.xml files. The bundle member entries are scraped for
    their LIDs, their reference types, and their member statuses. These values
    are put into the bundle_member_lid dictionary for crossmatching.

    For the bundle, all .xml and .lbxl files within the first level of
    subdirectories are found and scraped for their LIDs. Any LIDs that match the
    keys of the bundle member dictionary are recorded in a new dictionary
    bundle_member_index with the LID as the key and the member status, reference
    type, and path to the file as values. If a LID does not match any key
    within the bundle_member_lid dictionary, a statement will print. If a LID
    contains a collection term that does not match the filepath but is otherwise
    represented within the bundle, a warning message is printed but the file
    will remain within the bundle_member_index dictionary.

    The resulting dictionary bundle_member_index will contain the LIDs of all
    .xml or .lblx files within the first level of subdirectories as keys, with
    the member status, reference types, and file paths as values for each entry.
    This dictionary will then become exported as a .csv file and placed into
    the same location as the bundle.xml file for that bundle.
    """
    fullpaths = []
    bundle_member_index = {}

    def create_bundle_members(bundle_path):
        """Create a dictionary of LIDs, member status and reference type.

        The path to a directory that contains the bundle.xml file is parsed
        with lxml.objectify. The bundle member entries are found and scraped
        for their LID. This LID is put into the bundle_member_lid dictionary
        as a key with the reference type and the member status scraped and
        entered as values. The input 'bundle_path' is the path to the bundle.
        """
        bundle_file_path = None

        for path, subdirs, files in os.walk(bundle_path):
            for file in files:
                if file == 'bundle.xml':
                    bundle_file_path = os.path.join(path, file)

        if bundle_file_path is None:
            print('No bundle.xml file exists within this bundle')
            sys.exit(1)

        bundle_root = (objectify.parse(bundle_file_path,
                                       objectify.makeparser(
                                           remove_blank_text=True))
                                .getroot())

        bundle_member_entries = bundle_root.findall('pds:Bundle_Member_Entry',
                                                    namespaces=ns)

        for bundle_member_entry in bundle_member_entries:
            bundle_member_lid = bundle_member_entry.lid_reference
            bundle_member_index[bundle_member_lid] = {
                'LID': bundle_member_lid,
                'Reference Type': bundle_member_entry.reference_type,
                'Member Status': bundle_member_entry.member_status,
                'Path': ''}

    def fullpaths_populate(bundle_path):
        """Generate the filepaths to .xml and .lblx files within a subdirectory.

        The input 'directory' will be the path to the bundle directory_path.
        Any instance of .xml and .lblx files within the first level of
        subdirectories will be collected and appended to the list of fullpaths.
        """
        for root, dirs, files in os.walk(bundle_path):
            for file in files:
                if file.endswith(('.xml', '.lblx')):
                    fullpaths.append(os.path.join(root, file))
            break

    def index_bundle(list_of_paths):
        """Add the filepaths to the bundle_member_index.

        The input 'list_of_paths' is the previously generated 'fullpaths' from
        the fullpaths_populate function. If this function finds a LID whose 
        collection term is not shared with the path, it will print a terminal 
        message, but keep the file if it otherwise matches.
        """
        fullpaths_sorted = sorted(list_of_paths)
        for fullpath in fullpaths_sorted:
            root = (objectify.parse(fullpath,
                                    objectify.makeparser(
                                        remove_blank_text=True))
                    .getroot())
            shortpath = fullpath.replace(directory_path, bundle_name)
            lid = root.Identification_Area.logical_identifier.text
            if lid not in bundle_member_lids:
                print(f'LID {lid} found in file structure at {shortpath} but '
                       'is not a bundle member.')
            else:
                bundle_member_index[lid]['Path'] = shortpath

    def file_creator(bundle_location):
        """Create a .csv file in the bundle directory from the dictionary.

        This takes the bundle_location dictionary created by index_bundle
        and creates a csv file containing the dictionary's contents. This csv
        file is then placed in the same directory as the bundle.xml file for
        that bundle. The bundle_location is the path leading to the bundle.
        """
        with open(bundle_location + '/bundle_member_index.csv',
                  mode='w', encoding='utf8') as index_csv:
            bundle_member_index_writer = csv.DictWriter(
                index_csv,
                fieldnames=('LID',
                            'Reference Type',
                            'Member Status',
                            'Path'))
            bundle_member_index_writer.writeheader()
            for index in sorted(bundle_member_index):
                bundle_member_index_writer.writerow(bundle_member_index[index])
                
    create_bundle_members(directory_path)
    bundle_member_lids = ([bundle_member_index[x]['LID'] for x
                           in bundle_member_index])
    first_level_subdirectories = next(os.walk(directory_path))[1]
    # 'first_level_subdirectories' contains all of the subdirectories of the
    # top-level directory 'directory_path'. These are found by calling the
    # os.walk iterator once and extracting the list of directories returned,
    # which will always be at the top level.
    for first_level_subdirectory in first_level_subdirectories:
        file_location = os.path.join(directory_path, first_level_subdirectory)
        fullpaths_populate(file_location)
        index_bundle(sorted(fullpaths))

    for key in bundle_member_index:
        if bundle_member_index[key]['Path'] == '':
            if bundle_member_index[key]['Member Status'] == 'Primary':
                print( 'Primary bundle member '
                      f'{bundle_member_index[key]["LID"]} '
                       'has not been matched with a file path.')
                sys.exit(1)
            else:
                assert bundle_member_index[key]['Member Status'] == 'Secondary'
                print( 'Secondary bundle member '
                      f'{bundle_member_index[key]["LID"]} '
                       'has not been matched with a file path.')
    file_creator(directory_path)
################################################################################


ns = {'pds': 'http://pds.nasa.gov/pds4/pds/v1',
      'cassini': 'http://pds.nasa.gov/pds4/mission/cassini/v1'}

parser = argparse.ArgumentParser()
parser.add_argument('directorypath', type=str,
                    help='The path to the directory containing the bundles '
                         'you wish to scrape.')

args = parser.parse_args()

bundle_name = args.directorypath.split('/')[-1]
create_bundle_member_index(args.directorypath)
