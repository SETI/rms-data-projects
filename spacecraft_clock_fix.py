import argparse
import cspyce
from lxml import etree
from pathlib import Path

def start_time_replace(directory_path, pattern, kernel_dir):
    """
    Processes PDS4 label files in a given directory to update spacecraft_clock_start_count 
    and start_date_time based on exposure duration and spacecraft_clock_stop_count.

    This function:
    - Loads SPICE kernels from the specified kernel directory.
    - Iterates through all XML label files matching the given pattern in the directory.
    - Extracts spacecraft clock stop count, start count, and exposure duration.
    - Computes the corrected spacecraft clock start count and start date-time.
    - Updates and saves the modified XML files.

    Parameters:
        directory_path (str): Path to the directory containing the XML label files.
        pattern (str): File extension pattern to match label files (e.g., "lblx").
        kernel_dir (str): Path to the directory containing SPICE kernels.
    """

    loaded_kernels = []
    # Load cspyce kernels from kernel directory
    kernels = Path(kernel_dir)
    if not kernels.exists():
        print(f"Kernel directory {kernel_dir} does not exist!")
        return
    
    for file in kernels.iterdir():
        if file.suffix in ['.tsc', '.tls', '.bsp', '.tf']:
            cspyce.furnsh(str(file))
            loaded_kernels.append(str(file))  # Track loaded kernels

    # Define spacecraft ID
    cassini_id = -82  # SPICE ID for Cassini

    # Walk through all subdirectories and files
    directory_path = Path(directory_path)
    files = directory_path.rglob(f"*.{pattern}")  # rglob ensures all subdirectories are included
    for file_path in files:
        print('Now fixing:', file_path.name)
        
        # Parse the XML file
        tree = etree.parse(file_path)
        root = tree.getroot()

        # Get the namespaces
        namespaces = root.nsmap

        # Extract values safely
        stop_count_elem = root.find(".//cassini:spacecraft_clock_stop_count", namespaces=namespaces)
        start_count_elem = root.find(".//cassini:spacecraft_clock_start_count", namespaces=namespaces)
        start_time_elem = root.find(".//start_date_time", namespaces=namespaces)
        exposure_duration_elem = root.find(".//cassini:exposure_duration", namespaces=namespaces)

        if None in (stop_count_elem, start_count_elem, start_time_elem, exposure_duration_elem):
            print(f"Skipping {file_path}: Missing required elements.")
            continue

        stop_count = stop_count_elem.text
        exposure_duration = float(exposure_duration_elem.text) / 1000

        # Convert stop count to ephemeris time
        stop_count_e = cspyce.scs2e(cassini_id, stop_count)

        # Subtract exposure duration
        new_start_count_e = stop_count_e - exposure_duration
        new_start_count = cspyce.sce2s(cassini_id, new_start_count_e)
        new_start_count = f"{round(float(new_start_count.split('/')[1]))}.000"

        # Overwrite spacecraft_clock_start_count
        start_count_elem.text = new_start_count

        # Derive and update start_date_time
        new_start_time = f"{cspyce.et2utc(new_start_count_e, 'ISOC', 3)}Z"
        start_time_elem.text = new_start_time

        # Save the updated XML
        tree.write(file_path, pretty_print=True, xml_declaration=True, encoding="UTF-8")
        print(f"Updated {file_path}")

    for kernel in loaded_kernels:
        cspyce.unload(kernel)


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
