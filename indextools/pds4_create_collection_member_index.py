"""
Creates an index file of collection member information.

This tool takes the input in the form of a path to a collection_*.xml file. The
file is then parsed to find the collection product's filename.
The collection product's file is then scraped for LIDVIDs (separated into LID
and VID) and member status. These values are then put into a dictionary. Each
file in the collection member directory is then scraped for its LIDVID and
crossmatched with the dictionary. If a file matches, its filepath is placed in
the same entry as its LID, VID and member status information. If no match is
found, a message is printed. The file will still be included in the collection
index.

The resulting dictionary of collection member information is then put into an
output file. This output file is then placed inside the collection member
directory.
"""
import argparse
import csv
import os
from lxml import objectify

def get_member_filepath(collection_directory):
    
    collectionxml_file = None
    for path, subdirs, files in os.walk(collection_directory):
        for file in files:
            if 'collection' in file and file.endswith('.xml'):
                collectionxml_file = os.path.join(path, file)
                break
    return collectionxml_file


def get_collectionprod_file(collection_directory, collectionxml_file):
    """Scrape the collection_*.xml file for the collection product's filename.

    Inputs:
        collection_directory    The path to the collection directory.

        collectionxml_file      The path to the collection's .xml file.

    Returns:
        collection_product_filename    The path to the collection product's
                                       file.
    """
    ns = {'pds': 'http://pds.nasa.gov/pds4/pds/v1',
          'cassini': 'http://pds.nasa.gov/pds4/mission/cassini/v1'}

    collection_product_filename = None

    collection_file_root = (objectify.parse(collectionxml_file,
                            objectify.makeparser(remove_blank_text=True)))

    collection_file = collection_file_root.findall('pds:File_Area_Inventory',
                                                   namespaces=ns)

    collection_product_filename = os.path.join(collection_directory,
                                       collection_file[0].File.file_name.text)

    return collection_product_filename


def add_to_index(collection_product_filename, collection_member_index):
    """Add information to the collection_member_index dictionary.

    Inputs:
        collection_product_filename    The path to the collection product's
                                       file.

        collection_member_index        The dictionary of collection member
                                       information. It will contain the
                                       following:

            "LID"                          The LID (Logical IDentifier) of the
                                           data file.

            "Member Status"                The member status of the data
                                           product.

            "VID"                          The VID (Version IDentifier) of the
                                           data file.

            "Path"                         The path to the data product. This
                                           is left blank to be filled in later.
    """
    with open(collection_product_filename, 'r') as collection_prod_file:
        lines = collection_prod_file.readlines()
        for line in lines:
            parts = line.split(',')
            lidvid = parts[-1].strip()
            lid = lidvid.split('::')[0]
            vid = lidvid.split('::')[-1]
            if lid == vid:
                vid = ''
            collection_member_index[str(lidvid)] = {
                'LID': lid,
                'VID': vid,
                'Member Status': parts[0],
                'Path': '__'}


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


def index_collection(fullpaths, collection_member_index, collection_directory):
    """Match the .xml/.lblx files to their filepaths.

    Inputs:
        collection_member_index    The dictionary of collection information.

        fullpaths                  The paths to the .xml/.lblx files inside
                                   the collection.
    """
    collection = collection_directory.split('/')[-1]
    fullpaths_sorted = sorted(fullpaths)
    for fullpath in fullpaths_sorted:
        root = (objectify.parse(fullpath,
                                objectify.makeparser(
                                    remove_blank_text=True)).getroot())
        lid = str(root.Identification_Area.logical_identifier)
        vid = str(root.Identification_Area.version_id)
        lidvid = lid + '::' + vid
        shortpath = fullpath.replace(collection_directory, collection)
        if lidvid in collection_member_index:
            collection_member_index[lidvid]['Path'] = shortpath
        else:
            print(f'PDS4 label found but not a member of this bundle: '
                  f'{shortpath}, {lid}')
            

def file_creator(collection_directory, collection_member_index):
    """Create an output file out of collection_member_index.

    Inputs:
        collection_directory       The path to the collection.

        collection_member_index    The dictionary of collection information.
    """
    with open(os.path.join(collection_directory, 'collection_member_index.csv'),
              mode='w') as index_file:
        collection_member_indexer = csv.DictWriter(
            index_file,
            fieldnames=([
                'LID',
                'VID', 
                'Member Status',
                'Path'
                ]))
        collection_member_indexer.writeheader()
        for index in sorted(collection_member_index):
            collection_member_indexer.writerow(collection_member_index[index])


def main():
    collection_member_index = {}
    fullpaths = []
    collectionxml_file = get_member_filepath(args.collectionpath)
    file = collectionxml_file.split('/')[-1]
    collection_directory = collectionxml_file.replace('/' + file, '')
    collection_product_filename = get_collectionprod_file(collection_directory,
                                                          collectionxml_file)
    add_to_index(collection_product_filename, collection_member_index)
    fullpaths_populate(collection_directory, fullpaths)
    index_collection(fullpaths, collection_member_index, collection_directory)
    file_creator(collection_directory, collection_member_index)


parser = argparse.ArgumentParser()
parser.add_argument('collectionpath', type=str,
                    help='The path to the collection you wish to scrape')

args = parser.parse_args()

if __name__ == '__main__':
    main()
