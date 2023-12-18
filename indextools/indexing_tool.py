"""
XML Bundle Scraper

This script scrapes XML files within specified directories, extracts information from
user-defined XML elements, and generates a CSV index file. The script provides options
for customizing the extraction process, such as specifying XPath headers, limiting
search levels, and selecting elements to scrape.

Usage:
    python xml_bundle_scraper.py <directorypath> <pattern>
        [--nlevels NLEVELS]
        [--elements-file ELEMENTS_FILE]
        [--file-suffix FILE_SUFFIX]
        [--xpaths]

Arguments:
    directorypath        The path to the directory containing the bundle to scrape.
    pattern              The glob pattern for the files to index.
    --nlevels NLEVELS    The number of subdirectory levels to search (default: unlimited).
    --elements-file ELEMENTS_FILE
                         Optional text file containing elements to scrape.
    --file-suffix FILE_SUFFIX
                         The type of label file present within the collection (default: 'xml').
    --xpaths             Activate XPath headers in the final index file.
    --output-file OUTPUT_FILE
                         The output path and filename for the resulting index file.

Example:
    python xml_bundle_scraper.py /path/to/bundle_directory '*.xml' --nlevels 2
        --elements-file elements.txt --file-suffix xml --xpaths
"""

import argparse
from lxml import etree
import pandas as pd
from pathlib import Path
import re
import sys


def convert_header_to_tag(path, root, namespaces):
    """Convert an XPath expression to an XML tag.

    Inputs:
        path          XPath expression.
        root          The root element of the XML document.
        namespaces    Dictionary of XML namespace mappings.

    Returns:
        tag           Converted XML tag.
    """
    tag = str(root.xpath(path, namespaces=namespaces)[0].tag)

    return tag


def convert_header_to_xpath(root, xpath_find, namespaces):
    """Convert an XML header path to an XPath expression.

    Inputs:
        root           The root element of the XML document.
        xpath_find     Original XML header path.
        namespaces     Dictionary of XML namespace mappings.

    Returns:
        xpath_final    Converted XPath expression.
    """
    sections = xpath_find.split('/')
    xpath_final = ''
    portion = ''
    for sec in sections[1:]:
        portion = portion + '/' + sec
        tag = str(root.xpath(portion, namespaces=namespaces)[0].tag)
        xpath_final = xpath_final + '/' + tag

    return xpath_final


def get_member_files(directory, nlevels, regex):
    """Get a list of file paths within a directory up to a specified level.

    Inputs:
        directory    The directory to start the search.
        nlevels      The maximum number of levels to search (set to None for unlimited
                     levels).
        regex        Regular expression pattern for file name matching.

    Returns:
        file_paths   List of absolute file paths.
    """
    # Initialize an empty list to store file paths
    file_paths = []

    # Get the absolute path of the specified directory
    base_directory = Path(directory).resolve()

    # Start the search from the base directory with an initial level of 0
    search_files(base_directory, 0, nlevels, regex, file_paths)

    # Return the list of file paths
    return file_paths


def process_tags(xml_results, key, root, namespaces, prefixes, args):
    """Process XML tags based on the provided options.

    Inputs:
        xml_results    A dictionary containing XML data to be processed.
        key            The key representing the XML tag to be processed.
        root           The root element of the XML tree.
        namespaces     A dictionary containing XML namespace mappings.
        prefixes       A dictionary containing XML namespace prefixes.
        args           Command-line arguments.
    """
    if args.xpaths:
        key_new = convert_header_to_xpath(root, key, namespaces)
        for namespace in prefixes.keys():
            if namespace in key_new:
                key_new = key_new.replace(
                    '{'+namespace+'}', prefixes[namespace]+':')
        xml_results[key_new] = xml_results[key]
        del xml_results[key]
    else:
        key_new = convert_header_to_tag(key, root, namespaces)
        for namespace in prefixes.keys():
            if namespace in key_new:
                key_new = key_new.replace(
                    '{'+namespace+'}', prefixes[namespace]+':')
        xml_results[key_new] = xml_results[key]
        del xml_results[key]


def search_files(directory, current_level, nlevels, regex, file_paths):
    """Recursively search for files in a directory up to a specified level.

    Inputs:
        directory        The directory to start the search.
        current_level    The current depth level in the directory structure.
        nlevels          The maximum number of levels to search (set to None for
                         unlimited levels).
        regex            Regular expression pattern for file name matching.
        file_paths       List to store the absolute paths of matching files.
    """
    # Check if the specified number of levels is reached
    if nlevels is not None and current_level == nlevels:
        return

    # Iterate over items (files and directories) in the current directory
    for item in directory.iterdir():
        # If the item is a file and matches the specified regex pattern
        if item.is_file() and re.match(regex, item.name):
            # Get the absolute path of the file and add it to the file_paths list
            fullpath = item.resolve()
            file_paths.append(fullpath)
        # If the item is a directory, recursively call the search function
        elif item.is_dir():
            search_files(item, current_level + 1, nlevels, regex, file_paths)


