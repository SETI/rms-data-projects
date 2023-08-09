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


# FIXIT: add search for lidvid_reference
def add_bundle_data(bundle_member_entries, member_index):
    """Add the bundle member info to the member_index dictionary.

    Inputs:
        bundle_member_entries    The list of all Bundle_Member_Entry elements
                                 within the .xml document. These were located
                                 under a root element found via lxml.objectify

        member_index             The dictionary that will contain the inform ation
                                 regarding the data product.
    """
    for entry in bundle_member_entries:
        try:
            member_lid = str(entry.lid_reference)
        except AttributeError:
            member_lid = str(entry.lidvid_reference).split('::')[0]
        member_lid_short = member_lid.split(':')[-1]
        create_member_index(member_index,
                            ['LID', 'Reference Type', 'Member Status'],
                            '__',
                            member_lid)
        member_index[member_lid_short]['Reference Type'] = str(entry.reference_type)
        member_index[member_lid_short]['Member Status'] = str(entry.member_status)
        
        
def add_collection_data(directory, collectionprod_file, member_index):
    """Populate the member_index with information about collection members.

    Inputs:
        collectionprod_file    The path to the collection product file.

        member_index           The dictionary of indexed information.
    """
    with open(os.path.join(directory, collectionprod_file), 'r',
              encoding='utf8') as collection_prod_file:
        lines = collection_prod_file.readlines()
        for line in lines:
            parts = line.split(',')
            lidvid = parts[-1].strip()
            lid = lidvid.split('::')[0]
            lid_short = lid.split(':')[-1]
            vid = lidvid.split('::')[-1]
            if lid == vid:
                vid = ''
            create_member_index(member_index,
                                ['LID', 'VID', 'Member Status', 'Path'],
                                '__', lid)
            member_index[lid_short]['Member Status'] = parts[0]
            member_index[lid_short]['VID'] = vid


