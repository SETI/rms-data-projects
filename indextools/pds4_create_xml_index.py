"""
XML Bundle Scraper

This script scrapes XML files within specified directories, extracts information from
user-defined XML elements, and generates a CSV index file. The script provides options
for customizing the extraction process, such as specifying XPath headers, limiting
search levels, and selecting elements to scrape.

Usage:
    python xml_bundle_scraper.py <directorypath> <pattern>
        [--elements-file ELEMENTS_FILE]
        [--xpaths]
        [--output-file OUTPUT_FILE]
        [--verbose]
        [--sort-by SORT_BY] 
        [--clean-header-field-names]

Arguments:
    directorypath        The path to the directory containing the bundle to scrape.
    pattern              Filename pattern(s), possibly including wildcards like * and ?,
                         for files within <directorypath> to scrape for the index.
    --elements-file ELEMENTS_FILE
                         Optional text file containing elements to scrape.
    --xpaths             Activate XPath headers in the final index file.
    --output-file OUTPUT_FILE
                         The output path and filename for the resulting index file.
    --verbose            Activate verbose printed statements during runtime.
    --sort-by            Sort the index file by a chosen set of columns.
    --clean-header-field-names
                         Replace the ":" and "/" with Windows-friendly characters.

Example:
python3 pds4_create_xml_index.py <toplevel_directory> "glob_path1" "glob_path2" 
--output_file <outputfile> --elements-file sample_elements.txt --verbose
"""

import argparse
from lxml import etree
import pandas as pd
from pathlib import Path
import sys


def convert_header_to_tag(path, root, namespaces):
    """Convert an XPath expression to an XML tag.

    Inputs:
        path          XPath expression.
        root          The root element of the XML document.
        namespaces    Dictionary of XML namespace mappings.

    Returns:
        Converted XML tag.
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
        Converted XPath expression.
    """
    sections = xpath_find.split('/')
    xpath_final = ''
    portion = ''
    for sec in sections[1:]:
        portion = portion + '/' + sec
        tag = str(root.xpath(portion, namespaces=namespaces)[0].tag)
        xpath_final = xpath_final + '/' + tag

    return xpath_final


