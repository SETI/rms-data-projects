################################################################################
# label_support.py - Tools for generating metadata labels.
################################################################################
import time
import pdsparser

from pathlib                import Path
from filecache              import FCPath
from pdstemplate            import PdsTemplate
from pdstemplate.pds3table  import pds3_table_preprocessor

import metadata as meta

#===============================================================================
def _create_for_inventory(label_path, template_path, 
                          volume_id, creation_time, preserve_time):
    """Creates a label for a given geometry table.

    Args:
        label_path (Path): Path to the output label.
        template_path (Path): Path to the label template.
        volume_id (str): Volume ID.
        creation_time (xxx, optional): Creation time to use instead of the current time.
        preserve_time (bool, optional):
            If True, the creation time is copied from any existing
            label before it is overwrittten.
        
    Returns:
        None.
    """
    label_path = FCPath(label_path).retrieve()
    template_path = FCPath(template_path).retrieve()

    # Determine the creation time
    if preserve_time:
        local_path = label_path.retrieve()
        label = pdsparser.PdsLabel.from_file(local_path)
        creation_time = label.__getitem__('PRODUCT_CREATION_TIME')
    elif creation_time is None:
        creation_time = '%04d-%02d-%02dT%02d:00:00' % time.gmtime()[:4]

    # Generate the label
    fields = {'VOLUME_ID'           : volume_id,
              'PUBLICATION_DATE'    : creation_time[:10]}
    T = PdsTemplate(template_path, crlf=True, 
                    kwargs={'formats':True, 'numbers':True, 'validate':False})
    T.write(fields, label_path=label_path, mode='repair')

#===============================================================================
def _create_for_geometry(label_path, template_path, table_type):
    """Creates a label for a given geometry table.

    Args:
        label_path (Path): Path to the output label.
        template_path (Path): Path to the label template.
        table_type (str, optional): BODY, RING, SKY.

    Returns:
        None.
    """
    label_path = FCPath(label_path).retrieve()
    template_path = FCPath(template_path).retrieve()

    T = PdsTemplate(template_path, crlf=True, 
                    preprocess=pds3_table_preprocessor, 
                    kwargs={'formats':True, 'numbers':True, 'validate':False})
    T.write({'TABLE_TYPE': table_type}, label_path=label_path, mode='repair',)

#===============================================================================
def _create_for_index(label_path, template_path):
    """Creates a label for a given geometry table.

    Args:
        label_path (Path): Path to the output label.
        template_path (Path): Path to the label template.

    Returns:
        None.
    """
    label_path = FCPath(label_path).retrieve()
    template_path = FCPath(template_path).retrieve()

    T = PdsTemplate(template_path, crlf=True, 
                    preprocess=pds3_table_preprocessor, 
                    kwargs={'formats':False, 'numbers':True, 'validate':False})
    T.write({}, label_path=label_path, mode='repair',)

#===============================================================================
def _create_for_cumulative(label_path, template_path, table_type):
    """Creates a label for a given geometry table.

    Args:
        label_path (Path): Path to the output label.
        template_path (Path): Path to the label template.
        table_type (str, optional): BODY, RING, SKY.

    Returns:
        None.
    """
    label_path = FCPath(label_path).retrieve()
    template_path = FCPath(template_path).retrieve()

    T = PdsTemplate(template_path, crlf=True, 
                    preprocess=pds3_table_preprocessor, 
                    kwargs={'formats':True, 'numbers':True, 'validate':False})
    T.write({'TABLE_TYPE': table_type, 
             'INDEX_TYPE':'CUMULATIVE'}, label_path=label_path, mode='repair',)

#===============================================================================
def create(filepath, 
           system=None, creation_time=None, preserve_time=False, table_type=''):
    """Creates a label for a given geometry table.

    Args:
        filepath (str|Path|FCPath): Path to the local or remote geometry table.
        system (str): Name of system, for rings and moons.
        creation_time (xxx, optional): Creation time to use instead of the current time.
        preserve_time (bool, optional):
            If True, the creation time is copied from any existing
            label before it is overwrittten.
        table_type (str, optional): BODY, RING, SKY, SUPPLEMENTAL.

    Returns:
        None.
    """
    filepath = FCPath(filepath)
    if not filepath.exists():
        return

    table_type = table_type.upper()

    # Get the label path
    if not system:
        system = '' 
    filename = filepath.name
    dir = filepath.parent
    body = filepath.stem
    label_path = dir / (body + '.lbl')

    # Get the volume id
    underscore = filename.index('_')
    volume_id = filename[:underscore + 5]
    
    # Create an index label using the local template path
    if ('index' in body):
        template_name = meta.get_template_name(filename, volume_id)
        template_path = Path('./templates/').resolve() / (template_name + '.lbl')
        _create_for_index(label_path, template_path)
        return

    # Use the global template path for all other labels
    offset = 0 if not system else len(system) + 1
    template_path = Path(meta.GLOBAL_TEMPLATE_PATH) / Path('%s.lbl' % body[underscore+6+offset:])

    # Create an inventory label
    if ('inventory' in body):
        _create_for_inventory(label_path, template_path, 
                              volume_id, creation_time, preserve_time)
        return
        
    # Create a cumulative label
    if '999' in volume_id:      ## is this a safe assumption?
        _create_for_cumulative(label_path, template_path, table_type)
        return

    # Create a geometry label
    _create_for_geometry(label_path, template_path, table_type)
    
################################################################################
