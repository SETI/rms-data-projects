import argparse
import cspyce
import json
from lxml import etree
import re
from pathlib import Path
from datetime import datetime, timedelta

def replace_xml_header_in_text(file_path, new_header):
    # Read the original XML file as raw text
    with open(file_path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    # Find where the old header ends (after the full opening root tag)
    start_index = 0
    capturing_root = False

    for i, line in enumerate(lines):
        if "<" in line and not line.lstrip().startswith("<?"):
            capturing_root = True  # Found root tag, start tracking
            
        if capturing_root and ">" in line.strip():  
            start_index = i + 1  # Move to the next line after the root tag
            break  # Stop once the full root tag is found and closed

    # Merge new header with the remaining XML content (excluding the old root tag)
    updated_content = new_header + "".join(lines[start_index:])

    # Overwrite the original XML file with the updated content
    with open(file_path, "w", encoding="utf-8", newline="") as out_f:
        out_f.write(updated_content)


def extract_xml_headers(file_path):
    headers = []
    capturing_root = False  # Flag to track multi-line root tag

    with open(file_path, "r", encoding="utf-8") as f:
        for line in f:
            headers.append(line)  # Preserve original formatting

            # Detect start of root element
            if "<" in line and not line.lstrip().startswith("<?"):
                capturing_root = True
            
            # Detect end of root element (closing `>`)
            if capturing_root and ">" in line.strip():
                break  # Stop after capturing the full root tag

    xml_header_content = "".join(headers)  # Convert list to string while preserving format
    return xml_header_content  # Return as a variable instead of writing to a file

def add_modification_detail(file_path):
    """
    Opens the XML file as text, injects a new Modification_Detail entry in the correct place,
    and saves the file without affecting the rest of the formatting.
    """

    # Read the original XML file as raw text
    with open(file_path, "r", encoding="UTF-8") as f:
        lines = f.readlines()

    # Count occurrences of <Modification_Detail>
    mod_detail_count = sum(1 for line in lines if "<Modification_Detail>" in line)

    # If there are already two or more instances, exit the function
    if mod_detail_count >= 2:
        print("Two or more Modification_Detail entries exist. No changes made.")
        return

    # Locate the <Modification_History> section and capture indentation of existing <Modification_Detail>
    mod_history_start = None
    mod_detail_indent = None
    for i, line in enumerate(lines):
        if "<Modification_History>" in line:
            mod_history_start = i
        elif "<Modification_Detail>" in line and mod_history_start is not None:
            # Capture the indentation of the first existing <Modification_Detail> entry
            mod_detail_indent = line[:len(line) - len(line.lstrip())]
            break

    if mod_history_start is None:
        print("Modification_History section not found. No changes made.")
        return

    # If no existing <Modification_Detail> was found, default to 8 spaces (based on your structure)
    if mod_detail_indent is None:
        mod_detail_indent = " " * 8

    # Ensure the first line of <Modification_Detail> is aligned correctly with <Modification_History>
    mod_history_indent = lines[mod_history_start][:len(lines[mod_history_start]) - len(lines[mod_history_start].lstrip())]

    # Define the new Modification_Detail entry with aligned indentation
    new_mod_detail = f"""\
{mod_history_indent}    <Modification_Detail>
{mod_detail_indent}    <modification_date>2025-06-05</modification_date>
{mod_detail_indent}    <version_id>1.1</version_id>
{mod_detail_indent}    <description>
{mod_detail_indent}        Values have been corrected for start_date_time, stop_date_time,
{mod_detail_indent}            cassini:start_time_doy, and cassini:stop_time_doy.
{mod_detail_indent}        Updated cassini:mission_phase_name (for which multiple values are possible)
{mod_detail_indent}            in order to provide consistency across multiple instrument data sets.
{mod_detail_indent}        Inserted new Legacy_Metadata class to contain original values replaced
{mod_detail_indent}            by the above corrections.
{mod_detail_indent}        Updated values of fast_hk_item_name_1, fast_hk_item_name_2, fast_hk_item_name_3,
{mod_detail_indent}            and fast_hk_item_name_4 for consistency with attribute definitions.
{mod_detail_indent}        See urn:nasa:pds:cassini_vims_cruise:document:v2.0_modifications for details.
{mod_detail_indent}    </description>
{mod_detail_indent}</Modification_Detail>
"""

    # Insert after <Modification_History> but before existing <Modification_Detail>
    insert_position = mod_history_start + 1
    while insert_position < len(lines) and lines[insert_position].strip() == "":
        insert_position += 1  # Skip blank lines

    lines.insert(insert_position, new_mod_detail)  # Add with newline

    # Write back the modified content
    with open(file_path, "w", encoding="UTF-8") as f:
        f.writelines(lines)


def add_internal_reference_text(file_path):
    """
    Injects a new Internal_Reference into the Reference_List section of the XML file.
    Only inserts if the exact <lid_reference> line is not already present.
    """
    with open(file_path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    # Precise line match to avoid false positives
    target_line = "            <lid_reference>urn:nasa:pds:cassini_vims_cruise:document:v2.0_modifications</lid_reference>\n"
    if target_line in lines:
        print("Internal_Reference already exists. No changes made.")
        return

    new_ref_block = [
        "        <Internal_Reference>\n",
        "            <lid_reference>urn:nasa:pds:cassini_vims_cruise:document:v2.0_modifications</lid_reference>\n",
        "            <reference_type>data_to_document</reference_type>\n",
        "            <comment>\n",
        "                An overview of the changes made to the data product's label during the PDS4 migration progress.\n",
        "            </comment>\n",
        "        </Internal_Reference>\n"
    ]

    # Find where to insert (before first <External_Reference>)
    insert_index = None
    for i, line in enumerate(lines):
        if "<External_Reference>" in line:
            insert_index = i
            break

    if insert_index is None:
        for i, line in enumerate(lines):
            if "</Reference_List>" in line:
                insert_index = i
                break
        if insert_index is None:
            print("Reference_List not found. No changes made.")
            return

    # Insert and write back
    lines[insert_index:insert_index] = new_ref_block
    with open(file_path, "w", encoding="utf-8", newline="") as f:
        f.writelines(lines)

    print("Injected Internal_Reference into Reference_List.")


def add_legacy_metadata_block(file_path):
    """
    Injects a cassini:Legacy_Metadata block directly after VIMS_Specific_Attributes,
    using raw text replacement to preserve schema formatting. The block contains original
    values from start_date_time, stop_date_time, cassini:start_time_doy, and cassini:stop_time_doy.
    """
    with open(file_path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    if any("<cassini:Legacy_Metadata>" in line for line in lines):
        print("Legacy_Metadata entry already exists. Aborting.")
        return

    # Extract original values from those four fields
    start_time, stop_time = None, None
    start_doy, stop_doy = None, None

    for line in lines:
        if "<start_date_time>" in line:
            start_time = line.strip().replace("<start_date_time>", "").replace("</start_date_time>", "")
        elif "<stop_date_time>" in line:
            stop_time = line.strip().replace("<stop_date_time>", "").replace("</stop_date_time>", "")
        elif "<cassini:start_time_doy>" in line:
            start_doy = line.strip().replace("<cassini:start_time_doy>", "").replace("</cassini:start_time_doy>", "")
        elif "<cassini:stop_time_doy>" in line:
            stop_doy = line.strip().replace("<cassini:stop_time_doy>", "").replace("</cassini:stop_time_doy>", "")

    if None in (start_time, stop_time, start_doy, stop_doy):
        print("Could not find all required legacy source fields. Aborting injection.")
        return

    # Find where to insert — after the closing </cassini:VIMS_Specific_Attributes>
    insert_index = None
    for i, line in enumerate(lines):
        if "</cassini:VIMS_Specific_Attributes>" in line:
            insert_index = i + 1
            break

    if insert_index is None:
        print("Could not find </cassini:VIMS_Specific_Attributes> — no changes made.")
        return

    # Determine indentation level based on the previous line
    indent = lines[insert_index - 1][:len(lines[insert_index - 1]) - len(lines[insert_index - 1].lstrip())]

    legacy_block = [
        f"{indent}<cassini:Legacy_Metadata>\n",
        f"{indent}    <cassini:legacy_start_date_time>{start_time}</cassini:legacy_start_date_time>\n",
        f"{indent}    <cassini:legacy_stop_date_time>{stop_time}</cassini:legacy_stop_date_time>\n",
        f"{indent}    <cassini:legacy_start_time_doy>{start_doy}</cassini:legacy_start_time_doy>\n",
        f"{indent}    <cassini:legacy_stop_time_doy>{stop_doy}</cassini:legacy_stop_time_doy>\n",
        f"{indent}</cassini:Legacy_Metadata>\n"
    ]

    # Inject the block and write back
    lines[insert_index:insert_index] = legacy_block

    with open(file_path, "w", encoding="utf-8", newline="") as f:
        f.writelines(lines)

    print("Injected cassini:Legacy_Metadata block.")


def annotate_corrected_fields_with_comment(file_path):
    """
    Appends an inline comment to the corrected start/stop date/time and DOY fields to indicate
    they were updated for version 2.0.
    """
    comment = " <!-- Corrected for v2.0 (see Modification_Detail) -->"

    # Tags to annotate
    tags_to_annotate = [
        "start_date_time",
        "stop_date_time",
        "cassini:start_time_doy",
        "cassini:stop_time_doy"
    ]

    with open(file_path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    updated_lines = []
    for line in lines:
        stripped = line.strip()
        for tag in tags_to_annotate:
            # Only match lines with the full open and close tag on the same line
            if stripped.startswith(f"<{tag}>") and f"</{tag}>" in stripped:
                if comment not in line:
                    line = line.rstrip() + comment + "\n"
        updated_lines.append(line)

    with open(file_path, "w", encoding="utf-8", newline="") as f:
        f.writelines(updated_lines)

    print("Annotated corrected fields with inline comments.")


def cassini_mission_name(image_mid_time, mission_data, mission_phase_name):
    """
    Determines the mission phase name based on the image_mid_time and updates the XML.

    Parameters:
        image_mid_time (etree.Element): XML element containing the image time.
        mission_data (dict): Dictionary containing short_encounters and mission_periods.
        mission_phase_name (etree.Element): XML element to be updated.
    """

    # Try parsing as ISO 8601 (YYYY-MM-DDTHH:MM:SS.sssZ)
    try:
        image_dt = datetime.strptime(image_mid_time, "%Y-%m-%dT%H:%M:%S.%f")
    except ValueError:
        # Try parsing as Year-Day-of-Year (YYYY-DDDTHH:MM:SS.sss)
        try:
            image_dt = datetime.strptime(image_mid_time, "%Y-%jT%H:%M:%S.%f")
        except ValueError:
            print(f"Warning: Unable to parse image_mid_time {image_mid_time}. Keeping original value.")
            return

    # Check short encounters first
    for phase, time_range in mission_data["short_encounters"].items():
        start_dt = datetime.strptime(time_range[0], "%Y-%jT%H:%M:%S.%f")
        stop_dt = datetime.strptime(time_range[1], "%Y-%jT%H:%M:%S.%f")

        if start_dt <= image_dt <= stop_dt:
            mission_phase_name.text = phase
            return

    # If no short encounter matches, check mission periods
    for phase, time_range in mission_data["mission_periods"].items():
        start_dt = datetime.strptime(time_range[0], "%Y-%jT%H:%M:%S.%f")
        stop_dt = datetime.strptime(time_range[1], "%Y-%jT%H:%M:%S.%f")

        if start_dt <= image_dt <= stop_dt:
            mission_phase_name.text = phase
            return

    # If no match is found, keep the original value
    print(f"Warning: No mission phase found for time {image_mid_time}. "
          f"Keeping original value.")
    
import re

def update_schema_versions(file_path):
    """
    Updates schema filenames in the header of a PDS4 label by replacing old PDS4_*_1*_1* 
    versions with specified updated filenames. Does not replace entire lines.
    """

    replacements = {
        r"PDS4_PDS_1.*?\.sch":      "PDS4_PDS_1O00.sch",
        r"PDS4_DISP_1.*?\.sch":     "PDS4_DISP_1O00_1510.sch",
        r"PDS4_SP_1.*?\.sch":       "PDS4_SP_1O00_1320.sch",
        r"PDS4_CASSINI_1.*?\.sch":  "PDS4_CASSINI_1O00_1800.sch",

        r"PDS4_PDS_1.*?\.xsd":      "PDS4_PDS_1O00.xsd",
        r"PDS4_DISP_1.*?\.xsd":     "PDS4_DISP_1O00_1510.xsd",
        r"PDS4_SP_1.*?\.xsd":       "PDS4_SP_1O00_1320.xsd",
        r"PDS4_CASSINI_1.*?\.xsd":  "PDS4_CASSINI_1O00_1800.xsd"
    }

    with open(file_path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    updated_lines = []
    for line in lines:
        updated_line = line
        for pattern, replacement in replacements.items():
            updated_line = re.sub(pattern, replacement, updated_line)
        updated_lines.append(updated_line)

    with open(file_path, "w", encoding="utf-8", newline="") as f:
        f.writelines(updated_lines)

    print("Schema filenames updated successfully.")

    

def start_time_replace(directory_path, pattern, kernel_dir, mission_data):
    """
    Processes XML label files in a given directory to update spacecraft clock start times 
    and start date-times based on exposure duration and spacecraft clock stop counts.
    Also adds a Modification_Detail entry to the Modification_History section.

    Parameters:
        directory_path (str): Path to the directory containing the XML label files.
        pattern (str): File extension pattern to match label files (e.g., "lblx").
        kernel_dir (str): Path to the directory containing SPICE kernels.
    """

    # Load SPICE kernels from kernel directory
    kernels = Path(kernel_dir)
    if not kernels.exists():
        print(f"Error: Kernel directory '{kernel_dir}' does not exist!")
        return
    
    for file in kernels.iterdir():
        if file.suffix in ['.tsc', '.tls', '.bsp', '.tf']:  # Only load valid kernel types
            print(f"Loading kernel: {file}")
            cspyce.furnsh(str(file))

    # Define spacecraft ID
    cassini_id = -82  # SPICE ID for Cassini

    # Check if directory exists
    directory_path = Path(directory_path)
    if not directory_path.exists():
        print(f"Error: Directory '{directory_path}' does not exist!")
        return

    # Find matching files
    files = list(directory_path.glob(f"{pattern}"))

    for file_path in files:
        rounded = False
        instant = False
        print('Now fixing: ', file_path.name)

        # Adding the Modification_Detail entry BEFORE any lxml work will preserve the
        # format of the XML file.
        update_schema_versions(file_path)
        add_modification_detail(file_path)
        add_internal_reference_text(file_path)
        add_legacy_metadata_block(file_path)
        annotate_corrected_fields_with_comment(file_path)

        xml_headers = extract_xml_headers(file_path)
        
        # Parse the XML file
        tree = etree.parse(file_path)
        root = tree.getroot()

        # Get the namespaces
        namespaces = root.nsmap

        # Replace "Spacecraft" with "Host"
        # XPath to find all Observing_System_Component/type elements
        components = root.findall(".//Observing_System_Component/type",
                                namespaces=namespaces)

        for comp in components:
            if comp.text == "Spacecraft":
                comp.text = "Host"

        im = root.find(".//information_model_version", namespaces=namespaces)
        im.text = "1.24.0.0"

        # Extract values safely
        start_count_elem = root.find(".//cassini:spacecraft_clock_start_count",
                                     namespaces=namespaces)
        stop_count_elem = root.find(".//cassini:spacecraft_clock_stop_count",
                                    namespaces=namespaces)
        stop_time_elem = root.find(".//stop_date_time", namespaces=namespaces)
        start_time_elem = root.find(".//start_date_time", namespaces=namespaces)
        mission_phase_name = root.find(".//cassini:mission_phase_name",
                                       namespaces=namespaces)
        stop_time_doy = root.find(".//cassini:stop_time_doy", namespaces=namespaces)
        start_time_doy = root.find(".//cassini:start_time_doy", namespaces=namespaces)
        fast_hk_item_name_1 = root.find(".//cassini:fast_hk_item_name_1",
                                                namespaces=namespaces)
        fast_hk_item_name_2 = root.find(".//cassini:fast_hk_item_name_2",
                                                namespaces=namespaces)
        fast_hk_item_name_3 = root.find(".//cassini:fast_hk_item_name_3",
                                                namespaces=namespaces)
        fast_hk_item_name_4 = root.find(".//cassini:fast_hk_item_name_4",
                                                namespaces=namespaces)

        if None in (stop_count_elem, start_count_elem, start_time_elem):
            print(f"Skipping {file_path}: Missing required elements.")
            continue

        # Replacing values for the fast_hk_item_name_* attributes
        fast_hk_item_name_1.text = "not used"
        fast_hk_item_name_2.text = "not used"
        fast_hk_item_name_3.text = "not used"
        fast_hk_item_name_4.text = "not used"


        if str(stop_count_elem.text.split('.')[1]) == "000":
            rounded = True

        stop_count = stop_count_elem.text

        # Convert stop count to UTC
        stop_count_e = cspyce.scs2e(cassini_id, stop_count)
        stop_count_utc = cspyce.et2utc(stop_count_e, 'ISOC', 3)

        new_stop_time = datetime.strptime(stop_count_utc, "%Y-%m-%dT%H:%M:%S.%f")
        stop_time_elem.text = new_stop_time.strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"
        stop_time_doy.text = new_stop_time.strftime("%Y-%jT%H:%M:%S.%f")[:-3]

        # Converting start count
        start_count = start_count_elem.text

        # Convert stop count to UTC
        start_count_e = cspyce.scs2e(cassini_id, start_count)
        start_count_utc = cspyce.et2utc(start_count_e, 'ISOC', 3)

        new_start_time = datetime.strptime(start_count_utc, "%Y-%m-%dT%H:%M:%S.%f")
        start_time_elem.text = new_start_time.strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"
        start_time_doy.text = new_start_time.strftime("%Y-%jT%H:%M:%S.%f")[:-3]

        # Convert stop_date_time to datetime object
        stop_time_dt = datetime.strptime(stop_time_elem.text, "%Y-%m-%dT%H:%M:%S.%fZ")

        # Subtract exposure duration from stop_time
        start_time_dt = datetime.strptime(start_time_elem.text, "%Y-%m-%dT%H:%M:%S.%fZ")

        mid_time_dt = start_time_dt + (stop_time_dt - start_time_dt) / 2
        image_mid_time = mid_time_dt.strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3]

        cassini_mission_name(image_mid_time, mission_data, mission_phase_name)

        # Save the updated XML
        tree.write(file_path, pretty_print=True, xml_declaration=True, encoding="UTF-8")
        print(f"Updated {file_path}")

        replace_xml_header_in_text(file_path, xml_headers)

    # Clear all SPICE kernels after processing
    cspyce.kclear()
    print(cspyce.ktotal("ALL"))  # Should print the number of loaded kernels

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('directorypath', type=str, metavar='DIRECTORY_PATH',
                        help='The path to the directory')
    parser.add_argument('pattern', type=str, metavar='PATTERN',
                        help='The extension of the labels you want to fix')
    parser.add_argument('kernel_directory', type=str, metavar='KERNEL_DIRECTORY',
                        help='The path to the kernel directory')

    args = parser.parse_args()

    with open("mission_data.json", "r") as file:
        mission_data = json.load(file)

    start_time_replace(args.directorypath, args.pattern, args.kernel_directory,
                       mission_data)

if __name__ == '__main__':
    main()