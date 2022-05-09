################################################################################
# uvis_data_raw_labeler.py
#
# Create XML labels for the Cassini UVIS products.
#
# Syntax:
#   python euv_fuv_data_raw_labeler.py [--replace] path [path ...]
#
# A label will be created for each image file ("*.dat") found in each given
# path, recursively. This can be any combination of directories and individual
# data files.
#
# Use "--replace" to replace pre-existing labels. Otherwise, labels will only be
# generated for images that currently lack labels.
################################################################################

import os,sys
import numpy as np
import pdsparser
import vicar
import traceback
from xmltemplate import XmlTemplate
import textkernel
import tabulation
import julian

from SOLAR_SYSTEM_TARGETS import SOLAR_SYSTEM_TARGETS

EUV_FUV_TEMPLATE = XmlTemplate('euv_fuv_data_raw_template.xml')
HDAC_TEMPLATE = XmlTemplate('hdac_data_raw_template.xml')
HSP_TEMPLATE = XmlTemplate('hsp_data_raw_template.xml')

# Read the observation id table (2-column: date, Cassini observation ID) as list of character strings:
with open('observation_ids_mjtm_dropduplicates.tab') as f:
    recs = f.readlines()

# Create a dictionary of observation ids that when given a date, returns an observation id
OBSERVATION_IDS = {}
for rec in recs:
    #(date, obs_id) = rec.rstrip().replace('"','').split(',')
    (date, obs_id) = rec.rstrip().split(',') #strip off newline char, and split each line into its own list
    OBSERVATION_IDS[date] = obs_id

EOM = '2017-09-16T00:00:00' #End Of Mission

# Define global variables for time conversions
# Spacecraft CLocK, Temps Atomique International 
NEW_SCLK_FROM_TAI = None
NEW_TAI_FROM_SCLK = None
OLD_SCLK_FROM_TAI = None
OLD_TAI_FROM_SCLK = None

def INIT_SCLKS():
    # HSP had various timing issues to deal with (not relevant for EUV/FUV)
    global NEW_SCLK_FROM_TAI, NEW_TAI_FROM_SCLK
    global OLD_SCLK_FROM_TAI, OLD_TAI_FROM_SCLK

    if NEW_SCLK_FROM_TAI is not None: return

    tk = textkernel.from_file('cas00172.tsc') # SPICE file
    coeffts = np.array(tk['SCLK'][1]['COEFFICIENTS_82']).reshape(-1,3)
    sclk = (coeffts[:,0] + tk['SCLK_PARTITION_START_82']) / 256.
    tai = julian.tai_from_tdt(coeffts[:,1])

    tai_end = julian.tai_from_iso(EOM)
    rate_end = coeffts[-1,2]
    sclk_end = sclk[-1] + (tai_end - tai[-1]) / rate_end

    sclk = np.array(list(sclk) + [sclk_end])
    tai  = np.array(list(tai)  + [tai_end])
    cas00172 = tabulation.Tabulation(tai, sclk)
    NEW_SCLK_FROM_TAI = tabulation.Tabulation(tai, sclk)
    NEW_TAI_FROM_SCLK = tabulation.Tabulation(sclk, tai)

    tk = textkernel.from_file('cas00171.tsc')
    coeffts = np.array(tk['SCLK'][1]['COEFFICIENTS_82']).reshape(-1,3)
    sclk = (coeffts[:,0] + tk['SCLK_PARTITION_START_82']) / 256.
    tai = julian.tai_from_tdb(coeffts[:,1])

    tai_end = julian.tai_from_iso(EOM)
    rate_end = coeffts[-1,2]
    sclk_end = sclk[-1] + (tai_end - tai[-1]) / rate_end

    sclk = np.array(list(sclk) + [sclk_end])
    tai  = np.array(list(tai)  + [tai_end])
    cas00171 = tabulation.Tabulation(tai, sclk)
    OLD_SCLK_FROM_TAI = tabulation.Tabulation(tai, sclk)
    OLD_TAI_FROM_SCLK = tabulation.Tabulation(sclk, tai)

################################################################################

# Create a dictionary keyed by the body name in upper case,
# that returns a tuple of necessary information for creating an XML description of a target
# The imported SOLAR_SYSTEM_TARGETS is a list of tuples
# TARGET_DICT[NAME] = (name, lid_name, alt_names, target_type, primary, lid)

TARGET_DICT = {rec[0].upper():rec for rec in SOLAR_SYSTEM_TARGETS} # Dictionary comprehension - {key: value for record in list_of_solar_sys_targs}

# Sort out some random moons that were observed by Cassini and subsequently renamed
# e.g. assign the same tuple under HATI to S14_2004
TARGET_DICT['S12_2004'] = TARGET_DICT['S/2004 S 12']
TARGET_DICT['S13_2004'] = TARGET_DICT['S/2004 S 13']
TARGET_DICT['S14_2004'] = TARGET_DICT['HATI'   ]
TARGET_DICT['S18_2004'] = TARGET_DICT['BESTLA' ]
TARGET_DICT['S8_2004' ] = TARGET_DICT['FORNJOT']

