"""Create a csv file of a bundle set's members and their information.

This module creates an index of all .xml and .lblx files within a bundle set,
sorted alphabetically by LID, and then stores it in the attributed bundle
directory for each bundle within the bundle set. There is a single command-line
argument, the path to the bundle set.
"""
import argparse
import csv
from lxml import objectify
import os
import sys

def bundle_file_paths(bundle_path):
    """Find and store paths to all bundle.xml files in bundle set.

    Generates the paths to bundle.xml files for each bundle within the
    bundle set, then appends them to a list to be iterated through. The
    bundle_path is the path to the bundle set.
    """
    bundlepaths = []
    for path, subdirs, files in os.walk(bundle_path):
        for file in files:
            if file == 'bundle.xml':
                bundlepaths.append(os.path.join(path, file))

    return bundlepaths


def create_bundle_members(bundle_path, bundle_member_index):
    """Populate the bundle_member_index dictionary with bundle information.

    The path to the bundle.xml file is parsed with lxml.objectify. The
    bundle member entries are found and scraped for their LID. This LID is
    put into the bundle_member_index dictionary as a key with the same LID,
    reference type, member status and a placeholder for the filepaths
    as values. This dictionary is then returned to be referenced in the 
    index_bundle function for crossmatching. The input bundle_path is the 
    path to the bundle.
    """
    bundle_root = (objectify.parse(bundle_path,
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


def fullpaths_populate(fullpaths, bundle_path):
    """Generate the filepaths to .xml and .lblx files within a subdirectory.

    The input 'bundle_path' will be the path to the bundle directory.
    ny instance of .xml and .lblx files within the first level of
    subdirectories will be collected and appended to the list of fullpaths.
    """
    for root, dirs, files in os.walk(bundle_path):
        for file in files:
            if file.endswith(('.xml', '.lblx')):
                fullpaths.append(root + '/' + file)
        break


def index_bundle(bundle_path, list_of_paths, bundle_member_lids,
                 bundle_member_index, bundle_name):
    """Add the filepaths to the bundle_member_index dictionary.

    The input 'list_of_paths' is the previously generated 'fullpaths' from
    the fullpaths_populate function. If this function finds a LID whose 
    collection term is not shared with the path, it will print a warning
    message.
    """
    fullpaths_sorted = sorted(list_of_paths)
    for fullpath in fullpaths_sorted:
        root = (objectify.parse(fullpath,
                                objectify.makeparser(
                                    remove_blank_text=True))
                .getroot())
        shortpath = fullpath.replace(bundle_path, bundle_name)
        lid = root.Identification_Area.logical_identifier.text
        if lid not in bundle_member_lids:
            print(f'LID {lid} found in file structure at {shortpath} but '
                   'is not a bundle member.')
        else:
            bundle_member_index[lid]['Path'] = shortpath


def file_creator(bundle_location, bundle_member_index):
    """Create a .csv file in the bundle directory from the dictionary.

    This takes bundle_member_index and creates a csv file at the location
    of bundle_location. The bundle_location is the path leading to the 
    bundle.
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


def create_bundle_member_index(dirpath):
    """Create the bundle_member_index.csv files for the bundle set."""
    bundle_set_name = dirpath.split('/')[-1]
    bundlepaths = bundle_file_paths(dirpath)
    for bundlepath in bundlepaths:
        fullpaths = []
        bundle_member_index = {}
        create_bundle_members(bundlepath, bundle_member_index)
        bundle_member_lids = ([bundle_member_index[x]['LID'] for x
                               in bundle_member_index])
        bundlepath = bundlepath.replace('/bundle.xml', '')
        bundle_name = bundlepath.split('/')[-1]
        first_level_subdirectories = next(os.walk(bundlepath))[1]
        for first_level_subdirectory in first_level_subdirectories:
            file_location = bundlepath + '/' + first_level_subdirectory
            fullpaths_populate(fullpaths, file_location)
        bundle_name = bundle_set_name + '/' + bundle_name
        index_bundle(bundlepath, sorted(fullpaths), bundle_member_lids,
                     bundle_member_index, bundle_name)
        for key in bundle_member_index:
            if bundle_member_index[key]['Path'] == '':
                if bundle_member_index[key]['Member Status'] == 'Primary':
                    print( 'Primary bundle member '
                          f'{bundle_member_index[key]["LID"]} '
                           'has not been matched with a file path.')
                    sys.exit(1)
                else:
                    assert (bundle_member_index[key]
                                              ['Member Status']) == 'Secondary'
                    print( 'Secondary bundle member '
                          f'{bundle_member_index[key]["LID"]} '
                           'has not been matched with a file path.')
        
        file_creator(bundlepath, bundle_member_index)


ns = {'pds': 'http://pds.nasa.gov/pds4/pds/v1',
      'cassini': 'http://pds.nasa.gov/pds4/mission/cassini/v1'}

parser = argparse.ArgumentParser()
parser.add_argument('directorypath', type=str,
                    help='The path to the directory containing the bundles '
                         'you wish to scrape.')

args = parser.parse_args()

create_bundle_member_index(args.directorypath)
