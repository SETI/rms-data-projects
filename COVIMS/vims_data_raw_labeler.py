################################################################################
# vims_data_raw_labeler.py
#
# Create XML labels for the PDS4-reformatted Cassini ISS images.
#
# Syntax:
#   python iss_data_raw_labeler.py [--replace] path [path ...]
#
# A label will be created for each image file ("*.img") found in each given
# path, recursively. This can be any combination of directories and individual
# image files.
#
# Use "--replace" to replace pre-existing labels. Otherwise, labels will only be
# generated for images that currently lack labels.
################################################################################

import os,sys
import pdsparser
import vicar
import traceback
from xmltemplate import XmlTemplate

from SOLAR_SYSTEM_TARGETS import SOLAR_SYSTEM_TARGETS

TEMPLATE = XmlTemplate('iss_data_raw_template.xml')

################################################################################

# Create a dictionary keyed by the body name in upper case
# TARGET_DICT[NAME] = (name, alt_names, target_type, primary, lid)

TARGET_DICT = {rec[0].upper():rec for rec in SOLAR_SYSTEM_TARGETS}

# Every alt name translates to the name
for rec in TARGET_DICT.values():
    alt_names = rec[1]
    for alt_name in alt_names:
        TARGET_DICT[alt_name.upper()] = rec

# Local additions...
TARGET_DICT['MASURSKY'] = ('Masursky', ['2685 Masursky', 'NAIF ID 2002685'],
                'Asteroid', 'Sun',
                'urn:nasa:pds:context:target:asteroid.2685_masursky')

CIMS_TARGET_ABBREVIATIONS = {
    'AG': 'AEGAEON'   ,
    'AN': 'ANTHE'     ,
    'AT': 'ATLAS'     ,
    'CP': 'CALYPSO'   ,
    'DA': 'DAPHNIS'   ,
    'DI': 'DIONE'     ,
    'EN': 'ENCELADUS' ,
    'EP': 'EPIMETHEUS',
    'HE': 'HELENE'    ,
    'HY': 'HYPERION'  ,
    'IA': 'IAPETUS'   ,
    'JA': 'JANUS'     ,
    'ME': 'METHONE'   ,
    'MI': 'MIMAS'     ,
    'PA': 'PANDORA'   ,
    'PH': 'PHOEBE'    ,
    'PL': 'PALLENE'   ,
    'PM': 'PROMETHEUS',
    'PN': 'PAN'       ,
    'PO': 'POLYDEUCES',
    'RH': 'RHEA'      ,
    'SA': 'SATURN'    ,
    'TE': 'TETHYS'    ,
    'TI': 'TITAN'     ,
    'TL': 'TELESTO'   ,

    'RI': 'SATURN RINGS',
    'RA': 'SATURN RINGS',
    'RB': 'SATURN RINGS',
    'RC': 'SATURN RINGS',
    'RD': 'SATURN RINGS',
    'RE': 'SATURN RINGS',
    'RF': 'SATURN RINGS',
    'RG': 'SATURN RINGS',

    'JU': 'JUPITER'   ,
    'IO': 'IO'        ,
    'EU': 'EUROPA'    ,
    'GA': 'GANYMEDE'  ,
    'CA': 'CALLISTO'  ,
}

