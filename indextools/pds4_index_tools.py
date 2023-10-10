"""The collection of functions that can be used to scrape, index, and return a data
   product's information.
"""

import csv
import os
import sys
import re

from lxml import objectify


def add_bundle_data(bundle_member_entries, member_index):
    """Populate the member_index with information about bundle members.
    
    For each Bundle_Member_Entry, there is a search for either a lid_reference or a
    lidvid_reference attribute. The LID is extracted from the found attribute, then
    further shortened to the name of the data product. Then add_lid_to_member_index places
    the LID into the member_index dictionary. From there, the Reference Type and Member
    Status of the data product are added to the dictionary.
    
    Inputs:
        bundle_member_entries    The list of all Bundle_Member_Entry elements within the
                                 label document. These were located under a root element
                                 found via lxml.objectify.

        member_index             The dictionary to which information regarding the data
                                 products will be added.
    """
    for entry in bundle_member_entries:
        try:
            member_lid = str(entry.lid_reference)
        except AttributeError:
            member_lid = str(entry.lidvid_reference).split('::', maxsplit=1)[0]
        member_lid_short = member_lid.split(':')[-1]
        add_lid_to_member_index(['LID', 'Reference Type', 'Member Status'],
                                None, member_lid, member_index)
        member_index[member_lid_short]['Reference Type'] = str(entry.reference_type)
        member_index[member_lid_short]['Member Status'] = str(entry.member_status)


def add_collection_data(base_directory, collprod_path, member_index):
    """Populate the member_index with information about collection members.
    
    The collection product file is opened and read. For each entry within the collection
    product, the LIDVID of a data product is found and placed within the member_index
    dictionary as separate LID and VID components. In addition, the Member Status of the
    attributed data product is also included within member_index.

    Inputs:
        base_directory    The path to the base directory.

        collprod_path     The path to the collection product file.

        member_index      The dictionary of indexed information.
    """
    with open(os.path.join(base_directory, collprod_path), 'r',
              encoding='utf8') as collprod_file:
        for line in collprod_file:
            parts = line.split(',')
            lidvid = parts[-1].strip()
            lid = lidvid.split('::')[0]
            lid_short = lid.split(':')[-1]
            vid = lidvid.split('::')[-1]
            if lid == vid:
                vid = ''
            add_lid_to_member_index(['LID', 'VID', 'Member Status', 'Path'],
                                    None, lid, member_index)
            member_index[lid_short]['Member Status'] = parts[0]
            member_index[lid_short]['VID'] = vid


def add_lid_to_member_index(labels, filepath, lid, member_index):
    """Add LID, labels and other pertaining info to member_index.
    
    Creates a temporary dictionary that gets populated with the contents of the labels
    variable. If 'LID' is in labels, the 'LID' key will be given lid as a value. If 'Path'
    is in labels, the 'Path' key will be given filepath as a value. All other labels will
    be given None as values until they are replaced with their actual values in
    add_bundle_data (for bundle products) or add_collection_data (for collection
    products). This also creates the final version of member_index in the case of
    bundlesets.

    Inputs:
        labels          The labels to put into member_index.

        filepath        The path to the data product. If none exists, just
                        use None

        lid             The LID of the indexed data. This will be used as the identifier
                        for crossmatching.
        
        member_index    The dictionary that will contain the information of the data
                        products.
    """
    temp_dict = {}
    lid_short = lid.split(':')[-1]
    for label in labels:
        if label == 'LID':
            temp_dict[label] = lid
        elif label == 'Path':
            temp_dict[label] = filepath
        else:
            temp_dict[label] = None
    member_index[lid_short] = temp_dict
    
    if member_index == {}:
        print('Dictionary of data product information was not populated.')
        sys.exit(1)


def create_results_file(base_directory, keyword, member_index):
    """Create the file of the results.
    
    The file is opened within the base_directory. The file is named
    {keyword}_member_index.csv. The labels are taken from the keys of the nested
    dictionaries within member_index, and are used as fieldnames for the csv file.
    Each nested dictionary within member_index is then entered as a row into the csv file.

    Inputs:
        base_directory    The path to the base directory.

        keyword           The keyword to determine the name of the file.

        member_index      The index of data product information.
    """
    found_keys = list(member_index.keys())[0]
    labels = list(member_index[found_keys].keys())
    index_name = keyword+'_member_index.csv'
    with open(os.path.join(base_directory, index_name),
              mode='w', encoding='utf8') as index_file:
        member_index_writer = csv.DictWriter(index_file, fieldnames=labels)
        member_index_writer.writeheader()
        for index in member_index:
            member_index_writer.writerow(member_index[index])


