"""Create a csv file of a collection product's information.

This module creates an index file containing the LIDs, VIDs, Member Status,
and filepaths of each file within a collection product. There is a single
command-line argument, the path to the collection.
"""
import argparse
import os
import pds4_index_tools as tools


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('collectionpath', type=str,
                        help='The path to the collection you wish to scrape')

    args = parser.parse_args()
    
    basedir, collection_name = os.path.split(args.collectionpath)
    # Grab the path to the collection_*.xml file
    collectionlabel_file = tools.get_member_filepaths(args.collectionpath,
                                                      'collection',
                                                      collection_name)
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
    tools.add_collection_data(args.collectionpath, collprod_file,
                              member_index)
    collprod_paths = tools.find_all_data_products(args.collectionpath, 3,
                                                  collection_name)
    # Crossmatches the LIDS of files with the collection product file's
    # contents.
    tools.dataprod_crossmatch(collprod_paths, member_index,
                              args.collectionpath,
                              collection_name)
    tools.create_results_file(args.collectionpath, 'collection', member_index)


if __name__ == '__main__':
    main()
