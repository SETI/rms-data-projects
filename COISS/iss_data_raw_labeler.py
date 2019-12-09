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
# TARGET_DICT[NAME] = (name, lid_name, alt_names, target_type, primary, lid)

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
    'CANOPUS'  : ('Canopus'        , ['Alpha Carinae', 'Alpha Car'], 'alf_car'),
    'FOMALHAUT': ('Fomalhaut'      , ['Alpha Piscis Austrini', 'Alpha PsA'],
                                                                     'alf_psa'),
    'SPICA'    : ('Spica'          , ['Alpha Virginis', 'Alpha Vir'],'alf_vir'),
    'VEGA'     : ('Vega'           , ['Alpha Lyrae', 'Alpha Lyr'],   'alf_lyr'),
    '26TAU'    : ('26 Tauri'       , ['26 Tau'],                     '26_tau' ),
    '3CEN'     : ('3 Centauri'     , ['3 Cen'],                      '3_cen'  ),
    '78TAU'    : ('78 Tauri'       , ['78 Tau'],                     '78_tau' ),
    'CALSTAR3' : ('HR 996'         , [],                             'hr_996' ),

    'ALPARA'   : ('Alpha Arae'     , ['Alpha Ara'],                  'alf_ara'),
    'ALPAUR'   : ('Capella'        , ['Alpha Aurigae', 'Alpha Aur'], 'alf_aur'),
    'ALPBOO'   : ('Arcturus'       , ['Alpha Bootes', 'Alpha Boo'],  'alf_boo'),
    'ALPCEN'   : ('Alpha Centauri' , ['Alpha Cen'],                  'alf_cen'),
    'ALPCMA'   : ('Sirius'         , ['Alpha Canis Majoris',
                                      'Alpha CMa'],                  'alf_cma'),
    'ALPCMI'   : ('Procyon'        , ['Alpha Canis Minoris',
                                      'Alpha CMi'],                  'alf_cmi'),
    'ALPCRU'   : ('Alpha Crucis'   , ['Alpha Cru'],                  'alf_cru'),
    'ALPERI'   : ('Alpha Eridani'  , ['Alpha Eri'],                  'alf_eri'),
    'ALPLEO'   : ('Regulus'        , ['Alpha Leo', 'Alpha Leo'],     'alf_leo'),
    'ALPORI'   : ('Betelgeuse'     , ['Alpha Orionis', 'Alpha Ori'], 'alf_ori'),
    'ALPSCO'   : ('Antares'        , ['Alpha Scorpii', 'Alpha Sco'], 'alf_sco'),
    'ALPSEX'   : ('Alpha Sextantis', ['Alpha Sex'],                  'alf_sex'),
    'ALPTAU'   : ('Aldebaran'      , ['Alpha Tauri', 'Alpha Tau'],   'alf_tau'),
    'ALPTRA'   : ('Alpha Trianguli Australis',
                                     ['Alpha TrA'],                  'alf_tra'),
    'BETCEN'   : ('Beta Centauri'  , ['Beta Cen'],                   'bet_cen'),
    'BETCMA'   : ('Beta Canis Majoris',
                                     ['Beta CMa'],                   'bet_cma'),
    'BETCRU'   : ('Beta Crucis'    , ['Beta Cru'],                   'bet_cru'),
    'BETGRU'   : ('Beta Gruis'     , ['Beta Gru'],                   'bet_gru'),
    'BETLIB'   : ('Beta Librae'    , ['Beta Lib'],                   'bet_lib'),
    'BETLUP'   : ('Beta Lupi'      , ['Beta Lup'],                   'bet_lup'),
    'BETORI'   : ('Beta Orionis'   , ['Beta Ori'],                   'bet_ori'),
