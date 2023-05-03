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
    def __init__(self, message):
        super().__init__(message)
        

def get_member_filepaths(directory, filename, level):
    """ Find and store all .xml/.lblx files that contain the filename.
    
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
        raise FilepathsNotFound(f'No files containing {filename} ending in '
                                 '".xml" or ".lblx" could be found.')
    return files_found



def main():
    bundlefiles = get_member_filepaths(args.directorypath, args.filename,
                                       args.level_to_look)
    for i in bundlefiles:
        print(i)
    
    
parser = argparse.ArgumentParser()
parser.add_argument('directorypath', type=str,
                    help='The path to the directory containing the bundles '
                         'you wish to scrape.')
parser.add_argument('--filename', type=str,
                    help='The name of the files to look for. "bundle" or '
                    '"collection" work.')
parser.add_argument('--level-to-look', type=int,
                    help='The number of levels down you want to search for '
                         'files.')

args = parser.parse_args()

if __name__ == '__main__':
    main()