def process_tags(xml_results, key, root, namespaces, prefixes, args):
    """Process XML tags based on the provided options.

    If the --xpaths command is used, the XPath is converted into a format that
    contains the names and namespaces of all the parent elements of that element.
    If the --xpaths command is not used, the XPath is converted into the
    associated element tag of that element, and given its associated namespace. These
    values then replace their old versions in the xml_results dictionary.


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


def store_element_text(element, tree, results_dict):
    """Store text content of an XML element in a results dictionary.

    Inputs:
        element         The XML element.
        tree            The XML tree.
        results_dict    Dictionary to store results.
    """
    if element.text and element.text.strip():
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


def traverse_and_store(element, tree, results_dict, elements_to_scrape):
    """Traverse an XML tree and store text content of specified elements in a dictionary.

    Inputs:
        element               The current XML element.
        tree                  The XML tree.
        results_dict          Dictionary to store results.
        prefixes              Dictionary of XML namespace prefixes.
        elements_to_scrape    Optional list of elements to scrape.
    """
    tag = str(element.tag)
    if elements_to_scrape is None or any(tag.endswith("}" + elem)
                                         for elem in elements_to_scrape):
        store_element_text(element, tree, results_dict)
    for child in element:
        traverse_and_store(child, tree, results_dict, elements_to_scrape)


def write_results_to_csv(results_list, args, output_csv_path):
    """Write results from a list of dictionaries to a CSV file.

    Inputs:
        results_list          List of dictionaries containing results.
        output_csv_path       The output directory and filename.
    """
    rows = []
    for result_dict in results_list:
        lid = result_dict['LID']
        bundle_lid = ':'.join(lid.split(':')[:4])
        bundle = bundle_lid.split(':')[-1]

        row = {
            'LID': lid,
            'pds:filepath': result_dict['pds:filepath'],
            'pds:filename': result_dict['pds:filename'],
            'pds:bundle_lid': bundle_lid,
            'pds:bundle': bundle
        }
        row.update(result_dict['Results'])
        rows.append(row)

    df = pd.DataFrame(rows)

    # Reorder columns to have logical_identifier, FileName, FilePath, pds:bundle_lid, and pds:bundle
    columns_order = (['LID',
                      'pds:filename',
                      'pds:filepath',
                      'pds:bundle_lid',
                      'pds:bundle'] + [col for col in df.columns if col not in
                                       ['LID',
                                        'pds:filename',
                                        'pds:filepath',
                                        'pds:bundle_lid',
                                        'pds:bundle']])

    df = df[columns_order]

    if 'LID' in df.columns:
        df = df.drop(columns=['LID'])
    if args.elements_file:
        df = df.drop(columns=['pds:filename', 'pds:filepath',
                              'pds:bundle_lid', 'pds:bundle'])

    if args.sort_by:
        df.sort_values(by=args.sort_by, inplace=True)

    if args.clean_header_field_names:
        df.rename(columns=lambda x: x.replace(':', '_').replace('/', '__'), inplace=True)
        
    df.to_csv(output_csv_path, index=False, na_rep='NaN')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('directorypath', type=str,
                        help='The path to the directory containing the bundleset, bundle, '
                             'or collection you wish to scrape')

    parser.add_argument('pattern', type=str, nargs='+',
                        help='The glob pattern(s) for the files you wish to index. If '
                             'using multiple, separate with spaces and surround each '
                             'pattern with quotes.')

    parser.add_argument('--elements-file', type=str,
                        help='Optional text file containing elements to scrape. If not '
                             'specified, all elements found in the XML files are '
                             'included.')

    parser.add_argument('--xpaths', action='store_true',
                        help='If specified, use full XPaths in the column '
                             'headers. If not specified, use only elements tags.')

    parser.add_argument('--output-file', type=str,
                        help='The output filepath ending with your chosen filename for '
                             'the resulting index file')

    parser.add_argument('--verbose', action='store_true',
                        help='Turn on verbose mode and show the details of file scraping')

    parser.add_argument('--sort-by', type=str, nargs='+',
                        help='Sort resulting index file by one or more columns')

    parser.add_argument('--clean-header-field-names', action='store_true',
                        help='Replaces the ":" and "/" in the column headers with '
                             'alternative (legal friendly) characters')

    args = parser.parse_args()

    verboseprint = print if args.verbose else lambda *a, **k: None

    directory_path = Path(args.directorypath)
    patterns = args.pattern

    label_files = []
    all_results = []
    for pattern in patterns:
        files = directory_path.glob(f"{pattern}")
        label_files.extend(files)

    verboseprint(f'{len(label_files)} matching files found')

    if label_files == []:
        print(f'No files matching {pattern} found in directory: {directory_path}')
        sys.exit(1)

    if args.elements_file:
        verboseprint(
            f'Element file {args.elements_file} chosen for input.')
        with open(args.elements_file, 'r') as elements_file:
            elements_to_scrape = [line.strip() for line in elements_file]
            verboseprint(
                f'Chosen elements to scrape: {elements_to_scrape}')
    else:
        elements_to_scrape = None

    for file in label_files:
        verboseprint(f'Now scraping {file}')
        tree = etree.parse(str(file))
        root = tree.getroot()

        filepath = file.relative_to(args.directorypath)

        namespaces = root.nsmap
        namespaces['pds'] = namespaces.pop(None)
        prefixes = {v: k for k, v in namespaces.items()}

        xml_results = {}
        traverse_and_store(root, tree, xml_results, elements_to_scrape)

        for key in list(xml_results.keys()):
            process_tags(xml_results, key, root,
                         namespaces, prefixes, args)

        lid = xml_results.get('pds:logical_identifier', 'Missing_LID')

        # Append file path and file name to the dictionary
        result_dict = {'LID': lid, 'Results': xml_results,
                       'pds:filepath': filepath, 'pds:filename': file.name}

        all_results.append(result_dict)

    if args.output_file:
        output_path = args.output_file
    else:
        output_path = args.directorypath / Path('index_file.csv')

    verboseprint(f'Output file generated at {output_path}')
    write_results_to_csv(all_results, args, output_path)


if __name__ == '__main__':
    main()
