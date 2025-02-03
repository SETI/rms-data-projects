import argparse
import cspyce
from lxml import etree
from pathlib import Path
from datetime import datetime, timedelta

def add_modification_detail(root, namespaces):
    """
    Adds a new Modification_Detail entry to the Modification_History section in the XML.

    Parameters:
        root (etree.Element): The root element of the XML document.
        namespaces (dict): Dictionary of XML namespaces.
    """

    # Locate or create the <Modification_History> section
    mod_history = root.find(".//Modification_History", namespaces=namespaces)
    if mod_history is None:
        mod_history = etree.Element("Modification_History")
        root.append(mod_history)  # Append it to the root if it doesn't exist

    # Create new <Modification_Detail>
    mod_detail = etree.Element("Modification_Detail")

    mod_date = etree.SubElement(mod_detail, "modification_date")
    mod_date.text = "2025-01-30"

    version = etree.SubElement(mod_detail, "version_id")
    version.text = "1.1"

    description = etree.SubElement(mod_detail, "description")
    description.text = "Corrected values for spacecraft_clock_start_time and start_date_time."

    # Insert new modification at the beginning of <Modification_History>
    mod_history.insert(0, mod_detail)


def start_time_replace(directory_path, pattern, kernel_dir):
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

    print(f"Checking directory: {directory_path}")

    # Find matching files
    files = list(directory_path.glob(f"{pattern}"))
    print(f"Found {len(files)} files matching pattern *.{pattern}")

    for file_path in files:
        print('Now fixing:', file_path.name)
        
        # Parse the XML file
        tree = etree.parse(file_path)
        root = tree.getroot()

        # Get the namespaces
        namespaces = root.nsmap
        print("Namespaces:", namespaces)

        # Extract values safely
        stop_count_elem = root.find(".//cassini:spacecraft_clock_stop_count", namespaces=namespaces)
        start_count_elem = root.find(".//cassini:spacecraft_clock_start_count", namespaces=namespaces)
        stop_time_elem = root.find(".//stop_date_time", namespaces=namespaces)
        start_time_elem = root.find(".//start_date_time", namespaces=namespaces)
        exposure_duration_elem = root.find(".//cassini:exposure_duration", namespaces=namespaces)

        if None in (stop_count_elem, start_count_elem, start_time_elem, exposure_duration_elem):
            print(f"Skipping {file_path}: Missing required elements.")
            continue

        stop_count = stop_count_elem.text
        exposure_duration = float(exposure_duration_elem.text) / 1000

        # Convert stop count to UTC
        stop_count_e = cspyce.scs2e(cassini_id, stop_count)
        stop_count_utc = cspyce.et2utc(stop_count_e, 'ISOC', 3)

        # Convert to datetime object, and subtract seconds to create
        # spacecraft_clock_start_count in UTC
        stop_count_dt = datetime.strptime(stop_count_utc, "%Y-%m-%dT%H:%M:%S.%f")
        new_start_count_utc = stop_count_dt - timedelta(seconds=exposure_duration)

        # Convert spacecraft_clock_start_count back to spacecraft clock count, and
        # round the result.
        new_start_count_e = cspyce.utc2et(str(new_start_count_utc))
        new_start_count = cspyce.sce2s(cassini_id, new_start_count_e)
        new_start_count = f"{round(float(new_start_count.split('/')[1]))}.000"

        # Overwrite spacecraft_clock_start_count
        start_count_elem.text = new_start_count

        # Convert stop_date_time to datetime object
        stop_time_dt = datetime.strptime(stop_time_elem.text, "%Y-%m-%dT%H:%M:%S.%fZ")

        # Subtract exposure duration from stop_time
        new_start_time_dt = stop_time_dt - timedelta(seconds=exposure_duration)

        # Convert back to ISO format
        new_start_time = new_start_time_dt.strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"

        # Overwrite start_date_time
        start_time_elem.text = new_start_time

        # Call function to add Modification_Detail
        add_modification_detail(root, namespaces)

        # Ensure proper formatting
        etree.indent(tree, space="    ")

        # Save the updated XML
        tree.write(file_path, pretty_print=True, xml_declaration=True, encoding="UTF-8")
        print(f"Updated {file_path}")

    # Clear all SPICE kernels after processing
    cspyce.kclear()

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('directorypath', type=str, metavar='DIRECTORY_PATH',
                        help='The path to the directory')
    parser.add_argument('pattern', type=str, metavar='PATTERN',
                        help='The extension of the labels you want to fix')
    parser.add_argument('kernel_directory', type=str, metavar='KERNEL_DIRECTORY',
                        help='The path to the kernel directory')

    args = parser.parse_args()
    start_time_replace(args.directorypath, args.pattern, args.kernel_directory)

if __name__ == '__main__':
    main()
