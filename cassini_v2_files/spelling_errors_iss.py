#!/usr/bin/env python3
"""
fix_iss_labels.py

Recursively scan a directory for Cassini ISS labels and fix specific wording
issues in place.

This script targets labels for the Cassini Imaging Science Subsystem (ISS),
covering both `cassini_iss_cruise` and `cassini_iss_saturn` collections.
It opens each matching file, applies conservative text replacements, and
writes the updated contents back to the same path.

Usage:
    python fix_iss_labels.py /path/to/root "*.xml"

Example:
    # Fix all XML labels under a cruise bundle directory
    python fix_iss_labels.py /data/pds/cassini_iss_cruise "*.xml"

Notes:
    - Files are read and written as UTF-8. If decoding fails, the file is
      read with `errors="replace"` to avoid crashes and still proceed.
    - Only simple text replacements are performed; no XML parsing is used.

"""

from __future__ import annotations

import argparse
from pathlib import Path
import sys


def apply_replacements_iss(text: str) -> tuple[str, int]:
    """Apply conservative ISS wording fixes to the given text.

    The function performs simple, case-sensitive replacements that have been
    validated for ISS labels. Replacements are intentionally minimal to avoid
    unintended changes.

    Args:
        text: The file contents to process.

    Returns:
        A tuple of:
            - The modified text.
            - The total number of replacements performed.
    """
    replacements = [
        # Preferred phrasing used consistently in ISS labels
#        ("The content of this data file", "The contents of this data file"),
#        ("the content of this data file", "the contents of this data file"),
#        ("The Content of this data file", "The Contents of this data file"),
#        ("PDS4_CASSINI_1O00_1800", "PDS4_CASSINI_1O00_1810"),
#        ("Cassini Orbiter Imaging Science Subsystem - Wide Angle Camera", "Imaging Science Subsystem - Wide Angle"),
#        ("Cassini Orbiter Imaging Science Subsystem - Narrow Angle Camera", "Imaging Science Subsystem - Narrow Angle"),
#        ("PDS4_CASSINI_1O00_1800", "PDS4_CASSINI_1O00_1810"),
#        ("Test Image", "Test_Image"),
#        ("<type>Sun</type>", "<type>Star</type>"),
#        ("<comment>The ISS Data User's Guide</comment>", "<comment>The ISS Data User's Guide (PDS3). DOI: 10.17189/1504135</comment>"),
#        ("</cassini:image_mid_time>", "</cassini:image_mid_time> <!-- Corrected for v2.0 (see Modification_Detail) -->"),
#        ("</cassini:image_time>", "</cassini:image_time> <!-- Corrected for v2.0 (see Modification_Detail) -->"),
#        ("<!-- Corrected for v2.0 (see Modification_Detail) --> <!-- Corrected for v2.0 (see Modification_Detail) -->", "<!-- Corrected for v2.0 (see Modification_Detail) -->"),
#        ("<lid_reference>urn:nasa:pds:cassini_iss_cruise:document:iss-wa-camera-description</lid_reference>", "<lid_reference>urn:nasa:pds:cassini_iss_saturn:document:iss-wa-camera-description</lid_reference>"),
#        ("<lid_reference>urn:nasa:pds:cassini_iss_cruise:document:iss-na-camera-description</lid_reference>", "<lid_reference>urn:nasa:pds:cassini_iss_saturn:document:iss-na-camera-description</lid_reference>"),
#        ("<lid_reference>urn:nasa:pds:cassini_iss_cruise:document:edrsis</lid_reference>",
#            "<lid_reference>urn:nasa:pds:cassini_iss_saturn:document:edrsis</lid_reference>"),
        ("<comment>CASSINI Software Interface Specification, Imaging Science Subsystem Data Products</comment>",
        "<comment>CASSINI Software Interface Specification, Imaging Science Subsystem Data Products; DOI: 10.17189/k8sd-a680</comment>")
#        ("Iota Centauri", "Io Cen"),
#        (
#    "        <Internal_Reference>\n"
#    "            <lid_reference>urn:nasa:pds:cassini_iss_saturn:document:iss-data-user-guide</lid_reference>\n"
#    "            <reference_type>data_to_document</reference_type>\n"
#    "            <comment>The ISS Data User's Guide (PDS3). DOI: 10.17189/1504135</comment>\n"
#    "        </Internal_Reference>",
#    "        <Internal_Reference>\n"
#    "            <lid_reference>urn:nasa:pds:cassini_iss_saturn:document:iss-data-user-guide</lid_reference>\n"
#    "            <reference_type>data_to_document</reference_type>\n"
#    "            <comment>The ISS Data User's Guide (PDS3). DOI: 10.17189/1504135</comment>\n"
#    "        </Internal_Reference>\n"
#    "        <Internal_Reference>\n"
#    "            <lid_reference>urn:nasa:pds:cassini_iss_cruise:document:iss-na-camera-description</lid_reference>\n"
#    "            <reference_type>data_to_document</reference_type>\n"
#    "            <comment>Cassini Narrow Angle Camera Description</comment>\n"
#    "        </Internal_Reference>\n"
#    "        <Internal_Reference>\n"
#    "            <lid_reference>urn:nasa:pds:cassini_iss_cruise:document:iss-wa-camera-description</lid_reference>\n"
#    "            <reference_type>data_to_document</reference_type>\n"
#    "            <comment>Cassini Wide Angle Camera Description</comment>\n"
#    "        </Internal_Reference>\n"
#    "        <Internal_Reference>\n"
#    "            <lid_reference>urn:nasa:pds:cassini_iss_cruise:document:edrsis</lid_reference>\n"
#    "            <reference_type>data_to_document</reference_type>\n"
#    "            <comment>CASSINI Software Interface Specification, Imaging Science Subsystem Data Products</comment>\n"
#    "        </Internal_Reference>\n"
#    "        <Internal_Reference>\n"
#    "            <lid_reference>urn:nasa:pds:cassini_iss_cruise:document:v2.0-modifications</lid_reference>\n"
#    "            <reference_type>data_to_document</reference_type>\n"
#    "            <comment>\n"
#    "                An overview of the changes made to the data product's label during the Cassini v2.0 bundles update process.\n"
#    "            </comment>\n"
#    "        </Internal_Reference>"
#),
#(
#    "            <reference_type>data_to_browse</reference_type>\n"
#    "            <comment>\n"
#    "                The browse image in JPEG format that illustrates the scientific content\n"
#    "                of this image.\n"
#    "            </comment>\n"
#    "        </Internal_Reference>\n"
#    "        <Internal_Reference>\n"
#    "            <lid_reference>urn:nasa:pds:cassini_iss_cruise:document:v2.0-modifications</lid_reference>\n"
#    "            <reference_type>data_to_document</reference_type>\n"
#    "            <comment>\n"
#    "                An overview of the changes made to the data product's label during the Cassini v2.0 bundles update process.\n"
#    "            </comment>\n"
#    "        </Internal_Reference>",
#    "            <reference_type>data_to_browse</reference_type>\n"
#    "            <comment>\n"
#    "                The browse image in JPEG format that illustrates the scientific content\n"
#    "                of this image.\n"
#    "            </comment>\n"
#    "        </Internal_Reference>"
#)

#    "        <Internal_Reference>\n"
#    "            <lid_reference>urn:nasa:pds:cassini_iss_saturn:document:dpsis</lid_reference>\n"
#    "            <reference_type>data_to_document</reference_type>\n"
#    "            <comment>This file is an ASCII Text document of the VIMS Data Product SIS.</comment>\n"
#    "        </Internal_Reference>", ""),
#        (
#    "        </Internal_Reference>\n"
#    "\n"
#    "        <Internal_Reference>",
#    "        </Internal_Reference>\n"
#    "        <Internal_Reference>"
    ]
    count = 0
    for old, new in replacements:
        occurrences = text.count(old)
        if occurrences:
            text = text.replace(old, new)
            count += occurrences
    return text, count