def create_member_index(member_index, labels, shortpath, lid):
    """Create the empty index with correct labels and contents.

    Inputs:
        member_index    The dictionary that will contain the information
                        of the data product

        labels          The labels to put into member_index

        shortpath       The shortened path to the file. If none exists, just
                        use '_'

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
            temp_dict.update({label: '_'})
        temp_dict = dict((temp_dict.items()))
        member_index[lid.split(':')[-1]] = temp_dict
        
        
def dataprod_crossmatch(memberxml_paths, member_index, directory,
                          subdirectory_name):
    """Match the LID of a file to its counterpart in the dictionary.

    Inputs:
        memberxml_paths    The list of filepaths to files in the collection.

        member_index    The dictionary of indexed information.

        directory       The path to the directory containing the collection.

        subdirectory_name    The name of the collection member.

    """
    memberxml_paths_sorted = sorted(memberxml_paths)
    for path in memberxml_paths_sorted:
        root = (objectify.parse(os.path.join(directory.replace(
            subdirectory_name, ''), path
            ),
                                objectify.makeparser(
                                remove_blank_text=True))
                           .getroot())
        lid = str(root.Identification_Area.logical_identifier.text)
        if not any(lid in member_index[key]['LID'] for key in member_index):
            print(f'PDS4 label found but not a member of this collection: '
                  f'{path}, {lid}')
        else:
            for key in member_index:
                if lid == member_index[key]['LID']:
                    member_index[key]['Path'] = path


def file_creator(directory, keyword, member_index):
    """Create the file of the results.

    Inputs:
        directory       The path to the directory.

        keyword       The keyword to determine the name of the file.

        member_index    The index of bundle member/collection product
                        information.
    """
    _ = list(member_index.keys())[0]
    labels = list(member_index[_].keys())
    index_name = keyword+'_member_index.csv'
    with open(os.path.join(directory, index_name),
              mode='w', encoding='utf8') as index_file:
        member_index_writer = csv.DictWriter(
            index_file,
            fieldnames=labels)
        member_index_writer.writeheader()
        for index in member_index:
            member_index_writer.writerow(member_index[index])


def find_all_data_products(directory, nlevels, subdirectory_name):
    """Generate the paths to all .xml and .lblx files within a subdirectory.

    Any instance of .xml and .lblx files within the chosen level of
    subdirectories will be collected and appended to the list of xml filepaths.

    Inputs:
        directory    The path to the bundle directory.

        nlevels      The allowed level of subdirectories down the search
                     can go.

    Returns:
        memberxml_paths    The list to be populated with filepaths.
    """
    memberxml_paths = []
    directory = os.path.abspath(directory)
    for basedir, _, files in os.walk(directory):
        if basedir.count(os.sep) - directory.count(os.sep) < nlevels:
            for file in files:
                if file.endswith(('.xml', '.lblx')):
                    memberxml_paths.append(shortpaths(os.path.join(basedir, file),
                                     directory,
                                     directory[directory.find(subdirectory_name):]))

    if not memberxml_paths:
        raise FilepathsNotFound('No files ending in ".xml" or ".lblx" could '
                                'be found in the given levels.')

    return memberxml_paths


def get_bundle_entries(bundle_root, namespaces):
    """find and return all instances of Bundle_Member_Entry.

    Inputs:
        bundle_root              The root element of a given bundle.xml file

        namespaces               The namespaces of the bundle.xml's data
                                 products

    Returns:
        bundle_member_entries    A list containing all instances of
                                 Bundle_Member_Entry under the given
                                 root element.
    """
    bundle_member_entries = bundle_root.findall('pds:Bundle_Member_Entry',
                                                namespaces=namespaces)
    return bundle_member_entries


def get_bundle_lid(bundle_root):
    """Search a bundle.xml file for the LID.

    Inputs:
        bundle_root    The root element of a given bundle.xml file.

    Returns:
        bundle_lid     The LID of the bundle.xml file
    """
    bundle_lid = str(
        bundle_root.Identification_Area.logical_identifier.text)
    return bundle_lid


def get_collprod_filepath(collection_root, namespaces, collection_directory):
    """Return the collection product filepath from the collection_*.xml file.

    Inputs:
        collection_root                The root of the collection_*.xml file.

        namespaces                     The namespaces present in the
                                       collection_*.xml file.

        collection_directory           The directory containing the
                                       collection_*.xml file.

    Returns:
        collprod_filename    The collection product file.
    """
    collection_file = collection_root.findall('pds:File_Area_Inventory',
                                              namespaces=namespaces)
    collprod_filename = collection_file[0].File.file_name.text
    
    return collprod_filename


def get_index_root(directory, path):
    """Parse a data product .xml file and return its structured content.

    Inputs:
        path          The path to the data product's .xml file.

    Returns:
        index_root    The root element of the data product's .xml file.
    """
    index_root = (objectify.parse(os.path.join(directory, path),
                                  objectify.makeparser(
                                      remove_blank_text=True))
                  .getroot())
    return index_root


def get_member_filepaths(directory, nlevels, keyword, subdirectory_name):
    """Find and store all .xml/.lblx files whose filenames contain the keyword.

    Inputs:
        directory      The path to the directory containing the
                       bundle/collection.

        nlevels        The number of levels down within the directory the
                       search can go.

        keyword       The chosen keyword to search the directory with.

    Returns:
        files_found    The results of the file search. If empty, an exception
                       is raised.
    """
    files_found = []

    directory = os.path.abspath(directory)
    for basedir, _, files in os.walk(directory):
        if basedir.count(os.sep) - directory.count(os.sep) < nlevels:
            for file in files:
                if file.endswith(('.xml', '.lblx')):
                    if keyword in file:
                        files_found.append(shortpaths(os.path.join(basedir, file),
                                         directory,
                                         directory[directory.find(subdirectory_name):]))

    if not files_found:
        raise FilepathsNotFound(f'No files containing "{keyword}" ending in '
                                '".xml" or ".lblx" could be found in the '
                                'given levels.')
    return files_found


def get_schema(directory, xml_files):
    """Find all namespaces utilized by a bundle.

    Inputs:
        directory    The base directory that contains the bundle.xml file(s)
        
        xml_files    The filepath(s) of bundle.xml files to look in.
        
    Returns:
        namespaces    The dictionary of XML namespaces used in this bundle.
    """
    namespaces = {'pds': 'http://pds.nasa.gov/pds4/pds/v1',
                  'cassini': 'http://pds.nasa.gov/pds4/mission/cassini/v1'}
    for file in xml_files:
        file = os.path.join(directory, file)
        with open(file, 'r', encoding='utf8') as xml_file:
            lines = xml_file.readlines()
            for line in lines:
                if 'xmlns:' in line:
                    uri = line.replace('xmlns:', '').strip()
                    uri = uri.replace('"', '')
                    uri = uri.split('=')
                    namespaces.update({uri[0]: uri[-1]})
    return namespaces


def shortpaths(fullpath, directory, replacement_text):
    """Shorten the paths in the member_index dictionary.

    Inputs:

        fullpath             The original path of the file.

        directory            The path to the directory.

        replaceemnt_text     The text to replace within the fullpath

    Returns:
        shortpath            The shortened version of the filepath.
    """
    shortpath = fullpath.replace(directory, replacement_text)
    return shortpath
