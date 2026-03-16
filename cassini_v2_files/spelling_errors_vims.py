#!/usr/bin/env python3
"""
fix_vims_labels.py

Recursively scan a directory for Cassini VIMS labels and fix known typos and
minor language issues in place.

This script targets labels for the Cassini Visual and Infrared Mapping
Spectrometer (VIMS), covering both `cassini_vims_cruise` and
`cassini_vims_saturn` collections. It opens each matching file, applies
targeted text replacements, and writes the updated contents back to the same
path.

Usage:
    python fix_vims_labels.py /path/to/root "*.xml"

Example:
    # Fix all XML labels under a Saturn bundle directory
    python fix_vims_labels.py /data/pds/cassini_vims_saturn "*.xml"

Notes:
    - Files are read and written as UTF-8. If decoding fails, the file is
      read with `errors="replace"` to avoid crashes and still proceed.
    - Only plain text replacements are performed; no XML parsing is used.
    - Replacements reflect vetted issues observed across VIMS labels.

"""

from __future__ import annotations

import argparse
import re
from pathlib import Path
import sys


def apply_replacements_vims(text: str) -> tuple[str, int]:
    """Apply VIMS-specific typo and style fixes to the given text.

    The function performs a set of safe, conservative replacements aimed at
    correcting known issues in VIMS labels.

    Replacements performed:
        - "lastest" -> "latest"
        - "et. al." -> "et al."
        - "Includes" (mid-sentence) -> "includes"
        - "half-way" -> "halfway"
        - "Reference_Area" -> "Reference_List"
        - "; See" -> "; see"
        - "Near Infrared" -> "Near-Infrared"
        - "cummulative" -> "cumulative"
        - "The content of this data file" -> "The contents of this data file"
          (also fixes lowercase/title-case variants)

    Args:
        text: The file contents to process.

    Returns:
        A tuple of:
            - The modified text.
            - The total number of replacements performed.
    """
    count = 0

    # Simple, case-sensitive swaps
    simple_swaps = [
        ("lastest", "latest"),
        ("half-way", "halfway"),
        ("Reference_Area", "Reference_List"),
        ("; See", "; see"),
        ("cummulative", "cumulative"),
        ("The content of this data file", "The contents of this data file"),
        ("the content of this data file", "the contents of this data file"),
        ("The Content of this data file", "The contents of this data file"),
        ("catelog", "catalog"),
        ("25,2018", "25, 2018"),
        ("PDS4_CASSINI_1O00_1800", "PDS4_CASSINI_1O00_1810"),
        ("Test Image", "Test_Image"),
#        ("<comment>The ISS Data User's Guide</comment>", "<comment>The ISS Data User's Guide (PDS3). DOI: 10.17189/1504135</comment>"),
        ("<lid_reference>urn:nasa:pds:cassini_vims_saturn:document:v2.0_modifications</lid_reference>", "<lid_reference>urn:nasa:pds:cassini_vims_saturn:document:v2.0-modifications</lid_reference>"),
#        ("<name>Cassini Orbiter Visual and Infrared Mapping Spectrometer</name>", "<name>Visual and Infrared Mapping Spectrometer</name>"),
        ("<version_id>2.0</version_id>", "<version_id>1.1</version_id>"),
        ("<type>Sun</type>", "<type>Star</type>")
    ]
    for old, new in simple_swaps:
        occurrences = text.count(old)
        if occurrences:
            text = text.replace(old, new)
            count += occurrences

    # Regex: "et. al." -> "et al."
    text, n = re.subn(r"\bet\.\s+al\.", "et al.", text)
    count += n

    # Regex: lower "Includes" only when it's mid-sentence.
    # Heuristic: the immediate left context is not a sentence terminator.
    def lower_includes(match: re.Match) -> str:
        before = match.group(1)
        return before + "includes"

    text, n = re.subn(r"([^.!?]\s)Includes\b", lower_includes, text)
    count += n

    # Update existing dpsis Internal_Reference comment if it has the old text
    # Match the comment content within a dpsis Internal_Reference
    # Pattern handles multiline comments with varying whitespace
    old_comment_pattern = r"(<lid_reference>urn:nasa:pds:cassini_vims_saturn:document:dpsis</lid_reference>.*?<comment>\s*)(The VIMS Data Product Software Interface Specification \(SIS\)\.)(\s*</comment>)"
    new_comment_text = r"\1The VIMS Data Product Software Interface Specification (SIS); DOI: 10.17189/zmkk-j412\3"
    text, n = re.subn(old_comment_pattern, new_comment_text, text, flags=re.DOTALL)
    count += n

    # Add dpsis Internal_Reference if it doesn't already exist
    if "urn:nasa:pds:cassini_vims_saturn:document:dpsis" not in text:
        # Insert after the last Internal_Reference and before External_Reference
        # Pattern matches: closing tag of Internal_Reference, then External_Reference
        dpsis_reference = """        <Internal_Reference>
            <lid_reference>urn:nasa:pds:cassini_vims_saturn:document:dpsis</lid_reference>
            <reference_type>data_to_document</reference_type>
            <comment>
                The VIMS Data Product Software Interface Specification (SIS); DOI: 10.17189/zmkk-j412
            </comment>
        </Internal_Reference>"""
        # Match closing Internal_Reference tag (with any whitespace) followed by External_Reference
        pattern = r"(        </Internal_Reference>)(\s+)(        <External_Reference>)"
        replacement = r"\1\n" + dpsis_reference + r"\n\3"
        text, n = re.subn(pattern, replacement, text)
        count += n

    return text, count


def main() -> None:
    """Entry point for the VIMS label fixer.

    Parses CLI arguments, walks the directory tree, and applies text
    replacements in place to all files that match the provided glob pattern.

    Args:
        None. Arguments are read from sys.argv.

    Raises:
        SystemExit: If the root path does not exist.
    """
    p = argparse.ArgumentParser(
        description="Fix typos and small language issues in Cassini VIMS labels (in place)."
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

        new_txt, changes = apply_replacements_vims(txt)
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
