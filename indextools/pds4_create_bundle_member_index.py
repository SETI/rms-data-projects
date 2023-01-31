#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Dec 19 15:21:01 2022

@author: emiliesimpson

This module creates a index of all .xml and .lblx files within a bundle, 
sorted alphabetically by LID. Input argument must be the path to the bundle
directory. End the path with a forward slash.

"""
import argparse
import csv
from lxml import objectify
import os


class BadLID(Exception):
    """
    This exception is raised in the event that a LID does not contain a 
    collection term. 
    
    In the event BadLID gets raised, it means that the file the LID was 
    derived from is not represented within the bundle, and therefore may 
    be misplaced from another bundle. 
    """
    'The LID does not contain an accepted collection term'
    pass


def create_bundle_members(directory_path):
    """
    Creates a dictionary of collection terms and their associated member 
    status and reference type.
    
    Input parameters are the path to the bundle. Because all instances of 
    bundle.xml are found recursively, this function works for both bundles 
    and bundle sets.
    """
    # Not all bundle.xml files within a bundle contain the same bundle member
    # entries, so we need to walk through all instances of bundle.xml.
    for path, subdirs, files in os.walk(directory_path): 
        for file in files: 
            if file == 'bundle.xml': 
                bundle_file_paths.append(os.path.join(path, file))
                    
        for bundle_file_path in bundle_file_paths: 
            bundle_root = (objectify.parse(bundle_file_path, 
                                           objectify.makeparser(
                                           remove_blank_text=True))
                                    .getroot())
              
            bundle_member_entries = bundle_root.findall('pds:Bundle_Member_Entry', 
                                                     namespaces=ns)
            
            # Some files may belong to a subset of collections while existing in a 
            # larger subdirectory. To ensure they get sorted into the proper entry
            # within the dictionary, we search for all available collection terms
            # within all files named bundle.xml. This ensures that files not
            # present in all subdirectories get sorted regardless of location.
            for bundle_member in bundle_member_entries: 
                lid_whole = (bundle_member.lid_reference
                                          .text
                                          .split(':'))
                collection_term = lid_whole[-1]
                if collection_term not in collection_terms: 
                    collection_terms.append(collection_term)
                    collections[str(collection_term)] = ({
                         'Reference Type' : str(bundle_member.reference_type), 
                         'Member Status' : str(bundle_member.member_status)})
                   
                    
def create_bundle_member_index(directory_path, bundle_structure):
    """
    Generates the paths to the correct files, places them in the correct places 
    within the dictionary, and exports the final product as a .csv file to the 
    correct spot in the directory.
    
    Input parameters are the path to the bundle and the bundle format boolean. 
    The default is True, assuming a bundle format. If False, assumes a bundle 
    set format.
    """  
    #bundle grabber
    def fullpaths_populate(subdirectory):
        """
        Generates the list of fullpaths to all .xml and .lblx files within a 
        subdirectory.
        
        Input value is the path to the bundle. Any instance of .xml and .lblx 
        files within the top level of the subdirectory will be collected. 
        This includes any data products that reside in the top level.
        """
        for root, dirs, files in os.walk(subdirectory): 
            for file in files: 
                if file.endswith(('.xml', '.lblx')): 
                     fullpaths.append(os.path.join(root, file))
            break
        return fullpaths
    
    def index_bundle(list_of_paths):
        """
        Generates entries for bundle_member_index containing the LID, member 
        status, reference type, and path to the file.
        
        Input value is the previously generated return value 'fullpaths' from 
        the fullpaths_populate function. 
        If this function finds a LID whose collection term is not shared with 
        the path, it will raise a terminal message, but keep the file if it 
        otherwise matches.
        """
        fullpaths_sorted = sorted(list_of_paths)
        for fullpath in fullpaths_sorted: 
            root = (objectify.parse(fullpath,
                                    objectify.makeparser(remove_blank_text=True))
                             .getroot())
            lid = str(root.Identification_Area.logical_identifier)
            for term in collection_terms: 
                if term in lid:
                    if term not in fullpath:
                        print(f'PDS4 label found but not a member of this '
                              f'bundle: {fullpath}, {lid}.')
                        continue
                    elif not[term in lid for term in collection_terms]: 
                        raise BadLID
                    fullpath = fullpath.replace(directory_path, 
                                                bundle_name + '/')
                    bundle_member_index[lid] = (
                        {'LID' : lid,
                         'Reference Type' : collections[term]['Reference Type'],
                         'Member Status' : collections[term]['Member Status'],
                         'Path' : fullpath})
        return bundle_member_index
    
    def file_creator(bundle_location): 
        """
        Creates a .csv file within the bundle directory containing the contents
        of the bundle_member_index dictionary. 
        
        Input value is the path leading to the bundle. 
        """
        with open(bundle_location + '/bundle_member_index.csv',
                  mode='w') as index_csv: 
            bundle_member_index_writer = csv.DictWriter(index_csv, 
                                    fieldnames=['LID',
                                                'Reference Type',
                                                'Member Status',
                                                'Path'])
            bundle_member_index_writer.writeheader()
            for index in sorted(bundle_member_index): 
                bundle_member_index_writer.writerow(bundle_member_index[index])
    
    first_level_subdirectories = next(os.walk(directory_path))[1]
    
    # While the code to scrape a singular bundle is implemented as its own 
    # module, extra steps need to be taken in order to scrape individual 
    # bundles within a bundle set.
    if not bundle_structure: 
        for first_level_subdirectory in first_level_subdirectories: 
            fullpaths.clear()
            bundle_member_index.clear()
            file_location = directory_path + first_level_subdirectory
            bundle_directories = next(os.walk(file_location))[1]
            for bundle_directory in bundle_directories: 
                path_to_bundle = file_location + '/' + bundle_directory
                file_paths = fullpaths_populate(path_to_bundle)
                index_bundle(sorted(file_paths))
                file_creator(file_location)
    else: 
        for first_level_subdirectory in first_level_subdirectories: 
            file_location = directory_path + first_level_subdirectory
            file_paths = fullpaths_populate(file_location)
            index_bundle(sorted(file_paths))
            file_creator(directory_path)

ns = {'pds':'http://pds.nasa.gov/pds4/pds/v1',
      'cassini': 'http://pds.nasa.gov/pds4/mission/cassini/v1'}

collections = {}
bundle_file_paths = []
collection_terms = []
fullpaths = []
bundle_member_index = {}

parser = argparse.ArgumentParser()
parser.add_argument('directorypath', type=str, nargs=1,
                    help='The path to the directory containing the bundles '
                         'you wish to scrape.')

parser.add_argument('--bundle', action='store_true',
                    help='State this argument when you are scraping a bundle.')
parser.add_argument('--bundleset', dest='bundletype', 
                    action='store_false',
                    help='State this argument when you are scraping a bundle '
                         'set.')
parser.set_defaults(bundletype=True)

args = parser.parse_args()

bundle_name = args.directorypath[0].split('/')[-2]
create_bundle_members(args.directorypath[0])
create_bundle_member_index(args.directorypath[0], args.bundletype)