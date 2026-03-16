import argparse
from pathlib import Path
import shutil
import json
import html
import re
import hashlib


def infer_dataset_id_from_path(pds4_dir, pds3_dir):
    """Infer dataset_id from PDS4 or PDS3 directory path (e.g. cassini_iss_cruise)."""
    for path_str in (pds4_dir, pds3_dir):
        if not path_str:
            continue
        path = Path(path_str)
        for part in path.parts:
            if re.match(r'cassini_iss_[a-z]+', part):
                return part
    return 'cassini_iss_cruise'


def extract_dataset_id_from_label(label_text):
    """Extract dataset_id from logical_identifier in label (e.g. cassini_iss_saturn). Returns None if not found."""
    match = re.search(r'<logical_identifier>\s*urn:nasa:pds:([^:]+):', label_text)
    return match.group(1) if match else None


def _normalize_multiline_xml_content(value):
    """Escape for XML and normalize newlines so continuation lines use consistent indentation (24 spaces)."""
    escaped = html.escape(value)
    if '\n' not in escaped:
        return escaped
    lines = [line.strip() for line in escaped.splitlines() if line.strip()]
    if not lines:
        return ''
    continuation_indent = ' ' * 24
    return lines[0] + ''.join('\n' + continuation_indent + ln for ln in lines[1:])


