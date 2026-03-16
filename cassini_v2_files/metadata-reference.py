import re
from pathlib import Path

# Pattern to delete Internal_Reference blocks (handles optional data_raw)
_BLOCK_PATTERN = re.compile(
    r"""
    [ \t]*\n?                        # optional indentation + newline before
    <Internal_Reference>
    (?:(?!</Internal_Reference>).)*?
    <lid_reference>\s*
    urn:nasa:pds:cassini_(iss|vims)_(cruise|saturn):
    (?:data_raw:)?(body-geometry|ring-geometry|body-inventory|index)
    \s*</lid_reference>
    (?:(?!</Internal_Reference>).)*?
    </Internal_Reference>
    [ \t]*\n?                        # optional trailing spaces/newline after
    """,
    re.DOTALL | re.VERBOSE,
)

def remove_references_preserve_format(xml_file: Path) -> int:
    """
    Remove matching <Internal_Reference> blocks from one file.
    Returns the number of blocks removed.
    """
    text = xml_file.read_text(encoding="utf-8")
    count = 0

    def _count_and_remove(_m):
        nonlocal count
        count += 1
        return ""

    new_text = _BLOCK_PATTERN.sub(_count_and_remove, text)

    if count > 0:
        xml_file.write_text(new_text, encoding="utf-8")
    return count

def process_directory(base_dir: str, pattern: str = "1*.lblx") -> None:
    """
    Recursively crawl base_dir, processing files matching the glob pattern.
    """
    base = Path(base_dir)
    total_removed = 0
    total_files = 0

    for file in base.rglob(pattern):
        removed = remove_references_preserve_format(file)
        if removed:
            print(f"{file}: removed {removed} block(s)")
            total_removed += removed
        total_files += 1

    print(f"\nProcessed {total_files} file(s). Removed {total_removed} block(s).")

if __name__ == "__main__":
    # Example: crawl current directory for files like 1*.lblx
    process_directory("/Volumes/Emilie-Data/pds4-holdings/bundles/cassini_iss_cruise/data_raw", "13544*/1*.xml")