STAR_ABBREVS = {
    'CANOPUS'  : ('Canopus'    , ['alpha Car']),
    'FOMALHAUT': ('Fomalhaut'  , ['alpha PsA']),
    'SPICA'    : ('Spica'      , ['alpha Vir']),
    'VEGA'     : ('Vega'       , ['alpha Lyr']),
    '26TAU'    : ('26 Tau'     , []),
    '3CEN'     : ('3 Cen'      , []),
    'ALPARA'   : ('alpha Ara'  , []),
    'ALPAUR'   : ('alpha Aur'  , []),
    'ALPBOO'   : ('alpha Boo'  , ['Arcturus']),
    'ALPCEN'   : ('alpha Cen'  , []),
    'ALPCMA'   : ('alpha CMa'  , []),
    'ALPCMI'   : ('alpha CMi'  , []),
    'ALPCRU'   : ('alpha Cru'  , []),
    'ALPCRU'   : ('alpha Cru'  , []),
    'ALPERI'   : ('alpha Eri'  , []),
    'ALPLEO'   : ('alpha Leo'  , []),
    'ALPORI'   : ('alpha Ori'  , []),
    'ALPSCO'   : ('alpha Sco'  , []),
    'ALPSEX'   : ('alpha Sex'  , []),
    'ALPTAU'   : ('alpha Tau'  , []),
    'ALPVIR'   : ('alpha Vir'  , []),
    'ALPVIR'   : ('alpha Vir'  , []),
    'BETCEN'   : ('beta Cen'   , []),
    'BETCMA'   : ('beta CMa'   , []),
    'BETCRU'   : ('beta Cru'   , []),
    'BETLIB'   : ('beta Lib'   , []),
    'BETLUP'   : ('beta Lup'   , []),
    'BETORI'   : ('beta Ori'   , []),
    'BETORI'   : ('beta Ori'   , []),
    'BETPER'   : ('beta Per'   , []),
    'BETSGR'   : ('beta Sgr'   , []),
    'CHICEN'   : ('chi Cen'    , []),
    'DELAQR'   : ('delta Aqr'  , []),
    'DELCEN'   : ('delta Cen'  , []),
    'DELLUP'   : ('delta Lup'  , []),
    'DELPER'   : ('delta Per'  , []),
    'DELVIR'   : ('delta Vir'  , []),
    'EPSCAS'   : ('epsilon Cas', []),
    'EPSCEN'   : ('epsilon Cen', []),
    'EPSLUP'   : ('epsilon Lup', []),
    'EPSORI'   : ('epsilon Ori', []),
    'EPSPSA'   : ('epsilon PsA', []),
    'ETALUP'   : ('eta Lup'    , []),
    'ETAUMA'   : ('eta UMa'    , []),
    'GAMARA'   : ('gamma Ara'  , []),
    'GAMCAS'   : ('gamma Cas'  , []),
    'GAMCOL'   : ('gamma Col'  , []),
    'GAMCRU'   : ('gamma Cru'  , []),
    'GAMGRU'   : ('gamma Gru'  , []),
    'GAMLUP'   : ('gamma Lup'  , []),
    'GAMPEG'   : ('gamma Peg'  , []),
    'HD71334'  : ('HD 71334'   , []),
    'IOTCEN'   : ('iota Cen'   , []),
    'KAPCEN'   : ('kappa Cen'  , []),
    'KAPORI'   : ('kappa Ori'  , []),
    'LAMCET'   : ('lambda Cet' , []),
    'LAMSCO'   : ('lambda Sco' , []),
    'LMC303'   : ('LMC 303'    , []),
    'MUPSA'    : ('mu PsA'     , []),
    'NUCEN'    : ('nu Cen'     , []),
    'OMICET'   : ('omicron Cet', []),
    'PSICEN'   : ('psi Cen'    , []),
    'RCAS'     : ('R Cas'      , []),
    'RHYA'     : ('R Hya'      , []),
    'RLEO'     : ('R Leo'      , []),
    'THEARA'   : ('theta Ara'  , []),
    'THEHYA'   : ('theta Hya'  , []),
    'WHYA'     : ('W Hya'      , []),
    'ZETAORI'  : ('zeta Ori'   , []),
    'ZETCEN'   : ('zeta Cen'   , []),
    'ZETCMA'   : ('zeta CMa'   , []),
    'ZETOPH'   : ('zeta Oph'   , []),
    'ZETORI'   : ('zeta Ori'   , []),
    'ZETPER'   : ('zeta Per'   , []),
}

