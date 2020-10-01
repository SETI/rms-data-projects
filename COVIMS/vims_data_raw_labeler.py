################################################################################
# vims_data_raw_labeler.py
#
# Create XML labels for the PDS4-reformatted Cassini ISS images.
#
# Syntax:
#   python iss_data_raw_labeler.py [--replace] path [path ...]
#
# A label will be created for each cube file ("*.qub") found in each given
# path, recursively. This can be any combination of directories and individual
# image files.
#
# Use "--replace" to replace pre-existing labels. Otherwise, labels will only be
# generated for images that currently lack labels.
################################################################################

import os,sys
import pdsparser
import traceback
from xmltemplate import XmlTemplate

from SOLAR_SYSTEM_TARGETS import SOLAR_SYSTEM_TARGETS
from rc19_id import rc19_id_from_filename

TEMPLATE = XmlTemplate('vims_data_raw_template.xml')

# Create a mapping from new basename to PDS3 filepath
from VERSIONS import VERSIONS

PDS3_FILEPATHS = {}

# Fill in filepaths; results are ambiguous for files with multiple versions
with open('PDS3_FILES.txt') as f:
    paths = f.readlines()

for path in paths:
    path = path.rstrip()
    sclk = path[48:58]
    line = path[-8:-4]
    if line[0] == '_':
        newname = sclk + line + '.qub'
    else:
        newname = sclk + '.qub'
    PDS3_FILEPATHS[newname] = (path, [])

# Update info for versioned files
for (newname, label_tag, data_tag, path) in VERSIONS:
    newname = newname + '.qub'
    (best_path, version_list) = PDS3_FILEPATHS[newname]
    if label_tag == '1.0':
        PDS3_FILEPATHS[newname] = (path, version_list)
    else:
        version_list.append((path, label_tag, data_tag))
        PDS3_FILEPATHS[newname] = (best_path, version_list)

################################################################################

