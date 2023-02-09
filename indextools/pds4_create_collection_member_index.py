#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jan 25 12:36:24 2023

@author: emiliesimpson

This tool creates a .csv file listing the members of a collection, their 
associated member status, LID, their associated VID, and the attributed path. 
"""

import csv
import os

import argparse
from lxml import objectify
from lxml import etree

# FILE GENERATOR

def create_collection_member_index(directory_path, bundle_structure):

    for path, subdirs, files in os.walk(directory_path):
        for file in files:
            if 'collection_' in file:
                if file.endswith('.xml'):
                    collection_files.append(os.path.join(path, file))


    for collection_file_path in collection_files:
        
        collection = collection_file_path.split('/')[-2]
        
        collection_file_root = (objectify.parse(collection_file_path, 
                                objectify.makeparser(remove_blank_text=True)))
                                
        collection_file = collection_file_root.findall('pds:File_Area_Inventory',
                                                        namespaces=ns)
        
        collection_csv_path = os.path.join(directory_path + '/' + collection, 
                                           collection_file[0].File.file_name.text)
        print(collection_csv_path)
        
        with open(collection_csv_path, 'r') as csv_file:
            csv_lines = csv_file.readlines()
            for line in csv_lines:
                parts = line.split(',')
                lidvid = parts[-1]
                lid = lidvid.split('::')[0]
                vid = lidvid.split('::')[-1]
                collection_members[str(lid)] = {
                    'LID' : str(lid),
                    'Member Status' : parts[0],
                    'VID' : vid,
                    'Path' : '__'}
            
            
        for root, dirs, files in os.walk(directory_path + '/' + collection): 
            for file in files: 
                if file.endswith(('.xml', '.lblx')): 
                     fullpaths.append(os.path.join(root, file))
    return fullpaths 
                     
                     
                     
def file_writer(directory_path, filepaths):
    
    fullpaths_sorted = sorted(filepaths)
                 
    for fullpath in fullpaths_sorted:
            root = (objectify.parse(fullpath,
                                    objectify.makeparser(remove_blank_text=True))
                             .getroot())
            lid = str(root.Identification_Area.logical_identifier)
            if lid in collection_members:
                collection_members[lid]['Path'] = fullpath

    with open(directory_path + '/collection_member_index.csv',
              mode='w') as index_csv: 
        collection_member_index_writer = csv.DictWriter(index_csv, 
                                fieldnames=['LID',
                                            'Member Status',
                                            'Path',
                                            'VID'])
        collection_member_index_writer.writeheader()
        for index in sorted(collection_members): 
            collection_member_index_writer.writerow(collection_members[index])

ns = {'pds':'http://pds.nasa.gov/pds4/pds/v1',
      'cassini': 'http://pds.nasa.gov/pds4/mission/cassini/v1'}

collection_files = []
collection_members = {}
fullpaths = []


# =============================================================================
# directory_path = ('/Users/emiliesimpson/holdingsdisk/pds4-holdings'
#                   '/bundles/uranus_occs_earthbased')
# =============================================================================

        
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

# One function to get the files
# One function to fill the dictionary and write the csv

if args.bundletype:
    create_collection_member_index(args.directorypath[0], args.bundletype)
    file_writer(args.directorypath[0], fullpaths)
    
elif not args.bundletype:
    first_level_subdirectories = next(os.walk(args.directorypath[0]))[1]
    for first_level_subdirectory in first_level_subdirectories:
        create_collection_member_index((args.directorypath[0] + '/' + 
                                        first_level_subdirectory), 
                                        args.bundletype)
        file_writer(args.directorypath[0] + '/' + first_level_subdirectory, 
                    fullpaths)