# Put more records into TARGET_DICT: sort out alternative names (e.g. TARGET_DICT['SUN'] and TARGET_DICT['NAIF ID 10'] return same tuple) 
# Recall SOLAR_SYSTEM_TARGETS (which builds TARGET_DICT) takes the form (target_name, alt_names, target_type, primary, lid)
# Every alt name translates to the name
#for rec in TARGET_DICT.values():
# Fix for Python 3.x
for rec in list(TARGET_DICT.values()): # Force a list, so that dictionary doesn't change size while iterating
    alt_names = rec[1] # rec[1] is tuple of alternative names (SPICE, NAIF IDs)
    for alt_name in alt_names:
        TARGET_DICT[alt_name.upper()] = rec # Populate new dictionary elements with the same values (rec) corresponding to the new alt_name key

# CIMS IDs are how Cassini Observations were planned: each part of the mission was assigned to a particular instrument team 
# who would be observing a particular target (e.g. Saturn, the rings, Enceladus...)
# The ID has several parts: 3 digit number refers to orbit of Cassini, 2 char code refers to primary intended target, (up to) 9 character codename 

# Create a dictionary of 2-letter abbrevs referring to targets that will be used later to fix 
# any messes that creep into the label - e.g. target name = sky means that you'll have to go searching for what the intended science target actually was!
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

    'SW': 'SOLAR WIND',
}