# Create a dictionary keyed by the body name in upper case
# TARGET_DICT[NAME] = (name, lid_name, alt_names, target_type, primary, lid)

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
    'ARCTURUS' : ('Arcturus'       , ['Alpha Bootes', 'Alpha Boo'],  'alf_boo'),
    'FOMALHAUT': ('Fomalhaut'      , ['Alpha Piscis Austrini', 'Alpha PsA'],
                                                                     'alf_psa'),
    'SPICA'    : ('Spica'          , ['Alpha Virginis', 'Alpha Vir'],'alf_vir'),
    'CALSTAR3' : ('HR 996'         , ['kap1 Cet'],                   'kap01_cet'),
    '2CEN'     : ('2 Centauri'     , ['2 Cen', 'g Cen'],             'g_cen'  ),
    '30HER'    : ('30 Herculis'    , ['30 Her', 'g Her'],            'g_her' ),
    '30PSC'    : ('30 Piscium'     , ['30 Psc'],                     '30_psc' ),
    '56LEO'    : ('56 Leonis'      , ['56 Leo'],                     '56_leo' ),
    'ALPAUR'   : ('Capella'        , ['Alpha Aurigae', 'Alpha Aur'], 'alf_aur'),
    'ALPCEN'   : ('Alpha Centauri' , ['Alpha Cen'],                  'alf_cen'),
    'ALPCET'   : ('Alpha Ceti'     , ['Alpha Cet'],                  'alf_cet'),
    'ALPCMA'   : ('Sirius'         , ['Alpha Canis Majoris',
                                      'Alpha CMa'],                  'alf_cma'),
    'ALPCMI'   : ('Procyon'        , ['Alpha Canis Minoris',
                                      'Alpha CMi'],                  'alf_cmi'),
    'ALPHER'   : ('Alpha Herculis' , ['Alpha Her'],                  'alf_her'),
    'ALPHYA'   : ('Alpha Hydrae'   , ['Alpha Hya'],                  'alf_hya'),
    'ALPORI'   : ('Betelgeuse'     , ['Alpha Orionis', 'Alpha Ori'], 'alf_ori'),
    'ALPSCO'   : ('Antares'        , ['Alpha Scorpii', 'Alpha Sco'], 'alf_sco'),
    'ALPTAU'   : ('Aldebaran'      , ['Alpha Tauri', 'Alpha Tau'],   'alf_tau'),
    'ALPTRA'   : ('Alpha Trianguli Australis'
                                   , ['Alpha TrA'],                  'alf_tra'),
    'BETAND'   : ('Beta Andromedae', ['Beta And'],                   'bet_and'),
    'BETGRU'   : ('Beta Gruis'     , ['Beta Gru'],                   'bet_gru'),
    'BETORI'   : ('Beta Orionis'   , ['Beta Ori'],                   'bet_ori'),
    'BETPEG'   : ('Beta Pegasi'    , ['Beta Peg'],                   'bet_peg'),
    'BETUMI'   : ('Beta Ursae Minoris'
                                   , ['Beta UMi'],                   'bet_umi'),
    'CHIAQR'   : ('Chi Aquarii'    , ['Chi Aqr'],                    'chi_aqr'),
    'CHICYG'   : ('Chi Cygni'      , ['Chi Cyg'],                    'chi_cyg'),
    'CWLEO'    : ('CW Leonis'      , ['CW Leo', 'IRC +10216' ],      'irc_+10216'),
    'DELOPH'   : ('Delta Ophiuchi' , ['Delta Oph'],                  'del_oph'),
    'DELVIR'   : ('Delta Virginis' , ['Delta Vir'],                  'del_vir'),
    'EPSMUS'   : ('Epsilon Muscae' , ['Epsilon Mus'],                'eps_mus'),
    'EPSORI'   : ('Epsilon Orionis', ['Epsilon Ori'],                'eps_ori'),
    'ETASGR'   : ('Eta Sagittarii' , ['Eta Sgr'],                    'eta_sgr'),
    'GAMAND'   : ('Gamma Andromedae',['Gamma And'],                  'gam_and'),
    'GAMCRU'   : ('Gamma Crucis'   , ['Gamma Cru'],                  'gam_cru'),
    'GAMERI'   : ('Gamma Eridani'  , ['Gamma Eri'],                  'gam_eri'),
    'LAMAQR'   : ('Lambda Aquarii' , ['Lambda Aqr'],                 'lam_aqr'),
    'LAMVEL'   : ('Lambda Velorum' , ['Lambda Vel'],                 'lam_vel'),
    'MUCEP'    : ('Mu Cephei'      , ['Mu Cep'],                     'mu._cep' ),
    'MUGEM'    : ('Mu Geminorum'   , ['Mu Gem'],                     'mu._gem' ),
    'NUVIR'    : ('Nu Virginis'    , ['Nu Vir'],                     'nu._vir' ),
    'OMEVIR'   : ('Omega Virginis' , ['Omega Vir'],                  'ome_vir'),
    'OMICET'   : ('Omicron Ceti'   , ['Omicron Cet'],                'omi_cet'),
    'PI1GRU'   : ('Pi1 Gruis'      , ['Pi1 Gru'],                    'pi.01_gru'),
    'RAQR'     : ('R Aquarii'      , ['R Aqr'],                      'r_aqr'  ),
    'RCAS'     : ('R Cassiopeiae'  , ['R Cas'],                      'r_cas'  ),
    'RHOPER'   : ('Rho Persei'     , ['Rho Per'],                    'rho_per'),
    'RHYA'     : ('R Hydrae'       , ['R Hya'],                      'r_hya'  ),
    'RLEO'     : ('R Leo'          , ['R Leo'],                      'r_leo'  ),
    'RLYR'     : ('R Lyrae'        , ['R Lyr', '13 Lyr'],            '13_lyr' ),
    'RWLMI'    : ('RW Leonis Minoris'
                                   , ['RW LMi'],                     'rw_lmi' ),
    'RXLEP'    : ('RX Leporis'     , ['RX Lep'],                     'rx_lep' ),
    'SLEP'     : ('S Leporis'      , ['S Lep'],                      's_lep'  ),
    'TCEP'     : ('T Cephei'       , ['T Cep'],                      't_cep'  ),
    'TXCAM'    : ('TX Camelopardalis'
                                   , ['TX Cam'],                     'tx_cam' ),
    'VHYA'     : ('V Hydrae'       , ['V Hya'],                      'v_hya'  ),
    'VXSGR'    : ('VX Sagittarii'  , ['VX Sgr'],                     'vx_sgr' ),
    'WAQL'     : ('W Aquilae'      , ['W Aql'],                      'w_aql'  ),
    'WHYA'     : ('W Hydrae'       , ['W Hya'],                      'w_hya'  ),
    'XOPH'     : ('X Ophiuchi'     , ['X Oph'],                      'x_oph'  ),
    'ZETORI'   : ('Zeta Orionis'   , ['Zeta Ori'],                   'zet_ori'),
}