def migrate_iss(pds4_dir, pds3_dir, pattern, json_path, destination_path, dataset_id=None):
    # Define directories and patterns
    pds4_directory = Path(pds4_dir)
    pds3_directory = Path(pds3_dir)
    dest_root = Path(destination_path)

    # Load JSON calibration metadata
    with open(Path(json_path), 'r', encoding='utf-8') as jf:
        calibration_data = json.load(jf)

    # License block to insert
    license_block = '''        <License_Information>
            <name>Creative Common Public License CC0 1.0 (2024)</name>
            <description>Creative Commons Zero (CC0) license information</description>
            <Internal_Reference>
                <lid_reference>urn:nasa:pds:system_bundle:document_pds4_standards:creative_commons_zero_1.0.0</lid_reference>
                <reference_type>product_to_license</reference_type>
            </Internal_Reference>
        </License_Information>
    '''

    # Extract path components from pds3_directory
    # Path structure: .../COISS_1xxx/COISS_1001/data/1294561143_1295221348
    pds3_path_parts = pds3_directory.parts
    coiss_volume_pattern = None  # e.g., COISS_1xxx
    coiss_volume = None  # e.g., COISS_1001
    data_directory = None  # e.g., 1294561143_1295221348
    
    # Find COISS_*xxx pattern and COISS_#### pattern in the path
    for i, part in enumerate(pds3_path_parts):
        if re.match(r'COISS_\dxxx', part):
            coiss_volume_pattern = part
        elif re.match(r'COISS_\d{4}', part):
            coiss_volume = part
        elif part == 'data' and i + 1 < len(pds3_path_parts):
            data_directory = pds3_path_parts[i + 1]
    
    # Process files
    # Walk recursively under the top-level PDS4 directory and match the pattern
    for file_path in pds4_directory.rglob(pattern):
        try:
            name = file_path.stem
            new_name = f"{name}_calib.lblx"
            # Mirror the input directory structure under the destination root
            # Example:
            #   pds4_dir / subdir1 / subdir2 / file.lblx
            # becomes
            #   destination_path / subdir1 / subdir2 / file_calib.lblx
            rel_path = file_path.relative_to(pds4_directory)
            # Handle case where file is in root of pds4_directory (rel_path.parent is '.')
            if rel_path.parent == Path('.'):
                dest_dir = dest_root
            else:
                dest_dir = dest_root / rel_path.parent
            dest_dir.mkdir(parents=True, exist_ok=True)
            dest_path = dest_dir / new_name
            
            # Check if output file already exists - skip if it does
            if dest_path.exists():
                print(f"Skipping {name}: {new_name} already exists")
                continue

            # Extract calibration info - check before copying file
            lookup_key = f"{name}"
            calibration_info = calibration_data.get(lookup_key)

            if calibration_info is None:
                print(f"Skipping {name}: No calibration info found in JSON")
                continue

            # Resolve dataset_id for this file: CLI/passed value, or from source label LID, or from path, or default
            if dataset_id is not None:
                file_dataset_id = dataset_id
            else:
                source_text = file_path.read_text(encoding='utf-8')
                file_dataset_id = extract_dataset_id_from_label(source_text) or infer_dataset_id_from_path(pds4_dir, pds3_dir)
            
            # Copy the file only if calibration info exists
            shutil.copyfile(file_path, dest_path)

            # Convert flag values
            for key in calibration_info:
                if "FLAG" in key and calibration_info[key] in ("0", "1"):
                    calibration_info[key] = "ENABLED" if calibration_info[key] == "1" else "DISABLED"

            # Convert dark current correction type values
            for key in calibration_info:
                if "DARK_CURRENT_CORRECTION_TYPE" in key and calibration_info[key] in ("Interpolation method", "2-parameter method"):
                    if calibration_info[key] == "Interpolation method":
                        calibration_info[key] = "Interpolation model"
                    elif calibration_info[key] == "2-parameter method":
                        calibration_info[key] = "2-parameter model"
                    else:
                        continue

            # Build radiometric correction text separately to avoid nested f-string issues
            # Escape XML special chars (e.g. &, <) before inserting into the element
            radiometric_text = ""
            if "RADIOMETRIC_CORRECTION_TEXT" in calibration_info:
                raw = calibration_info["RADIOMETRIC_CORRECTION_TEXT"]
                escaped = html.escape(raw)
                lines = [f'                        {line.strip()};' for line in escaped.split(";") if line.strip()]
                radiometric_text = f'''                    <cassini:radiometric_correction_text>
{chr(10).join(lines)}
                    </cassini:radiometric_correction_text>'''
            
            # Build cassini block with proper indentation (16 spaces for opening/closing, 20 for children)
            cassini_block = f'''                <cassini:ISS_Calibrated_Attributes>
{f'                    <cassini:dark_current_correction_type>{html.escape(calibration_info["DARK_CURRENT_CORRECTION_TYPE"])}</cassini:dark_current_correction_type>' if "DARK_CURRENT_CORRECTION_TYPE" in calibration_info else ""}
{f'                    <cassini:dark_current_file_name>{html.escape(calibration_info["DARK_CURRENT_FILE_NAME"])}</cassini:dark_current_file_name>' if "DARK_CURRENT_FILE_NAME" in calibration_info else ""}
{f'                    <cassini:dark_current_parameter_file>{html.escape(calibration_info["DARK_CURRENT_PARAM_FILE"])}</cassini:dark_current_parameter_file>' if "DARK_CURRENT_PARAM_FILE" in calibration_info else ""}
{f'                    <cassini:nonlinearity_correction_flag>{html.escape(calibration_info["NONLINEARITY_CORRECTION_FLAG"])}</cassini:nonlinearity_correction_flag>' if "NONLINEARITY_CORRECTION_FLAG" in calibration_info else ""}
{f'                    <cassini:flat_field_correction_flag>{html.escape(calibration_info["FLATFIELD_CORRECTION_FLAG"])}</cassini:flat_field_correction_flag>' if "FLATFIELD_CORRECTION_FLAG" in calibration_info else ""}
{f'                    <cassini:slope_file_name>{html.escape(calibration_info["SLOPE_FILE_NAME"])}</cassini:slope_file_name>' if "SLOPE_FILE_NAME" in calibration_info else ""}
{f'                    <cassini:gain_correction>{html.escape(calibration_info["GAIN_CORRECTION"])}</cassini:gain_correction>' if "GAIN_CORRECTION" in calibration_info else ""}
{f'                    <cassini:geometry_projection_type>{html.escape(calibration_info["GEOMETRY_PROJECTION_TYPE"])}</cassini:geometry_projection_type>' if "GEOMETRY_PROJECTION_TYPE" in calibration_info else ""}
{f'                    <cassini:exposure_correction_flag>{html.escape(calibration_info["EXPOSURE_CORRECTION_FLAG"])}</cassini:exposure_correction_flag>' if "EXPOSURE_CORRECTION_FLAG" in calibration_info else ""}
{f'                    <cassini:shutter_offset_file_name>{html.escape(calibration_info["SHUTTER_OFFSET_FILE_NAME"])}</cassini:shutter_offset_file_name>' if "SHUTTER_OFFSET_FILE_NAME" in calibration_info else ""}
{f'                    <cassini:exposure_offset>{html.escape(calibration_info["EXPOSURE_OFFSET"])}</cassini:exposure_offset>' if "EXPOSURE_OFFSET" in calibration_info else ""}
{radiometric_text}
{f'                    <cassini:calibration_units>{html.escape(calibration_info["UNITS"])}</cassini:calibration_units>' if "UNITS" in calibration_info else ""}
{f'                    <cassini:calibration_stage>{html.escape(calibration_info["CALIBRATION_STAGE"])}</cassini:calibration_stage>' if "CALIBRATION_STAGE" in calibration_info else ""}
{f'                    <cassini:ab_pixel_correction_flag>{html.escape(calibration_info["AB_PIXEL_CORRECTION_FLAG"])}</cassini:ab_pixel_correction_flag>' if "AB_PIXEL_CORRECTION_FLAG" in calibration_info else ""}
{f'                    <cassini:bias_subtraction_text>{html.escape(calibration_info["BIAS_SUBTRACTION_TEXT"])}</cassini:bias_subtraction_text>' if "BIAS_SUBTRACTION_TEXT" in calibration_info else ""}
{f'                    <cassini:data_conversion_text>{html.escape(calibration_info["DATA_CONVERSION_TEXT"])}</cassini:data_conversion_text>' if "DATA_CONVERSION_TEXT" in calibration_info else ""}
{f'                    <cassini:flat_field_file_name>{_normalize_multiline_xml_content(calibration_info["FLAT_FIELD_FILE_NAME"])}\n                    </cassini:flat_field_file_name>' if "FLAT_FIELD_FILE_NAME" in calibration_info else ""}
{f'                    <cassini:uneven_bit_weight_correction_flag>{html.escape(calibration_info["UNEVEN_BIT_WEIGHT_CORRECTION_FLAG"])}</cassini:uneven_bit_weight_correction_flag>' if "UNEVEN_BIT_WEIGHT_CORRECTION_FLAG" in calibration_info else ""}
                </cassini:ISS_Calibrated_Attributes>
'''

            text = dest_path.read_text(encoding='utf-8')

            # Add proc namespace and schema references
            # Add proc xml-model after cassini xml-model
            proc_xml_model = '''<?xml-model href="https://pds.nasa.gov/pds4/proc/v1/PDS4_PROC_1O00_1400.sch"
    schematypens="http://purl.oclc.org/dsdl/schematron"?>
'''
            # Find the last xml-model line and insert proc after it
            text = re.sub(
                r'(<\?xml-model href="https://pds\.nasa\.gov/pds4/mission/cassini/v1/PDS4_CASSINI_1O00_1810\.sch"\s+schematypens="http://purl\.oclc\.org/dsdl/schematron"\?>\n)',
                r'\1' + proc_xml_model,
                text
            )
            
            # Add proc namespace declaration
            text = re.sub(
                r'(xmlns:cassini="http://pds\.nasa\.gov/pds4/mission/cassini/v1"\n)',
                r'\1  xmlns:proc="http://pds.nasa.gov/pds4/proc/v1"\n',
                text
            )
            
            # Add proc schema location
            text = re.sub(
                r'(http://pds\.nasa\.gov/pds4/mission/cassini/v1 https://pds\.nasa\.gov/pds4/mission/cassini/v1/PDS4_CASSINI_1O00_1810\.xsd)(">)',
                r'\1\n  http://pds.nasa.gov/pds4/proc/v1 https://pds.nasa.gov/pds4/proc/v1/PDS4_PROC_1O00_1400.xsd\2',
                text
            )

            # Update logical_identifier
            text = re.sub(
                r"<logical_identifier>.*?</logical_identifier>",
                f"<logical_identifier>urn:nasa:pds:{file_dataset_id}:data_calibrated:{name}_calib</logical_identifier>",
                text,
                flags=re.DOTALL,
            )

            # Update title to include _calib in filename
            text = re.sub(
                r'<title>Cassini ISS Image ([^<]+)\.img</title>',
                f'<title>Cassini ISS Calibrated Image {name}_calib.img</title>',
                text,
            )

            # Update Observation_Area comment to reference PDS4 label creation
            # Extract first 5 digits for the path pattern (e.g., 12945xxxxx)
            name_prefix = name[:5] if len(name) >= 5 else name
            new_comment = f'''        <comment>
            This label was created from the original PDS4 label:
            {file_dataset_id}/data_raw/{name_prefix}xxxxx/{name}.lblx
            The contents of this label include metadata extracted from
            the calibrated PDS3 data product.
        </comment>'''
            # Match the entire comment block from Observation_Area
            text = re.sub(
                r'        <comment>\s*This data file was migrated from the original PDS3 file:.*?</comment>',
                new_comment,
                text,
                flags=re.DOTALL,
            )

            # Update processing_level from Raw to Calibrated
            text = re.sub(
                r'<processing_level>Raw</processing_level>',
                '<processing_level>Calibrated</processing_level>',
                text,
            )

            # Remove v2.0 correction comments (no longer pertinent)
            text = re.sub(
                r'\s*<!-- Corrected for v2\.0 \(see Modification_Detail\) -->',
                '',
                text,
            )

            # Update version_id from 1.1 to 1.0
            text = re.sub(
                r'<version_id>1\.1</version_id>',
                '<version_id>1.0</version_id>',
                text,
            )

            # Update Modification_History: Remove 1.1 entry and replace 1.0 entry
            new_modification_detail = '''            <Modification_Detail>
                <modification_date>2025-12-02</modification_date>
                <version_id>1.0</version_id>
                <description>Initial PDS4 Version.</description>
            </Modification_Detail>'''
            
            # Remove the 1.1 Modification_Detail entry (match the entire block with proper whitespace)
            text = re.sub(
                r'            <Modification_Detail>.*?<modification_date>2025-03-03</modification_date>.*?<version_id>1\.1</version_id>.*?</Modification_Detail>\s*',
                '',
                text,
                flags=re.DOTALL,
            )
            
            # Replace the 1.0 Modification_Detail entry (match the entire block with proper whitespace)
            text = re.sub(
                r'            <Modification_Detail>.*?<modification_date>2020-03-31</modification_date>.*?<version_id>1\.0</version_id>.*?<description>Initial PDS4 Version\. Migrated from the PDS3 data product\.</description>.*?</Modification_Detail>',
                new_modification_detail,
                text,
                flags=re.DOTALL,
            )

            # Clean the block and ensure proper formatting
            cleaned_block = "\n".join([line for line in cassini_block.splitlines() if line.strip() != ""])
            
            # Inject cassini block - check if Legacy_Metadata exists in the original file
            # IMPORTANT: We NEVER create/inject a Legacy_Metadata section if it doesn't exist.
            # We only work with existing Legacy_Metadata sections.
            insertion_point = text.find('<cassini:Legacy_Metadata>')
            if insertion_point == -1:
                # No Legacy_Metadata found - do NOT create one. Inject calibrated attributes after </ISS_Specific_Attributes>
                iss_end = text.find('</cassini:ISS_Specific_Attributes>')
                if iss_end == -1:
                    print(f"No <cassini:Legacy_Metadata> or </cassini:ISS_Specific_Attributes> found in {name}_calib.lblx")
                    continue
                # Find the end of the line containing </ISS_Specific_Attributes>
                line_end = text.find('\n', iss_end)
                if line_end == -1:
                    line_end = len(text)
                # Insert the block after </ISS_Specific_Attributes> with proper newline
                updated_text = text[:line_end] + "\n" + cleaned_block + text[line_end:]
            else:
                
                # Insert the block with proper newline before it
                # Remove any trailing whitespace before insertion point, then add newline and block
                updated_text = text[:insertion_point].rstrip() + "\n" + cleaned_block + "\n" + text[insertion_point:]
                
                # Fix Legacy_Metadata indentation if needed (should be 16 spaces to match ISS_Specific_Attributes)
                updated_text = re.sub(
                    r'^(\s*)<cassini:Legacy_Metadata>',
                    r'                <cassini:Legacy_Metadata>',
                    updated_text,
                    flags=re.MULTILINE
                )
                updated_text = re.sub(
                    r'^(\s*)</cassini:Legacy_Metadata>',
                    r'                </cassini:Legacy_Metadata>',
                    updated_text,
                    flags=re.MULTILINE
                )

            # Inject proc:Processing_Information block after </cassini:Cassini>
            processing_info_block = '''            <proc:Processing_Information>
                <Local_Internal_Reference>
                    <local_identifier_reference>image</local_identifier_reference>
                    <local_reference_type>processing_information_to_data_object</local_reference_type>
                </Local_Internal_Reference>
                <proc:Process>
                    <proc:Software>
                        <proc:name>CISSCAL</proc:name>
                        <proc:software_id>Cassini Imaging Science Subsystem Calibration</proc:software_id>
                        <proc:software_version_id>4.0</proc:software_version_id> <!--Note: Version 4.0 is identical to 4.1, except for documentation-->
                        <proc:software_availability>Open source</proc:software_availability>
                        <proc:description>Calibration software used to create this calibrated product. See internal references to software documents and user guide in the Reference_List of this label.</proc:description>
                        <External_Reference>
                            <reference_text>CO-CAL-ISSNA/ISSWA-2-EDR-V4.2:COISS_0011:extras/cisscal</reference_text>
                            <description>
                                The Cassini ISS Calibration (CISSCAL) software package, version 4.0. 
                                For more information, please see see chapters 3 and 4 of the ISS Data User's Guide. 
                                The original PDS3 directory containing the CISSCAL source code (in the form of documents, without any warranty as usable software) along with some supporting documents is given in the reference_text, as dataset_id:volume_id:directory_path.
                            </description>
                        </External_Reference>
                    </proc:Software>
                </proc:Process>
            </proc:Processing_Information>'''
            
            # Find </cassini:Cassini> and insert Processing_Information after it
            cassini_end = updated_text.find('</cassini:Cassini>')
            if cassini_end != -1:
                # Find the end of the line containing </cassini:Cassini>
                line_end = updated_text.find('\n', cassini_end)
                if line_end == -1:
                    line_end = len(updated_text)
                # Insert the block after the closing tag with proper newline
                updated_text = updated_text[:line_end] + '\n' + processing_info_block + updated_text[line_end:]
            else:
                print(f"Warning: </cassini:Cassini> not found in {name}_calib.lblx")

            # Inject license block after </Modification_Detail>
            updated_text = re.sub(
                r"(</Modification_History>)",
                r"\1\n" + license_block.rstrip(),
                updated_text,
                count=1
            )

            # Remove Telemetry Table
            updated_text = re.sub(
                r'\s*<!-- Telemetry Table -->\s*<Array>.*?<local_identifier>telemetry-table</local_identifier>.*?</Array>\s*',
                '',
                updated_text,
                flags=re.DOTALL,
            )

            # Remove Line Prefix Bytes block
            updated_text = re.sub(
                r'\s*<!-- Line prefix bytes -->\s*<Array_2D>.*?</Array_2D>\s*',
                '',
                updated_text,
                flags=re.DOTALL,
            )

            # Extract path information from existing Source_Product_External for constructing new entry
            # Pattern matches: CO-E/V/J-ISSNA/ISSWA-2-EDR-V1.0:COISS_1001:data/1295221411_1313633653:N1308947228_1.IMG
            existing_source_match = re.search(
                r'<external_source_product_identifier>\s*(?:CO-E/V/J-ISSNA/ISSWA-2-EDR-V1\.0:)?(COISS_\d+):data/(\d+_\d+):([^\s<]+)',
                updated_text,
                re.DOTALL
            )
            
            # Use extracted path components or fallback to extracted values
            volume_pattern = coiss_volume_pattern if coiss_volume_pattern else 'COISS_1xxx'
            data_dir = data_directory if data_directory else None
            
            # Determine instrument type for external_source_product_identifier (ISSWA for wide, ISSNA for narrow)
            name_lower = name.lower()
            instrument_type = 'ISSWA' if name_lower.endswith('w') else 'ISSNA'
            
            if existing_source_match:
                volume_from_existing = existing_source_match.group(1)  # e.g., COISS_1001 (from existing Source_Product_External)
                path_part = existing_source_match.group(2)  # e.g., 1295221411_1313633653 (from existing Source_Product_External)
                filename_part = existing_source_match.group(3).strip()  # e.g., N1308947228_1.IMG
                # Construct CALIB filename: replace .IMG with _CALIB.IMG
                calib_filename = filename_part.replace('.IMG', '_CALIB.IMG')
                # Use values from existing Source_Product_External as they're correct for this specific file
                final_volume = volume_from_existing
                final_data_dir = path_part
                # Format: CO-E/V/J-ISSNA/ISSWA-2-EDR-V1.0:calibrated:COISS_1xxx:COISS_1001:data/...
                external_source_id = f'CO-E/V/J-{instrument_type}-2-EDR-V1.0:calibrated:{volume_pattern}:{final_volume}:data/{final_data_dir}:{calib_filename}'
            else:
                # Fallback if pattern doesn't match - use name to construct
                # Detect camera type from name suffix (w = wide, n = narrow)
                camera_prefix = 'N' if name_lower.endswith('n') else 'W'  # Default to W if not n
                
                # Use volume from path or default
                final_volume = coiss_volume if coiss_volume else 'COISS_1001'
                
                # Extract image number from name (e.g., 1294561143w -> 1294561143)
                image_num_match = re.search(r'(\d+)', name)
                if image_num_match:
                    image_num = image_num_match.group(1)
                    # Use data_dir from path if available, otherwise construct from image_num
                    final_data_dir = data_dir if data_dir else f'{image_num}_{image_num}'
                    # Format: CO-E/V/J-ISSNA/ISSWA-2-EDR-V1.0:calibrated:COISS_1xxx:COISS_1001:data/...
                    external_source_id = f'CO-E/V/J-{instrument_type}-2-EDR-V1.0:calibrated:{volume_pattern}:{final_volume}:data/{final_data_dir}:{camera_prefix}{image_num}_1_CALIB.IMG'
                else:
                    # If no numbers found, use name directly and construct a reasonable path
                    # Remove suffix letter (w/n) and extract alphanumeric part
                    name_base = re.sub(r'[^a-zA-Z0-9]', '', name.rstrip('wn'))
                    final_data_dir = data_dir if data_dir else f'{name_base}_{name_base}'
                    # Format: CO-E/V/J-ISSNA/ISSWA-2-EDR-V1.0:calibrated:COISS_1xxx:COISS_1001:data/...
                    external_source_id = f'CO-E/V/J-{instrument_type}-2-EDR-V1.0:calibrated:{volume_pattern}:{final_volume}:data/{final_data_dir}:{camera_prefix}{name_base}_CALIB.IMG'
            
            # Inject calibration document references after edrsis in Reference_List
            calibration_docs = f'''<Internal_Reference>
            <lid_reference>urn:nasa:pds:{file_dataset_id}:document:in_flight_cal</lid_reference>
            <reference_type>data_to_document</reference_type>
            <comment>
                In-Flight Calibration of the Cassini ISS.
            </comment>
        </Internal_Reference>
        <Internal_Reference>
            <lid_reference>urn:nasa:pds:{file_dataset_id}:document:theoretical_basis</lid_reference>
            <reference_type>data_to_document</reference_type>
            <comment>
                Theoretical Basis for the Cassini CISSCAL Program.
            </comment>
        </Internal_Reference>
        '''
            # Insert calibration doc references after edrsis Internal_Reference
            updated_text = re.sub(
                rf'(        <Internal_Reference>\s*<lid_reference>urn:nasa:pds:{re.escape(file_dataset_id)}:document:edrsis</lid_reference>.*?</Internal_Reference>\s*)',
                r'\1' + calibration_docs,
                updated_text,
                flags=re.DOTALL,
            )
            
            # Inject new Internal_Reference and Source_Product_External entries before existing Source_Product_External
            new_references = f'''        <Internal_Reference>
            <lid_reference>urn:nasa:pds:{file_dataset_id}:data_raw:{name}</lid_reference>
            <reference_type>data_to_raw_product</reference_type>
            <comment>
                The raw product from which this calibrated product was produced.
            </comment>
        </Internal_Reference>
        <Source_Product_External>
            <external_source_product_identifier>
                {external_source_id}
            </external_source_product_identifier>
            <reference_type>data_to_raw_source_product</reference_type>
            <curating_facility>PDS RMS Node</curating_facility>
            <description>
                Calibrated ISS images were produced in PDS3 style but not peer-reviewed.
                They have been available since 2016 in the holdings of the PDS Ring-Moon
                Systems node and are currently listed as part of the RMS Annex,
                urn:nasa:rms-annex:{file_dataset_id}
            </description>
        </Source_Product_External>
'''
            # Insert before the existing Source_Product_External
            updated_text = re.sub(
                r'(        </Internal_Reference>\s*)(        <Source_Product_External>)',
                r'\1' + new_references + r'\2',
                updated_text,
                flags=re.DOTALL,
            )

            # Fix merged comment after </Header>
            updated_text = re.sub(
                r'(</Header>)<!-- The image -->',
                r'\1\n\n<!-- The image -->',
                updated_text
            )

            # Fix closing tag formatting
            updated_text = re.sub(
                r'(</Array_2D_Image>)(</File_Area_Observational>)',
                r'\1\n    \2',
                updated_text
            )

            dest_path.write_text(updated_text, encoding='utf-8')
            print(f"Updated {name}_calib.lblx")

        except Exception as e:
            print(f"Failed to process {file_path}: {e}")