# Checked by MRS on May 6, 2020
# Updated by MRS on May 16-17, 2020
# HSP did a lot of targeting at stars (through occultation experiments)
# Create a dictionary of scraped information from CIMS IDs of alternate names of stars (aliases)
STAR_ABBREVS = {
    '126TAU'   : ('126 Tauri'           , ['126 Tau'],                      '126_tau'),
    '28SGR'    : ('28 Sagittarii'       , ['28 Sgr'],                       '28_sgr'),
    '205839'   : ('b Centauri'          , ['b Cen', 'HD 129116', 'SAO 205839'], 'b_cen'),
    '26TAU'    : ('26 Tauri'            , ['26 Tau'],                       '26_tau' ),
    '2CEN'     : ('g Centauri'          , ['g Cen', '2 Cen'],               'g_cen'  ),
    '30HER'    : ('30 Herculis'         , ['30 Her'],                       'g_her' ),
    '30PSC'    : ('30 Piscium'          , ['30 Psc'],                       '30_psc' ),
    '3CEN'     : ('3 Centauri'          , ['3 Cen'],                        '3_cen'  ),
    '56LEO'    : ('56 Leonis'           , ['56 Leo'],                       '56_leo' ),
    '78TAU'    : ('78 Tauri'            , ['78 Tau'],                       'tet02_tau' ),
    'ALP1CRU'  : ('Alpha1 Crucis'       , ['Alpha1 Cru'],                   'alf01_cru'),
    'ALPARA'   : ('Alpha Arae'          , ['Alpha Ara'],                    'alf_ara'),
    'ALPAUR'   : ('Capella'             , ['Alpha Aurigae', 'Alpha Aur'],   'alf_aur'),
    'ALPCEN'   : ('Alpha Centauri'      , ['Alpha Cen'],                    'alf_cen'),
    'ALPCET'   : ('Alpha Ceti'          , ['Alpha Cet'],                    'alf_cet'),
    'ALPCMA'   : ('Sirius'              , ['Alpha Canis Majoris', 'Alpha CMa'], 'alf_cma'),
    'ALPCMI'   : ('Procyon'             , ['Alpha Canis Minoris', 'Alpha CMi'], 'alf_cmi'),
    'ALPCRU'   : ('Alpha Crucis'        , ['Alpha Cru'],                    'alf_cru'),
    'ALPERI'   : ('Alpha Eridani'       , ['Alpha Eri'],                    'alf_eri'),
    'ALPHER'   : ('Alpha Herculis'      , ['Alpha Her'],                    'alf_her'),
    'ALPHYA'   : ('Alpha Hydrae'        , ['Alpha Hya'],                    'alf_hya'),
    'ALPLEO'   : ('Regulus'             , ['Alpha Leo', 'Alpha Leo'],       'alf_leo'),
    'ALPLUP'   : ('Alpha Lupi'          , ['Alpha Lup'],                    'alf_lup'),
    'ALPLYR'   : ('Alpha Lyrae'         , ['Alpha Lyr'],                    'alf_lyr'),
    'ALPORI'   : ('Betelgeuse'          , ['Alpha Orionis', 'Alpha Ori'],   'alf_ori'),
    'ALPPAV'   : ('Alpha Pavonis'       , ['Alpha Pav'],                    'alf_pav'),
    'ALPSCO'   : ('Antares'             , ['Alpha Scorpii', 'Alpha Sco'],   'alf_sco'),
    'ALPSEX'   : ('Alpha Sextantis'     , ['Alpha Sex'],                    'alf_sex'),
    'ALPTAU'   : ('Aldebaran'           , ['Alpha Tauri', 'Alpha Tau'],     'alf_tau'),
    'ALPTRA'   : ('Alpha Trianguli Australis', ['Alpha TrA'],               'alf_tra'),
    'ARCTURUS' : ('Arcturus'            , ['Alpha Bootes', 'Alpha Boo'],    'alf_boo'),
    'BETAND'   : ('Beta Andromedae'     , ['Beta And'],                     'bet_and'),
    'BETCEN'   : ('Beta Centauri'       , ['Beta Cen', 'SAO  '],            'bet_cen'),
    'BETCMA'   : ('Beta Canis Majoris'  , ['Beta CMa'],                     'bet_cma'),
    'BETCRU'   : ('Beta Crucis'         , ['Beta Cru'],                     'bet_cru'),
    'BETGRU'   : ('Beta Gruis'          , ['Beta Gru'],                     'bet_gru'),
    'BETHYA'   : ('Beta Hydrae'         , ['Beta Hya'],                     'bet_hya'),
    'BETLIB'   : ('Beta Librae'         , ['Beta Lib'],                     'bet_lib'),
    'BETLUP'   : ('Beta Lupi'           , ['Beta Lup'],                     'bet_lup'),
    'BETORI'   : ('Beta Orionis'        , ['Beta Ori'],                     'bet_ori'),
    'BETPEG'   : ('Beta Pegasi'         , ['Beta Peg'],                     'bet_peg'),
    'BETPER'   : ('Algol'               , ['Beta Perei', 'Beta Per'],       'bet_per'),
    'BETPSA'   : ('Beta Piscis Austrini', ['Beta PsA'],                     'bet_psa'),
    'BETSGR'   : ('Beta1 Sagittarii'    , ['Beta1 Sgr'],                    'bet01_sgr'),
    'BETUMI'   : ('Beta Ursae Minoris'  , ['Beta UMi'],                     'bet_umi'),
    'CALSTAR3' : ('HR 996'              , ['Kappa1 Cet'],                   'kap01_cet'),
    'CANOPUS'  : ('Canopus'             , ['Alpha Carinae', 'Alpha Car'],   'alf_car'),
    'CHIAQR'   : ('Chi Aquarii'         , ['Chi Aqr'],                      'chi_aqr'),
    'CHICEN'   : ('Chi Centauri'        , ['Chi Cen'],                      'chi_cen'),
    'CHICYG'   : ('Chi Cygni'           , ['Chi Cyg'],                      'chi_cyg'),
    'CWLEO'    : ('CW Leonis'           , ['CW Leo', 'IRC +10216'],         'irc_+10216' ),
    'DELAQR'   : ('Delta Aquarii'       , ['Delta Aqr'],                    'del_aqr'),
    'DELCEN'   : ('Delta Centauri'      , ['Delta Cen'],                    'del_cen'),
    'DELCET'   : ('Delta Ceti'          , ['Delta Cet'],                    'del_cet'),
    'DELLUP'   : ('Delta Lupi'          , ['Delta Lup'],                    'del_lup'),
    'DELOPH'   : ('Delta Ophiuchi'      , ['Delta Oph'],                    'del_oph'),
    'DELORI'   : ('Delta Orionis'       , ['Delta Ori'],                    'del_ori'),
    'DELPER'   : ('Delta Persei'        , ['Delta Per'],                    'del_per'),
    'DELSCO'   : ('Delta Scorpii'       , ['Delta Sco'],                    'del_sco'),
    'DELVIR'   : ('Delta Virginis'      , ['Delta Vir'],                    'del_vir'),
    'EPSCAS'   : ('Epsilon Cassiopeiae' , ['Epsilon Cas'],                  'eps_cas'),
    'EPSCEN'   : ('Epsilon Centauri'    , ['Epsilon Cen'],                  'eps_cen'),
    'EPSCMA'   : ('Epsilon Canis Majoris',['Epsilon CMa'],                  'eps_cma'),
    'EPSLUP'   : ('Epsilon Lupi'        , ['Epsilon Lup'],                  'eps_lup'),
    'EPSMIC'   : ('Epsilon Microscopii' , ['Epsilon Mic'],                  'eps_mic'),
    'EPSMUS'   : ('Epsilon Muscae'      , ['Epsilon Mus'],                  'eps_mus'),
    'EPSORI'   : ('Epsilon Orionis'     , ['Epsilon Ori'],                  'eps_ori'),
    'EPSPEG'   : ('Epsilon Pegasi'      , ['Epsilon Peg'],                  'eps_peg'),
    'EPSPER'   : ('Epsilon Persei'      , ['Epsilon Per'],                  'eps_per'),
    'EPSPSA'   : ('Epsilon Piscis Austrini', ['Epsilon PsA'],               'eps_psa'),
    'EPSSGR'   : ('Epsilon Sagittarii'  , ['Epsilon Sgr'],                  'eps_sgr'),
    'ETACAR'   : ('Eta Carinae'         , ['Eta Car'],                      'eta_car'),
    'ETACMA'   : ('Eta Canis Majoris'   , ['Eta CMa'],                      'eta_cma'),
    'ETALUP'   : ('Eta Lupi'            , ['Eta Lup'],                      'eta_lup'),
    'ETASGR'   : ('Eta Sagittarii'      , ['Eta Sgr'],                      'eta_sgr'),
    'ETAUMA'   : ('Eta Ursae Majoris'   , ['Eta UMa'],                      'eta_uma'),
    'FOMALHAUT': ('Fomalhaut'           , ['Alpha Piscis Austrini', 'Alpha PsA'], 'alf_psa'),
    'GAMAND'   : ('Gamma Andromedae'    , ['Gamma And'],                    'gam_and'),
    'GAMARA'   : ('Gamma Arae'          , ['Gamma Ara'],                    'gam_ara'),
    'GAMCAS'   : ('Gamma Cassiopeiae'   , ['Gamma Cas'],                    'gam_cas'),
    'GAMCNC'   : ('Gamma Cancri'        , ['Gamma Cnc'],                    'gam_cnc'),
    'GAMCOL'   : ('Gamma Columbae'      , ['Gamma Col'],                    'gam_col'),
    'GAMCRU'   : ('Gamma Crucis'        , ['Gamma Cru'],                    'gam_cru'),
    'GAMERI'   : ('Gamma Eridani'       , ['Gamma Eri'],                    'gam_eri'),
    'GAMGRU'   : ('Gamma Gruis'         , ['Gamma Gru'],                    'gam_gru'),
    'GAMLUP'   : ('Gamma Lupi'          , ['Gamma Lup'],                    'gam_lup'),
    'GAMORI'   : ('Gamma Orionis'       , ['Gamma Ori'],                    'gam_ori'),
    'GAMPEG'   : ('Gamma Pegasi'        , ['Gamma Peg'],                    'gam_peg'),
    'HD339'    : ('HD 339479'           , [],                               'hd_339479'),
    'HD37962'  : ('HD 37962'            , [],                               'hd_37962'),
    'HD205905' : ('HD 205905'           , [],                               'hd_205905'),
    'HD71334'  : ('HD 71334'            , [],                               'hd_71334'),
    'IOTCEN'   : ('Iota Centauri'       , ['Iota Cen'],                     'io_cen' ),
    'IOTORI'   : ('Iota Orionis'        , ['Iota Ori'],                     'io_ori' ),
    'KAPCEN'   : ('Kappa Centauri'      , ['Kappa Cen'],                    'kap_cen'),
    'KAPCMA'   : ('Kappa Canis Majoris' , ['Kappa CMa'],                    'kap_cma'),
    'KAPORI'   : ('Kappa Orionis'       , ['Kappa Ori'],                    'kap_ori'),
    'KAPSCO'   : ('Kappa Scorpii'       , ['Kappa Sco'],                    'kap_sco'),
    'KAPVEL'   : ('Kappa Velorum'       , ['Kappa Vel'],                    'kap_vel'),
    'L2PUP'    : ('L2 Puppis'           , ['L2 Pup'],                       'l02_pup'),
    'LAMAQL'   : ('Lambda Aquilae'      , ['Lambda Aql'],                   'lam_aql'),
    'LAMAQR'   : ('Lambda Aquarii'      , ['Lambda Aqr'],                   'lam_aqr'),
    'LAMCET'   : ('Lambda Ceti'         , ['Lambda Cet'],                   'lam_cet'),
    'LAMSCO'   : ('Lambda Scorpii'      , ['Lambda Sco'],                   'lam_sco'),
    'LAMTAU'   : ('Lambda Tauri'        , ['Lambda Tau'],                   'lam_tau'),
    'LAMVEL'   : ('Lambda Velorum'      , ['Lambda Vel'],                   'lam_vel'),
    'LMC303'   : ('LMC 303'             , ['LMC 303'],                      'lmc_303'),
    'MUCEN'    : ('Mu Centauri'         , ['Mu Cen'],                       'mu_cen' ),
    'MUCEP'    : ('Mu Cephei'           , ['Mu Cep'],                       'mu_cep' ),
    'MUGEM'    : ('Mu Geminorum'        , ['Mu Gem'],                       'mu_gem' ),
    'MUPSA'    : ('Mu Piscis Austrini'  , ['Mu PsA'],                       'mu_psa' ),
    'MUSCO'    : ('Mu Scorpii'          , ['Mu Sco'],                       'mu_sco' ),
    'MUSGR'    : ('Mu Sagittarii'       , ['Mu Sgr'],                       'mu_sgr' ),
    'NMLTAURI' : ('IK Tauri'            , ['IK Tau', 'NML Tau'],            'ik_tau'),
    'NUCEN'    : ('Nu Centauri'         , ['Nu Cen'],                       'nu_cen' ),
    'NUVIR'    : ('Nu Virginis'         , ['Nu Vir'],                       'nu_vir' ),
    'OMEVIR'   : ('Omega Virginis'      , ['Omega Vir'],                    'ome_vir'),
    'OMICET'   : ('Omicron Ceti'        , ['Omicron Cet'],                  'omi_cet'),
    'PI1GRU'   : ('Pi1 Gruis'           , ['Pi1 Gru'],                      'pi.01_gru'),
    'PI4ORI'   : ('Pi4 Orionis'         , ['Pi4 Ori'],                      'pi.04_ori'),
    'PSICEN'   : ('Psi Centauri'        , ['Psi Cen'],                      'psi_cen'),
    'RAQL'     : ('R Aquila'            , ['R Aql'],                        'r_aql'  ),
    'RAQR'     : ('R Aquarii'           , ['R Aqr'],                        'r_aqr'  ),
    'RCAR'     : ('R Carina'            , ['R Car'],                        'r_car'  ),
    'RCAS'     : ('R Cassiopeiae'       , ['R Cas'],                        'r_cas'  ),
    'RDORADUS' : ('R Doradus'           , ['R Dor'],                        'r_dor'  ),
    'RHOPER'   : ('Rho Persei'          , ['Rho Per'],                      'rho_per'),
    'RHYA'     : ('R Hydrae'            , ['R Hya'],                        'r_hya'  ),
    'RLEO'     : ('R Leo'               , ['R Leo'],                        'r_leo'  ),
    'RLYR'     : ('R Lyrae'             , ['R Lyr', '13 Lyr'],              '13_lyr' ),
    'RSCNC'    : ('RS Cancer'           , ['RS Cnc'],                       'rs_cnc' ),
    'RWLMI'    : ('RW Leonis Minoris'   , ['RW LMi'],                       'rw_lmi' ),
    'RXLEP'    : ('RX Leporis'          , ['RX Lep'],                       'rx_lep' ),
    'SIGSGR'   : ('Sigma Sagittarii'    , ['Sigma Sgr'],                    'sig_sgr'),
    'SLEP'     : ('S Leporis'           , ['S Lep'],                        's_lep'  ),
    'SPICA'    : ('Spica'               , ['Alpha Virginis', 'Alpha Vir'],  'alf_vir'),
    'TAU78'    : ('78 Tauri'            , ['78 Tau'],                       'tet02_tau'),
    'TCEP'     : ('T Cephei'            , ['T Cep'],                        't_cep'  ),
    'THEARA'   : ('Theta Arae'          , ['Theta Ara'],                    'tet_ara'),
    'THECAR'   : ('Theta Carinae'       , ['Theta Car'],                    'tet_car'),
    'THEHYA'   : ('Theta Hydrae'        , ['Theta Hya'],                    'tet_hya'),
    'TXCAM'    : ('TX Camelopardalis'   , ['TX Cam'],                       'tx_cam' ),
    'VEGA'     : ('Vega'                , ['Alpha Lyrae', 'Alpha Lyr'],     'alf_lyr'),
    'VHYA'     : ('V Hydrae'            , ['V Hya'],                        'v_hya'  ),
    'VXSGR'    : ('VX Sagittarii'       , ['VX Sgr'],                       'vx_sgr' ),
    'VYCMA'    : ('VY Canis Majoris'    , ['VY CMa'],                       'vy_cma' ),
    'WAQL'     : ('W Aquilae'           , ['W Aql'],                        'w_aql'  ),
    'WHYA'     : ('W Hydrae'            , ['W Hya'],                        'w_hya'  ),
    'XICET'    : ('Xi2 Ceti'            , ['Xi2 Cet'],                      'ksi02_cet'),
    'XOPH'     : ('X Ophiuchi'          , ['X Oph'],                        'x_oph'  ),
    'ZETCEN'   : ('Zeta Centauri'       , ['Zeta Cen'],                     'zet_cen'),
    'ZETCMA'   : ('Zeta Canis Majoris'  , ['Zeta CMa'],                     'zet_cma'),
    'ZETOPH'   : ('Zeta Ophiuchi'       , ['Zeta Oph'],                     'zet_oph'),
    'ZETORI'   : ('Zeta Orionis'        , ['Zeta Ori'],                     'zet_ori'),
    'ZETPER'   : ('Zeta Persei'         , ['Zeta Per'],                     'zet_per'),
    'ZETPUP'   : ('Zeta Puppis'         , ['Zeta Pup'],                     'zet_pup'),
}

