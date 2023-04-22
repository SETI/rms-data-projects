"""
This tool creates a .csv file listing the members of a collection, their
associated member status, LID, VID, and the filepath.
"""
import argparse
import csv
import os
from lxml import objectify


def get_collectioncsv_file(collection_directory, collectionxml_file):
    """Scrape the collection.xml files for the collection.csv filenames.

    Inputs:
        collection_directory      The path to the collection directory.

        collectionxml_file         The path to the collection.xml file.

    Returns:
        collection_csv_path    The path to the collection's csv file.
    """
    namespaces = {'pds':'http://pds.nasa.gov/pds4/pds/v1',
                  'cassini': 'http://pds.nasa.gov/pds4/mission/cassini/v1'}

    collection_csv_path = None

    collection_file_root = (objectify.parse(collectionxml_file,
                            objectify.makeparser(remove_blank_text=True)))

    collection_file = collection_file_root.findall('pds:File_Area_Inventory',
                                                    namespaces=namespaces)

    collection_csv_path = os.path.join(collection_directory,
                                         collection_file[0].File.file_name.text)

    return collection_csv_path


def add_to_index(collection_csv_path, collection_members):
    """Add information to the collection_members dictionary.

    Inputs:
        collection_csv_path    The path to the collection csv file.

        collection_members     The dictionary of collection member information.
                               It will contain the following:

            "LID"                  The LID (Logical IDentifier) of the data
                                   file.

            "Member Status"        The member status of the data product.

            "VID"                  The VID (Version IDentifier) of the data
                                   file.

            "Path"                 The path to the data product. This is left
                                   blank to be filled in later.
    """
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


def fullpaths_populate(collection_directory, fullpaths):
    """Find and store all paths to .xml/.lblx files in a collection.

    Inputs:
        collection_directory     The path to the collection.

        fullpaths                The paths to the .xml/.lblx files inside the
                                 collection.
    """
    for root, dirs, files in os.walk(collection_directory):
        for file in files:
            if file.endswith(('.xml', '.lblx')):
                fullpaths.append(os.path.join(root, file))


def index_collections(collection_members, fullpaths):
    """Match the .xml/.lblx files to their filepaths.

    Inputs:
        collection_members       The dictionary of collection information.

        fullpaths                The paths to the .xml/.lblx files inside the
                                 collection.
    """
    fullpaths_sorted = sorted(fullpaths)
    for fullpath in fullpaths_sorted:
        root = (objectify.parse(fullpath,
                                    objectify.makeparser(
                                        remove_blank_text=True)).getroot())
        lid = str(root.Identification_Area.logical_identifier)
        if lid in collection_members:
            collection_members[lid]['Path'] = fullpath


def file_creator(collection_directory, collection_members):
    """Create a csv file out of the contents of collection_members.

    Inputs:
        collection_directory    The path to the collection.

        collection members      The dictionary of collection information.
    """
    with open(os.path.join(collection_directory, 'collection_member_index.csv'),
              mode='w') as index_csv:
        collection_member_index_writer = csv.DictWriter(index_csv,
                                fieldnames=['LID',
                                            'Member Status',
                                            'Path',
                                            'VID'])
        collection_member_index_writer.writeheader()
        for index in sorted(collection_members):
            collection_member_index_writer.writerow(collection_members[index])


def main():
    collection_members = {}
    fullpaths = []
    collectionxml_file = args.collectionpath
    file = args.collectionpath.split('/')[-1]
    collection_directory = collectionxml_file.replace(file, '')
    collection_csv_path = get_collectioncsv_file(collection_directory,
                                                collectionxml_file)
    add_to_index(collection_csv_path, collection_members)
    fullpaths_populate(collection_directory, fullpaths)
    index_collections(collection_members, fullpaths)
    file_creator(collection_directory, collection_members)


parser = argparse.ArgumentParser()
parser.add_argument('collectionpath', type=str,
                    help='The path to the collection you wish to scrape')
parser.set_defaults(bundletype=True)

args = parser.parse_args()

if __name__ == '__main__':
    main()
    