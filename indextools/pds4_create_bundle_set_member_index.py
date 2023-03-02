"""Create a csv file of a bundle's bundle members and their information.

This module creates an index of all .xml and .lblx files within a bundle set,
sorted alphabetically by LID and then stores it in the attributed bundle
directory for each bundle within the bundle set. There is a single command-line
argument, the path to the bundle directory.
"""
import argparse
import csv
from lxml import objectify
import os


class BadLID(Exception):
    """This exception is raised if a LID does not contain a collection term.

    In the event BadLID gets raised, it means that the file the LID was
    derived from is not represented within the bundle, and therefore may
    be misplaced from another bundle.
    """


def create_bundle_member_index(directory_path):
    """Generate a .csv file containing information about the bundle directory.

    This function derives the bundle member information by creating file paths
    to all known bundle.xml files. For each bundle.xml file, the bundle member
    entries are scraped for their LIDs, their reference types, and their member
    statuses. These values are put into the bundle_member_lid dictionary for
    crossmatching.

    For each bundle, all .xml and .lbxl files within the first level of
    subdirectories are found and scraped for their LIDs. Any LIDs that match the
    keys of the bundle member dictionary are recorded in a new dictionary
    bundle_member_index with the LID as the key and the member status, reference
    type, and path to the file as values. If a LID does not match any key
    within the bundle_member_lid dictionary, an error is raised. If a LID
    contains a collection term that does not match the filepath but is otherwise
    represented within the bundle, a warning is raised but the file will
    remain within the bundle_member_index dictionary.

    The resulting dictionary bundle_member_index will contain the LIDs of all
    .xml or .lblx files within the first level of subdirectories as keys, with
    the member status, reference types, and file paths as values for each entry.
    This dictionary will then become exported as a .csv file and placed into
    the same location as the bundle.xml file for that bundle.
    """
    collection_terms = []
    bundle_member_lid = {}

    def bundle_file_paths(bundle_path):
        """Generate a .csv file containing data about the bundle directory.

        Generates the paths to bundle.xml files for each bundle within the
        bundle set, then appends them to a list to be iterated through. The
        directory_path is the path to the bundle set.
        """
        bundlepaths = []

        for path, subdirs, files in os.walk(bundle_path):
            for file in files:
                if file == 'bundle.xml':
                    bundlepaths.append(os.path.join(path, file))

        return bundlepaths

    def create_bundle_members(bundle_path):
        """Create a dictionary of LIDs, member status and reference type.

        The path to the bundle.xml file is parsed with lxml.objectify. The
        bundle member entries are found and scraped for their LID. This LID is
        put into the bundle_member_lid dictionary as a key with the reference
        type and the member status scraped and entered as values. This
        dictionary is then returned to be referenced in the index_bundle
        function for crossmatching. The input directory_path is the path to
        the bundle.
        """
        bundle_root = (objectify.parse(bundle_path,
                                       objectify.makeparser(
                                           remove_blank_text=True))
                       .getroot())

        bundle_member_entries = bundle_root.findall('pds:Bundle_Member_Entry',
                                                    namespaces=ns)

        for bundle_member in bundle_member_entries:
            lid_whole = (bundle_member.lid_reference
                                      .text
                                      .split(':'))
            collection_term = lid_whole[-1]
            collection_terms.append(collection_term)
            bundle_member_lid[collection_term] = ({
                'Reference Type': bundle_member.reference_type,
                'Member Status': bundle_member.member_status})

        return bundle_member_lid

    def fullpaths_populate(directory):
        """Generate the filepaths to .xml and .lblx files within a subdirectory.

        The input 'subdirectory' will be the path to the bundle directory_path.
        Any instance of We only look at subdirectories one level down
        from directory_path..xml and .lblx files within the first level of
        subdirectories will be collected and appended to the list of fullpaths.
        The break in the loop ensures that os.walk does not go into
        subdirectories deeper than the first level.
        """
        for root, dirs, files in os.walk(directory):
            for file in files:
                if file.endswith(('.xml', '.lblx')):
                    fullpaths.append(os.path.join(root, file))
            break

        return fullpaths

    def index_bundle(list_of_paths):
        """Fill the bundle_member_index dictionary with bundle member data.

        The input 'list_of_paths' is the previously generated return value
        'fullpaths' from the fullpaths_populate function. If this function
        finds a LID whose collection term is not shared with the path, it will
        raise a terminal message, but keep the file if it otherwise matches.
        """
        fullpaths_sorted = sorted(list_of_paths)
        for fullpath in fullpaths_sorted:
            root = (objectify.parse(fullpath,
                                    objectify.makeparser(
                                        remove_blank_text=True))
                    .getroot())
            lid = root.Identification_Area.logical_identifier.text
            if not any(term in lid for term in collection_terms):
                raise BadLID
            for term in collection_terms:
                if term in lid:
                    if term not in fullpath:
                        print(f'PDS4 label found but not a member of this '
                              f'bundle: {fullpath}, {lid}.')
                        continue
                    fullpath = fullpath.replace(directory_path,
                                                bundle_name)
                    bundle_member_index[lid] = (
                        ({'LID': lid,
                          'Reference Type':
                              bundle_member_lid[term]['Reference Type'],
                          'Member Status':
                              bundle_member_lid[term]['Member Status'],
                         'Path': fullpath}))

        return bundle_member_index

    def file_creator(bundle_location):
        """Create a .csv file in the bundle directory from the dictionary.

        This takes the bundle_member_index dictionary created by index_bundle
        and creates a csv file containing the dictionary's contents. This csv
        file is then placed in the same directory as the bundle.xml file for
        that bundle. Input value is the path leading to the bundle.
        """
        with open(bundle_location + '/bundle_member_index.csv',
                  mode='w', encoding='utf8') as index_csv:
            bundle_member_index_writer = csv.DictWriter(
                index_csv,
                fieldnames=('LID',
                            'Reference Type',
                            'Member Status',
                            'Path'))
            bundle_member_index_writer.writeheader()
            for index in sorted(bundle_member_index):
                bundle_member_index_writer.writerow(bundle_member_index[index])

    # Due to the nature of bundle sets, extra steps are necessary to ensure that
    # the attributed files for the bundle are not stacked on top of a previous
    # bundle's results. The list of bundle.xml paths ensures that each iteration
    # contains information specific to that bundle, rather than relying on all
    # bundles within a bundle set to contain the same reference types and
    # member status.
    bundlepaths = bundle_file_paths(directory_path)
    for bundlepath in bundlepaths:
        fullpaths = []
        bundle_member_index = {}
        create_bundle_members(bundlepath)
        path_to_bundle = bundlepath.replace('/bundle.xml', '')
        bundle_terms = next(os.walk(path_to_bundle))[1]
        for bundle_term in bundle_terms:
            bundledir = os.path.join(path_to_bundle, bundle_term)
            file_paths = fullpaths_populate(bundledir)
        index_bundle(sorted(file_paths))
        file_creator(path_to_bundle)
    return


ns = {'pds': 'http://pds.nasa.gov/pds4/pds/v1',
      'cassini': 'http://pds.nasa.gov/pds4/mission/cassini/v1'}

parser = argparse.ArgumentParser()
parser.add_argument('directorypath', type=str, nargs=1,
                    help='The path to the directory containing the bundles '
                         'you wish to scrape.')

args = parser.parse_args()

bundle_name = args.directorypath[0].split('/')[-1]
create_bundle_member_index(args.directorypath[0])