# Add stars to the target list
for (name, alts) in STAR_ABBREVS.values():
    TARGET_DICT[name.upper()] = (name, alts, 'Star', 'N/A',
        'urn:nasa:pds:context:target:star.%s' % name.lower().replace(' ','_'))

def vims_target_info(target_name, target_desc, observation_id):

    name = target_name.upper()
    desc = target_desc.upper()

    # Special cases
    if name == 'DUST' or desc == 'DUST_RAM_DIRECTION':
        return ('Dust', [], 'Dust', 'N/A',
                'urn:nasa:pds:context:target:dust.dust')

    if 'MASURSKY' in observation_id:
        return (
    # Read the target name out of the OBSERVATION_ID
    abbrev = ''
    try:
        parts = observation_id.split('_')
        abbrev = parts[1][-2:]
        obsname = CIMS_TARGET_ABBREVIATIONS[abbrev]
    except (KeyError, IndexError, ValueError):
        obsname = ''

    target_keys = set()

    # If target_name is 'SATURN', but it's really a ring image, omit Saturn
    if name == 'SATURN' and ('RING' in desc or obsname == 'SATURN RINGS'):
        name = ''

    # Add three options to the set of names
    for key in (name, desc, obsname):
        if key in TARGET_DICT:
            rec = TARGET_DICT[key]
            target_keys.add(rec[0])

    # Ring targeting is sometimes encoded in TARGET_DESC
    if 'RING' in desc:
        target_keys.add('Saturn Rings')

    # Star IDs are sometimes encoded in the OBSERVATION_ID
    for (key,value) in STAR_ABBREVS.items():
        if key in observation_id:
            target_keys.add(value[0])

    # If our set is not empty, we're done:
    if len(target_keys):
        keys = list(target_keys)
        keys.sort()
        return [TARGET_DICT[k.upper()] for k in keys]

    # Growing increasingly desperate...
    if 'DARK' in observation_id:
       return [('Dark', [], 'Calibration Field', 'N/A',
                'urn:nasa:pds:context:target:calibration_field.dark')]

    if 'SCAT' in observation_id:
       return [('Scat Light', [], 'Calibration Field', 'N/A',
                'urn:nasa:pds:context:target:calibration_field.scat_light')]

    if 'LAMP' in observation_id:
       return [('Cal Lamps', [], 'Calibrator', 'N/A',
                'urn:nasa:pds:context:target:calibrator.cal_lamps')]

    if 'FLAT' in observation_id:
       return [('Flat Field', [], 'Calibrator', 'N/A',
                'urn:nasa:pds:context:target:calibrator.flat_field')]

    if 'TEST' in observation_id:
       return [('Test Image', [], 'Calibrator', 'N/A',
                'urn:nasa:pds:context:target:calibrator.test_image')]

    if 'STAR' in (name, desc) or 'ST_' in observation_id:
       return [('Star', [], 'Star', 'N/A',
                'urn:nasa:pds:context:target:calibration_field.star')]

    if 'SKY' in (name, desc) or 'SK_' in observation_id:
       return [('Sky', [], 'Sky', 'N/A',
                'urn:nasa:pds:context:target:calibration_field.sky')]

    raise ValueError('unrecognized target: %s %s %s', target_name, target_desc,
                                                      observation_id)

################################################################################

PURPOSES = {
    'SCIENCE'    : 'Science',
    'CALIBRATION': 'Calibration',
    'ENGINEERING': 'Engineering',
}

def vims_purpose(image_observation_type):
    """Image purpose, one of Calibration, Engineering, or Science."""

    if isinstance(image_observation_type, tuple):
        return [s.capitalize() for s in image_observation_type]

    return [image_observation_type.capitalize()]

################################################################################

def write_pds4_label(datafile, pds3_label):

    def get_naif_id(alts):
        """Find the NAIF ID among the alt names for a target."""

        naif_id = 'N/A'
        for alt in alts:
            if alt.startswith('NAIF ID'):
                naif_id = int(alt[7:])

        return naif_id

    # Read the PDS3 label and the VICAR header, fixing known syntax errors
    label_text = open(pds3_label).read()
    label_text = label_text.replace('../../label/','')
    label_text = label_text.replace(' N/A\r\n', ' "N/A"\r\n')
    label_text = label_text.replace('\r','') # pyparsing is not set up for <CR>

    label = pdsparser.PdsLabel.from_string(label_text).as_dict()
    vicar_image = vicar.VicarImage.from_file(datafile)
    header = vicar_image.as_dict()

    # Define the lookup dictionary, with the PDS3 label taking precedence
    lookup = header.copy()
    lookup.update(label)

    # Define all the derived quantities
    lookup['datafile'] = datafile
    lookup['eol_lblsize'] = vicar_image.extension_lblsize

    lookup['purposes'] = vims_purpose

    # Special care for target identifications
    target_info = vims_target_info(label['TARGET_NAME'],
                                   label['TARGET_DESC'],
                                   label['OBSERVATION_ID'])

    target_names    = []
    target_naif_ids = []
    target_types    = []
    target_lids     = []
    primary_names    = []
    primary_naif_ids = []
    primary_lids     = []

    for k in range(len(target_info)):
        target_names.append(target_info[k][0])
        target_naif_ids.append(get_naif_id(target_info[k][1]))
        target_types.append(target_info[k][2])
        primary_names.append(target_info[k][3])
        target_lids.append(target_info[k][4])

        if primary_names[-1] == 'N/A':
            primary_naif_ids.append('N/A')
            primary_lids.append('N/A')
        else:
            primary_info = TARGET_DICT[primary_names[-1].upper()]
            primary_naif_ids.append(get_naif_id(primary_info[1]))
            primary_lids.append(primary_info[4])

    lookup['target_names'    ] = target_names
    lookup['target_naif_ids' ] = target_naif_ids
    lookup['target_types'    ] = target_types
    lookup['target_lids'     ] = target_lids 
    lookup['primary_names'   ] = primary_names
    lookup['primary_naif_ids'] = primary_naif_ids
    lookup['primary_lids'    ] = primary_lids

    pds3_filename = label['^IMAGE'][0]
    lookup['pre_pds_version_number'] = pds3_filename.split('_')[1][:-4]

    # Write the label
    labelfile = datafile[:-4] + '.xml'
    TEMPLATE.write(lookup, labelfile)

################################################################################
# Command line interface
################################################################################

def label1(pds4_file, replace=False):
    """Generate one label file, replacing a pre-existing one only if necessary.
    """

    try:
        pds4_file = os.path.abspath(pds4_file)
        if not replace and os.path.exists(pds4_file[:-4] + '.xml'):
            return

        parts = pds4_file.split('/data_raw/')
        pds3_label = parts[0] + '/pds3-labels/' + parts[1][:-3] + 'lbl'

        print('data_raw/' + parts[1])
        write_pds4_label(pds4_file, pds3_label)

    # A KeyboardInterrupt must stop the program
    except KeyboardInterrupt:
        sys.exit(1)

    # For any other exception, print an error message and keep going
    except Exception as e:
        print('*** error for: ', pds4_file)
        print(e)
        (etype, value, tb) = sys.exc_info()
        print(''.join(traceback.format_tb(tb)))

### MAIN PROGRAM

def main():

    # Get the command line args
    args = sys.argv[1:]

    # Set the replace flag if it's in the argument list
    if '--replace' in args:
        replace = True
        args.remove('--replace')
    else:
        replace = False

    # Step through the args
    for arg in args:

        # Case 1: Label a single image
        if os.path.isfile(arg):
          if arg.endswith('.img'):
            label1(arg, replace)

        # Case 2: Label all the images in a directory tree, recursively
        elif os.path.isdir(arg):
          for root, dirs, files in os.walk(os.path.join(arg)):
            for name in files:
              if name.endswith('.img'):

                filename = os.path.join(root, name)
                label1(filename, replace)

if __name__ == '__main__': main()

################################################################################
