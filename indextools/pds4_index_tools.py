"""The collection of functions that can be used to scrape, index, and return
a data product's information.
"""

import csv
import os

from lxml import objectify


class FilepathsNotFound(Exception):
    """Stop the program if no files were found."""

    def __init__(self, message):
        super().__init__(message)


def get_member_filepaths(directory, nlevels, filename):
    """Find and store all .xml/.lblx files that contain the filename.

    Inputs:
        directory      The path to the directory containing the
                       bundle/collection.

        nlevels        The number of levels down within the directory the
                       search can go.

        filename       The chosen keyword to search the directory with.

    Returns:
        files_found    The results of the file search. If empty, an exception
                       is raised.
    """
    files_found = []

    directory = os.path.abspath(directory)
    for root, __, files in os.walk(directory):
        if root.count(os.sep) - directory.count(os.sep) < nlevels:
            for file in files:
                if file.endswith(('.xml', '.lblx')):
                    if filename in file:
                        files_found.append(os.path.join(root, file))

    if not files_found:
        raise FilepathsNotFound(f'No files containing "{filename}" ending in '
                                '".xml" or ".lblx" could be found in the '
                                'given levels.')
    return files_found


def get_schema(xml_files):
    """Find all namespaces utilized by a bundle.

    Inputs:
        xml_files    The filepath(s) of bundle.xml files to look in.
    """
    namespaces = {'pds': 'http://pds.nasa.gov/pds4/pds/v1',
                  'cassini': 'http://pds.nasa.gov/pds4/mission/cassini/v1'}
    for file in xml_files:
        with open(file, 'r', encoding='utf8') as xml_file:
            xml_file = xml_file.readlines()
            for line in xml_file:
                if 'xmlns:' in line:
                    line = line.replace('xmlns:', '').strip()
                    line = line.replace('"', '')
                    line = line.split('=')
                    namespaces.update({line[0]: line[-1]})
    return namespaces


def fullpaths_populate(directory, nlevels):
    """Generate the fullpaths to .xml and .lblx files within a subdirectory.

    Any instance of .xml and .lblx files within the chosen level of
    subdirectories will be collected and appended to the list of fullpaths.

    Inputs:
        directory    The path to the bundle directory.

        nlevels      The allowed level of subdirectories down the search
                     can go.

    Returns:
        fullpaths    The list to be populated with filepaths.
    """
    fullpaths = []
    directory = os.path.abspath(directory)
    for root, __, files in os.walk(directory):
        if root.count(os.sep) - directory.count(os.sep) < nlevels:
            for file in files:
                if file.endswith(('.xml', '.lblx')):
                    fullpaths.append(root + '/' + file)

    if not fullpaths:
        raise FilepathsNotFound('No files ending in ".xml" or ".lblx" could '
                                'be found in the given levels.')

    return fullpaths


def create_member_index(member_index, labels, shortpath, lid):
    """Create the empty index with correct labels and contents.

    Inputs:
        member_index    The dictionary that will contain the information
                        of the data product

        labels          The labels to put into member_index

        shortpath       The shortened path to the file. If none exists, just
                        use '__'

        lid             The LID of the indexed data. This will be used as the
                        identifier for crossmatching.
    """

    temp_dict = {}
    for label in labels:
        if label == 'LID':
            temp_dict.update({label: lid})
        elif label == 'Path':
            temp_dict.update({label: shortpath})
        else:
            temp_dict.update({label: '__'})
        temp_dict = dict((temp_dict.items()))
        member_index[lid] = temp_dict


def get_index_root(path):
    """Return the root of the data product .xml file.

    Inputs:
        path          The path to the data product's .xml file.

    Returns:
        index_root    The lxml root of the data product.
    """
    index_root = (objectify.parse(path,
                                  objectify.makeparser(
                                      remove_blank_text=True))
                  .getroot())
    return index_root


def get_bundle_lid(bundle_root):
    """Search the xml file for the LID.

    Inputs:
        bundle_root    The root of the bundle.xml file.

    Returns:
        bundle_lid     The LID of the bundle.xml file
    """
    bundle_lid = str(
        bundle_root.Identification_Area.logical_identifier.text)
    return bundle_lid


def get_bundle_entries(bundle_root, namespaces):
    """Grab the bundle member entries containing the bundle information.

    Inputs:
        bundle_root              The root of the bundle.xml file

        namespaces               The namespaces of the bundle.xml's data products

    Returns:
        bundle_member_entries    The entries of the bundle members containing
                                 the info for the index.
    """
    bundle_member_entries = bundle_root.findall('pds:Bundle_Member_Entry',
                                                namespaces=namespaces)
    return bundle_member_entries


