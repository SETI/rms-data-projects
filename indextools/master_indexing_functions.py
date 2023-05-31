import csv
from lxml import objectify
import os


class FilepathsNotFound(Exception):
    """Stop the program if no files were found."""

    def __init__(self, message):
        super().__init__(message)


def get_member_filepaths(directory, filename):
    """Find and store all .xml/.lblx files that contain the filename.

    Inputs:
        directory    The path to the directory containing the
                     bundle/collection.

        filename     The chosen keyword to search the directory with.

    Returns:
        files_found    The results of the file search. If empty, an exception
                       is raised.
    """
    files_found = []
    if 'bundle' in filename:
        level = 2
    else:
        assert filename == 'collection'
        level = 3

    directory = os.path.abspath(directory)
    for root, dirs, files in os.walk(directory):
        if root.count(os.sep) - directory.count(os.sep) < level:
            for file in files:
                if file.endswith(('.xml', '.lblx')):
                    if filename in file:
                        files_found.append(os.path.join(root, file))

    if files_found == []:
        raise FilepathsNotFound(f'No files containing "{filename}" ending in '
                                '".xml" or ".lblx" could be found in the '
                                'given levels.')
    return files_found


def get_schema(bundlexml_files, namespaces):
    """Find all namespaces utilized by a bundle.

    Inputs:
        bundlexml_files    The filepath(s) of bundle.xml files to look in.

        namespaces         The dictionary to contain the namespaces of the
                           bundle.
    """
    for file in bundlexml_files:
        with open(file, 'r') as xml_file:
            xml_file = xml_file.readlines()
            for line in xml_file:
                if 'xmlns:' in line:
                    line = line.replace('xmlns:', '').strip()
                    line = line.replace('"', '')
                    line = line.split('=')
                    namespaces.update({line[0]: line[-1]})


def add_to_index(filepath, filename, namespaces):
    """Fills index with appropriate contents according to specified filename.

    Inputs:
        filepath      The path(s) to the file containing the information

        filename      The keyword to determine which file to look for.

        namespaces    The xml schema to use in lxml parsing

    Returns:
        member_index        The index dictionary that will contain
                            information depending on the filename.
    """
    member_index = {}
    if 'bundle' in filename:
        if len(filepath) > 1:
            for file in filepath:
                bundle_root = (objectify.parse(file,
                                               objectify.makeparser(
                                                   remove_blank_text=True))
                               .getroot())
                bundle_lid = str(
                    bundle_root.Identification_Area.logical_identifier.text)
                member_index[bundle_lid] = ({
                    'LID': bundle_lid,
                    'Path': file})
        else:
            for file in filepath:
                bundle_root = (objectify.parse(file,
                                               objectify.makeparser(
                                                   remove_blank_text=True))
                               .getroot())
                bundle_member_entries = bundle_root.findall(
                    'pds:Bundle_Member_Entry',
                    namespaces=namespaces
                )
                for bundle_entry in bundle_member_entries:
                    member_lid = str(bundle_entry.lid_reference)
                    member_index[member_lid] = {
                        'LID': member_lid,
                        'Reference Type': str(bundle_entry.reference_type),
                        'Member Status': str(bundle_entry.member_status),
                        'Path': '__'}

    else:
        assert filename == 'collection'

        for file in filepath:
            collection_file_root = (objectify.parse(file,
                                    objectify.makeparser(
                                        remove_blank_text=True))
                                    )

            collection_file = collection_file_root.findall(
                'pds:File_Area_Inventory',
                namespaces=namespaces
            )

            collection_product_name = file.replace(file.split('/')[-1],
                                                   collection_file[0].File
                                                                     .file_name
                                                                     .text)

            with open(collection_product_name, 'r') as collection_prod_file:
                lines = collection_prod_file.readlines()
                for line in lines:
                    parts = line.split(',')
                    lidvid = parts[-1].strip()
                    lid = lidvid.split('::')[0]
                    vid = lidvid.split('::')[-1]
                    if lid == vid:
                        vid = ''
                    member_index[str(lidvid)] = {
                        'LID': lid,
                        'VID': vid,
                        'Member Status': parts[0],
                        'Path': '__'}
    return member_index


def fullpaths_populate(directory, filename):
    """Generate the fullpaths to .xml and .lblx files within a subdirectory.

    Any instance of .xml and .lblx files within the chosen level of
    subdirectories will be collected and appended to the list of fullpaths.

    Inputs:
        directory    The path to the bundle directory.

        level        The allowed level of subdirectories the search can go.

    Returns:
        fullpaths    The list to be populated with filepaths.
    """
    fullpaths = []
    if filename == 'bundle':
        level = 2
    else:
        assert filename == 'collection'
        level = 3
    directory = os.path.abspath(directory)
    for root, dirs, files in os.walk(directory):
        if root.count(os.sep) - directory.count(os.sep) < level:
            for file in files:
                if file.endswith(('.xml', '.lblx')):
                    fullpaths.append(root + '/' + file)

    if fullpaths == []:
        raise FilepathsNotFound('No files ending in ".xml" or ".lblx" could '
                                'be found in the given levels.')

    return fullpaths


def match_lids_to_files(fullpaths, filename, member_index):
    """Match the LID of a file to its counterpart in the dictionary.

    Inputs:
        fullpaths       The paths to the collected files.

        filename        The keyword to determine which file to look for.

        member_index    The dictionary of indexed information
    """
    fullpaths_sorted = sorted(fullpaths)
    if filename == 'bundle':
        if any('__' in entry['Path'] for entry in member_index.values()):
            for path in fullpaths_sorted:
                bundle_root = (objectify.parse(path,
                                               objectify.makeparser(
                                                   remove_blank_text=True))
                               .getroot())
                lid = str(
                    bundle_root.Identification_Area.logical_identifier.text)
                if lid in member_index:
                    member_index[lid]['Path'] = path
                else:
                    print(f'PDS4 label found but not a member of this bundle: '
                          f'{path}, {lid}')
        else:
            pass

    else:
        assert filename == 'collection'
        for path in fullpaths:
            collection_root = (objectify.parse(path,
                                               objectify.makeparser(
                                                   remove_blank_text=True))
                               .getroot())
            lid = str(collection_root.Identification_Area.logical_identifier)
            vid = str(collection_root.Identification_Area.version_id)
            lidvid = lid + '::' + vid
            if lidvid in member_index:
                member_index[lidvid]['Path'] = path
            else:
                print(f'PDS4 label found but not a member of this bundle: '
                      f'{path}, {lid}')


def shortpaths(directory, bundle_name, member_index):
    """Shorten the paths in the member_index dictionary.

    Inputs:
        directory            The path to the directory.

        subdirectory_name    The name of the source directory.

        member_index         The dictionary of indexed information.
    """
    for key in member_index:
        fullpath = member_index[key]['Path']
        shortpath = fullpath.replace(directory, bundle_name + '/')
        member_index[key]['Path'] = shortpath


def file_creator(directory, filename, member_index):
    """Create the file of the results.

    Inputs:
        directory       The path to the directory.

        file_name       The keyword to determine the contents.

        member_index    The index of bundle member/collection product
                        information.
    """
    # These are kept here until they have a place within the index population
    # functions.
    __ = list(member_index.keys())[0]
    labels = list(member_index[__].keys())
    index_name = filename+'_member_index.csv'
    with open(os.path.join(directory, index_name),
              mode='w', encoding='utf8') as index_file:
        member_index_writer = csv.DictWriter(
            index_file,
            fieldnames=labels)
        member_index_writer.writeheader()
        for index in sorted(member_index):
            member_index_writer.writerow(member_index[index])