def calculate_md5(file_path):
    """Calculate MD5 checksum of a file."""
    hash_md5 = hashlib.md5()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()

def fix_file_name(lblx_path):
    """Fix the file_name attribute to include _calib before the extension."""
    try:
        # Read the label file
        text = lblx_path.read_text(encoding='utf-8')
        
        # Find file_name pattern: <file_name>name.img</file_name> and add _calib before .img
        # Pattern matches: <file_name>name.img</file_name> where name doesn't already have _calib
        pattern = r'(<file_name>)([^<]+?)(\.img)(</file_name>)'
        
        def replace_filename(match):
            prefix = match.group(1)
            name = match.group(2)
            ext = match.group(3)
            suffix = match.group(4)
            # Only add _calib if it's not already there
            if '_calib' not in name:
                return f"{prefix}{name}_calib{ext}{suffix}"
            return match.group(0)  # Return unchanged if _calib already present
        
        if re.search(pattern, text):
            updated_text = re.sub(pattern, replace_filename, text)
            if updated_text != text:
                lblx_path.write_text(updated_text, encoding='utf-8')
                print(f"Updated file_name in {lblx_path.name}")
                return True
        return False
            
    except Exception as e:
        print(f"Failed to fix file_name in {lblx_path}: {e}")
        return False

