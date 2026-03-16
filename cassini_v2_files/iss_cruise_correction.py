import argparse
import cspyce
import json
from lxml import etree
from pathlib import Path
from datetime import datetime, timedelta



def replace_modification_detail_v11(file_path):
    """
    Find the <Modification_Detail> block whose <version_id> is 1.1 and replace it
    with the 2025-08-11 description/update text, preserving the original indentation.

    If the new block already exists (date or key phrase match), this is a no-op.
    """
    NEW_DATE = "2025-08-11"
    NEW_SIG_PHRASE = "Values have been corrected for start_date_time, stop_date_time,"
    with open(file_path, "r", encoding="UTF-8") as f:
        lines = f.readlines()

    i = 0
    changed = False
    while i < len(lines):
        line = lines[i]
        if "<Modification_Detail>" not in line:
            i += 1
            continue

        # Locate the end of this <Modification_Detail> block
        start_idx = i
        end_idx = None
        j = i
        while j < len(lines):
            if "</Modification_Detail>" in lines[j]:
                end_idx = j
                break
            j += 1
        if end_idx is None:
            # Malformed block; bail out of this occurrence
            i += 1
            continue

        block = "".join(lines[start_idx:end_idx + 1])

        # Only act on version_id 1.1 blocks
        if "<version_id>1.1</version_id>" not in block:
            i = end_idx + 1
            continue

        # If already updated, skip
        if (f"<modification_date>{NEW_DATE}</modification_date>" in block) or (NEW_SIG_PHRASE in block):
            i = end_idx + 1
            continue

        # Build replacement with preserved indentation
        indent = lines[start_idx][:len(lines[start_idx]) - len(lines[start_idx].lstrip())]
        ind1 = indent + "    "
        ind2 = indent + "        "
        ind3 = indent + "            "

        new_block = (
            f"{indent}<Modification_Detail>\n"
            f"{ind1}<modification_date>{NEW_DATE}</modification_date>\n"
            f"{ind1}<version_id>1.1</version_id>\n"
            f"{ind1}<description>\n"
            f"{ind2}Values have been corrected for start_date_time, stop_date_time,\n"
            f"{ind3}cassini:start_time_doy, and cassini:stop_time_doy, cassini:image_mid_time,\n"
            f"{ind3}and cassini:image_time.\n"
            f"{ind2}Updated cassini:mission_phase_name (for which multiple values are possible)\n"
            f"{ind3}in order to provide consistency across multiple instrument data sets.\n"
            f"{ind2}Inserted new Legacy_Metadata class to contain original values replaced\n"
            f"{ind3}by the above corrections.\n"
            f"{ind2}Updated values of inst_cmprs_rate_expected_bits and inst_cmprs_rate_actual_bits\n"
            f"{ind3}for consistency with attribute definitions.\n"
            f"{ind2}See urn:nasa:pds:cassini_iss_cruise:document:v2.0_modifications for details.\n"
            f"{ind1}</description>\n"
            f"{indent}</Modification_Detail>\n"
        )

        # Replace the block
        lines[start_idx:end_idx + 1] = [new_block]
        changed = True
        # continue scanning in case there are multiple 1.1 blocks (rare)
        i = start_idx + 1

    if changed:
        with open(file_path, "w", encoding="UTF-8", newline="") as f:
            f.writelines(lines)
        print(f"Updated 1.1 Modification_Detail in {file_path}")
    else:
        print(f"No update needed for {file_path}")

def add_internal_reference_text(file_path):
    """
    Ensures the correct Internal_Reference for the Cassini VIMS v2.0 modifications is present.
    
    - If a 'cassini_vims_cruise' LID is found, replace it with 'cassini_vims_saturn' and exit.
    - If no reference is found, inject a new Internal_Reference block as before.
    """
    with open(file_path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    cruise_line = "            <lid_reference>urn:nasa:pds:cassini_vims_cruise:document:v2.0_modifications</lid_reference>\n"
    saturn_line = "            <lid_reference>urn:nasa:pds:cassini_vims_saturn:document:v2.0_modifications</lid_reference>\n"

    # CASE 1: If cruise LID is present, replace it with saturn and exit
    if cruise_line in lines:
        print("Found cruise LID, replacing with saturn LID.")
        lines = [line.replace("cassini_vims_cruise", "cassini_vims_saturn") for line in lines]
        with open(file_path, "w", encoding="utf-8", newline="") as f:
            f.writelines(lines)
        return

    # CASE 2: If saturn LID already exists, exit with no changes
    if saturn_line in lines:
        print("Internal_Reference with saturn LID already exists. No changes made.")
        return

    # Otherwise, inject a new Internal_Reference block as before
    new_ref_block = [
        "        <Internal_Reference>\n",
        saturn_line,
        "            <reference_type>data_to_document</reference_type>\n",
        "            <comment>\n",
        "                An overview of the changes made to the data product's label during the Cassini v2.0 bundles update process.\n",
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

    print("Injected Internal_Reference with saturn LID into Reference_List.")

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

    # start_time_replace(args.directorypath, args.pattern, args.kernel_directory,
    #                    mission_data)

if __name__ == '__main__':
    main()