# Star aliases
STAR_ABBREVS['ALCEN'    ] = STAR_ABBREVS['ALPCEN'  ]
STAR_ABBREVS['ALFBOO'   ] = STAR_ABBREVS['ARCTURUS']
STAR_ABBREVS['ALFORI'   ] = STAR_ABBREVS['ALPORI'  ]
STAR_ABBREVS['ALFSCO'   ] = STAR_ABBREVS['ALPSCO'  ]
STAR_ABBREVS['ALPBOO'   ] = STAR_ABBREVS['ARCTURUS']
STAR_ABBREVS['ALPVIR'   ] = STAR_ABBREVS['SPICA'   ]
STAR_ABBREVS['ALFVIR'   ] = STAR_ABBREVS['SPICA'   ]
STAR_ABBREVS['CALSTAR1' ] = STAR_ABBREVS['VEGA'    ]
STAR_ABBREVS['CALSTAR2' ] = STAR_ABBREVS['78TAU'   ]
STAR_ABBREVS['CWSTAR'   ] = STAR_ABBREVS['CWLEO'   ]
STAR_ABBREVS['ECSTAR'   ] = STAR_ABBREVS['ETACAR'  ]
STAR_ABBREVS['GAMMA_ORI'] = STAR_ABBREVS['GAMORI'  ]
STAR_ABBREVS['OMICRONCT'] = STAR_ABBREVS['OMICET'  ]
STAR_ABBREVS['SAO205839'] = STAR_ABBREVS['205839'  ]
STAR_ABBREVS['STARCALCW'] = STAR_ABBREVS['CWLEO'   ]
STAR_ABBREVS['STARCALEC'] = STAR_ABBREVS['ETACAR'  ]
STAR_ABBREVS['STARCHRCW'] = STAR_ABBREVS['CWLEO'   ]
STAR_ABBREVS['STARCHREC'] = STAR_ABBREVS['ETACAR'  ]
STAR_ABBREVS['WHYDRAE'  ] = STAR_ABBREVS['WHYA'    ]
STAR_ABBREVS['XI2CET'   ] = STAR_ABBREVS['XICET'   ]
STAR_ABBREVS['ZETAORI'  ] = STAR_ABBREVS['ZETORI'  ]