def fix_md5_checksum(lblx_path):
    """Fix the MD5 checksum in a *_calib.lblx file by calculating it from the corresponding .img file."""
    try:
        # Read the label file
        text = lblx_path.read_text(encoding='utf-8')
        
        # Try to find the file_name from the label first
        file_name_match = re.search(r'<file_name>([^<]+)</file_name>', text)
        if file_name_match:
            img_filename = file_name_match.group(1)
            img_path = lblx_path.parent / img_filename
            # If file doesn't exist, try the _calib variant
            if not img_path.exists() and '_calib' not in img_filename:
                # Try adding _calib before .img extension
                base_name, ext = img_filename.rsplit('.', 1) if '.' in img_filename else (img_filename, '')
                calib_filename = f"{base_name}_calib.{ext}" if ext else f"{base_name}_calib"
                calib_img_path = lblx_path.parent / calib_filename
                if calib_img_path.exists():
                    img_path = calib_img_path
        else:
            # Fallback: If lblx is "name_calib.lblx", try "name_calib.img" first, then "name.img"
            base_name = lblx_path.stem  # This already includes _calib
            img_path = lblx_path.parent / f"{base_name}.img"
            if not img_path.exists():
                # Try without _calib
                base_name_no_calib = base_name.replace("_calib", "")
                img_path = lblx_path.parent / f"{base_name_no_calib}.img"
        
        if not img_path.exists():
            print(f"Warning: {img_path} not found for {lblx_path.name}")
            return False
        
        # Calculate MD5 of the .img file
        md5_checksum = calculate_md5(img_path)
        
        # Find and replace the md5_checksum value
        # Pattern matches: <md5_checksum>any_value</md5_checksum>
        pattern = r'(<md5_checksum>)([^<]+)(</md5_checksum>)'
        
        # Check if MD5 checksum is already correct
        match = re.search(pattern, text)
        if match:
            current_checksum = match.group(2)
            # Only update if the checksum is different
            if current_checksum == md5_checksum:
                return False  # Already correct, no need to update
            
            # Use a function for replacement to avoid regex backreference issues
            def replace_checksum(m):
                return m.group(1) + md5_checksum + m.group(3)
            
            updated_text = re.sub(pattern, replace_checksum, text)
            lblx_path.write_text(updated_text, encoding='utf-8')
            print(f"Updated MD5 checksum in {lblx_path.name}: {md5_checksum}")
            return True
        else:
            print(f"Warning: No <md5_checksum> tag found in {lblx_path.name}")
            return False
            
    except Exception as e:
        print(f"Failed to fix MD5 checksum in {lblx_path}: {e}")
        return False