#     'BETPER'   : ('Algol'          , ['Beta Perei', 'Beta Per'],     'bet_per'),
    'BETPER'   : ('Algol'          , ['Beta Persei', 'Beta Per'],    'bet_per'),
    'BETSGR'   : ('Beta Sagittarii', ['Beta Sgr'],                   'bet_sgr'),
    'CHICEN'   : ('Chi Centauri'   , ['Chi Cen'],                    'chi_cen'),
    'CWLEO'    : ('CW Leonis'      , ['CW Leo' ],                    'cw_leo' ),
    'DELAQR'   : ('Delta Aquarii'  , ['Delta Aqr'],                  'del_aqr'),
    'DELCEN'   : ('Delta Centauri' , ['Delta Cen'],                  'del_cen'),
    'DELLUP'   : ('Delta Lupi'     , ['Delta Lup'],                  'del_lup'),
    'DELPER'   : ('Delta Persei'   , ['Delta Per'],                  'del_per'),
    'DELVIR'   : ('Delta Virginis' , ['Delta Vir'],                  'del_vir'),
    'EPSCAS'   : ('Epsilon Cassiopeiae',
                                     ['Epsilon Cas'],                'eps_cas'),
    'EPSCEN'   : ('Epsilon Centauri',
                                     ['Epsilon Cen'],                'eps_cen'),
    'EPSLUP'   : ('Epsilon Lupi'   , ['Epsilon Lup'],                'eps_lup'),
    'EPSORI'   : ('Epsilon Orionis', ['Epsilon Ori'],                'eps_ori'),
    'EPSPSA'   : ('Epsilon Piscis Austrini',
                                     ['Epsilon PsA'],                'eps_psa'),
    'ETALUP'   : ('Eta Lupi'       , ['Eta Lup'],                    'eta_lup'),
    'ETAUMA'   : ('Eta Ursae Majoris',
                                     ['Eta UMa'],                    'eta_uma'),
    'ETACAR'   : ('Eta Carinae'    , ['Eta Car'],                    'eta_car'),
    'GAMARA'   : ('Gamma Arae'     , ['Gamma Ara'],                  'gam_ara'),
    'GAMCAS'   : ('Gamma Cassiopeiae',
                                     ['Gamma Cas'],                  'gam_cas'),
    'GAMCOL'   : ('Gamma Columbae' , ['Gamma Col'],                  'gam_col'),
    'GAMCRU'   : ('Gamma Crucis'   , ['Gamma Cru'],                  'gam_cru'),
    'GAMGRU'   : ('Gamma Gruis'    , ['Gamma Gru'],                  'gam_gru'),
    'GAMLUP'   : ('Gamma Lupi'     , ['Gamma Lup'],                  'gam_lup'),
    'GAMPEG'   : ('Gamma Pegasi'   , ['Gamma Peg'],                  'gam_peg'),
    'Gamma_Ori': ('Gamma Orionis'  , ['Gamma Ori'],                  'gam_ori'),
    'HD71334'  : ('HD 71334'       , ['HD 71334' ],                  'hd_71334'),
    'HD339'    : ('HD 339479'      , ['HD 339479'],                  'hd_339479'),
    'IOTCEN'   : ('Iota Centauri'  , ['Iota Cen'],                   'io_cen' ),
    'KAPCEN'   : ('Kappa Centauri' , ['Kappa Cen'],                  'kap_cen'),
    'KAPORI'   : ('Kappa Orionis'  , ['Kappa Ori'],                  'kap_ori'),
    'LAMCET'   : ('Lambda Ceti'    , ['Lambda Cet'],                 'lam_cet'),
    'LAMSCO'   : ('Lambda Scorpii' , ['Lambda Sco'],                 'lam_sco'),
    'LMC303'   : ('LMC 303'        , ['LMC 303'],                    'lmc_303'),
    'MUPSA'    : ('Mu Piscis Austrini',
                                     ['Mu PsA'],                     'mu_psa' ),
    'NMLTAURI' : ('NML Tauri'      , ['NML Tau', 'IK Tau'],          'nml_tau'),
    'NUCEN'    : ('Nu Centauri'    , ['Nu Cen'],                     'nu_cen' ),
    'OMICET'   : ('Omicron Ceti'   , ['Omicron Cet'],                'omi_cet'),
    'PSICEN'   : ('Psi Centauri'   , ['Psi Cen'],                    'psi_cen'),
    'RCAS'     : ('R Cassiopeiae'  , ['R Cas'],                      'r_cas'  ),
    'RDORADUS' : ('R Doradus'      , ['R Dor'],                      'r_dor'  ),
    'RHYA'     : ('R Hydrae'       , ['R Hya'],                      'r_hya'  ),
    'RLEO'     : ('R Leo'          , ['R Leo'],                      'r_leo'  ),
    'TAU78'    : ('78 Tauri'       , ['78 Tau'],                     '78_tau' ),
    'THEARA'   : ('Theta Arae'     , ['Theta Ara'],                  'tet_ara'),
    'THEHYA'   : ('Theta Hydrae'   , ['Theta Hya'],                  'tet_hya'),
    'WHYA'     : ('W Hydrae'       , ['W Hya'],                      'w_hya'  ),
    'ZETCEN'   : ('Zeta Centauri'  , ['Zeta Cen'],                   'zet_cen'),
    'ZETCMA'   : ('Zeta Canis Majoris',
                                     ['Zeta CMa'],                   'zet_cma'),
    'ZETOPH'   : ('Zeta Ophiuchi'  , ['Zeta Oph'],                   'zet_oph'),
    'ZETORI'   : ('Zeta Orionis'   , ['Zeta Ori'],                   'zet_ori'),
    'ZETPER'   : ('Zeta Persei'    , ['Zeta Per'],                   'zet_per'),
}

