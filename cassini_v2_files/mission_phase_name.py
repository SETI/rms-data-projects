import argparse
import json
import re
from datetime import datetime
from pathlib import Path
from lxml import etree
import cspyce


def update_schema_versions(file_path):
    """
    Updates schema filenames in the header of a PDS4 label by replacing old PDS4_* versions
    with specified updated filenames.
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


def extract_xml_headers(file_path):
    headers = []
    capturing_root = False
    with open(file_path, "r", encoding="utf-8") as f:
        for line in f:
            headers.append(line)
            if "<" in line and not line.lstrip().startswith("<?"):
                capturing_root = True
            if capturing_root and ">" in line.strip():
                break
    return "".join(headers)


def replace_xml_header_in_text(file_path, new_header):
    with open(file_path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    start_index = 0
    capturing_root = False
    for i, line in enumerate(lines):
        if "<" in line and not line.lstrip().startswith("<?"):
            capturing_root = True
        if capturing_root and ">" in line.strip():
            start_index = i + 1
            break

    updated_content = new_header + "".join(lines[start_index:])
    with open(file_path, "w", encoding="utf-8", newline="") as out_f:
        out_f.write(updated_content)


def add_modification_detail(file_path):
    with open(file_path, "r", encoding="UTF-8") as f:
        lines = f.readlines()

    mod_detail_count = sum(1 for line in lines if "<Modification_Detail>" in line)
    if mod_detail_count >= 2:
        print("Two or more Modification_Detail entries exist. No changes made.")
        return

    mod_history_start = None
    mod_detail_indent = None
    for i, line in enumerate(lines):
        if "<Modification_History>" in line:
            mod_history_start = i
        elif "<Modification_Detail>" in line and mod_history_start is not None:
            mod_detail_indent = line[:len(line) - len(line.lstrip())]
            break

    if mod_history_start is None:
        print("Modification_History section not found. No changes made.")
        return

    if mod_detail_indent is None:
        mod_detail_indent = " " * 8

    mod_history_indent = lines[mod_history_start][:len(lines[mod_history_start]) - len(lines[mod_history_start].lstrip())]

    new_mod_detail = f"""\
{mod_history_indent}    <Modification_Detail>
{mod_detail_indent}    <modification_date>2025-07-15</modification_date>
{mod_detail_indent}    <version_id>1.1</version_id>
{mod_detail_indent}    <description>
{mod_detail_indent}        Values have been corrected for cassini:image_mid_time and cassini:image_time.
{mod_detail_indent}        Updated cassini:mission_phase_name (for which multiple values are possible)
{mod_detail_indent}            in order to provide consistency across multiple instrument data sets.
{mod_detail_indent}        For further details, see the v2.0_modifications document referenced below
{mod_detail_indent}            in the Reference_List.
{mod_detail_indent}    </description>
{mod_detail_indent}</Modification_Detail>
"""

    insert_position = mod_history_start + 1
    while insert_position < len(lines) and lines[insert_position].strip() == "":
        insert_position += 1

    lines.insert(insert_position, new_mod_detail)
    with open(file_path, "w", encoding="UTF-8") as f:
        f.writelines(lines)


def cassini_mission_name(image_mid_time, mission_data, mission_phase_name):
    image_mid_time_text = image_mid_time.text
    try:
        image_dt = datetime.strptime(image_mid_time_text, "%Y-%m-%dT%H:%M:%S.%f")
    except ValueError:
        try:
            image_dt = datetime.strptime(image_mid_time_text, "%Y-%jT%H:%M:%S.%f")
        except ValueError:
            print(f"Warning: Unable to parse image_mid_time {image_mid_time_text}. Keeping original value.")
            return

    for phase, time_range in mission_data["short_encounters"].items():
        start_dt = datetime.strptime(time_range[0], "%Y-%jT%H:%M:%S.%f")
        stop_dt = datetime.strptime(time_range[1], "%Y-%jT%H:%M:%S.%f")
        if start_dt <= image_dt <= stop_dt:
            mission_phase_name.text = phase
            return

    for phase, time_range in mission_data["mission_periods"].items():
        start_dt = datetime.strptime(time_range[0], "%Y-%jT%H:%M:%S.%f")
        stop_dt = datetime.strptime(time_range[1], "%Y-%jT%H:%M:%S.%f")
        if start_dt <= image_dt <= stop_dt:
            mission_phase_name.text = phase
            return

    print(f"Warning: No mission phase found for time {image_mid_time_text}. Keeping original value.")


def add_internal_reference_text(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    if any("urn:nasa:pds:cassini_vims_cruise:document:v2.0_modifications" in line for line in lines):
        print("Internal_Reference already exists. No changes made.")
        return

    new_ref_block = [
        "        <Internal_Reference>\n",
        "            <lid_reference>urn:nasa:pds:cassini_vims_cruise:document:v2.0_modifications</lid_reference>\n",
        "            <reference_type>data_to_document</reference_type>\n",
        "            <comment>\n",
        "                An overview of the changes made to the data product's label during the Cassini v2.0 bundles update process.\n",
        "            </comment>\n",
        "        </Internal_Reference>\n"
    ]

    insert_index = None
    for i, line in enumerate(lines):
        if "<Source_Product_External>" in line:
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

    print(f"Inserting Internal_Reference at line {insert_index}")
    lines[insert_index:insert_index] = new_ref_block
    with open(file_path, "w", encoding="utf-8", newline="") as f:
        f.writelines(lines)
    print(f"Injected Internal_Reference into {file_path}")


def start_time_replace(directory_path, pattern, kernel_dir, mission_data):
    kernels = Path(kernel_dir)
    if not kernels.exists():
        print(f"Error: Kernel directory '{kernel_dir}' does not exist!")
        return
    for file in kernels.iterdir():
        if file.suffix in ['.tsc', '.tls', '.bsp', '.tf']:
            print(f"Loading kernel: {file}")
            cspyce.furnsh(str(file))

    cassini_id = -82
    directory_path = Path(directory_path)
    if not directory_path.exists():
        print(f"Error: Directory '{directory_path}' does not exist!")
        return

    files = list(directory_path.glob(f"{pattern}"))

    for file_path in files:
        print('Now fixing: ', file_path.name)

        # STEP 1: Update schema + add modification detail
        update_schema_versions(file_path)
        add_modification_detail(file_path)

        xml_headers = extract_xml_headers(file_path)
        tree = etree.parse(file_path)
        root = tree.getroot()
        namespaces = root.nsmap

        # STEP 2: Update fields in-memory
        vid = root.find(".//Identification_Area/version_id", namespaces=namespaces)
        vid.text = "1.1"

        components = root.findall(".//Observing_System_Component/type", namespaces=namespaces)
        for comp in components:
            if comp.text == "Spacecraft":
                comp.text = "Host"

        im = root.find(".//information_model_version", namespaces=namespaces)
        im.text = "1.24.0.0"

        mission_phase_name = root.find(".//cassini:mission_phase_name", namespaces=namespaces)
        image_mid_time = root.find(".//cassini:image_mid_time", namespaces=namespaces)
        
        cassini_mission_name(image_mid_time, mission_data, mission_phase_name)

        # STEP 3: Save main XML updates
        tree.write(file_path, pretty_print=True, xml_declaration=True, encoding="UTF-8")
        replace_xml_header_in_text(file_path, xml_headers)
        print(f"Updated {file_path}")

        # STEP 4: NOW inject Internal_Reference LAST
        add_internal_reference_text(file_path)

    cspyce.kclear()
    print(cspyce.ktotal("ALL"))


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

    start_time_replace(args.directorypath, args.pattern, args.kernel_directory, mission_data)


if __name__ == '__main__':
    main()