def fix_proc_namespace(lblx_path):
    """Add missing xmlns:proc namespace declaration after xmlns:cassini and before xsi:schemaLocation."""
    try:
        # Read the label file
        text = lblx_path.read_text(encoding='utf-8')
        
        # Check if xmlns:proc is already present
        if 'xmlns:proc="http://pds.nasa.gov/pds4/proc/v1"' in text:
            return False  # Already present, no fix needed
        
        # Check if proc:Processing_Information is used (need the namespace)
        if 'proc:Processing_Information' not in text:
            return False  # proc namespace not used, no fix needed
        
        # Pattern to insert xmlns:proc after xmlns:cassini and before xsi:schemaLocation.
        # Allow arbitrary whitespace/newlines (and other attributes) between them (multi-line root element).
        pattern = r'(xmlns:cassini="http://pds\.nasa\.gov/pds4/mission/cassini/v1")([\s\S]*?)(xsi:schemaLocation=)'
        replacement = r'\1 xmlns:proc="http://pds.nasa.gov/pds4/proc/v1"\2\3'
        
        if re.search(pattern, text):
            updated_text = re.sub(pattern, replacement, text)
            if updated_text != text:
                lblx_path.write_text(updated_text, encoding='utf-8')
                print(f"Added xmlns:proc namespace in {lblx_path.name}")
                return True
        else:
            print(f"Warning: Could not find insertion point for xmlns:proc in {lblx_path.name}")
        return False
            
    except Exception as e:
        print(f"Failed to fix proc namespace in {lblx_path}: {e}")
        return False

