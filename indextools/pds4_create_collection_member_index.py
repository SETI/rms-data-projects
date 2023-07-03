"""Create a csv file of a collection product's information.

This module creates an index file containing the LIDs, VIDs, Member Status,
and filepaths of each file within a collection product. There is a single
command-line argument, the path to the collection.
"""
import argparse
import pds4_index_tools as tools


def main():
    collection_name = args.collectionpath.split('/')[-2]
    # Grab the path to the collection_*.xml file
    collectionxml_file = tools.get_member_filepaths(args.collectionpath, 3,
                                                    'collection')
    collection_root = tools.get_index_root(collectionxml_file[0])
    namespaces = tools.get_schema(collectionxml_file)
    # Grab the collection product file
    collectionprod_file = tools.get_collection_entries(collection_root, namespaces,
                                                       args.collectionpath)
    member_index = {}
    # Populate the member_index with required data, except filepaths
    tools.add_collection_data(collectionprod_file, member_index)
    fullpaths = tools.fullpaths_populate(args.collectionpath, 3)
    # Crossmatches the LIDS of files with the collection product file's
    # contents.
    tools.collection_crossmatch(fullpaths, member_index, args.collectionpath,
                                collection_name)
    tools.file_creator(args.collectionpath, 'collection', member_index)


parser = argparse.ArgumentParser()
parser.add_argument('collectionpath', type=str,
                    help='The path to the collection you wish to scrape')

args = parser.parse_args()

if __name__ == '__main__':
    main()