def dataprod_crossmatch(label_paths, base_directory, subdirectory, member_index):
    """Match the LID of a file to its counterpart in the member_index.
    
    Each path within label_paths is parsed and scraped for its LID. If this LID exists as
    an entry in member_index, the 'Path' key is set to this value. If it has
    no match within member_index, a message is printed with the path and the LID.

    Inputs:
        label_paths       The list of data product label filepaths.

        base_directory    The path to the base directory.

        subdirectory      The name of the subdirectory containing the data products.
        
        member_index      The dictionary of indexed information.
    """
    for path in sorted(label_paths):
        root = (objectify.parse(os.path.join(base_directory, path),
                                objectify.makeparser(remove_blank_text=True)).getroot())
        lid = str(root.Identification_Area.logical_identifier.text)
        if not any(lid in member_index[key]['LID'] for key in member_index):
            print(f'PDS4 label found but not a member of the {subdirectory} collection: '
                  f'{path}, {lid}')
        else:
            for key in member_index:
                if lid == member_index[key]['LID']:
                    member_index[key]['Path'] = path


def get_bundle_member_entries(bunprod_root, namespaces):
    """Find and return all instances of Bundle_Member_Entry.
    
    The root element of the bundle product file is scraped for all instances of
    Bundle_Member_Entry. These attributes contain the information that will later
    be put into member_index.

    Inputs:
        bunprod_root             The root element of a given bundle product file.

        namespaces               The namespaces of the bundle product's schema.

    Returns:
        A list containing all instances of Bundle_Member_Entry under the given root
        element.
    """
    bundle_member_entries = bunprod_root.findall('pds:Bundle_Member_Entry',
                                                 namespaces=namespaces)
    return bundle_member_entries


def get_bundle_lid(bunprod_root):
    """Search a bundle label file for the LID.
    
    Takes the root element of the bundle product file and searches for the
    logical_identifier attribute. This attribute contains the LID of the bundle product.
    This value is then returned.

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
    
    The root element of the collection product label is scraped for all instances of
    File_Area_Inventory. The name of the collection product file is then scraped from
    File_Area_Inventory and returned.
    
    Inputs:
        collection_root    The root of the collection label file.

        namespaces         The namespaces present in the collection label file.

    Returns:
        collprod           The collection product file.
    """
    collection_file = collection_root.findall('pds:File_Area_Inventory',
                                                  namespaces=namespaces)
    
    try:
        collprod = collection_file[0].File.file_name.text
        return collprod
    
    except IndexError:
        print(f'Provided root element {collection_root} does not contain a '
               'File_Area_Inventory element.')
        sys.exit(1)


def get_index_root(base_directory, path):
    """Parse a data product label file and return its structured content.
    
    The root element of the data product label file is parsed from the file path and
    returned as a root element object.

    Inputs:
        base_directory    The path to the base directory.

        path              The path to the data product file.

    Returns:
        index_root        The root element of the data product file.
    """
    index_root = (objectify.parse(os.path.join(base_directory, path),
                                  objectify.makeparser(
                                      remove_blank_text=True))
                  .getroot())
    return index_root


def get_member_files(directory, nlevels, basedir, regex):
    """Find and return all .xml/.lblx files whose filenames match the regex.
    
    This function will return the first instance of an .xml/lblx file that exists within
    the directory structure in every subdirectory. When a match is found, the value for
    subdirs is reset to [], preventing any further recursion within that subdirectory
    and returning to the top level for the next search.

    Inputs:
        directory         The path to the base directory.
        
        nlevels           The number of subdirectory levels the search is limited to.
                          If nlevels = 2, the search returns the toplevel label file.
                          If nlevels = None, it will return all data products.

        basedir           The path to the directory one level above directory.
        
        file_type         The type of file to look for. 

    Returns:
        files_found       The results of the file search.
    """
    file_paths = []
    base_directory = os.path.abspath(directory)
    base_dir_sep = base_directory.count(os.sep)
    for subdir, dirs, files in os.walk(base_directory):
        if nlevels is None or subdir.count(os.sep) - base_dir_sep < nlevels:
            for file in files:
                if re.match(regex, file):
                    file_paths.append(shortpaths(os.path.join(subdir, file), basedir))
                    dirs[:] = []
                    
    return file_paths


def get_namespaces(bunprod_root):
    """Find all namespaces utilized by a bundle.
    
    The namespaces of the bundle product are found with lxml.nsmap and returned
    as a dictionary with the prefixes as the keys and the namespace URIs as the
    values.
    Inputs:
        bunprod_root      The root element of the bundle product

    Returns:
        namespaces        The namespaces of the bundle product schema.
    """
    namespaces = bunprod_root.nsmap
    namespaces['pds'] = namespaces.pop(None)
                
    return namespaces


def shortpaths(fullpath, base_directory):
    """Shorten the filepath.
    
    This function shortens the filepath to begin at the top level of a chosen directory.

    Inputs:
        fullpath            The original path of the file.

        base_directory      The path to the base directory.

    Returns:
        shortpath           The shortened version of the filepath.
    """
    shortpath = os.path.relpath(fullpath, start=base_directory)
    return shortpath
