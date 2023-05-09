"""Create indexes of bundle members and collections in bundles and bundlesets.

This file contains the shared functions of pds4_create_bundle_member_index.py,
pds4_create_budnleset_member_index.py, and pds4_create_collection_member_
index.py. 

"""
import argparse
import csv
from lxml import objectify
import os
import sys


class FilepathsNotFound(Exception):
    """Stop the program if no files were found in get_member_filepaths."""
    
    def __init__(self, message):
        super().__init__(message)
        

def get_member_filepaths(directory, filename, level):
    """Find and store all .xml/.lblx files that contain the filename.
    
    Inputs:
        directory    The path to the directory containing the bundle/collection.
        
        filename     The chosen keyword to search the directory with.
        
        level        The allowed level of subdirectories the search can go.
        
    Returns:
        files_found    The results of the file search. If empty, an exception
                       is raised.
    """
    files_found = []
    directory = os.path.abspath(directory)
    for root, dirs, files in os.walk(directory):
        if root.count(os.sep) - directory.count(os.sep) < level:
            for file in files:
                if file.endswith(('.xml', '.lblx')):
                    if filename in file:
                        files_found.append(os.path.join(root, file))
                        
    if files_found == []:
        raise FilepathsNotFound(f'No files containing "{filename}" ending in '
                                 '".xml" or ".lblx" could be found in the '
                                 'given levels.')
    return files_found


def get_schema(bundlexml_files, namespaces):
    """Find all namespaces utilized by a bundle.
    
    Inputs:
        bundlexml_files    The filepath(s) of bundle.xml files to look in.
        
        namespaces         The dictionary to contain the namespaces of the
                           bundle.
    """
    for file in bundlexml_files:
        with open(file, 'r') as xml_file:
            xml_file = xml_file.readlines()
            for line in xml_file:
                if 'xmlns:' in line:
                    line = line.replace('xmlns:', '').strip()
                    line = line.replace('"', '')
                    line = line.split('=')
                    namespaces.update({line[0]: line[-1]})
    return namespaces


# Get bundle members

def get_bundle_members(filepath, ns):
    """Get all Bundle_Member_Entry sections from a bundle.xml file.

    Input:
        bundlexml_path               Path to the bundle.xml file.
        
        ns                           The bundle namespaces.

    Returns:
        bundle_member_entries        All elements within the bundle.xml file
                                     that are tagged "Bundle_Member_Entry".
    """
    bundle_root = (objectify.parse(filepath,
                                   objectify.makeparser(
                                       remove_blank_text=True))
                   .getroot())

    bundle_member_entries = bundle_root.findall('pds:Bundle_Member_Entry',
                                                namespaces=ns)

    return bundle_member_entries


def fullpaths_populate(directory, level):
    """Generate the fullpaths to .xml and .lblx files within a subdirectory.

    Any instance of .xml and .lblx files within the chosen level of
    subdirectories will be collected and appended to the list of fullpaths.

    Inputs:
        directory    The path to the bundle directory.

        level        The allowed level of subdirectories the search can go.
        
    Returns:
        fullpaths    The list to be populated with filepaths.
    """
    fullpaths = []
    directory = os.path.abspath(directory)
    for root, dirs, files in os.walk(directory):
        if root.count(os.sep) - directory.count(os.sep) < level:
            for file in files:
                if file.endswith(('.xml', '.lblx')):
                    fullpaths.append(root + '/' + file)
    
    if fullpaths == []:
        raise FilepathsNotFound('No files ending in ".xml" or ".lblx" could '
                                'be found in the given levels.')


def add_to_index():
    pass

# NOT TESTED YET
def file_creator(directory, file_name, fields, member_index):
    """Create the file of the results."""
    fieldnames = {}
    # These are kept here until they have a place within the index population
    # functions.
    fieldnames['collection'] = ['LID', 'VID', 'Member Status', 'Path']
    fieldnames['bundle'] = ['LID', 'Reference Type', 'Member Status', 'Path']
    fieldnames['bundleset'] = ['LID', 'Path']
    index_name = file_name+'_member_index.csv'
    with open(os.path.join(directory, index_name),
              mode='w', encoding='utf8') as index_file:
        member_index_writer = csv.DictWriter(
            index_file,
            fieldnames=fieldnames[file_name])
        member_index_writer.writeheader()
        for index in sorted(member_index):
            member_index_writer.writerow(member_index[index])


def shortpaths(): pass



