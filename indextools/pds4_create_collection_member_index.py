"""Create a csv file of a collection product's information.

This module creates an index file containing the LIDs, VIDs, Member Status,
and filepaths of each file within a collection product. There are two command-line
arguments.

Usage:

python pds4_create_collection_member_index.py <collection_dir> [--filesuffix (xml|lblx)]

<collection_dir> is the root directory of the collection.
If given, --filesuffix specifies the type of label file; if not given, the default is xml
"""
import argparse
import os
import re
import sys
import pds4_index_tools as tools


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('collectionpath', type=str,
                        help='The path to the collection you wish to scrape')
    
    parser.add_argument('--filesuffix', type=str, default='xml',
                        help='The type of label file present within the collection')

    args = parser.parse_args()
    
    regex = r'[\w-]+\.(?:'+re.escape(args.filesuffix)+')'
    basedir, collection_name = os.path.split(args.collectionpath)
    # For collectionlabel_file, nlevels is set to 1 to limit the search to the top level.
    collectionlabel_file = tools.get_member_files(args.collectionpath,
                                                  1,
                                                  basedir,
                                                  regex)
    
    if len(collectionlabel_file) == 0:
        print(f'No label files ending in "{args.filesuffix}" exist '
              f'within this directory: {args.collectionpath}')
        sys.exit(1)
            
    if len(collectionlabel_file) > 1:
        print(f'Chosen directory {args.collectionpath} contains too '
              f'many toplevel label files: {collectionlabel_file}')
        sys.exit(1)
            
    collection_root = tools.get_index_root(basedir, collectionlabel_file[0])
    namespaces = tools.get_namespaces(collection_root)
    # Grab the collection product file
    collprod_file = tools.get_collprod_filepath(collection_root,
                                                namespaces)
    member_index = {}
    # Populate the member_index with required data, except filepaths
    tools.add_collection_data(args.collectionpath, collprod_file, member_index)
    collprod_paths = tools.get_member_files(args.collectionpath,
                                            None, 
                                            basedir,
                                            regex)
    # Crossmatches the LIDS of files with the collection product file's
    # contents.
    tools.dataprod_crossmatch(collprod_paths,
                              basedir,
                              collection_name,
                              member_index)
    for key in member_index:
        if member_index[key]['Path'] is None:
            lid = member_index[key]['LID']
            print(f'Data product with LID {lid} has no attributed filepath.')
            sys.exit(1)
        
    tools.create_results_file(args.collectionpath, 'collection', member_index)


if __name__ == '__main__':
    main()