def store_element_text(element, tree, results_dict, prefixes):
    """Store text content of an XML element in a results dictionary.

    Inputs:
        element         The XML element.
        tree            The XML tree.
        results_dict    Dictionary to store results.
        prefixes        Dictionary of XML namespace prefixes.
    """
    if element.text and element.text.strip():
        tag = str(element.tag)
        xpath = tree.getpath(element)
        text = ' '.join(element.text.strip().split())

        # Check if the tag already exists in the results dictionary
        if xpath in results_dict:
            # If the tag already exists, create a list to store multiple values
            if not isinstance(results_dict[xpath], list):
                results_dict[xpath] = [results_dict[xpath]]
            results_dict[xpath].append(text)
        else:
            results_dict[xpath] = text


def traverse_and_store(element, tree, results_dict, prefixes, elements_to_scrape):
    """Traverse an XML tree and store text content of specified elements in a dictionary.

    Inputs:
        element               The current XML element.
        tree                  The XML tree.
        results_dict          Dictionary to store results.
        prefixes              Dictionary of XML namespace prefixes.
        elements_to_scrape    Optional list of elements to scrape.
    """
    xpath = str(tree.getpath(element))
    tag = str(element.tag)
    if elements_to_scrape is None or any(tag.endswith("}" + elem)
                                         for elem in elements_to_scrape):
        store_element_text(element, tree, results_dict, prefixes)
    for child in element:
        traverse_and_store(child, tree, results_dict,
                           prefixes, elements_to_scrape)


def write_results_to_csv(results_list, output_csv_path):
    """Write results from a list of dictionaries to a CSV file.

    Inputs:
        results_list          List of dictionaries containing results.
        output_csv_path       The output directory and filename.
    """
    rows = []
    for result_dict in results_list:
        lid = result_dict['LID']
        blid = ':'.join(lid.split(':')[:4])
        bundle = blid.split(':')[-1]

        row = {
            'LID': lid,
            'pds:spec': result_dict['pds:spec'],
            'pds:fname': result_dict['pds:fname'],
            'pds:blid': blid,
            'pds:bundle': bundle
        }
        row.update(result_dict['Results'])
        rows.append(row)

    df = pd.DataFrame(rows)

    # Reorder columns to have logical_identifier, FileName, FilePath, pds:blid, and pds:bundle
    columns_order = (['LID',
                      'pds:fname',
                      'pds:spec',
                      'pds:blid',
                      'pds:bundle'] + [col for col in df.columns if col not in
                                       ['LID',
                                        'pds:fname',
                                        'pds:spec',
                                        'pds:blid',
                                        'pds:bundle']])

    df = df[columns_order]

    if 'LID' in df.columns:
        df = df.drop(columns=['LID'])
    df.to_csv(output_csv_path, index=False, na_rep='NaN')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('directorypath', type=str,
                        help='The path to the directory containing the bundle '
                             'you wish to scrape')

    parser.add_argument('pattern', type=str,
                        help='The glob pattern for the files you wish to index')

    # Argument for specifying the number of levels to search
    parser.add_argument('--nlevels', type=int, default=None,
                        help='The number of subdirectory levels to search')

    # Argument for specifying elements to scrape from a text file
    parser.add_argument('--elements-file', type=str,
                        help='Optional text file containing elements to scrape')

    parser.add_argument('--file-suffix', type=str, default='.xml',
                        help='The type of label file present within the collection')

    parser.add_argument('--xpaths', action='store_true',
                        help='A flag that will activate XPath headers in the final '
                             'index file')

    parser.add_argument('--output-file', type=str,
                        help='The output filepath ending with your chosen filename for '
                             'the resulting index file')

    args = parser.parse_args()

    pattern_path = Path(args.directorypath)
    directories = pattern_path.glob(args.pattern)
    all_results = []

    for directory in directories:
        # Existing code to process each directory...
        directory = directory.resolve()  # Convert to absolute path

        nlevels = args.nlevels
        regex = r'[\w-]+('+args.file_suffix+')'

        # Call get_member_files for the current subdirectory
        label_files = get_member_files(directory, nlevels, regex)

        if label_files == []:
            print(f'No files with suffix {args.file_suffix} found in '
                  f'directory: {directory}')
            sys.exit(1)

        if args.elements_file:
            with open(args.elements_file, 'r') as elements_file:
                elements_to_scrape = [line.strip() for line in elements_file]
        else:
            elements_to_scrape = None

        for file in label_files:
            tree = etree.parse(file)
            root = tree.getroot()

            namespaces = root.nsmap
            namespaces['pds'] = namespaces.pop(None)
            prefixes = {v: k for k, v in namespaces.items()}

            xml_results = {}
            traverse_and_store(root, tree, xml_results,
                               prefixes, elements_to_scrape)

            for key in list(xml_results.keys()):
                process_tags(xml_results, key, root,
                             namespaces, prefixes, args)

            lid = xml_results.get('pds:logical_identifier', 'Missing_LID')

            # Append file path and file name to the dictionary
            result_dict = {'LID': lid, 'Results': xml_results,
                           'pds:spec': str(file), 'pds:fname': file.name}

            all_results.append(result_dict)

    if args.output_file:
        output_path = args.output_file
        write_results_to_csv(all_results, args.output_file)
    else:
        output_path = args.directorypath
        write_results_to_csv(
            all_results, args.directorypath / Path('index_file.csv'))


if __name__ == '__main__':
    main()