# Star aliases
STAR_ABBREVS['ALPBOO' ] = STAR_ABBREVS['ARCTURUS']
STAR_ABBREVS['ALFBOO' ] = STAR_ABBREVS['ARCTURUS']
STAR_ABBREVS['ALFORI' ] = STAR_ABBREVS['ALPORI'  ]
STAR_ABBREVS['ALFSCO' ] = STAR_ABBREVS['ALPSCO'  ]
STAR_ABBREVS['ALCEN'  ] = STAR_ABBREVS['ALPCEN'  ]
STAR_ABBREVS['CWSTAR' ] = STAR_ABBREVS['CWLEO'   ]
STAR_ABBREVS['ZETAORI'] = STAR_ABBREVS['ZETORI'  ]

# Add stars to the target list
for (name, alts, lid) in STAR_ABBREVS.values():
    TARGET_DICT[name.upper()] = (name, alts, 'Star', 'N/A',
                                 'urn:nasa:pds:context:target:star.%s' % lid)

def vims_target_info(target_name, target_desc, observation_id,
                     sequence_title, filename):

    name = target_name.upper()
    desc = target_desc.upper()
    obs_id = observation_id.upper()
    sequence_title = sequence_title.upper()

    # Known error
    if desc == 'BETPEG': desc = ''

    # Read the target name out of the OBSERVATION_ID
    abbrev = ''
    obsname = ''
    if len(obs_id) > 3 and obs_id[:3] not in ('ICO','BG_','19V'):
        try:
            parts = obs_id.split('_')
            abbrev = parts[1][-2:]
            obsname = CIMS_TARGET_ABBREVIATIONS[abbrev]
        except (KeyError, IndexError, ValueError):
            pass

    target_keys = set()

    # This might be Jupiter's rings, not Saturn's rings
    if name == 'JUPITER' and obsname == 'SATURN RINGS':
        obsname = 'JUPITER RINGS'
        name = ''

    # If target_name is 'SATURN', but it's really a ring image, omit Saturn
    if name == 'SATURN' and ('RING' in desc or obsname == 'SATURN RINGS'):
        name = ''

    # Add three options to the set of names
    for key in (name, desc, obsname, sequence_title):
        if key in TARGET_DICT:
            rec = TARGET_DICT[key]
            target_keys.add(rec[0])

    # Ring targeting is sometimes encoded in TARGET_DESC
    if 'RING' in desc:
        target_keys.add('Saturn Rings')

    # Star IDs are sometimes encoded in the OBSERVATION_ID
    for (key,value) in STAR_ABBREVS.items():
        if key in obs_id or key in sequence_title:
            target_keys.add(value[0])

    # If our set is not empty, we're done:
    if len(target_keys):
        keys = list(target_keys)
        keys.sort()
        return [TARGET_DICT[k.upper()] for k in keys]

    if 'MASURSKY' in obs_id:
        return [TARGET_DICT['MASURSKY']]

    # Growing increasingly desperate...
    if 'SCAT' in obs_id or 'STRAYL' in obs_id or 'SCATL' in obs_id:
        return [('Scat Light', [], 'Calibration Field', 'N/A',
                 'urn:nasa:pds:context:target:calibration_field.scat_light')]

    if 'DARK SKY' in (name, desc):
        return [('Dark Sky', [], 'Calibration Field', 'N/A',
                 'urn:nasa:pds:context:target:calibration_field.dark_sky')]

    if 'SKY' in (name, desc) and 'SK_' in obs_id:
        return [('Sky', [], 'Calibration Field', 'N/A',
                 'urn:nasa:pds:context:target:calibration_field.sky')]

    if 'GEOMCAL' in obs_id or 'CALIB' in desc or 'CALIB' in obs_id:
        return [('Sky', [], 'Calibration Field', 'N/A',
                 'urn:nasa:pds:context:target:calibration_field.sky')]

    if 'PLEIADES' in obs_id:
        return [('Pleiades', ['Cl Melotte 22'], 'Star Cluster', 'N/A',
                 'urn:nasa:pds:context:target:star_cluster.cl_melotte_22')]

    if name == 'DUST':
        return [('Dust', [], 'Dust', 'N/A',
                 'urn:nasa:pds:context:target:dust.dust')]

    if 'TEST' in obs_id or 'TEST' in sequence_title or 'TRIGGER' in obs_id:
        return [('Test Image', [], 'Calibrator', 'N/A',
                 'urn:nasa:pds:context:target:calibrator.test_image')]

    if 'TRANSIT' in obs_id or 'STARCAL' in obs_id or 'STAROBS' in obs_id:
        print 'unknown star: %s %s %s %s' % (target_name, target_desc,
                                             observation_id, filename)
        return [('Star', [], 'Calibration Field', 'N/A',
                 'urn:nasa:pds:context:target:calibration_field.star')]

    print 'unknown target: %s %s %s %s' % (target_name, target_desc,
                                           observation_id, filename)

    return [('Unknown', [], 'Calibrator', 'N/A',
             'urn:nasa:pds:context:target:calibrator.unk')]

