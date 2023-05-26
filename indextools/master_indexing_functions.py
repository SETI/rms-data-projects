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
        

def get_member_filepaths(directory, filename):
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
    if filename == 'bundle':
        level = 2
    else:
        assert filename == 'collection'
        level = 3
        
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


directory = '/Users/emiliesimpson/Emilie-Data/pds4-holdings/bundles/cassini_vims_cruise/'
filename = 'bundle'

x = get_member_filepaths(directory, filename)

# =============================================================================
# # In-progress function
# def add_to_index(filepath, filename, namespaces, member_index):
#     """Fills index with appropriate contents according to specified filename.
#     
#     Inputs:
#         filepath        the path(s) to the file containing the information
#         
#         filename        The keyword to determine which file to look for.
#         
#         namespaces        The xml schema to use in lxml parsing
#         
#         member_index        The index dictionary that will contain
#                             information depending on the filename.
#                                 
#     """
#     if 'bundle' in filename:
#         if filename == 'bundleset':
#             for file in filepath:
#                 bundle_root = (objectify.parse(file,
#                                                objectify.makeparser(
#                                                    remove_blank_text=True))
#                                         .getroot())
#                 bundle_lid = str(bundle_root.Identification_Area.logical_identifier.text)
#                 member_index[bundle_lid] = ({
#                     'LID': bundle_lid,
#                     'Path': file})
#         else:
#             assert filename == 'bundle'
#             bundle_root = (objectify.parse(filepath,
#                                            objectify.makeparser(
#                                                remove_blank_text=True))
#                                     .getroot())
#             bundle_member_entries = bundle_root.findall('pds:Bundle_Member_Entry',
#                                                         namespaces=namespaces)
#             for bundle_member_entry in bundle_member_entries:
#                 member_lid = bundle_member_entry.lid_reference
#                 member_index[member_lid] = {
#                     'LID': member_lid,
#                     'Reference Type': bundle_member_entry.reference_type,
#                     'Member Status': bundle_member_entry.member_status,
#                     'Path': '__'}
#             
#         
#     else:
#         assert filename == 'collection'
# 
#         collection_file_root = (objectify.parse(filepath,
#                                 objectify.makeparser(remove_blank_text=True)))
#         
#         collection_file = collection_file_root.findall('pds:File_Area_Inventory',
#                                                        namespaces=namespaces)
# 
#         collection_product_filename = filepath.replace(filepath.split('/')[-1],
#                                                    collection_file[0].File
#                                                                      .file_name
#                                                                      .text)
#     
#         with open(collection_product_filename, 'r') as collection_prod_file:
#             lines = collection_prod_file.readlines()
#             for line in lines:
#                 parts = line.split(',')
#                 lidvid = parts[-1].strip()
#                 lid = lidvid.split('::')[0]
#                 vid = lidvid.split('::')[-1]
#                 if lid == vid:
#                     vid = ''
#                 member_index[str(lidvid)] = {
#                     'LID': lid,
#                     'VID': vid,
#                     'Member Status': parts[0],
#                     'Path': '__'}
#                 
#                 
# def shortpaths(directory, bundle_name, member_index, fullpath):
#     """Shorten the paths in the member_index dictionary.
#     
#     Inputs:
#         directory            The path to the directory.
# 
#         subdirectory_name    The name of the source directory.
# 
#         member_index         The dictionary of indexed information.
# 
#         fullpath             The original path of the data file.
#     """
#     for key in member_index:
#         fullpath = member_index[key]['Path']
#         shortpath = fullpath.replace(directory, bundle_name)
#         member_index[key]['Path'] = shortpath
# 
# 
# def fullpaths_populate(directory, level):
#     """Generate the fullpaths to .xml and .lblx files within a subdirectory.
# 
#     Any instance of .xml and .lblx files within the chosen level of
#     subdirectories will be collected and appended to the list of fullpaths.
# 
#     Inputs:
#         directory    The path to the bundle directory.
# 
#         level        The allowed level of subdirectories the search can go.
#         
#     Returns:
#         fullpaths    The list to be populated with filepaths.
#     """
#     fullpaths = []
#     directory = os.path.abspath(directory)
#     for root, dirs, files in os.walk(directory):
#         if root.count(os.sep) - directory.count(os.sep) < level:
#             for file in files:
#                 if file.endswith(('.xml', '.lblx')):
#                     fullpaths.append(root + '/' + file)
#     
#     if fullpaths == []:
#         raise FilepathsNotFound('No files ending in ".xml" or ".lblx" could '
#                                 'be found in the given levels.')
# 
# 
# 
# 
# # NOT TESTED YET
# def file_creator(directory, file_name, member_index):
#     """Create the file of the results.
#     
#     Inputs:
#         directory    The path to the directory.
#         
#         file_name    The keyword to determine the contents.
#         
#         member_index    The index of bundle member/collection product
#                         information.
#     """
#     fieldnames = {}
#     # These are kept here until they have a place within the index population
#     # functions.
#     fieldnames['collection'] = ['LID', 'VID', 'Member Status', 'Path']
#     fieldnames['bundle'] = ['LID', 'Reference Type', 'Member Status', 'Path']
#     fieldnames['bundleset'] = ['LID', 'Path']
#     index_name = file_name+'_member_index.csv'
#     with open(os.path.join(directory, index_name),
#               mode='w', encoding='utf8') as index_file:
#         member_index_writer = csv.DictWriter(
#             index_file,
#             fieldnames=fieldnames[file_name])
#         member_index_writer.writeheader()
#         for index in sorted(member_index):
#             member_index_writer.writerow(member_index[index])
# 
# 
# def match_lids_to_files(fullpaths, filename, member_index):
# =============================================================================
    fullpaths_sorted = sorted(fullpaths)
    if 'bundle' in filename:
        if filename == 'bundleset':
            pass
        else:
            assert filename == 'bundle'
            for path in fullpaths_sorted:
                bundle_root = (objectify.parse(path,
                                               objectify.makeparser(
                                                   remove_blank_text=True))
                                        .getroot())
                lid = str(bundle_root.Identification_Area.logical_identifier.text)
                if lid in member_index:
                    member_index[lid]['Path'] = path
                else:
                    print(f'PDS4 label found but not a member of this bundle: '
                          f'{path}, {lid}')

    else:
        assert filename == 'collections'
        collection_root = (objectify.parse(path,
                                       objectify.makeparser(
                                           remove_blank_text=True))
                                .getroot())
        lid = str(collection_root.Identification_Area.logical_identifier.text)
        if lid in member_index:
            member_index[lid]['Path'] = path
        else:
            print(f'PDS4 label found but not a member of this bundle: '
                  f'{path}, {lid}')
    return member_index



