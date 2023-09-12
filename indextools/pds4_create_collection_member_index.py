"""Create a csv file of a collection product's information.

This module creates an index file containing the LIDs, VIDs, Member Status,
and filepaths of each file within a collection product. There are two command-line
arguments, the path to the collection and the file type of the label files. The label
files can be .xml or .lblx files, but if none are specified, it will default to .xml.
"""
import argparse
import os
import sys
import pds4_index_tools as tools


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('collectionpath', type=str,
                        help='The path to the collection you wish to scrape')
    
    parser.add_argument('--filesuffix', nargs='?',  const=1, type=str, default='xml',
                        help='The type of label file present within the collection')

    args = parser.parse_args()
    
    basedir, collection_name = os.path.split(args.collectionpath)
    # Grab the path to the collection_*.xml file
    collectionlabel_file = tools.get_member_files(args.collectionpath,
                                                  1,
                                                  collection_name,
                                                  args.filesuffix)
    
    if len(collectionlabel_file) == 0:
        try:
            raise tools.NoLabelsFound(f'No label files ending in "{args.filesuffix}" exist '
                                          f'within this directory: {args.collectionpath}')
        except tools.NoLabelsFound as e:
            print(e)
            sys.exit(1)
            
    if len(collectionlabel_file) > 1:
        try:
            raise tools.TooManyLabels(f'Chosen directory {args.collectionpath} contains too '
                                      f'many toplevel label files: {collectionlabel_file}')
        except tools.TooManyLabels as e:
            print(e)
            sys.exit(1)
            
    collection_root = tools.get_index_root(args.collectionpath.replace(
        collection_name, ''),
        collectionlabel_file[0])
    namespaces = tools.get_namespaces(args.collectionpath.replace(
        collection_name, ''),
        collectionlabel_file)
    # Grab the collection product file
    collprod_file = tools.get_collprod_filepath(collection_root,
                                                namespaces)
    member_index = {}
    # Populate the member_index with required data, except filepaths
    tools.add_collection_data(args.collectionpath, collprod_file, member_index)
    collprod_paths = tools.get_member_files(args.collectionpath,
                                            None, 
                                            collection_name,
                                            args.filesuffix)
    # Crossmatches the LIDS of files with the collection product file's
    # contents.
    tools.dataprod_crossmatch(collprod_paths,
                              args.collectionpath,
                              collection_name,
                              member_index)
    for key in member_index:
        try:
            if member_index[key]['Path'] == None:
                lid = member_index[key]['LID']
                raise tools.MissingLabel(f'Data product with LID {lid} has no attributed '
                                          'filepath.')
        except tools.MissingLabel as e:
            print(e)
            sys.exit(1)
        
    tools.create_results_file(args.collectionpath, 'collection', member_index)


if __name__ == '__main__':
    main()