def fix_mode(directory):
    """Apply fixes to all *_calib.lblx files in the given directory."""
    directory_path = Path(directory)
    
    if not directory_path.exists():
        print(f"Error: Directory {directory} does not exist")
        return
    
    if not directory_path.is_dir():
        print(f"Error: {directory} is not a directory")
        return
    
    # Find all *_calib.lblx files recursively
    calib_files = list(directory_path.rglob("*_calib.lblx"))
    
    if not calib_files:
        print(f"No *_calib.lblx files found in {directory}")
        return
    
    print(f"Found {len(calib_files)} *_calib.lblx file(s) to process")
    
    # Apply fixes
    for lblx_file in calib_files:
        # Fix 1: file_name attribute (add _calib before extension)
        fix_file_name(lblx_file)
        # Fix 2: MD5 checksum
        fix_md5_checksum(lblx_file)
        # Fix 3: Add missing xmlns:proc namespace declaration
        fix_proc_namespace(lblx_file)
    
    print("Fix mode completed")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--fix-mode', action='store_true',
                        help='Run in fix mode: find all *_calib.lblx files and apply fixes')
    parser.add_argument('--directory', type=str, metavar='DIRECTORY',
                        help='Directory to search for *_calib.lblx files (required with --fix-mode)')
    parser.add_argument('pds4_directory', type=str, nargs='?', metavar='PDS4_DIRECTORY',
                        help='The path to the PDS4 directory (required without --fix-mode)')
    parser.add_argument('pds3_directory', type=str, nargs='?', metavar='PDS3_DIRECTORY',
                        help='The path to the PDS3 directory (required without --fix-mode)')
    parser.add_argument('pattern', type=str, nargs='?', metavar='PATTERN',
                        help='The extension of the labels you want to migrate into PDS4 (required without --fix-mode)')
    parser.add_argument('json_path', type=str, nargs='?', metavar='JSON_PATH',
                        help='The path to the JSON file containing information for cruise'
                             ' or saturn (required without --fix-mode)')
    parser.add_argument('destination_path', type=str, nargs='?', metavar='DEST_PATH',
                        help='The path to where you want the final labels to go (required without --fix-mode)')
    parser.add_argument('--dataset-id', type=str, metavar='DATASET_ID',
                        help='Dataset ID for LIDs/paths (e.g. cassini_iss_cruise). If omitted, inferred per file from each label\'s logical_identifier (preserves cruise vs saturn).')

    args = parser.parse_args()

    if args.fix_mode:
        if not args.directory:
            parser.error("--directory is required when using --fix-mode")
        fix_mode(args.directory)
    else:
        if not all([args.pds4_directory, args.pds3_directory, args.pattern, args.json_path, args.destination_path]):
            parser.error("All migration arguments are required when not using --fix-mode")
        migrate_iss(args.pds4_directory, args.pds3_directory, args.pattern, args.json_path,
                    args.destination_path, dataset_id=args.dataset_id)

if __name__ == '__main__':
    main()