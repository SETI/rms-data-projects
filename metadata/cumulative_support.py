################################################################################
# cumulative_support.py - Code for cumulative index files
################################################################################
import config
import fnmatch

import metadata as meta
import metadata.label_support as lab

from pathlib import Path

#===============================================================================
def _cat_rows(volume_tree, cumulative_dir, volume_glob, table_type,
              exclude=None, volume=None):
    """Creates the cumulative files for a collection of volumes.

    Args:
        volume_tree (Path): Root of the tree containing the volumes.
        exclude (list, optional): List of volumes to exclude.
        volume (str, optional): If given, only this volume is processed.
    """
    logger = meta.get_logger()

    # Walk the input tree, adding lines for each found volume
    logger.info('Building Cumulative %s table' % table_type)
    content = []
    for root, dirs, files in volume_tree.walk(top_down=True):
        # __skip directory will not be scanned, so it's safe for test results
        if '__skip' in root.as_posix():
            continue

        # Ignore cumulative directory
        if cumulative_dir.name in root.as_posix():
            continue

        # Sort directories 
        dirs.sort()
        root = Path(root)

        # Determine notional set and volume
        parts = root.parts
        set = parts[-2]
        vol = parts[-1]

        # Test whether this root is a volume
        if fnmatch.filter([vol], volume_glob):
            if not volume or vol == volume:
                if vol != cumulative_dir.name:
                    volume_id = config.get_volume_id(root)
                    cumulative_id = config.get_volume_id(cumulative_dir)

                    # Check existence of table
                    try:
                        table_file = list(root.glob('*%s.tab' % table_type.lower()))[0]
                    except IndexError:
                        continue

                    # Copy table file to cumulative index
                    cumulative_file = Path(table_file.as_posix().replace(volume_id, cumulative_id))
                    lines = meta.read_txt_file(table_file)
                    content += lines

    # Write table and label
    if content:
        logger.info('Writing cumulative file %s.' % cumulative_file)
        meta.write_txt_file(cumulative_file, content)

        logger.info('Writing cumulative label.')
        lab.create(cumulative_file, table_type=table_type)

#===============================================================================
def get_args(host=None, selection=None, exclude=None):

    # Get parser with common args
    parser = meta.get_common_args(host=host)

    # Add parser for index args
    gr = parser.add_argument_group('Cumulative Arguments')
    gr.add_argument('--exclude', '-e', nargs='*', type=str, metavar='exclude',
                    default=exclude, 
                    help='''List of volumes to exclude.''')

    # Return parser
    return parser

#===============================================================================
def create_cumulative_indexes(volume_tree, cumulative_dir,
                              exclude=None, volume=None):
    """Creates the cumulative files for a collection of volumes.

    Args:
        volume_tree (Path): Root of the tree containing the volumes.
        cumulative_dir (Path): Directory in which to place the cumulative files.
        exclude (list, optional): List of volumes to exclude.
        glob (str, optional): Glob pattern for index files.
        volume (str, optional): If given, only this volume is processed.
    """
    volume_tree = Path(volume_tree)
    cumulative_dir = Path(cumulative_dir)

    logger = meta.get_logger()
    logger.info('New cumulative indexes for %s.' % volume_tree.name)

    # Build volume glob
    volume_glob = meta.get_volume_glob(volume_tree.name)

    # Build the cumulative tables
    _cat_rows(volume_tree, cumulative_dir, volume_glob, 'SKY_SUMMARY',
              exclude=exclude, volume=volume)
    _cat_rows(volume_tree, cumulative_dir, volume_glob, 'BODY_SUMMARY',
              exclude=exclude, volume=volume)
    _cat_rows(volume_tree, cumulative_dir, volume_glob, 'RING_SUMMARY',
              exclude=exclude, volume=volume)
    _cat_rows(volume_tree, cumulative_dir, volume_glob, 'SUPPLEMENTAL_INDEX',
              exclude=exclude, volume=volume)