# Star aliases
STAR_ABBREVS['CALSTAR1' ] = STAR_ABBREVS['VEGA'  ]
STAR_ABBREVS['CALSTAR2' ] = STAR_ABBREVS['78TAU' ]
STAR_ABBREVS['ECSTAR'   ] = STAR_ABBREVS['ETACAR']
STAR_ABBREVS['CWSTAR'   ] = STAR_ABBREVS['CWLEO' ]
STAR_ABBREVS['STARCALEC'] = STAR_ABBREVS['ETACAR']
STAR_ABBREVS['STARCALCW'] = STAR_ABBREVS['CWLEO' ]
STAR_ABBREVS['STARCHREC'] = STAR_ABBREVS['ETACAR']
STAR_ABBREVS['STARCHRCW'] = STAR_ABBREVS['CWLEO' ]
STAR_ABBREVS['ALFORI'   ] = STAR_ABBREVS['ALPORI']
STAR_ABBREVS['ALFBOO'   ] = STAR_ABBREVS['ALPBOO']
STAR_ABBREVS['ALFSCO'   ] = STAR_ABBREVS['ALPSCO']
STAR_ABBREVS['ALCEN'    ] = STAR_ABBREVS['ALPCEN']
STAR_ABBREVS['ALPVIR'   ] = STAR_ABBREVS['SPICA' ]
STAR_ABBREVS['GAMMA_ORI'] = STAR_ABBREVS['Gamma_Ori']
STAR_ABBREVS['OMICRONCT'] = STAR_ABBREVS['OMICET']
STAR_ABBREVS['ZETAORI'  ] = STAR_ABBREVS['ZETORI']
STAR_ABBREVS['WHYDRAE'  ] = STAR_ABBREVS['WHYA'  ]

# Add stars to the target list
for (name, alts, lid) in STAR_ABBREVS.values():
    TARGET_DICT[name.upper()] = (name, alts, 'Star', 'N/A',
                                 'urn:nasa:pds:context:target:star.%s' % lid)

