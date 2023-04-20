"""Create a csv file of a bundle's members and their information.

This module creates an index of all bundle member LIDs, reference types, and 
member status. The filepaths to any bundle member .xml/.lblx files within the 
first level of subdirectories is also included in the index. The final product 
is then put into a csv file and placed inside the bundle directory. 
"""
import argparse
import csv
from lxml import objectify
import os
import sys


def get_bundle_filepaths(bundle_directory):
    """Find and return the filepath of the bundle's bundle.xml file.
    
    In the event a path to the bundle.xml file is not found, a terminal
    message will print.
    
    Inputs:
        bundle_directory    The path to the bundle directory.
        
    Returns:
        bundlexml_path     The path to the bundle.xml file within the bundle.
    """
    bundlexml_path = None
    for path, subdirs, files in os.walk(bundle_directory):
        for file in files:
            if file == 'bundle.xml':
                bundlexml_path = os.path.join(path, file)
                break

    if bundlexml_path is None:
        print('No bundle.xml file exists within this bundle')
        sys.exit(1)
        
    return bundlexml_path
    
    
def get_bundle_members(bundlexml_path, ns):
    """Get all Bundle_Member_Entry sections from a bundle.xml file.
    
    Input:
        bundlexml_path               Path to the bundle.xml file
        
    Returns:
        bundle_member_entries    All elements within the bundle.xml file that
                                 are tagged "Bundle_Member_Entry"
    """
    bundle_root = (objectify.parse(bundlexml_path,
                                   objectify.makeparser(
                                       remove_blank_text=True))
                            .getroot())

    bundle_member_entries = bundle_root.findall('pds:Bundle_Member_Entry',
                                                namespaces=ns)
    
    return bundle_member_entries


def add_to_index(bundle_member_entry, bundle_member_index):
    """Scrape the LID from the bundle.xml file.
    
    Inputs:
        bundle_member_entry    The element within the bundle.xml file 
                               containing the necessary information about the
                               bundle member.
                             
        bundle_member_index    The dictionary of bundle member information that
                               will have the following added to it:
                                   
            "LID"                  The LID of the bundle member
            
            "Reference Type"       The reference type of the bundle member
            
            "Member Status"        The member status of the bundle member
                                   ('Primary' or 'Secondary')
                                   
            "Path"                 The path to the .xml/.lblx file for the
                                   bundle member. The "Path" section is 
                                   intentionally left blank. This will be 
                                   filled in later in the index_bundle function.
    """
    bundle_member_lid = bundle_member_entry.lid_reference
    bundle_member_index[bundle_member_lid] = {
        'LID': bundle_member_lid,
        'Reference Type': bundle_member_entry.reference_type,
        'Member Status': bundle_member_entry.member_status,
        'Path': ''}


def fullpaths_populate(bundle_directory, fullpaths):
    """Generate the filepaths to .xml and .lblx files within a subdirectory.
    
    Any instance of .xml and .lblx files within the first level of
    subdirectories will be collected and appended to the list of fullpaths.
    
    Inputs:
        bundle_directory    The path to the bundle directory
        
        fullpaths      The list to be populated with filepaths
    """
    for root, dirs, files in os.walk(bundle_directory):
        for file in files:
            if file.endswith(('.xml', '.lblx')):
                fullpaths.append(root + '/' + file)
        break


def index_bundle(fullpaths, bundle_directory, bundle_member_lids,
                 bundle_member_index, bundle_name):
    """Add the filepaths to the bundle_member_index.
    
    If this function finds a LID whose 
    collection term is not shared with the path, it will print a terminal 
    message.
    
    Inputs:
        fullpaths              The list of filepaths to all .xml/.lblx files 
                               within the bundle that exist inside the first 
                               level of subdirectories.
                     
        bundle_directory         The path to the bundle directory
        
        bundle_member_lids     The LIDs of all the bundle members that belong in
                               the bundle.
                              
        bundle_member_index    The dictionary containing the information of all
                               bundle members within a bundle.
                               
        bundle_name            The name of the bundle.
    """
    fullpaths_sorted = sorted(fullpaths)
    for fullpath in fullpaths_sorted:
        root = (objectify.parse(fullpath,
                                objectify.makeparser(
                                    remove_blank_text=True))
                .getroot())
        lid = root.Identification_Area.logical_identifier.text
        if lid not in bundle_member_lids:
            print(f'LID {lid} found in file structure at '
                  f'{fullpath.replace(bundle_directory, bundle_name)} but is '
                   'not a bundle member.')
        else:
            bundle_member_index[lid]['Path'] = fullpath
            
            
def get_shortpath(bundle_member_index, bundle_directory, bundle_name):
    """Replace the filepath for a bundle member with a shortened version.

    Inputs:
        bundle_member_index    The dictionary containing the information of all
                               bundle members within a bundle.
                               
        bundle_directory        Path to the bundle directory.
        
        bundle_name           Name of the bundle.
    """
    for key in bundle_member_index:
        fullpath = bundle_member_index[key]['Path']
        shortpath = fullpath.replace(bundle_directory, bundle_name)
        bundle_member_index[key]['Path'] = shortpath
            

def file_creator(bundle_location, bundle_member_index):
    """Create a .csv file in the bundle directory from the dictionary.

    This takes the bundle_member_index dictionary and creates a csv file 
    containing the dictionary's contents. This csv file is then placed in the 
    top level of the  bundle.
    
    Inputs:
        bundle_location        The path to the bundle
        
        bundle_member_index    The dictionary containing the information of all
                               bundle members within a bundle.
    """
    with open(os.path.join(bundle_location, 'bundle_member_index.csv'),
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
                
def main():
    ns = {'pds': 'http://pds.nasa.gov/pds4/pds/v1',
          'cassini': 'http://pds.nasa.gov/pds4/mission/cassini/v1'}
    bundle_member_index = {}
    fullpaths = []
    bundle_name = args.directorypath.split('/')[-1]
    bundle_directory = args.directorypath
    bundlexml_path = get_bundle_filepaths(bundle_directory)
    bundle_member_entries = get_bundle_members(bundlexml_path, ns)
    for bundle_member_entry in bundle_member_entries:
        add_to_index(bundle_member_entry, bundle_member_index)
    bundle_member_lids = ([bundle_member_index[x]['LID'] for x
                           in bundle_member_index])
    first_level_subdirectories = next(os.walk(bundle_directory))[1]
    # 'first_level_subdirectories' contains all of the subdirectories of the
    # top-level directory 'bundle_directory'. These are found by calling the
    # os.walk iterator once and extracting the list of directories returned,
    # which will always be at the top level.
    for first_level_subdirectory in first_level_subdirectories:
        file_location = bundle_directory + '/' + first_level_subdirectory
        fullpaths_populate(file_location, fullpaths)
        index_bundle(sorted(fullpaths), bundle_directory, bundle_member_lids,
                     bundle_member_index, bundle_name)

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
    get_shortpath(bundle_member_index, bundle_directory, bundle_name)
    file_creator(bundle_directory, bundle_member_index)
    
################################################################################

parser = argparse.ArgumentParser()
parser.add_argument('directorypath', type=str,
                    help='The path to the directory containing the bundles '
                         'you wish to scrape.')

args = parser.parse_args()

if __name__ == '__main__':
    main()