def main() -> None:
    """Entry point for the ISS label fixer.

    Parses CLI arguments, walks the directory tree, and applies text
    replacements in place to all files that match the provided glob pattern.

    Args:
        None. Arguments are read from sys.argv.

    Raises:
        SystemExit: If the root path does not exist.
    """
    p = argparse.ArgumentParser(
        description="Fix minor wording in Cassini ISS labels (in place)."
    )
    p.add_argument("root", help="Directory to scan recursively.")
    p.add_argument(
        "pattern",
        help="Glob pattern for file names (e.g. '*.xml', '*_v*.lblx').",
    )
    args = p.parse_args()

    root = Path(args.root)
    if not root.exists():
        print(f"ERROR: {root} does not exist.", file=sys.stderr)
        raise SystemExit(1)

    total_files = 0
    total_changes = 0
    for path in root.rglob(args.pattern):
        if not path.is_file():
            continue
        try:
            txt = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            txt = path.read_text(errors="replace")

        new_txt, changes = apply_replacements_iss(txt)
        if changes:
            path.write_text(new_txt, encoding="utf-8")
            total_files += 1
            total_changes += changes
            print(
                f"[fixed] {path}  (+{changes} change{'s' if changes != 1 else ''})"
            )

    print(f"Done. Files modified: {total_files}, total replacements: {total_changes}")


if __name__ == "__main__":
    main()