# Add stars to the target dictionary
for (name, alts, lid) in STAR_ABBREVS.values(): # Create new star entries to the TARGET_DICT with uppercase name key, and the familiar tuple of (target_name, alt_names, target_type, primary, lid)
    TARGET_DICT[name.upper()] = (name, alts, 'Star', 'N/A',
                                 'urn:nasa:pds:context:target:star.%s' % lid)
# Add miscellaneous things to the target dict
TARGET_DICT['SOLAR WIND'] = ('Solar Wind', [], 'Plasma Stream', 'N/A',
                             'urn:nasa:pds:context:target:plasma_stream.solar_wind')

TARGET_DICT['STAR'] = ('Star', [], 'Calibration Field', 'N/A',
                        'urn:nasa:pds:context:target:calibration_field.star')

TARGET_DICT['CALIBRATION'] = ('Calibration', [], 'Calibrator', 'N/A',
                        'urn:nasa:pds:context:target:calibrator.calibration')

TARGET_DICT['UNK'] = ('Unknown', [], 'Calibrator', 'N/A',
                        'urn:nasa:pds:context:target:calibrator.unk')

def uvis_target_info(target_name, observation_id, purpose_str, filename):
    """
    Identify the targets that may be mis-identified, or duplicate-identified, inside PDS3 labels
    
    Parameters
    ----------
    target_name : string
        Name of target, e.g. Mimas, S14_2014
    observation_id : string
        CIMS ID
    purpose_str : string
        The science goal, obtained from PDS3 label
    filename : string
        DESCRIPTION.

    Returns
    -------
    list
        Returns targets for each of the keys that are present in the PDS3 label

    """
    target_keys = set() # a set is initiated as it will contain only unique elements)

    # Perform some error repairs
    if target_name == 'S RINGS':
        target_name = 'SATURN RINGS'

    if target_name == 'ATLAS:': # fix erroneous colon
        target_name = 'ATLAS'

    if target_name == 'IPH': # interplanetary?
        target_name = 'SOLAR WIND'

    # If there's a 2-letter target abbreviation present, then expand it into full name
    # Handle ME, PO, DA, etc. for Methone, Polydeuces, Daphnis, etc
    if target_name in CIMS_TARGET_ABBREVIATIONS:
        target_name = CIMS_TARGET_ABBREVIATIONS[target_name]

    # If the target name is NOT non-applicable, then insert target_name into target_keys
    if target_name != 'N/A':
        target_keys.add(target_name) # adds a (unique) element to the set. If an element already exists in the set, then it does not get added

    # Read the target name from the OBSERVATION_ID
    abbrev = ''
    obsname = ''
    if len(observation_id) > 3:
        try:
            # Perform string manipulation to pick out 2-letter CIMS ID abbreviation from obs id
            parts = observation_id.split('_')
            abbrev = parts[1][-2:]
            obsname = CIMS_TARGET_ABBREVIATIONS[abbrev] # Look up that 2-letter CIMS ID abbreviation in the CIMS dictionary
            # Don''t repeat a target if  there's more than one
            target_keys.add(obsname)
        except (KeyError, IndexError, ValueError):
            pass

    # Handle Cassini UVIS quirks
    # Include the rings if it appears in the purpose
    if ' rings' in purpose_str:
        target_keys.add('SATURN RINGS')# Because target_keys is a set, if 'SATURN RINGS' already present then it won't duplicate

    # Star IDs are encoded in the OBSERVATION_ID
    named_star_found = False # Initiate flag as off
    # Loop through the dictionary of star abbreviations 
    # If the key is found in the observation ID, then insert the name of that star to the target_keys set.
    for (key,value) in STAR_ABBREVS.items():
        if key in observation_id:
            target_keys.add(value[0])
            named_star_found = True # switch flag on

    # Handle 'STAR' - if a star's target name has been found, then we don't need a generic 'star'
    if 'STAR' in target_keys and named_star_found:
        target_keys.remove('STAR')

    if 'STAR' in target_keys: # print warning message if unknown star is in target_keys
        print('unknown star: %s %s %s' % (target_name, observation_id, filename))

    # Handle 'UNK' - if there are multiple entries in the target_keys set, then 'UNK' isn't adding any info, so remove it 
    if 'UNK' in target_keys:
        if len(target_keys) > 1:
            target_keys.remove('UNK')
        else: # If the only target found is "UNK", then print a warning message
            print('unknown target: %s %s %s' % (target_name, observation_id,
                                                filename))

    # If our set is not empty, we're done:
    if len(target_keys): 
        keys = list(target_keys) # convert set to list
        keys.sort()
        return [TARGET_DICT[k.upper()] for k in keys]

    print('unknown target: %s %s %s' % (target_name, observation_id, filename))

    return [('Unknown', [], 'Calibrator', 'N/A',
             'urn:nasa:pds:context:target:calibrator.unk')] # If reach the end and cannot find target, then return Unknown

