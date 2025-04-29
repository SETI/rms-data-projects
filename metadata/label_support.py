################################################################################
# label_support.py - Tools for generating metadata labels.
################################################################################
import time
import pdsparser

from filecache              import FCPath
from pdstemplate            import PdsTemplate
from pdstemplate.pds3table  import pds3_table_preprocessor

import metadata as meta

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
        table_type (str, optional): BODY, RING, SKY, SUPPLEMENTAL_INDEX, INVENTORY.

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
    
    # Default template path
    offset = 0 if not system else len(system) + 1
    template_path = FCPath(meta.GLOBAL_TEMPLATE_PATH) / FCPath('%s.lbl' % body[underscore+6+offset:])
    if 'index' in body:
        template_name = meta.get_template_name(filename, volume_id)
        template_path = FCPath('./templates/').resolve() / (template_name + '.lbl')

    # Default preprocessor
    preprocess = pds3_table_preprocessor
    if 'inventory' in body:
        preprocess = None

    # Default template dictionary
    fields = {'VOLUME_ID'           : volume_id,
              'TABLE_TYPE'          : table_type}

    # Cumulative index
    if '999' in volume_id:
        fields['TABLE_TYPE'] = 'CUMULATIVE'

    # Generate label
    T = PdsTemplate(template_path, crlf=True, 
                    preprocess=preprocess, 
                    kwargs={'formats':True, 'numbers':True, 'validate':False})
    T.write(fields, label_path=label_path, mode='repair')
    
    return
    
################################################################################
