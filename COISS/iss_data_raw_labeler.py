################################################################################
# iss_data_raw_labeler.py
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

# These are known errors
TARGET_DICT['HYROKKIN'] = TARGET_DICT['HYRROKKIN']
TARGET_DICT['SKADI'   ] = TARGET_DICT['SKATHI'   ]
TARGET_DICT['THRYM'   ] = TARGET_DICT['THRYMR'   ]
TARGET_DICT['SUTTUNG' ] = TARGET_DICT['SUTTUNGR' ]
TARGET_DICT['METHON'  ] = TARGET_DICT['METHONE'  ]
TARGET_DICT['K07S4'   ] = TARGET_DICT['AEGAEON'  ]

TARGET_DICT['S12_2004'] = TARGET_DICT['S/2004 S 12']
TARGET_DICT['S13_2004'] = TARGET_DICT['S/2004 S 13']
TARGET_DICT['S14_2004'] = TARGET_DICT['S/2004 S 14']
TARGET_DICT['S18_2004'] = TARGET_DICT['S/2004 S 18']
TARGET_DICT['S8_2004' ] = TARGET_DICT['S/2004 S 8' ]

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

def iss_target_info(target_name, target_desc, observation_id):

    name = target_name.upper()
    desc = target_desc.upper()

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

WIDE_WAVELENGTHS = {
    'VIO'  :  420.,
    'BL1'  :  463.,
    'GRN'  :  568.,
    'CL1'  :  634.,
    'CL2'  :  634.,
    'RED'  :  647.,
    'HAL'  :  656.,
    'IRP0' :  705.,
    'IRP90':  705.,
    'MT2'  :  728.,
    'IR1'  :  740.,
    'CB2'  :  752.,
    'IR2'  :  852.,
    'MT3'  :  890.,
    'IR3'  :  917.,
    'CB3'  :  939.,
    'IR4'  : 1000.,
    'IR5'  : 1027.,
    ('IR1','IR2'): 826.,
    ('IR2','IR1'): 826.,
}

NARROW_WAVELENGTHS = {
    'UV1'   :  264.,
    'UV2'   :  306.,
    'UV3'   :  343.,
    'BL2'   :  441.,
    'BL1'   :  455.,
    'GRN'   :  569.,
    'CB1b'  :  603.,
    'CB1B'  :  603.,
    'CB1'   :  619.,
    'MT1'   :  619.,
    'P0'    :  633.,
    'P120'  :  633.,
    'P60'   :  633.,
    'CB1a'  :  635.,
    'CB1A'  :  635.,
    'RED'   :  649.,
    'CL1'   :  651.,
    'CL2'   :  651.,
    'HAL'   :  656.,
    'MT2'   :  727.,
    'IRP0'  :  738.,
    'CB2'   :  750.,
    'IR1'   :  750.,
    'IR2'   :  861.,
    'MT3'   :  889.,
    'IR3'   :  928.,
    'CB3'   :  938.,
    'IR4'   : 1001.,

    ('UV2','UV3'): 318.,
    ('RED','GRN'): 601.,
    ('RED','IR1'): 702.,
    ('IR2','IR1'): 827.,
    ('IR2','IR3'): 902.,
    ('IR4','IR3'): 996.,

    ('UV3','UV2'): 318.,
    ('GRN','RED'): 601.,
    ('IR1','RED'): 702.,
    ('IR1','IR2'): 827.,
    ('IR3','IR2'): 902.,
    ('IR3','IR4'): 996.,
}

WAVELENGTHS = {
    'ISSNA': NARROW_WAVELENGTHS,
    'ISSWA': WIDE_WAVELENGTHS,
}

POLARIZERS = set(['IRP0', 'IRP90', 'P0', 'P60', 'P120'])

def iss_wavelength_range(filter1, filter2, instrument_id):
    """Return the wavelength range, one of Ultraviolet, Visible or Near
    Infrared."""

    def wavelength_nm(filter1, filter2, instrument_id):
        if filter1 == 'CL1':
            filter = filter2
        elif filter2 == 'CL2':
            filter = filter1
        elif filter1 in POLARIZERS:
            return filter2
        elif filter2 in POLARIZERS:
            return filter1
        else:
            filter = (filter1,filter2)

        try:
            return WAVELENGTHS[instrument_id][filter]
        except KeyError:
            pass

        wavelength1 = WAVELENGTHS[instrument_id][filter1]
        wavelength2 = WAVELENGTHS[instrument_id][filter2]

        # OK because it's just for wavelength_range
        return (wavelength1 + wavelength2) / 2.

    wavelength = wavelength_nm(filter1, filter2, instrument_id)

    if wavelength < 400:
        return 'Ultraviolet'

    if wavelength <= 651:   # 651, not 650, so CL1 and CL2 are Visible not NIR
        return 'Visible'

    return 'Near Infrared'

################################################################################

PURPOSES = {
    'SCIENCE'    : 'Science',
    'SUPPORT'    : 'Observation Geometry',
    'CALIBRATION': 'Calibration',
    'OPNAV'      : 'Navigation',
    'ENGINEERING': 'Engineering',
}

def iss_purpose(image_observation_type, observation_id):
    """Image purpose, one of Calibration, Checkout, Engineering, Navigation,
    Observation Geometry, or Science."""

    if image_observation_type in PURPOSES:
        return PURPOSES[image_observation_type]

    if 'MASURSKY' in observation_id:
        return 'Science'

    if observation_id == "ISS_C22JU_17ATM1X1000_PRIME":
        return 'Science'    # I don't know why this one was "UNK"

    return 'Checkout'       # Seems to be right for everything that's left

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

    lookup['wavelength_range'] = iss_wavelength_range(label['FILTER_NAME'][0],
                                                      label['FILTER_NAME'][1],
                                                      label['INSTRUMENT_ID'])

    lookup['purposes'] = [iss_purpose(obstype, label['OBSERVATION_ID'])
                          for obstype in label['IMAGE_OBSERVATION_TYPE']]

    # Special care for target identifications
    target_info = iss_target_info(label['TARGET_NAME'],
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