def get_naif_id(alts):
    """Find the NAIF ID among the alt names for a target."""

    naif_id = 'N/A'
    for alt in alts:
        if alt.startswith('NAIF ID'):
            naif_id = int(alt[7:])

    return naif_id

################################################################################

PURPOSES = [
    ('RPWS'      , 'Science'    ),
    ('calibrat'  , 'Calibration'),
    ('Calibrat'  , 'Calibration'),
    ('flat-field', 'Calibration'),
    ('response'  , 'Calibration'),
    ('function'  , 'Calibration'),
    ('solar port', 'Calibration'),
    ('engineer'  , 'Engineering'),
    ('evaluate'  , 'Engineering'),
    ('EOM'       , 'Engineering'),
    ('warm'      , 'Engineering'),
]

def uvis_purpose(purpose_str, target_name):
    """Image purpose, one of Calibration, Checkout, Engineering, Navigation,
    Observation Geometry, or Science."""

    if target_name.upper().startswith('CALIB'):
        return 'Calibration'

    for (match, purpose) in PURPOSES:
        if match in purpose_str:
            return purpose

    return 'Science'       # Seems to be right for everything that's left

################################################################################

def write_uvis_pds4_label(datafile, pds3_label):

    # Read the PDS3 label and the VICAR header, fixing known syntax errors
    with open(pds3_label) as f:
        label_text = f.read()

    label_text = label_text.replace('\r','') # pyparsing is not set up for <CR>
    label = pdsparser.PdsLabel.from_string(label_text).as_dict()

    # Define the lookup dictionary
    lookup = label.copy()
    is_qube = ('QUBE' in label) # If 'QUBE' in label then is_qube is True, otherwise False
    lookup['is_qube'] = is_qube # Add this Boolean key to the lookup dictionary
    if is_qube:
        lookup.update(label['QUBE'])
        pds3_filename = label['^QUBE']
    elif ('SPECTRUM' in label):
        lookup.update(label['SPECTRUM'])
        pds3_filename = label['^SPECTRUM']
    else:
        lookup.update(label['TIME_SERIES'])
        pds3_filename = label['^TIME_SERIES']

    # Define all the derived quantities
    lookup['datafile'] = datafile
    basename = os.path.basename(datafile)
    lookup['basename'] = basename
    #inst = basename.split('_')[-1][:-4]
    inst = basename.split('_')[0][:-4] # Use modified filepath
    lookup['inst'] = inst

    desc = lookup['DESCRIPTION']
    k = desc.find('The purpose of this observation')
    if k < 0:
        purpose_str = ''
    else:
        purpose_str = desc[k:]
    lookup['purpose_str'] = purpose_str
    lookup['purpose'] = uvis_purpose(purpose_str, lookup['TARGET_NAME'])

    #observation_id = OBSERVATION_IDS[basename[:14]]
    observation_id = OBSERVATION_IDS[basename[3:-4]] # fix bug with basenames that include seconds ( _ss.dat)
    lookup['OBSERVATION_ID'] = observation_id

    # For EUV/FUV...
    if inst in ('euv', 'fuv'):

      # Find window(s)
      if 'UL_CORNER_SPATIAL' in lookup:
        lookup['UL_CORNER_LINE'] = [lookup['UL_CORNER_SPATIAL' ]]
        lookup['UL_CORNER_BAND'] = [lookup['UL_CORNER_SPECTRAL']]
        lookup['LR_CORNER_LINE'] = [lookup['LR_CORNER_SPATIAL' ]]
        lookup['LR_CORNER_BAND'] = [lookup['LR_CORNER_SPECTRAL']]
        lookup['BAND_BIN'] = [1]
        lookup['LINE_BIN'] = [1]

      if not isinstance(lookup['UL_CORNER_LINE'], list):
        lookup['UL_CORNER_LINE'] = [lookup['UL_CORNER_LINE']]
        lookup['UL_CORNER_BAND'] = [lookup['UL_CORNER_BAND']]
        lookup['LR_CORNER_LINE'] = [lookup['LR_CORNER_LINE']]
        lookup['LR_CORNER_BAND'] = [lookup['LR_CORNER_BAND']]
        lookup['BAND_BIN'] = [lookup['BAND_BIN']]
        lookup['LINE_BIN'] = [lookup['LINE_BIN']]

      # Locate the calibration file(s)
      lookup['calibration_files'] = []
      cal_flag = 0 # initialise switch to off
      for version in ('2','3','4','5'): # There are no v1 calibrations
        #calpath = (datafile.replace('data_raw_','calibration_data_')[:-8] +
        #           '_cal_' + version + datafile[-8:])
          calpath = (datafile.replace('data_raw','calibration')[:-4] + # [:-4] slices off '.dat'
                   '_cal_' + version + datafile[-4:]) # use modified filepath 

          if os.path.exists(calpath):
              lookup['calibration_files'].append(os.path.basename(calpath))
              cal_flag+=1
      if not cal_flag:
          print("No calibration files found for datafile:", datafile)


    # For HDAC, determine mode
    if inst == 'hdac':
        if sum(lookup['D_LEVEL']) + sum(lookup['H_LEVEL']) == 0:
            lookup['mode'] = 'photometer'
        else:
            lookup['mode'] = 'modulation'

    # For HDAC in modulation mode, count trailing zeros
    if inst == 'hdac':
      if lookup['mode'] == 'modulation':
        data = np.fromfile(datafile, dtype='uint16')
        nonzeros = len(data)
        while data[nonzeros-1] == 0:
            nonzeros -= 1

        zeros = len(data) - nonzeros
        if zeros:
            print('%d trailing HDAC zeros found:' % zeros, datafile)

        lookup['zeros'] = zeros
        lookup['nonzeros'] = nonzeros
      else:
        lookup['zeros'] = 0
        lookup['nonzeros'] = lookup['ROWS']

    # For HDAC, determine the duration
    if inst == 'hdac':
        lookup['duration'] = lookup['nonzeros'] * 0.125

    # For HSP, determine start time, reference time, duration
    if inst == 'hsp':
        texp = lookup['SAMPLING_PARAMETER_INTERVAL'] / 1000.
        lookup['texp'] = texp

        INIT_SCLKS()
        old_start_tai = julian.tai_from_iso(lookup['START_TIME']) - texp
        start_sclk = OLD_SCLK_FROM_TAI(old_start_tai)
        new_start_tai = NEW_TAI_FROM_SCLK(start_sclk)
        lookup['shift_secs'] = new_start_tai - old_start_tai

        stop_sclk = start_sclk + texp * lookup['ROWS']
        new_stop_tai = NEW_TAI_FROM_SCLK(stop_sclk)
        lookup['delta'] = (new_stop_tai - new_start_tai) / lookup['ROWS']

        lookup['new_start_tai'] = new_start_tai
        lookup['new_stop_tai'] = new_stop_tai
        lookup['start_sclk'] = start_sclk

    # Special care for target identifications
    target_info = uvis_target_info(label['TARGET_NAME'], observation_id,
                                   purpose_str, datafile)

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

    # Write the label
    labelfile = datafile[:-4] + '.xml'

    if inst in ('euv', 'fuv'):
        EUV_FUV_TEMPLATE.write(lookup, labelfile)
    elif inst == 'hdac':
        HDAC_TEMPLATE.write(lookup, labelfile)
    else:
        HSP_TEMPLATE.write(lookup, labelfile)