def iss_target_info(target_name, target_desc, observation_id, shutter_mode_id,
                    sequence_title, filename):

    name = target_name.upper()
    desc = target_desc.upper()
    obs_id = observation_id.upper()
    sequence_title = sequence_title.upper()

    # Read the target name out of the OBSERVATION_ID
    abbrev = ''
    obsname = ''
    if len(obs_id) > 3 and obs_id[:3] not in ('ICO', 'V2_', 'LUN', 'EAR', 'MAS'):
        try:
            parts = obs_id.split('_')
            abbrev = parts[1][-2:]
            obsname = CIMS_TARGET_ABBREVIATIONS[abbrev]
        except (KeyError, IndexError, ValueError):
            pass

    target_keys = set()

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
    if len(target_keys) and shutter_mode_id != 'DISABLED':
        keys = list(target_keys)
        keys.sort()
        return [TARGET_DICT[k.upper()] for k in keys]

    # Growing increasingly desperate...
    if shutter_mode_id != 'DISABLED':
        if 'SCAT' in obs_id or 'STRAYLITE' in obs_id or 'SCATLIGHT' in obs_id:
            return [('Scat Light', [], 'Calibration Field', 'N/A',
                     'urn:nasa:pds:context:target:calibration_field.scat_light')]

        if 'LAMP' in obs_id:
            return [('Cal Lamps', [], 'Calibrator', 'N/A',
                     'urn:nasa:pds:context:target:calibrator.cal_lamps')]

        if 'DARK SKY' in (name, desc):
            return [('Dark Sky', [], 'Calibration Field', 'N/A',
                     'urn:nasa:pds:context:target:calibration_field.dark_sky')]

        if 'SKY' in (name, desc) and 'SK_' in obs_id:
            return [('Sky', [], 'Calibration Field', 'N/A',
                     'urn:nasa:pds:context:target:calibration_field.sky')]

        if desc == 'PROBE':
            return [('Probe', [], 'Equipment', 'N/A',
                     'urn:nasa:pds:context:target:equipment.probe')]

        if 'GEOMCALIB' in obs_id or 'CALIBR' in obs_id:
            return [('Sky', [], 'Calibration Field', 'N/A',
                     'urn:nasa:pds:context:target:calibration_field.sky')]

        if 'PLEIADES' in obs_id:
            return [('Pleiades', [], 'Star Cluster', 'N/A',
                     'urn:nasa:pds:context:target:star_cluster.pleiades')]

        if 'DUSTBAND' in obs_id:
            return [('Dust', [], 'Dust', 'N/A',
                     'urn:nasa:pds:context:target:dust.pleiades')]

        if 'FLAT' in obs_id:
            return [('Flat Field', [], 'Calibrator', 'N/A',
                     'urn:nasa:pds:context:target:calibrator.flat_field')]

    if 'TEST' in obs_id or 'TEST' in sequence_title or 'NOISY' in obs_id:
        return [('Test Image', [], 'Calibrator', 'N/A',
                 'urn:nasa:pds:context:target:calibrator.test_image')]

    if 'CHECKOUT' in obs_id or 'CHKOUT' in sequence_title:
        return [('Checkout', [], 'Calibrator', 'N/A',
                 'urn:nasa:pds:context:target:calibrator.checkout')]

    if shutter_mode_id == 'DISABLED' or (shutter_mode_id != 'ENABLED' and
                                         'DARK' in obs_id):
        return [('Dark', [], 'Calibration Field', 'N/A',
                 'urn:nasa:pds:context:target:calibration_field.dark')]

    # Special cases
    if 'TRIGGER' in obs_id or obs_id in ('ISS_C39OT_INSTRADT001_CIRS',
                                         'UVIS_C26ST_EUVCHECK001_PRIME_C',
                                         'VIMS_C25AR_SLITDITHER_2PIX_PRI'):
        return [('Sky', [], 'Calibration Field', 'N/A',
                 'urn:nasa:pds:context:target:calibration_field.sky')]

    if 'STAR' in obs_id or 'TRANSIT' in obs_id or 'BRIGHT' in obs_id:
        print 'unknown star: %s %s %s %s' % (target_name, target_desc,
                                             observation_id, filename)
        return [('Star', [], 'Calibration Field', 'N/A',
                 'urn:nasa:pds:context:target:calibration_field.star')]

    if 'DECON' in sequence_title:
        return [TARGET_DICT['SPICA']]

    print 'unknown target: %s %s %s %s' % (target_name, target_desc,
                                           observation_id, filename)

    return [('Unknown', [], 'Calibrator', 'N/A',
             'urn:nasa:pds:context:target:calibrator.unk')]

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
    label_text = label_text.replace('0000-000T00:00:00.000', 'INVALID_DATE')
    label_text = label_text.replace('\r','') # pyparsing is not set up for <CR>

    label = pdsparser.PdsLabel.from_string(label_text).as_dict()
    if label['EARTH_RECEIVED_START_TIME'] == 'INVALID_DATE':    # known error
        label['EARTH_RECEIVED_START_TIME'] = '0000-000T00:00:00.000'

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
                                  label['OBSERVATION_ID'],
                                  label['SHUTTER_MODE_ID'],
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