def add_bundle_data(bundle_member_entries, member_index):
    """Add the bundle member info to the member_index dictionary.

    Inputs:
        bundle_member_entries    The entries of the bundle members containing
                                 the info for the index.

        member_index             The dictionary that will contain the information
                                 of the data product.
    """
    for entry in bundle_member_entries:
        member_lid = str(entry.lid_reference)
        create_member_index(member_index,
                            ['LID', 'Reference Type', 'Member Status'],
                            '__',
                            member_lid)
        member_index[member_lid]['Reference Type'] = str(entry.reference_type)
        member_index[member_lid]['Member Status'] = str(entry.member_status)


def bundle_crossmatch(fullpaths, member_index, directory,
                      subdirectory_name):
    """Match the LID of a file to its counterpart in the dictionary.

    Inputs:
        fullpaths            The paths to the collected files.

        member_index         The dictionary of indexed information.

        directory            The path to the directory containing the
                             bundle/collection.

        subdirectory_name    The name of the bundle member.
    """
    fullpaths_sorted = sorted(fullpaths)
    for path in fullpaths_sorted:
        bundle_root = (objectify.parse(path,
                                       objectify.makeparser(
                                           remove_blank_text=True))
                       .getroot())
        lid = str(
            bundle_root.Identification_Area.logical_identifier.text)
        if lid in member_index:
            path = shortpaths(path, directory, subdirectory_name)
            member_index[lid]['Path'] = path
        else:
            path = shortpaths(path, directory, subdirectory_name)
            print(f'PDS4 label found but not a member of this bundle: '
                  f'{path}, {lid}')


def get_collection_entries(collection_root, namespaces, collection_directory):
    """Return the collection product filepath from the collection_*.xml file.

    Inputs:
        collection_root                The root of the collection_*.xml file.

        namespaces                     The namespaces present in the
                                       collection_*.xml file.

        collection_directory           The directory containing the
                                       collection_*.xml file.

    Returns:
        collection_product_filename    The collection product file.
    """
    collection_file = collection_root.findall('pds:File_Area_Inventory',
                                              namespaces=namespaces)
    collection_product_filename = os.path.join(collection_directory,
                                               collection_file[0].File
                                               .file_name
                                               .text)
    return collection_product_filename


def add_collection_data(collectionprod_file, member_index):
    """Populate the member_index with the collection product information.

    Inputs:
        collectionprod_file    The path to the collection product file.

        member_index           The dictionary of indexed information.
    """
    with open(collectionprod_file, 'r', encoding='utf8') as collection_prod_file:
        lines = collection_prod_file.readlines()
        for line in lines:
            parts = line.split(',')
            lidvid = parts[-1].strip()
            lid = lidvid.split('::')[0]
            vid = lidvid.split('::')[-1]
            if lid == vid:
                vid = ''
            create_member_index(member_index,
                                ['LID', 'VID', 'Member Status', 'Path'],
                                '__', lid)
            member_index[lid]['Member Status'] = parts[0]
            member_index[lid]['VID'] = vid


def collection_crossmatch(fullpaths, member_index, directory,
                          subdirectory_name):
    """Match the LID of a file to its counterpart in the dictionary.

    Inputs:
        fullpaths    The list of filepaths to files in the collection.

        member_index    The dictionary of indexed information.

        directory       The path to the directory containing the collection.

        subdirectory_name    The name of the collection member.

    """
    fullpaths_sorted = sorted(fullpaths)
    for path in fullpaths_sorted:
        collection_root = (objectify.parse(path,
                                           objectify.makeparser(
                                               remove_blank_text=True))
                           .getroot())
        lid = str(collection_root.Identification_Area.logical_identifier)
        path = shortpaths(path, directory, subdirectory_name)
        if lid in member_index:
            member_index[lid]['Path'] = path
        else:
            print(f'PDS4 label found but not a member of this collection: '
                  f'{path}, {lid}')


def shortpaths(fullpath, directory, subdirectory_name):
    """Shorten the paths in the member_index dictionary.

    Inputs:

        fullpath             The original path of the file.

        directory            The path to the directory.

        subdirectory_name    The name of the source directory.

    Returns:
        shortpath            The shortened version of the filepath.
    """
    shortpath = fullpath.replace(directory, subdirectory_name + '/')
    return shortpath


def file_creator(directory, filename, member_index):
    """Create the file of the results.

    Inputs:
        directory       The path to the directory.

        filename       The keyword to determine the name of the file.

        member_index    The index of bundle member/collection product
                        information.
    """
    __ = list(member_index.keys())[0]
    labels = list(member_index[__].keys())
    index_name = filename+'_member_index.csv'
    with open(os.path.join(directory, index_name),
              mode='w', encoding='utf8') as index_file:
        member_index_writer = csv.DictWriter(
            index_file,
            fieldnames=labels)
        member_index_writer.writeheader()
        for index in member_index:
            member_index_writer.writerow(member_index[index])