################################################################################
# Command line interface
################################################################################

def label1(pds4_file, replace=False):
    """Generate one label file, replacing a pre-existing one only if necessary.
    """

    try:
        pds4_file = os.path.abspath(pds4_file) # expands filename to be the whole path
        if not replace and os.path.exists(pds4_file[:-4] + '.xml'):
           print("Replace==False and file already exists: ", pds4_file[:-4] + '.xml')
           return

        parts = pds4_file.split('/data_raw') # split at bundle level
        print('data_raw' + parts[1]) #print everything after 'data_raw/'

        #pds3_label = pds4_file.replace( 'cassini_uvis_saturn', 'pds3-labels')
        pds3_label = pds4_file.replace( 'data_raw', 'raw_labels') # The PDS3 labels are in a parallel directory tree ('/raw_labels/') to the PDS4 data files ('/data_raw/')
        #pds3_label = pds3_label.replace('cassini_uvis_cruise', 'pds3-labels')
        pds3_label = pds3_label[:-4] + '.lbl'

        write_uvis_pds4_label(pds4_file, pds3_label)

    # A KeyboardInterrupt must stop the program
    except KeyboardInterrupt:
        sys.exit(1)

    # For any other exception, print an error message and keep going (produces a useful error log that helps with debugging)

    except Exception as e:
        print('*** error for: ', pds4_file)
        print(e)
        (etype, value, tb) = sys.exc_info()
        print(''.join(traceback.format_tb(tb)))

### MAIN PROGRAM

def main():

    # Get the command line args as a list
    args = sys.argv[1:] # The 0th element is the name of the script itself

    # Set the replace flag if it's in the argument list
    if '--replace' in args:
        replace = True
        args.remove('--replace')
    else:
        replace = False

    # Step through the args
    for arg in args:

        # Case 1: Label a single image (single filename rather than directory)
        if os.path.isfile(arg):
          if arg.endswith('.dat'):
            label1(arg, replace) 

        # Case 2: Label all the images in a directory tree, recursively
        elif os.path.isdir(arg):
          for root, dirs, files in os.walk(os.path.join(arg)):
            for name in files: # Loop over each file in directory
              if name.endswith('.dat'): # skips over anything that isn't .dat

                filename = os.path.join(root, name)
                label1(filename, replace)

if __name__ == '__main__': main()

################################################################################
