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


def add_bundle_data(bundle_member_entries, member_index):
    """Populate the member_index with information about bundle members.

    Inputs:
        bundle_member_entries    The list of all Bundle_Member_Entry elements
                                 within the label document. These were located
                                 under a root element found via lxml.objectify

        member_index             The dictionary that will contain the
                                 information regarding the data products.
    """
    for entry in bundle_member_entries:
        try:
            member_lid = str(entry.lid_reference)
        except AttributeError:
            member_lid = str(entry.lidvid_reference).split('::', maxsplit=1)[0]
        member_lid_short = member_lid.split(':')[-1]
        create_member_index(member_index,
                            ['LID', 'Reference Type', 'Member Status'],
                            '__',
                            member_lid)
        member_index[member_lid_short]['Reference Type'] = str(
            entry.reference_type)
        member_index[member_lid_short]['Member Status'] = str(
            entry.member_status)


def add_collection_data(directory, collprod_path, member_index):
    """Populate the member_index with information about collection members.

    Inputs:
        directory        The path to the base directory.

        collprod_file    The path to the collection product file.

        member_index     The dictionary of indexed information.
    """
    with open(os.path.join(directory, collprod_path), 'r',
              encoding='utf8') as collprod_contents:
        lines = collprod_contents.readlines()
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


def create_member_index(member_index, labels, filepath, lid):
    """Create the empty index with correct labels and contents.

    Inputs:
        member_index    The dictionary that will contain the information
                        of the data products.

        labels          The labels to put into member_index.

        filepath        The path to the data product. If none exists, just
                        use '_'

        lid             The LID of the indexed data. This will be used as the
                        identifier for crossmatching.
    """

    temp_dict = {}
    for label in labels:
        if label == 'LID':
            temp_dict.update({label: lid})
        elif label == 'Path':
            temp_dict.update({label: filepath})
        else:
            temp_dict.update({label: '_'})
        temp_dict = dict((temp_dict.items()))
        member_index[lid.split(':')[-1]] = temp_dict


def dataprod_crossmatch(label_paths, member_index, directory,
                        subdirectory_name):
    """Match the LID of a file to its counterpart in the dictionary.

    Inputs:
        label_paths          The list of data product label filepaths.

        member_index         The dictionary of indexed information.

        directory            The path to the base directory.

        subdirectory_name    The name of the subdirectory containing the data
                             products.

    """
    label_paths_sorted = sorted(label_paths)
    for path in label_paths_sorted:
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
        directory       The path to the base directory.

        keyword         The keyword to determine the name of the file.

        member_index    The index of data product information.
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
    subdirectories will be collected and appended to the list of filepaths.

    Inputs:
        directory            The path to the base directory.

        nlevels              The allowed level of subdirectories down the
                             search can go.

        subdirectory_name    The name of the subdirectory containing the data
                             products.

    Returns:
        memberlabel_paths      The list to be populated with filepaths.
    """
    label_paths = []
    directory = os.path.abspath(directory)
    for subdir, _, files in os.walk(directory):
        if subdir.count(os.sep) - directory.count(os.sep) < nlevels:
            for file in files:
                if file.endswith(('.xml', '.lblx')):
                    label_paths.append(shortpaths(
                        os.path.join(subdir, file),
                        directory,
                        directory[directory.find(subdirectory_name):])
                    )

    if not label_paths:
        raise FilepathsNotFound('No files ending in ".xml" or ".lblx" could '
                                'be found in the given levels.')

    return label_paths


def get_bundle_entries(bunprod_root, namespaces):
    """find and return all instances of Bundle_Member_Entry.

    Inputs:
        bunprod_root             The root element of a given bundle product
                                 file.

        namespaces               The namespaces of the bundle product's schema.

    Returns:
        bundle_member_entries    A list containing all instances of
                                 Bundle_Member_Entry under the given
                                 root element.
    """
    bundle_member_entries = bunprod_root.findall('pds:Bundle_Member_Entry',
                                                 namespaces=namespaces)
    return bundle_member_entries


def get_bundle_lid(bunprod_root):
    """Search a bundle label file for the LID.

    Inputs:
        bunprod_root    The root element of a given bundle label file

    Returns:
        bunprod_lid     The LID of the bundle label file
    """
    bunprod_lid = str(
        bunprod_root.Identification_Area.logical_identifier.text)
    return bunprod_lid


def get_collprod_filepath(collection_root, namespaces):
    """Return the collection product filepath from the collection label file.

    Inputs:
        collection_root    The root of the collection label file.

        namespaces         The namespaces present in the
                           collection label file.

    Returns:
        collprod           The collection product file.
    """
    collection_file = collection_root.findall('pds:File_Area_Inventory',
                                              namespaces=namespaces)
    collprod = collection_file[0].File.file_name.text

    return collprod


def get_index_root(directory, path):
    """Parse a data product label file and return its structured content.

    Inputs:
        directory     The path to the base directory.

        path          The path to the data product file.

    Returns:
        index_root    The root element of the data product file.
    """
    index_root = (objectify.parse(os.path.join(directory, path),
                                  objectify.makeparser(
                                      remove_blank_text=True))
                  .getroot())
    return index_root


def get_member_filepaths(directory, nlevels, keyword, subdirectory_name):
    """Find and store all .xml/.lblx files whose filenames contain the keyword.

    Inputs:
        directory            The path to the base directory.

        nlevels              The number of levels down within the directory the
                             search can go.

        keyword              The chosen keyword to search the directory with.

        subdirectory_name    The name of the subdirectory containing the data
                             products.

    Returns:
        files_found          The results of the file search. If empty, an
                             exception is raised.
    """
    files_found = []

    directory = os.path.abspath(directory)
    for subdir, _, files in os.walk(directory):
        if subdir.count(os.sep) - directory.count(os.sep) < nlevels:
            for file in files:
                if file.endswith(('.xml', '.lblx')):
                    if keyword in file:
                        files_found.append(shortpaths(
                            os.path.join(subdir, file),
                            directory,
                            directory[directory.find(subdirectory_name):])
                        )

    if not files_found:
        raise FilepathsNotFound(f'No files containing "{keyword}" ending in '
                                '".xml" or ".lblx" could be found in the '
                                'given levels.')
    return files_found


def get_schema(directory, label_files):
    """Find all namespaces utilized by a bundle.

    Inputs:
        directory      The path to the base directory.

        label_files    The filepath(s) of label files to look in.

    Returns:
        namespaces     The namespaces of the bundle product schema.
    """
    namespaces = {'pds': 'http://pds.nasa.gov/pds4/pds/v1',
                  'cassini': 'http://pds.nasa.gov/pds4/mission/cassini/v1'}
    for label_file in label_files:
        label_filepath = os.path.join(directory, label_file)
        with open(label_filepath, 'r', encoding='utf8') as bunprod_file:
            lines = bunprod_file.readlines()
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

        directory            The path to the base directory.

        replacement_text     The text to replace within the fullpath.

    Returns:
        shortpath            The shortened version of the filepath.
    """
    shortpath = fullpath.replace(directory, replacement_text)
    return shortpath