################################################################################

PURPOSES = {
    'SCIENCE'    : 'Science',
    'CALIBRATION': 'Calibration',
    'ENGINEERING': 'Engineering',
}

def vims_purpose(image_observation_type):
    """Image purpose, one of Calibration, Engineering, or Science."""

    if isinstance(image_observation_type, list):
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

    # Read the PDS3 label and the ISIS2 header, fixing known syntax errors
    with open(pds3_label) as f:
        label_text = f.read()

    # Add missing quotes around N/A in many labels
    label_text = label_text.replace('" N/A"', ' "N/A"')
    label_text = label_text.replace(' N/A', ' "N/A"')
    label_text = label_text.replace('(N/A', '("N/A"')
    label_text = label_text.replace(',N/A', ',"N/A"')

    # Handle multi-line comments
    recs = label_text.split('\n')
    changed = False
    for k,rec in enumerate(recs):
        if '/*' in rec and '*/' not in rec:
            recs[k] = rec[:-2] + '*/' + rec[-2:]
            changed = True
        if '*/' in rec and '/*' not in rec:
            recs[k] = '/*' + rec
            changed = True

    if changed:
        label_text = '\n'.join(recs)

    label_text = label_text.replace('\r','') # pyparsing is not set up for <CR>

    label = pdsparser.PdsLabel.from_string(label_text).as_dict()

    # Handle cases where a single string appears in place of a pair
    if isinstance(label['BACKGROUND_SAMPLING_MODE_ID'], str):
        print 'single value for BACKGROUND_SAMPLING_MODE_ID:', label['BACKGROUND_SAMPLING_MODE_ID']
        label['BACKGROUND_SAMPLING_MODE_ID'] = (label['BACKGROUND_SAMPLING_MODE_ID'],
                                                'Information not provided')

    # Read ISIS2 header
    isis_header = pdsparser.PdsLabel.from_file(datafile)
    header = isis_header.as_dict()

    # Define the lookup dictionary, with the PDS3 label taking precedence
    lookup = header.copy()
    lookup.update(label)
    lookup.update(label['SPECTRAL_QUBE'])

    # Define all the derived quantities
    lookup['datafile'] = datafile
    lookup['purposes'] = vims_purpose(label['IMAGE_OBSERVATION_TYPE'])

    history_rec0 = header['^HISTORY'][0]
    history_recs = header['^QUBE'][0] - header['^HISTORY'][0]
    lookup['history_rec0'] = history_rec0
    lookup['history_recs'] = history_recs

    lookup['qube_rec0'] = header['^QUBE'][0]
    lookup['qube_recs'] = header['^SIDEPLANE'][0] - header['^QUBE'][0]

    if '^PADDING' not in header:
        header['^PADDING'] = (header['FILE_RECORDS'] + 1, 'RECORDS')

    if '^BACKPLANE' not in header:
        header['^BACKPLANE'] = (header['^PADDING'][0], 'RECORDS')
        header['^CORNER'] = header['^BACKPLANE']

    lookup['sideplane_rec0'] = header['^SIDEPLANE'][0]
    lookup['sideplane_recs'] = header['^BACKPLANE'][0] - header['^SIDEPLANE'][0]

    lookup['backplane_rec0'] = header['^BACKPLANE'][0]
    lookup['backplane_recs'] = header['^CORNER'][0] - header['^BACKPLANE'][0]
    lookup['backplane_bytes'] = 4 * lookup['CORE_ITEMS'][0] * lookup['CORE_ITEMS'][2]

    lookup['corner_rec0'] = header['^CORNER'][0]
    lookup['corner_recs'] = header['^PADDING'][0] - header['^CORNER'][0]

    lookup['padding_rec0'] = header['^PADDING'][0]
    lookup['padding_recs'] = header['FILE_RECORDS'] + 1 - header['^PADDING'][0]

    if 'PADDING' in header:
        lookup['padding_bytes'] = header['PADDING']['CORE_ITEMS']
    else:
        lookup['padding_bytes'] = 0

    # Clean up the backplanes...
    if lookup['BAND_SUFFIX_NAME'] == 'N/A':
        lookup['BAND_SUFFIX_NAME'] = []

    for k,name in enumerate(lookup['BAND_SUFFIX_NAME']):
        lookup['BAND_SUFFIX_NAME'][k] = name.strip()

    # Special care for target identifications
    target_info = vims_target_info(label['TARGET_NAME'],
                                   label['TARGET_DESC'],
                                   label['OBSERVATION_ID'],
                                   label['SEQUENCE_TITLE'], datafile)

    target_names    = []
    target_alts     = []
    target_naif_ids = []
    target_types    = []
    target_lids     = []
    primary_names    = []
    primary_naif_ids = []
    primary_lids     = []

    for k in range(len(target_info)):
        target_names.append(target_info[k][0])
        target_alts.append(target_info[k][1])
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
    lookup['target_alts'     ] = target_alts
    lookup['target_naif_ids' ] = target_naif_ids
    lookup['target_types'    ] = target_types
    lookup['target_lids'     ] = target_lids
    lookup['primary_names'   ] = primary_names
    lookup['primary_naif_ids'] = primary_naif_ids
    lookup['primary_lids'    ] = primary_lids

    pds3_filename = label['^QUBE'][0]
    if '_' in pds3_filename:
        pre_pds4_version_number = pds3_filename.split('_')[1].split('.')[0]
    else:           # handle missing pre-PDS4 version in at least one label
        pre_pds4_version_number = 1
    lookup['pre_pds4_version_number'] = pre_pds4_version_number

    # Look at the history section of the ISIS2 header for any comments
    with open(datafile, 'rb') as f:
        f.seek((history_rec0 - 1) * 512)
        buffer = f.read(history_recs * 512)

#     buffer = buffer.replace('\r','')
    recs = buffer.split('\r\n')
    recs = [r for r in recs if not r.startswith('|')]   # remove comments if any
    buffer = '\n'.join(recs)

    history_header = pdsparser.PdsLabel.from_string(buffer)
    lookup['HISTORY'] = history_header.as_dict()['VIMS2PDS4']

    # Determine the RC19 ID for the wavelength bin mapping
    lookup['RC19_ID'] = rc19_id_from_filename(datafile)

    # PDS3 filepath
    (lookup['pds3_filepath'],
     lookup['versions']) = PDS3_FILEPATHS[os.path.basename(datafile)]

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

        pds3_label = pds4_file[:-3] + 'lbl'
        if os.path.exists(pds3_label):
            print pds3_label
        else:
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
          if arg.endswith('.qub'):
            label1(arg, replace)

        # Case 2: Label all the images in a directory tree, recursively
        elif os.path.isdir(arg):
          for root, dirs, files in os.walk(os.path.join(arg)):
            for name in files:
              if name.endswith('.qub'):

                filename = os.path.join(root, name)
                label1(filename, replace)

if __name__ == '__main__': main()

################################################################################
