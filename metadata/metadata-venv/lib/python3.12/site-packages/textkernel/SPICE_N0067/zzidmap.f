C$Procedure ZZIDMAP ( Private --- SPICE body ID/name assignments )

      SUBROUTINE  ZZIDMAP( BLTCOD, BLTNAM )

C$ Abstract
C
C     The default SPICE body/ID mapping assignments available
C     to the SPICE library.
C
C$ Disclaimer
C
C     THIS SOFTWARE AND ANY RELATED MATERIALS WERE CREATED BY THE
C     CALIFORNIA INSTITUTE OF TECHNOLOGY (CALTECH) UNDER A U.S.
C     GOVERNMENT CONTRACT WITH THE NATIONAL AERONAUTICS AND SPACE
C     ADMINISTRATION (NASA). THE SOFTWARE IS TECHNOLOGY AND SOFTWARE
C     PUBLICLY AVAILABLE UNDER U.S. EXPORT LAWS AND IS PROVIDED "AS-IS"
C     TO THE RECIPIENT WITHOUT WARRANTY OF ANY KIND, INCLUDING ANY
C     WARRANTIES OF PERFORMANCE OR MERCHANTABILITY OR FITNESS FOR A
C     PARTICULAR USE OR PURPOSE (AS SET FORTH IN UNITED STATES UCC
C     SECTIONS 2312-2313) OR FOR ANY PURPOSE WHATSOEVER, FOR THE
C     SOFTWARE AND RELATED MATERIALS, HOWEVER USED.
C
C     IN NO EVENT SHALL CALTECH, ITS JET PROPULSION LABORATORY, OR NASA
C     BE LIABLE FOR ANY DAMAGES AND/OR COSTS, INCLUDING, BUT NOT
C     LIMITED TO, INCIDENTAL OR CONSEQUENTIAL DAMAGES OF ANY KIND,
C     INCLUDING ECONOMIC DAMAGE OR INJURY TO PROPERTY AND LOST PROFITS,
C     REGARDLESS OF WHETHER CALTECH, JPL, OR NASA BE ADVISED, HAVE
C     REASON TO KNOW, OR, IN FACT, SHALL KNOW OF THE POSSIBILITY.
C
C     RECIPIENT BEARS ALL RISK RELATING TO QUALITY AND PERFORMANCE OF
C     THE SOFTWARE AND ANY RELATED MATERIALS, AND AGREES TO INDEMNIFY
C     CALTECH AND NASA FOR ALL THIRD-PARTY CLAIMS RESULTING FROM THE
C     ACTIONS OF RECIPIENT IN THE USE OF THE SOFTWARE.
C
C$ Required_Reading
C
C     NAIF_IDS
C
C$ Keywords
C
C     BODY MAPPINGS
C
C$ Declarations

      IMPLICIT NONE

      INCLUDE              'zzbodtrn.inc'

      INTEGER              BLTCOD(NPERM)
      CHARACTER*(MAXL)     BLTNAM(NPERM)

C$ Brief_I/O
C
C     VARIABLE  I/O  DESCRIPTION
C     --------  ---  --------------------------------------------------
C     BLTCOD     O   List of default integer ID codes.
C     BLTNAM     O   List of default names.
C     NPERM      P   Number of name/ID mappings.
C
C$ Detailed_Input
C
C     None.
C
C$ Detailed_Output
C
C     BLTCOD   The array of NPERM elements listing the body ID codes.
C
C     BLTNAM   The array of NPERM elements listing the body names
C              corresponding to the ID entry in BLTCOD
C
C$ Parameters
C
C     NPERM    The length of both BLTCOD, BLTNAM
C              (read from zzbodtrn.inc).
C
C$ Exceptions
C
C     None.
C
C$ Files
C
C     None.
C
C$ Particulars
C
C     Each ith entry of BLTCOD maps to the ith entry of BLTNAM.
C
C$ Examples
C
C     Simple to use, a call the ZZIDMAP returns the arrays defining the
C     name/ID mappings.
C
C
C        INCLUDE            'zzbodtrn.inc'
C
C        INTEGER             ID  ( NPERM )
C        CHARACTER*(MAXL)    NAME( NPERM )
C
C        CALL ZZIDMAP( ID, NAME )
C
C$ Restrictions
C
C     None.
C
C$ Literature_References
C
C     None.
C
C$ Author_and_Institution
C
C     E.D. Wright, 10-DEC-2021 (JPL)
C
C$ Version
C
C-    SPICELIB Version 1.0.10, 10-DEC-2021 (EDW) (JDR) (BVS)
C
C        Added:
C
C             -652   MERCURY TRANSFER MODULE
C             -652   MTM
C             -652   BEPICOLOMBO MTM
C             -255   PSYC
C             -243   VIPER
C             -242   LUNAR TRAILBLAZER
C             -240   SMART LANDER FOR INVESTIGATING MOON
C             -240   SLIM
C             -239   MARTIAN MOONS EXPLORATION
C             -239   MMX
C             -210   LICIA
C             -210   LICIACUBE
C             -197   EXOMARS_LARA
C             -197   LARA
C             -174   EXM RSP RM
C             -174   EXM ROVER
C             -174   EXOMARS ROVER
C             -173   EXM RSP SP
C             -173   EXM SURFACE PLATFORM
C             -173   EXOMARS SP
C             -172   EXM RSP SCC
C             -172   EXM SPACECRAFT COMPOSITE
C             -172   EXOMARS SCC
C             -168   PERSEVERANCE
C             -168   MARS 2020
C             -168   MARS2020
C             -168   M2020
C             -164   LUNAR FLASHLIGHT
C             -156   ADITYA
C             -156   ADIT
C             -155   KPLO
C             -155   KOREAN PATHFINDER LUNAR ORBITER
C             -153   CH2L
C             -153   CHANDRAYAAN-2 LANDER
C             -148   DFLY
C             -148   DRAGONFLY
C             -135   DART
C             -135   DOUBLE ASTEROID REDIRECTION TEST
C             -119   MARS_ORBITER_MISSION_2
C             -119   MOM2
C              -96   PARKER SOLAR PROBE
C              -72   JNSB
C              -72   JANUS_B
C              -57   LUNAR ICECUBE
C              -45   JNSA
C              -45   JANUS_A
C              -43   IMAP
C              -39   LUNAR POLAR HYDROGEN MAPPER
C              -39   LUNAH-MAP
C              -37   HYB2
C              -37   HAYABUSA 2
C              -37   HAYABUSA2
C              -33   NEOS
C              -33   NEO SURVEYOR
C           399035   DSS-35
C           399036   DSS-36
C           399056   DSS-56
C           399069   DSS-69
C          2000052   52_EUROPA
C          2000052   52 EUROPA
C          2162173   RYUGU
C          2486958   ARROKOTH
C         20000617   PATROCLUS_BARYCENTER
C         20000617   PATROCLUS BARYCENTER
C         20003548   EURYBATES_BARYCENTER
C         20003548   EURYBATES BARYCENTER
C         20011351   LEUCUS
C         20015094   POLYMELE
C         20021900   ORUS
C         20052246   DONALDJOHANSON
C         20065803   DIDYMOS_BARYCENTER
C         20065803   DIDYMOS BARYCENTER
C        120000617   MENOETIUS
C        120003548   QUETA
C        120065803   DIMORPHOS
C        920000617   PATROCLUS
C        920003548   EURYBATES
C        920065803   DIDYMOS
C
C        Modified assignments
C
C             -152   CH2O
C             -152   CHANDRAYAAN-2 ORBITER
C
C        Removed assignments
C
C             -164   YOHKOH
C             -164   SOLAR-A
C             -135   DRTS-W
C              -69   PSYC
C              -54   ASTEROID RETRIEVAL MISSION
C              -54   ARM
C
C        Reimplemented spelling change:
C
C           MAGACLITE to MEGACLITE
C
C        Edited the header to comply with NAIF standard.
C
C-    SPICELIB Version 1.0.9, 04-APR-2017 (EDW)
C
C        Added information stating the frames subsystem performs
C        frame ID-name mappings and the DSK subsystem performs
C        surface ID-name mappings.
C
C        Edited body/ID assignment format to indicate whitespace
C        between 'NAME' and Comments.
C
C        Added:
C
C             -302   HELIOS 2
C             -301   HELIOS 1
C             -198   NASA-ISRO SAR MISSION
C             -198   NISAR
C             -159   EURC
C             -159   EUROPA CLIPPER
C             -152   CH2
C             -152   CHANDRAYAAN-2
C             -143   TRACE GAS ORBITER
C             -143   TGO
C             -143   EXOMARS 2016 TGO
C             -117   EDL DEMONSTRATOR MODULE
C             -117   EDM
C             -117   EXOMARS 2016 EDM
C              -76   CURIOSITY
C              -69   PSYC
C              -66   MCOB
C              -66   MARCO-B
C              -65   MCOA
C              -65   MARCO-A
C              -62   EMM
C              -62   EMIRATES MARS MISSION
C              -49   LUCY
C              -28   JUPITER ICY MOONS EXPLORER
C              -28   JUICE
C              553   DIA
C          2000016   PSYCHE
C          2101955   BENNU
C
C        Removed assignments:
C
C             -159   EUROPA ORBITER
C              -69   MPO
C              -69   MERCURY PLANETARY ORBITER
C
C        Modified assignments
C
C             -121   MERCURY PLANETARY ORBITER
C             -121   MPO
C             -121   BEPICOLOMBO MPO
C              -68   MERCURY MAGNETOSPHERIC ORBITER
C              -68   MMO
C              -68   BEPICOLOMBO MMO
C
C-    SPICELIB Version 1.0.8, 06-MAY-2014 (EDW)
C
C        Edited text comments in Asteroids section and Comets section.
C
C        Eliminated "PI" IAU Number from "CHARON" description.
C
C        HYROKKIN (644) spelling corrected to HYRROKKIN.
C
C        Added:
C
C             -750   SPRINT-AS
C             -189   NSYT
C             -189   INSIGHT
C             -170   JWST
C             -170   JAMES WEBB SPACE TELESCOPE
C             -144   SOLO
C             -144   SOLAR ORBITER
C              -96   SPP
C              -96   SOLAR PROBE PLUS
C              -64   ORX
C              -64   OSIRIS-REX
C              -54   ARM
C              -54   ASTEROID RETRIEVAL MISSION
C              -12   LADEE
C               -3   MOM
C               -3   MARS ORBITER MISSION
C                0   SOLAR_SYSTEM_BARYCENTER
C                1   MERCURY_BARYCENTER
C                2   VENUS_BARYCENTER
C                3   EARTH_BARYCENTER
C                4   MARS_BARYCENTER
C                5   JUPITER_BARYCENTER
C                6   SATURN_BARYCENTER
C                7   URANUS_BARYCENTER
C                8   NEPTUNE_BARYCENTER
C                9   PLUTO_BARYCENTER
C              644   HYRROKKIN
C              904   KERBEROS
C              905   STYX
C          1003228   C/2013 A1
C          1003228   SIDING SPRING
C          2000002   PALLAS
C          2000511   DAVIDA
C
C        Removed assignments:
C
C             -486   HERSCHEL
C             -489   PLANCK
C             -187   SOLAR PROBE
C
C-    SPICELIB Version 1.0.7, 20-MAY-2010 (EDW)
C
C        Edit to vehicle ID list to correct -76 not in proper
C        numerical (descending) order.
C
C        Added:
C
C               -5   AKATSUKI
C               -5   VCO
C             -121   BEPICOLOMBO
C             -177   GRAIL-A
C             -181   GRAIL-B
C             -202   MAVEN
C             -205   SOIL MOISTURE ACTIVE AND PASSIVE
C             -205   SMAP
C             -362   RADIATION BELT STORM PROBE A
C             -362   RBSP_A
C             -363   RADIATION BELT STORM PROBE B
C             -363   RBSP_B
C              550   HERSE
C              653   AEGAEON
C          1000093   TEMPEL_1
C          2000021   LUTETIA
C          2004179   TOUTATIS
C
C-    SPICELIB Version 1.0.6, 08-APR-2009 (EDW)
C
C        Added:
C
C               -5   PLC
C               -5   PLANET-C
C              -68   MMO
C              -68   MERCURY MAGNETOSPHERIC ORBITER
C              -69   MPO
C              -69   MERCURY PLANETARY ORBITER
C          2002867   STEINS
C             -140   EPOCH
C             -140   DIXI
C
C-    SPICELIB Version 1.0.5, 09-JAN-2008 (EDW)
C
C        Added:
C
C              -18   LCROSS
C              -29   NEXT
C              -86   CH1
C              -86   CHANDRAYAAN-1
C             -131   KAGUYA
C             -140   EPOXI
C             -151   CHANDRA
C             -187   SOLAR PROBE
C              636   AEGIR
C              637   BEBHIONN
C              638   BERGELMIR
C              639   BESTLA
C              640   FARBAUTI
C              641   FENRIR
C              642   FORNJOT
C              643   HATI
C              644   HYROKKIN
C              645   KARI
C              646   LOGE
C              647   SKOLL
C              648   SURTUR
C              649   ANTHE
C              650   JARNSAXA
C              651   GREIP
C              652   TARQEQ
C              809   HALIMEDE
C              810   PSAMATHE
C              811   SAO
C              812   LAOMEDEIA
C              813   NESO
C
C        NAIF modified the Jovian system listing to conform to the
C        current (as of this date) name/body mapping.
C
C              540   MNEME
C              541   AOEDE
C              542   THELXINOE
C              543   ARCHE
C              544   KALLICHORE
C              545   HELIKE
C              546   CARPO
C              547   EUKELADE
C              548   CYLLENE
C              549   KORE
C
C        Removed assignments:
C
C             -172   SPACETECH-3 COMBINER
C             -174   PLUTO-KUIPER EXPRESS
C             -175   PLUTO-KUIPER EXPRESS SIMULATION
C             -205   SPACETECH-3 COLLECTOR
C              514   1979J2
C              515   1979J1
C              516   1979J3
C              610   1980S1
C              611   1980S3
C              612   1980S6
C              613   1980S13
C              614   1980S25
C              615   1980S28
C              616   1980S27
C              617   1980S26
C              706   1986U7
C              707   1986U8
C              708   1986U9
C              709   1986U4
C              710   1986U6
C              711   1986U3
C              712   1986U1
C              713   1986U2
C              714   1986U5
C              715   1985U1
C              718   1986U10
C              901   1978P1
C
C        Spelling correction:
C
C           MAGACLITE to MEGACLITE
C
C        Rename:
C
C           ERRIAPO to ERRIAPUS
C           STV-1 to STV51
C           STV-2 to STV52
C           STV-3 to STV53
C
C
C-    SPICELIB Version 1.0.4, 01-NOV-2006 (EDW)
C
C        NAIF removed several provisional name/ID mappings from
C        the Jovian system listing:
C
C           539         'HEGEMONE'              JXXXIX
C           540         'MNEME'                 JXL
C           541         'AOEDE'                 JXLI
C           542         'THELXINOE'             JXLII
C           543         'ARCHE'                 JXLIII
C           544         'KALLICHORE'            JXLIV
C           545         'HELIKE'                JXLV
C           546         'CARPO'                 JXLVI
C           547         'EUKELADE'              JXLVII
C           548         'CYLLENE'               JXLVIII
C
C        The current mapping set for the range 539-561:
C
C              540   ARCHE
C              541   EUKELADE
C              546   HELIKE
C              547   AOEDE
C              548   HEGEMONE
C              551   KALLICHORE
C              553   CYLLENE
C              560   CARPO
C              561   MNEME
C
C        The new mapping leaves the IDs 539, 542-545, 549, 550, 552,
C        554-559 unassigned.
C
C        Added:
C
C              635   DAPHNIS
C              722   FRANCISCO
C              723   MARGARET
C              724   FERDINAND
C              725   PERDITA
C              726   MAB
C              727   CUPID
C              -61   JUNO
C              -76   MSL
C              -76   MARS SCIENCE LABORATORY
C             -212   STV-1
C             -213   STV-2
C             -214   STV-3
C              902   NIX
C              903   HYDRA
C             -85    LRO
C             -85    LUNAR RECON ORBITER
C             -85    LUNAR RECONNAISSANCE ORBITER
C
C        Spelling correction
C
C              632   METHODE to METHONE
C
C-    SPICELIB Version 1.0.3, 14-NOV-2005 (EDW)
C
C        Added:
C
C              539   HEGEMONE
C              540   MNEME
C              541   AOEDE
C              542   THELXINOE
C              543   ARCHE
C              544   KALLICHORE
C              545   HELIKE
C              546   CARPO
C              547   EUKELADE
C              548   CYLLENE
C              631   NARVI
C              632   METHODE
C              633   PALLENE
C              634   POLYDEUCES
C          2025143   ITOKAWA
C              -98   NEW HORIZONS
C             -248   VENUS EXPRESS, VEX
C             -500   RSAT, SELENE Relay Satellite, SELENE Rstar, Rstar
C             -502   VSAT, SELENE VLBI Radio Satellite,
C                    SELENE VRAD Satellite, SELENE Vstar
C           399064   DSS-64
C
C        Change in spelling:
C
C              623   SUTTUNG to SUTTUNGR
C              627   SKADI   to SKATHI
C              630   THRYM   to THRYMR
C
C-    SPICELIB Version 1.0.2, 20-DEC-2004 (EDW)
C
C        Edited parse code to correctly process embedded
C        parentheses in a body name.
C
C        Added:
C
C           Due to the previous definition of Parkes with DSS-05,
C           the Parkes ID remains 399005.
C
C             -486   HERSCHEL
C             -489   PLANCK
C           399049   DSS-49
C           399055   DSS-55
C             -203   DAWN
C          1000012   67P/CHURYUMOV-GERASIMENKO (1969 R1)
C          1000012   CHURYUMOV-GERASIMENKO
C          398989    NOTO
C             -84    PHOENIX
C            -131    SELENE
C            -238    SMART-1, S1, SM1, SMART1
C            -130    HAYABUSA
C
C-    SPICELIB Version 1.0.1, 19-DEC-2003 (EDW)
C
C        Added:
C              -79   SPITZER
C          2000216   KLEOPATRA
C
C-    SPICELIB Version 1.0.0, 27-JUL-2003 (EDW)
C
C        Added:
C              -47   GNS
C              -74   MRO
C              -74   MARS RECON ORBITER
C             -130   MUSES-C
C             -142   TERRA
C             -154   AQUA
C             -159   EUROPA ORBITER
C             -190   SIM
C             -198   INTEGRAL
C             -227   KEPLER
C             -234   STEREO AHEAD
C             -235   STEREO BEHIND
C             -253   OPPORTUNITY
C             -254   SPIRIT
C              528   AUTONOE
C              529   THYONE
C              530   HERMIPPE
C              531   AITNE
C              532   EURYDOME
C              533   EUANTHE
C              534   EUPORIE
C              535   ORTHOSIE
C              536   SPONDE
C              537   KALE
C              538   PASITHEE
C              619   YMIR
C              620   PAALIAQ
C              621   TARVOS
C              622   IJIRAQ
C              623   SUTTUNG
C              624   KIVIUQ
C              625   MUNDILFARI
C              626   ALBIORIX
C              627   SKADI
C              628   ERRIAPO
C              629   SIARNAQ
C              630   THRYM
C              718   PROSPERO
C              719   SETEBOS
C              720   STEPHANO
C              721   TRINCULO
C           398990   NEW NORCIA
C          2431011   DACTYL
C          2000001   CERES
C          2000004   VESTA
C
C        Renamed:
C
C              -25   LPM to
C              -25   LP
C
C             -180   MUSES-C to
C             -130   MUSES-B
C
C             -172   STARLIGHT COMBINER to
C             -172   SPACETECH-3 COMBINER
C
C             -205   STARLIGHT COLLECTOR to
C             -205   SPACETECH-3 COLLECTOR
C
C        Removed:
C             -172   SLCOMB
C
C
C-&

C$ Index_Entries
C
C     body ID mapping
C
C-&

C
C     A script generates this file. Do not edit by hand.
C     Edit the creation script to modify the contents of
C     ZZIDMAP.
C

      BLTCOD(1) =   0
      BLTNAM(1) =  'SOLAR_SYSTEM_BARYCENTER'

      BLTCOD(2) =   0
      BLTNAM(2) =  'SSB'

      BLTCOD(3) =   0
      BLTNAM(3) =  'SOLAR SYSTEM BARYCENTER'

      BLTCOD(4) =   1
      BLTNAM(4) =  'MERCURY_BARYCENTER'

      BLTCOD(5) =   1
      BLTNAM(5) =  'MERCURY BARYCENTER'

      BLTCOD(6) =   2
      BLTNAM(6) =  'VENUS_BARYCENTER'

      BLTCOD(7) =   2
      BLTNAM(7) =  'VENUS BARYCENTER'

      BLTCOD(8) =   3
      BLTNAM(8) =  'EARTH_BARYCENTER'

      BLTCOD(9) =   3
      BLTNAM(9) =  'EMB'

      BLTCOD(10) =   3
      BLTNAM(10) =  'EARTH MOON BARYCENTER'

      BLTCOD(11) =   3
      BLTNAM(11) =  'EARTH-MOON BARYCENTER'

      BLTCOD(12) =   3
      BLTNAM(12) =  'EARTH BARYCENTER'

      BLTCOD(13) =   4
      BLTNAM(13) =  'MARS_BARYCENTER'

      BLTCOD(14) =   4
      BLTNAM(14) =  'MARS BARYCENTER'

      BLTCOD(15) =   5
      BLTNAM(15) =  'JUPITER_BARYCENTER'

      BLTCOD(16) =   5
      BLTNAM(16) =  'JUPITER BARYCENTER'

      BLTCOD(17) =   6
      BLTNAM(17) =  'SATURN_BARYCENTER'

      BLTCOD(18) =   6
      BLTNAM(18) =  'SATURN BARYCENTER'

      BLTCOD(19) =   7
      BLTNAM(19) =  'URANUS_BARYCENTER'

      BLTCOD(20) =   7
      BLTNAM(20) =  'URANUS BARYCENTER'

      BLTCOD(21) =   8
      BLTNAM(21) =  'NEPTUNE_BARYCENTER'

      BLTCOD(22) =   8
      BLTNAM(22) =  'NEPTUNE BARYCENTER'

      BLTCOD(23) =   9
      BLTNAM(23) =  'PLUTO_BARYCENTER'

      BLTCOD(24) =   9
      BLTNAM(24) =  'PLUTO BARYCENTER'

      BLTCOD(25) =   10
      BLTNAM(25) =  'SUN'

      BLTCOD(26) =   199
      BLTNAM(26) =  'MERCURY'

      BLTCOD(27) =   299
      BLTNAM(27) =  'VENUS'

      BLTCOD(28) =   399
      BLTNAM(28) =  'EARTH'

      BLTCOD(29) =   301
      BLTNAM(29) =  'MOON'

      BLTCOD(30) =   499
      BLTNAM(30) =  'MARS'

      BLTCOD(31) =   401
      BLTNAM(31) =  'PHOBOS'

      BLTCOD(32) =   402
      BLTNAM(32) =  'DEIMOS'

      BLTCOD(33) =   599
      BLTNAM(33) =  'JUPITER'

      BLTCOD(34) =   501
      BLTNAM(34) =  'IO'

      BLTCOD(35) =   502
      BLTNAM(35) =  'EUROPA'

      BLTCOD(36) =   503
      BLTNAM(36) =  'GANYMEDE'

      BLTCOD(37) =   504
      BLTNAM(37) =  'CALLISTO'

      BLTCOD(38) =   505
      BLTNAM(38) =  'AMALTHEA'

      BLTCOD(39) =   506
      BLTNAM(39) =  'HIMALIA'

      BLTCOD(40) =   507
      BLTNAM(40) =  'ELARA'

      BLTCOD(41) =   508
      BLTNAM(41) =  'PASIPHAE'

      BLTCOD(42) =   509
      BLTNAM(42) =  'SINOPE'

      BLTCOD(43) =   510
      BLTNAM(43) =  'LYSITHEA'

      BLTCOD(44) =   511
      BLTNAM(44) =  'CARME'

      BLTCOD(45) =   512
      BLTNAM(45) =  'ANANKE'

      BLTCOD(46) =   513
      BLTNAM(46) =  'LEDA'

      BLTCOD(47) =   514
      BLTNAM(47) =  'THEBE'

      BLTCOD(48) =   515
      BLTNAM(48) =  'ADRASTEA'

      BLTCOD(49) =   516
      BLTNAM(49) =  'METIS'

      BLTCOD(50) =   517
      BLTNAM(50) =  'CALLIRRHOE'

      BLTCOD(51) =   518
      BLTNAM(51) =  'THEMISTO'

      BLTCOD(52) =   519
      BLTNAM(52) =  'MEGACLITE'

      BLTCOD(53) =   520
      BLTNAM(53) =  'TAYGETE'

      BLTCOD(54) =   521
      BLTNAM(54) =  'CHALDENE'

      BLTCOD(55) =   522
      BLTNAM(55) =  'HARPALYKE'

      BLTCOD(56) =   523
      BLTNAM(56) =  'KALYKE'

      BLTCOD(57) =   524
      BLTNAM(57) =  'IOCASTE'

      BLTCOD(58) =   525
      BLTNAM(58) =  'ERINOME'

      BLTCOD(59) =   526
      BLTNAM(59) =  'ISONOE'

      BLTCOD(60) =   527
      BLTNAM(60) =  'PRAXIDIKE'

      BLTCOD(61) =   528
      BLTNAM(61) =  'AUTONOE'

      BLTCOD(62) =   529
      BLTNAM(62) =  'THYONE'

      BLTCOD(63) =   530
      BLTNAM(63) =  'HERMIPPE'

      BLTCOD(64) =   531
      BLTNAM(64) =  'AITNE'

      BLTCOD(65) =   532
      BLTNAM(65) =  'EURYDOME'

      BLTCOD(66) =   533
      BLTNAM(66) =  'EUANTHE'

      BLTCOD(67) =   534
      BLTNAM(67) =  'EUPORIE'

      BLTCOD(68) =   535
      BLTNAM(68) =  'ORTHOSIE'

      BLTCOD(69) =   536
      BLTNAM(69) =  'SPONDE'

      BLTCOD(70) =   537
      BLTNAM(70) =  'KALE'

      BLTCOD(71) =   538
      BLTNAM(71) =  'PASITHEE'

      BLTCOD(72) =   539
      BLTNAM(72) =  'HEGEMONE'

      BLTCOD(73) =   540
      BLTNAM(73) =  'MNEME'

      BLTCOD(74) =   541
      BLTNAM(74) =  'AOEDE'

      BLTCOD(75) =   542
      BLTNAM(75) =  'THELXINOE'

      BLTCOD(76) =   543
      BLTNAM(76) =  'ARCHE'

      BLTCOD(77) =   544
      BLTNAM(77) =  'KALLICHORE'

      BLTCOD(78) =   545
      BLTNAM(78) =  'HELIKE'

      BLTCOD(79) =   546
      BLTNAM(79) =  'CARPO'

      BLTCOD(80) =   547
      BLTNAM(80) =  'EUKELADE'

      BLTCOD(81) =   548
      BLTNAM(81) =  'CYLLENE'

      BLTCOD(82) =   549
      BLTNAM(82) =  'KORE'

      BLTCOD(83) =   550
      BLTNAM(83) =  'HERSE'

      BLTCOD(84) =   553
      BLTNAM(84) =  'DIA'

      BLTCOD(85) =   699
      BLTNAM(85) =  'SATURN'

      BLTCOD(86) =   601
      BLTNAM(86) =  'MIMAS'

      BLTCOD(87) =   602
      BLTNAM(87) =  'ENCELADUS'

      BLTCOD(88) =   603
      BLTNAM(88) =  'TETHYS'

      BLTCOD(89) =   604
      BLTNAM(89) =  'DIONE'

      BLTCOD(90) =   605
      BLTNAM(90) =  'RHEA'

      BLTCOD(91) =   606
      BLTNAM(91) =  'TITAN'

      BLTCOD(92) =   607
      BLTNAM(92) =  'HYPERION'

      BLTCOD(93) =   608
      BLTNAM(93) =  'IAPETUS'

      BLTCOD(94) =   609
      BLTNAM(94) =  'PHOEBE'

      BLTCOD(95) =   610
      BLTNAM(95) =  'JANUS'

      BLTCOD(96) =   611
      BLTNAM(96) =  'EPIMETHEUS'

      BLTCOD(97) =   612
      BLTNAM(97) =  'HELENE'

      BLTCOD(98) =   613
      BLTNAM(98) =  'TELESTO'

      BLTCOD(99) =   614
      BLTNAM(99) =  'CALYPSO'

      BLTCOD(100) =   615
      BLTNAM(100) =  'ATLAS'

      BLTCOD(101) =   616
      BLTNAM(101) =  'PROMETHEUS'

      BLTCOD(102) =   617
      BLTNAM(102) =  'PANDORA'

      BLTCOD(103) =   618
      BLTNAM(103) =  'PAN'

      BLTCOD(104) =   619
      BLTNAM(104) =  'YMIR'

      BLTCOD(105) =   620
      BLTNAM(105) =  'PAALIAQ'

      BLTCOD(106) =   621
      BLTNAM(106) =  'TARVOS'

      BLTCOD(107) =   622
      BLTNAM(107) =  'IJIRAQ'

      BLTCOD(108) =   623
      BLTNAM(108) =  'SUTTUNGR'

      BLTCOD(109) =   624
      BLTNAM(109) =  'KIVIUQ'

      BLTCOD(110) =   625
      BLTNAM(110) =  'MUNDILFARI'

      BLTCOD(111) =   626
      BLTNAM(111) =  'ALBIORIX'

      BLTCOD(112) =   627
      BLTNAM(112) =  'SKATHI'

      BLTCOD(113) =   628
      BLTNAM(113) =  'ERRIAPUS'

      BLTCOD(114) =   629
      BLTNAM(114) =  'SIARNAQ'

      BLTCOD(115) =   630
      BLTNAM(115) =  'THRYMR'

      BLTCOD(116) =   631
      BLTNAM(116) =  'NARVI'

      BLTCOD(117) =   632
      BLTNAM(117) =  'METHONE'

      BLTCOD(118) =   633
      BLTNAM(118) =  'PALLENE'

      BLTCOD(119) =   634
      BLTNAM(119) =  'POLYDEUCES'

      BLTCOD(120) =   635
      BLTNAM(120) =  'DAPHNIS'

      BLTCOD(121) =   636
      BLTNAM(121) =  'AEGIR'

      BLTCOD(122) =   637
      BLTNAM(122) =  'BEBHIONN'

      BLTCOD(123) =   638
      BLTNAM(123) =  'BERGELMIR'

      BLTCOD(124) =   639
      BLTNAM(124) =  'BESTLA'

      BLTCOD(125) =   640
      BLTNAM(125) =  'FARBAUTI'

      BLTCOD(126) =   641
      BLTNAM(126) =  'FENRIR'

      BLTCOD(127) =   642
      BLTNAM(127) =  'FORNJOT'

      BLTCOD(128) =   643
      BLTNAM(128) =  'HATI'

      BLTCOD(129) =   644
      BLTNAM(129) =  'HYRROKKIN'

      BLTCOD(130) =   645
      BLTNAM(130) =  'KARI'

      BLTCOD(131) =   646
      BLTNAM(131) =  'LOGE'

      BLTCOD(132) =   647
      BLTNAM(132) =  'SKOLL'

      BLTCOD(133) =   648
      BLTNAM(133) =  'SURTUR'

      BLTCOD(134) =   649
      BLTNAM(134) =  'ANTHE'

      BLTCOD(135) =   650
      BLTNAM(135) =  'JARNSAXA'

      BLTCOD(136) =   651
      BLTNAM(136) =  'GREIP'

      BLTCOD(137) =   652
      BLTNAM(137) =  'TARQEQ'

      BLTCOD(138) =   653
      BLTNAM(138) =  'AEGAEON'

      BLTCOD(139) =   799
      BLTNAM(139) =  'URANUS'

      BLTCOD(140) =   701
      BLTNAM(140) =  'ARIEL'

      BLTCOD(141) =   702
      BLTNAM(141) =  'UMBRIEL'

      BLTCOD(142) =   703
      BLTNAM(142) =  'TITANIA'

      BLTCOD(143) =   704
      BLTNAM(143) =  'OBERON'

      BLTCOD(144) =   705
      BLTNAM(144) =  'MIRANDA'

      BLTCOD(145) =   706
      BLTNAM(145) =  'CORDELIA'

      BLTCOD(146) =   707
      BLTNAM(146) =  'OPHELIA'

      BLTCOD(147) =   708
      BLTNAM(147) =  'BIANCA'

      BLTCOD(148) =   709
      BLTNAM(148) =  'CRESSIDA'

      BLTCOD(149) =   710
      BLTNAM(149) =  'DESDEMONA'

      BLTCOD(150) =   711
      BLTNAM(150) =  'JULIET'

      BLTCOD(151) =   712
      BLTNAM(151) =  'PORTIA'

      BLTCOD(152) =   713
      BLTNAM(152) =  'ROSALIND'

      BLTCOD(153) =   714
      BLTNAM(153) =  'BELINDA'

      BLTCOD(154) =   715
      BLTNAM(154) =  'PUCK'

      BLTCOD(155) =   716
      BLTNAM(155) =  'CALIBAN'

      BLTCOD(156) =   717
      BLTNAM(156) =  'SYCORAX'

      BLTCOD(157) =   718
      BLTNAM(157) =  'PROSPERO'

      BLTCOD(158) =   719
      BLTNAM(158) =  'SETEBOS'

      BLTCOD(159) =   720
      BLTNAM(159) =  'STEPHANO'

      BLTCOD(160) =   721
      BLTNAM(160) =  'TRINCULO'

      BLTCOD(161) =   722
      BLTNAM(161) =  'FRANCISCO'

      BLTCOD(162) =   723
      BLTNAM(162) =  'MARGARET'

      BLTCOD(163) =   724
      BLTNAM(163) =  'FERDINAND'

      BLTCOD(164) =   725
      BLTNAM(164) =  'PERDITA'

      BLTCOD(165) =   726
      BLTNAM(165) =  'MAB'

      BLTCOD(166) =   727
      BLTNAM(166) =  'CUPID'

      BLTCOD(167) =   899
      BLTNAM(167) =  'NEPTUNE'

      BLTCOD(168) =   801
      BLTNAM(168) =  'TRITON'

      BLTCOD(169) =   802
      BLTNAM(169) =  'NEREID'

      BLTCOD(170) =   803
      BLTNAM(170) =  'NAIAD'

      BLTCOD(171) =   804
      BLTNAM(171) =  'THALASSA'

      BLTCOD(172) =   805
      BLTNAM(172) =  'DESPINA'

      BLTCOD(173) =   806
      BLTNAM(173) =  'GALATEA'

      BLTCOD(174) =   807
      BLTNAM(174) =  'LARISSA'

      BLTCOD(175) =   808
      BLTNAM(175) =  'PROTEUS'

      BLTCOD(176) =   809
      BLTNAM(176) =  'HALIMEDE'

      BLTCOD(177) =   810
      BLTNAM(177) =  'PSAMATHE'

      BLTCOD(178) =   811
      BLTNAM(178) =  'SAO'

      BLTCOD(179) =   812
      BLTNAM(179) =  'LAOMEDEIA'

      BLTCOD(180) =   813
      BLTNAM(180) =  'NESO'

      BLTCOD(181) =   999
      BLTNAM(181) =  'PLUTO'

      BLTCOD(182) =   901
      BLTNAM(182) =  'CHARON'

      BLTCOD(183) =   902
      BLTNAM(183) =  'NIX'

      BLTCOD(184) =   903
      BLTNAM(184) =  'HYDRA'

      BLTCOD(185) =   904
      BLTNAM(185) =  'KERBEROS'

      BLTCOD(186) =   905
      BLTNAM(186) =  'STYX'

      BLTCOD(187) =   -1
      BLTNAM(187) =  'GEOTAIL'

      BLTCOD(188) =   -3
      BLTNAM(188) =  'MOM'

      BLTCOD(189) =   -3
      BLTNAM(189) =  'MARS ORBITER MISSION'

      BLTCOD(190) =   -5
      BLTNAM(190) =  'AKATSUKI'

      BLTCOD(191) =   -5
      BLTNAM(191) =  'VCO'

      BLTCOD(192) =   -5
      BLTNAM(192) =  'PLC'

      BLTCOD(193) =   -5
      BLTNAM(193) =  'PLANET-C'

      BLTCOD(194) =   -6
      BLTNAM(194) =  'P6'

      BLTCOD(195) =   -6
      BLTNAM(195) =  'PIONEER-6'

      BLTCOD(196) =   -7
      BLTNAM(196) =  'P7'

      BLTCOD(197) =   -7
      BLTNAM(197) =  'PIONEER-7'

      BLTCOD(198) =   -8
      BLTNAM(198) =  'WIND'

      BLTCOD(199) =   -12
      BLTNAM(199) =  'VENUS ORBITER'

      BLTCOD(200) =   -12
      BLTNAM(200) =  'P12'

      BLTCOD(201) =   -12
      BLTNAM(201) =  'PIONEER 12'

      BLTCOD(202) =   -12
      BLTNAM(202) =  'LADEE'

      BLTCOD(203) =   -13
      BLTNAM(203) =  'POLAR'

      BLTCOD(204) =   -18
      BLTNAM(204) =  'MGN'

      BLTCOD(205) =   -18
      BLTNAM(205) =  'MAGELLAN'

      BLTCOD(206) =   -18
      BLTNAM(206) =  'LCROSS'

      BLTCOD(207) =   -20
      BLTNAM(207) =  'P8'

      BLTCOD(208) =   -20
      BLTNAM(208) =  'PIONEER-8'

      BLTCOD(209) =   -21
      BLTNAM(209) =  'SOHO'

      BLTCOD(210) =   -23
      BLTNAM(210) =  'P10'

      BLTCOD(211) =   -23
      BLTNAM(211) =  'PIONEER-10'

      BLTCOD(212) =   -24
      BLTNAM(212) =  'P11'

      BLTCOD(213) =   -24
      BLTNAM(213) =  'PIONEER-11'

      BLTCOD(214) =   -25
      BLTNAM(214) =  'LP'

      BLTCOD(215) =   -25
      BLTNAM(215) =  'LUNAR PROSPECTOR'

      BLTCOD(216) =   -27
      BLTNAM(216) =  'VK1'

      BLTCOD(217) =   -27
      BLTNAM(217) =  'VIKING 1 ORBITER'

      BLTCOD(218) =   -28
      BLTNAM(218) =  'JUPITER ICY MOONS EXPLORER'

      BLTCOD(219) =   -28
      BLTNAM(219) =  'JUICE'

      BLTCOD(220) =   -29
      BLTNAM(220) =  'STARDUST'

      BLTCOD(221) =   -29
      BLTNAM(221) =  'SDU'

      BLTCOD(222) =   -29
      BLTNAM(222) =  'NEXT'

      BLTCOD(223) =   -30
      BLTNAM(223) =  'VK2'

      BLTCOD(224) =   -30
      BLTNAM(224) =  'VIKING 2 ORBITER'

      BLTCOD(225) =   -30
      BLTNAM(225) =  'DS-1'

      BLTCOD(226) =   -31
      BLTNAM(226) =  'VG1'

      BLTCOD(227) =   -31
      BLTNAM(227) =  'VOYAGER 1'

      BLTCOD(228) =   -32
      BLTNAM(228) =  'VG2'

      BLTCOD(229) =   -32
      BLTNAM(229) =  'VOYAGER 2'

      BLTCOD(230) =   -33
      BLTNAM(230) =  'NEOS'

      BLTCOD(231) =   -33
      BLTNAM(231) =  'NEO SURVEYOR'

      BLTCOD(232) =   -37
      BLTNAM(232) =  'HYB2'

      BLTCOD(233) =   -37
      BLTNAM(233) =  'HAYABUSA 2'

      BLTCOD(234) =   -37
      BLTNAM(234) =  'HAYABUSA2'

      BLTCOD(235) =   -39
      BLTNAM(235) =  'LUNAR POLAR HYDROGEN MAPPER'

      BLTCOD(236) =   -39
      BLTNAM(236) =  'LUNAH-MAP'

      BLTCOD(237) =   -40
      BLTNAM(237) =  'CLEMENTINE'

      BLTCOD(238) =   -41
      BLTNAM(238) =  'MEX'

      BLTCOD(239) =   -41
      BLTNAM(239) =  'MARS EXPRESS'

      BLTCOD(240) =   -43
      BLTNAM(240) =  'IMAP'

      BLTCOD(241) =   -44
      BLTNAM(241) =  'BEAGLE2'

      BLTCOD(242) =   -44
      BLTNAM(242) =  'BEAGLE 2'

      BLTCOD(243) =   -45
      BLTNAM(243) =  'JNSA'

      BLTCOD(244) =   -45
      BLTNAM(244) =  'JANUS_A'

      BLTCOD(245) =   -46
      BLTNAM(245) =  'MS-T5'

      BLTCOD(246) =   -46
      BLTNAM(246) =  'SAKIGAKE'

      BLTCOD(247) =   -47
      BLTNAM(247) =  'PLANET-A'

      BLTCOD(248) =   -47
      BLTNAM(248) =  'SUISEI'

      BLTCOD(249) =   -47
      BLTNAM(249) =  'GNS'

      BLTCOD(250) =   -47
      BLTNAM(250) =  'GENESIS'

      BLTCOD(251) =   -48
      BLTNAM(251) =  'HUBBLE SPACE TELESCOPE'

      BLTCOD(252) =   -48
      BLTNAM(252) =  'HST'

      BLTCOD(253) =   -49
      BLTNAM(253) =  'LUCY'

      BLTCOD(254) =   -53
      BLTNAM(254) =  'MARS PATHFINDER'

      BLTCOD(255) =   -53
      BLTNAM(255) =  'MPF'

      BLTCOD(256) =   -53
      BLTNAM(256) =  'MARS ODYSSEY'

      BLTCOD(257) =   -53
      BLTNAM(257) =  'MARS SURVEYOR 01 ORBITER'

      BLTCOD(258) =   -55
      BLTNAM(258) =  'ULYSSES'

      BLTCOD(259) =   -57
      BLTNAM(259) =  'LUNAR ICECUBE'

      BLTCOD(260) =   -58
      BLTNAM(260) =  'VSOP'

      BLTCOD(261) =   -58
      BLTNAM(261) =  'HALCA'

      BLTCOD(262) =   -59
      BLTNAM(262) =  'RADIOASTRON'

      BLTCOD(263) =   -61
      BLTNAM(263) =  'JUNO'

      BLTCOD(264) =   -62
      BLTNAM(264) =  'EMM'

      BLTCOD(265) =   -62
      BLTNAM(265) =  'EMIRATES MARS MISSION'

      BLTCOD(266) =   -64
      BLTNAM(266) =  'ORX'

      BLTCOD(267) =   -64
      BLTNAM(267) =  'OSIRIS-REX'

      BLTCOD(268) =   -65
      BLTNAM(268) =  'MCOA'

      BLTCOD(269) =   -65
      BLTNAM(269) =  'MARCO-A'

      BLTCOD(270) =   -66
      BLTNAM(270) =  'VEGA 1'

      BLTCOD(271) =   -66
      BLTNAM(271) =  'MCOB'

      BLTCOD(272) =   -66
      BLTNAM(272) =  'MARCO-B'

      BLTCOD(273) =   -67
      BLTNAM(273) =  'VEGA 2'

      BLTCOD(274) =   -68
      BLTNAM(274) =  'MERCURY MAGNETOSPHERIC ORBITER'

      BLTCOD(275) =   -68
      BLTNAM(275) =  'MMO'

      BLTCOD(276) =   -68
      BLTNAM(276) =  'BEPICOLOMBO MMO'

      BLTCOD(277) =   -70
      BLTNAM(277) =  'DEEP IMPACT IMPACTOR SPACECRAFT'

      BLTCOD(278) =   -72
      BLTNAM(278) =  'JNSB'

      BLTCOD(279) =   -72
      BLTNAM(279) =  'JANUS_B'

      BLTCOD(280) =   -74
      BLTNAM(280) =  'MRO'

      BLTCOD(281) =   -74
      BLTNAM(281) =  'MARS RECON ORBITER'

      BLTCOD(282) =   -76
      BLTNAM(282) =  'CURIOSITY'

      BLTCOD(283) =   -76
      BLTNAM(283) =  'MSL'

      BLTCOD(284) =   -76
      BLTNAM(284) =  'MARS SCIENCE LABORATORY'

      BLTCOD(285) =   -77
      BLTNAM(285) =  'GLL'

      BLTCOD(286) =   -77
      BLTNAM(286) =  'GALILEO ORBITER'

      BLTCOD(287) =   -78
      BLTNAM(287) =  'GIOTTO'

      BLTCOD(288) =   -79
      BLTNAM(288) =  'SPITZER'

      BLTCOD(289) =   -79
      BLTNAM(289) =  'SPACE INFRARED TELESCOPE FACILITY'

      BLTCOD(290) =   -79
      BLTNAM(290) =  'SIRTF'

      BLTCOD(291) =   -81
      BLTNAM(291) =  'CASSINI ITL'

      BLTCOD(292) =   -82
      BLTNAM(292) =  'CAS'

      BLTCOD(293) =   -82
      BLTNAM(293) =  'CASSINI'

      BLTCOD(294) =   -84
      BLTNAM(294) =  'PHOENIX'

      BLTCOD(295) =   -85
      BLTNAM(295) =  'LRO'

      BLTCOD(296) =   -85
      BLTNAM(296) =  'LUNAR RECON ORBITER'

      BLTCOD(297) =   -85
      BLTNAM(297) =  'LUNAR RECONNAISSANCE ORBITER'

      BLTCOD(298) =   -86
      BLTNAM(298) =  'CH1'

      BLTCOD(299) =   -86
      BLTNAM(299) =  'CHANDRAYAAN-1'

      BLTCOD(300) =   -90
      BLTNAM(300) =  'CASSINI SIMULATION'

      BLTCOD(301) =   -93
      BLTNAM(301) =  'NEAR EARTH ASTEROID RENDEZVOUS'

      BLTCOD(302) =   -93
      BLTNAM(302) =  'NEAR'

      BLTCOD(303) =   -94
      BLTNAM(303) =  'MO'

      BLTCOD(304) =   -94
      BLTNAM(304) =  'MARS OBSERVER'

      BLTCOD(305) =   -94
      BLTNAM(305) =  'MGS'

      BLTCOD(306) =   -94
      BLTNAM(306) =  'MARS GLOBAL SURVEYOR'

      BLTCOD(307) =   -95
      BLTNAM(307) =  'MGS SIMULATION'

      BLTCOD(308) =   -96
      BLTNAM(308) =  'PARKER SOLAR PROBE'

      BLTCOD(309) =   -96
      BLTNAM(309) =  'SPP'

      BLTCOD(310) =   -96
      BLTNAM(310) =  'SOLAR PROBE PLUS'

      BLTCOD(311) =   -97
      BLTNAM(311) =  'TOPEX/POSEIDON'

      BLTCOD(312) =   -98
      BLTNAM(312) =  'NEW HORIZONS'

      BLTCOD(313) =   -107
      BLTNAM(313) =  'TROPICAL RAINFALL MEASURING MISSION'

      BLTCOD(314) =   -107
      BLTNAM(314) =  'TRMM'

      BLTCOD(315) =   -112
      BLTNAM(315) =  'ICE'

      BLTCOD(316) =   -116
      BLTNAM(316) =  'MARS POLAR LANDER'

      BLTCOD(317) =   -116
      BLTNAM(317) =  'MPL'

      BLTCOD(318) =   -117
      BLTNAM(318) =  'EDL DEMONSTRATOR MODULE'

      BLTCOD(319) =   -117
      BLTNAM(319) =  'EDM'

      BLTCOD(320) =   -117
      BLTNAM(320) =  'EXOMARS 2016 EDM'

      BLTCOD(321) =   -119
      BLTNAM(321) =  'MARS_ORBITER_MISSION_2'

      BLTCOD(322) =   -119
      BLTNAM(322) =  'MOM2'

      BLTCOD(323) =   -121
      BLTNAM(323) =  'MERCURY PLANETARY ORBITER'

      BLTCOD(324) =   -121
      BLTNAM(324) =  'MPO'

      BLTCOD(325) =   -121
      BLTNAM(325) =  'BEPICOLOMBO MPO'

      BLTCOD(326) =   -127
      BLTNAM(326) =  'MARS CLIMATE ORBITER'

      BLTCOD(327) =   -127
      BLTNAM(327) =  'MCO'

      BLTCOD(328) =   -130
      BLTNAM(328) =  'MUSES-C'

      BLTCOD(329) =   -130
      BLTNAM(329) =  'HAYABUSA'

      BLTCOD(330) =   -131
      BLTNAM(330) =  'SELENE'

      BLTCOD(331) =   -131
      BLTNAM(331) =  'KAGUYA'

      BLTCOD(332) =   -135
      BLTNAM(332) =  'DART'

      BLTCOD(333) =   -135
      BLTNAM(333) =  'DOUBLE ASTEROID REDIRECTION TEST'

      BLTCOD(334) =   -140
      BLTNAM(334) =  'EPOCH'

      BLTCOD(335) =   -140
      BLTNAM(335) =  'DIXI'

      BLTCOD(336) =   -140
      BLTNAM(336) =  'EPOXI'

      BLTCOD(337) =   -140
      BLTNAM(337) =  'DEEP IMPACT FLYBY SPACECRAFT'

      BLTCOD(338) =   -142
      BLTNAM(338) =  'TERRA'

      BLTCOD(339) =   -142
      BLTNAM(339) =  'EOS-AM1'

      BLTCOD(340) =   -143
      BLTNAM(340) =  'TRACE GAS ORBITER'

      BLTCOD(341) =   -143
      BLTNAM(341) =  'TGO'

      BLTCOD(342) =   -143
      BLTNAM(342) =  'EXOMARS 2016 TGO'

      BLTCOD(343) =   -144
      BLTNAM(343) =  'SOLO'

      BLTCOD(344) =   -144
      BLTNAM(344) =  'SOLAR ORBITER'

      BLTCOD(345) =   -146
      BLTNAM(345) =  'LUNAR-A'

      BLTCOD(346) =   -148
      BLTNAM(346) =  'DFLY'

      BLTCOD(347) =   -148
      BLTNAM(347) =  'DRAGONFLY'

      BLTCOD(348) =   -150
      BLTNAM(348) =  'CASSINI PROBE'

      BLTCOD(349) =   -150
      BLTNAM(349) =  'HUYGENS PROBE'

      BLTCOD(350) =   -150
      BLTNAM(350) =  'CASP'

      BLTCOD(351) =   -151
      BLTNAM(351) =  'AXAF'

      BLTCOD(352) =   -151
      BLTNAM(352) =  'CHANDRA'

      BLTCOD(353) =   -152
      BLTNAM(353) =  'CH2O'

      BLTCOD(354) =   -152
      BLTNAM(354) =  'CHANDRAYAAN-2 ORBITER'

      BLTCOD(355) =   -153
      BLTNAM(355) =  'CH2L'

      BLTCOD(356) =   -153
      BLTNAM(356) =  'CHANDRAYAAN-2 LANDER'

      BLTCOD(357) =   -154
      BLTNAM(357) =  'AQUA'

      BLTCOD(358) =   -155
      BLTNAM(358) =  'KPLO'

      BLTCOD(359) =   -155
      BLTNAM(359) =  'KOREAN PATHFINDER LUNAR ORBITER'

      BLTCOD(360) =   -156
      BLTNAM(360) =  'ADITYA'

      BLTCOD(361) =   -156
      BLTNAM(361) =  'ADIT'

      BLTCOD(362) =   -159
      BLTNAM(362) =  'EURC'

      BLTCOD(363) =   -159
      BLTNAM(363) =  'EUROPA CLIPPER'

      BLTCOD(364) =   -164
      BLTNAM(364) =  'LUNAR FLASHLIGHT'

      BLTCOD(365) =   -165
      BLTNAM(365) =  'MAP'

      BLTCOD(366) =   -166
      BLTNAM(366) =  'IMAGE'

      BLTCOD(367) =   -168
      BLTNAM(367) =  'PERSEVERANCE'

      BLTCOD(368) =   -168
      BLTNAM(368) =  'MARS 2020'

      BLTCOD(369) =   -168
      BLTNAM(369) =  'MARS2020'

      BLTCOD(370) =   -168
      BLTNAM(370) =  'M2020'

      BLTCOD(371) =   -170
      BLTNAM(371) =  'JWST'

      BLTCOD(372) =   -170
      BLTNAM(372) =  'JAMES WEBB SPACE TELESCOPE'

      BLTCOD(373) =   -172
      BLTNAM(373) =  'EXM RSP SCC'

      BLTCOD(374) =   -172
      BLTNAM(374) =  'EXM SPACECRAFT COMPOSITE'

      BLTCOD(375) =   -172
      BLTNAM(375) =  'EXOMARS SCC'

      BLTCOD(376) =   -173
      BLTNAM(376) =  'EXM RSP SP'

      BLTCOD(377) =   -173
      BLTNAM(377) =  'EXM SURFACE PLATFORM'

      BLTCOD(378) =   -173
      BLTNAM(378) =  'EXOMARS SP'

      BLTCOD(379) =   -174
      BLTNAM(379) =  'EXM RSP RM'

      BLTCOD(380) =   -174
      BLTNAM(380) =  'EXM ROVER'

      BLTCOD(381) =   -174
      BLTNAM(381) =  'EXOMARS ROVER'

      BLTCOD(382) =   -177
      BLTNAM(382) =  'GRAIL-A'

      BLTCOD(383) =   -178
      BLTNAM(383) =  'PLANET-B'

      BLTCOD(384) =   -178
      BLTNAM(384) =  'NOZOMI'

      BLTCOD(385) =   -181
      BLTNAM(385) =  'GRAIL-B'

      BLTCOD(386) =   -183
      BLTNAM(386) =  'CLUSTER 1'

      BLTCOD(387) =   -185
      BLTNAM(387) =  'CLUSTER 2'

      BLTCOD(388) =   -188
      BLTNAM(388) =  'MUSES-B'

      BLTCOD(389) =   -189
      BLTNAM(389) =  'NSYT'

      BLTCOD(390) =   -189
      BLTNAM(390) =  'INSIGHT'

      BLTCOD(391) =   -190
      BLTNAM(391) =  'SIM'

      BLTCOD(392) =   -194
      BLTNAM(392) =  'CLUSTER 3'

      BLTCOD(393) =   -196
      BLTNAM(393) =  'CLUSTER 4'

      BLTCOD(394) =   -197
      BLTNAM(394) =  'EXOMARS_LARA'

      BLTCOD(395) =   -197
      BLTNAM(395) =  'LARA'

      BLTCOD(396) =   -198
      BLTNAM(396) =  'INTEGRAL'

      BLTCOD(397) =   -198
      BLTNAM(397) =  'NASA-ISRO SAR MISSION'

      BLTCOD(398) =   -198
      BLTNAM(398) =  'NISAR'

      BLTCOD(399) =   -200
      BLTNAM(399) =  'CONTOUR'

      BLTCOD(400) =   -202
      BLTNAM(400) =  'MAVEN'

      BLTCOD(401) =   -203
      BLTNAM(401) =  'DAWN'

      BLTCOD(402) =   -205
      BLTNAM(402) =  'SOIL MOISTURE ACTIVE AND PASSIVE'

      BLTCOD(403) =   -205
      BLTNAM(403) =  'SMAP'

      BLTCOD(404) =   -210
      BLTNAM(404) =  'LICIA'

      BLTCOD(405) =   -210
      BLTNAM(405) =  'LICIACUBE'

      BLTCOD(406) =   -212
      BLTNAM(406) =  'STV51'

      BLTCOD(407) =   -213
      BLTNAM(407) =  'STV52'

      BLTCOD(408) =   -214
      BLTNAM(408) =  'STV53'

      BLTCOD(409) =   -226
      BLTNAM(409) =  'ROSETTA'

      BLTCOD(410) =   -227
      BLTNAM(410) =  'KEPLER'

      BLTCOD(411) =   -228
      BLTNAM(411) =  'GLL PROBE'

      BLTCOD(412) =   -228
      BLTNAM(412) =  'GALILEO PROBE'

      BLTCOD(413) =   -234
      BLTNAM(413) =  'STEREO AHEAD'

      BLTCOD(414) =   -235
      BLTNAM(414) =  'STEREO BEHIND'

      BLTCOD(415) =   -236
      BLTNAM(415) =  'MESSENGER'

      BLTCOD(416) =   -238
      BLTNAM(416) =  'SMART1'

      BLTCOD(417) =   -238
      BLTNAM(417) =  'SM1'

      BLTCOD(418) =   -238
      BLTNAM(418) =  'S1'

      BLTCOD(419) =   -238
      BLTNAM(419) =  'SMART-1'

      BLTCOD(420) =   -239
      BLTNAM(420) =  'MARTIAN MOONS EXPLORATION'

      BLTCOD(421) =   -239
      BLTNAM(421) =  'MMX'

      BLTCOD(422) =   -240
      BLTNAM(422) =  'SMART LANDER FOR INVESTIGATING MOON'

      BLTCOD(423) =   -240
      BLTNAM(423) =  'SLIM'

      BLTCOD(424) =   -242
      BLTNAM(424) =  'LUNAR TRAILBLAZER'

      BLTCOD(425) =   -243
      BLTNAM(425) =  'VIPER'

      BLTCOD(426) =   -248
      BLTNAM(426) =  'VEX'

      BLTCOD(427) =   -248
      BLTNAM(427) =  'VENUS EXPRESS'

      BLTCOD(428) =   -253
      BLTNAM(428) =  'OPPORTUNITY'

      BLTCOD(429) =   -253
      BLTNAM(429) =  'MER-1'

      BLTCOD(430) =   -254
      BLTNAM(430) =  'SPIRIT'

      BLTCOD(431) =   -254
      BLTNAM(431) =  'MER-2'

      BLTCOD(432) =   -255
      BLTNAM(432) =  'PSYC'

      BLTCOD(433) =   -301
      BLTNAM(433) =  'HELIOS 1'

      BLTCOD(434) =   -302
      BLTNAM(434) =  'HELIOS 2'

      BLTCOD(435) =   -362
      BLTNAM(435) =  'RADIATION BELT STORM PROBE A'

      BLTCOD(436) =   -362
      BLTNAM(436) =  'RBSP_A'

      BLTCOD(437) =   -363
      BLTNAM(437) =  'RADIATION BELT STORM PROBE B'

      BLTCOD(438) =   -363
      BLTNAM(438) =  'RBSP_B'

      BLTCOD(439) =   -500
      BLTNAM(439) =  'RSAT'

      BLTCOD(440) =   -500
      BLTNAM(440) =  'SELENE Relay Satellite'

      BLTCOD(441) =   -500
      BLTNAM(441) =  'SELENE Rstar'

      BLTCOD(442) =   -500
      BLTNAM(442) =  'Rstar'

      BLTCOD(443) =   -502
      BLTNAM(443) =  'VSAT'

      BLTCOD(444) =   -502
      BLTNAM(444) =  'SELENE VLBI Radio Satellite'

      BLTCOD(445) =   -502
      BLTNAM(445) =  'SELENE VRAD Satellite'

      BLTCOD(446) =   -502
      BLTNAM(446) =  'SELENE Vstar'

      BLTCOD(447) =   -502
      BLTNAM(447) =  'Vstar'

      BLTCOD(448) =   -550
      BLTNAM(448) =  'MARS-96'

      BLTCOD(449) =   -550
      BLTNAM(449) =  'M96'

      BLTCOD(450) =   -550
      BLTNAM(450) =  'MARS 96'

      BLTCOD(451) =   -550
      BLTNAM(451) =  'MARS96'

      BLTCOD(452) =   -652
      BLTNAM(452) =  'MERCURY TRANSFER MODULE'

      BLTCOD(453) =   -652
      BLTNAM(453) =  'MTM'

      BLTCOD(454) =   -652
      BLTNAM(454) =  'BEPICOLOMBO MTM'

      BLTCOD(455) =   -750
      BLTNAM(455) =  'SPRINT-A'

      BLTCOD(456) =   50000001
      BLTNAM(456) =  'SHOEMAKER-LEVY 9-W'

      BLTCOD(457) =   50000002
      BLTNAM(457) =  'SHOEMAKER-LEVY 9-V'

      BLTCOD(458) =   50000003
      BLTNAM(458) =  'SHOEMAKER-LEVY 9-U'

      BLTCOD(459) =   50000004
      BLTNAM(459) =  'SHOEMAKER-LEVY 9-T'

      BLTCOD(460) =   50000005
      BLTNAM(460) =  'SHOEMAKER-LEVY 9-S'

      BLTCOD(461) =   50000006
      BLTNAM(461) =  'SHOEMAKER-LEVY 9-R'

      BLTCOD(462) =   50000007
      BLTNAM(462) =  'SHOEMAKER-LEVY 9-Q'

      BLTCOD(463) =   50000008
      BLTNAM(463) =  'SHOEMAKER-LEVY 9-P'

      BLTCOD(464) =   50000009
      BLTNAM(464) =  'SHOEMAKER-LEVY 9-N'

      BLTCOD(465) =   50000010
      BLTNAM(465) =  'SHOEMAKER-LEVY 9-M'

      BLTCOD(466) =   50000011
      BLTNAM(466) =  'SHOEMAKER-LEVY 9-L'

      BLTCOD(467) =   50000012
      BLTNAM(467) =  'SHOEMAKER-LEVY 9-K'

      BLTCOD(468) =   50000013
      BLTNAM(468) =  'SHOEMAKER-LEVY 9-J'

      BLTCOD(469) =   50000014
      BLTNAM(469) =  'SHOEMAKER-LEVY 9-H'

      BLTCOD(470) =   50000015
      BLTNAM(470) =  'SHOEMAKER-LEVY 9-G'

      BLTCOD(471) =   50000016
      BLTNAM(471) =  'SHOEMAKER-LEVY 9-F'

      BLTCOD(472) =   50000017
      BLTNAM(472) =  'SHOEMAKER-LEVY 9-E'

      BLTCOD(473) =   50000018
      BLTNAM(473) =  'SHOEMAKER-LEVY 9-D'

      BLTCOD(474) =   50000019
      BLTNAM(474) =  'SHOEMAKER-LEVY 9-C'

      BLTCOD(475) =   50000020
      BLTNAM(475) =  'SHOEMAKER-LEVY 9-B'

      BLTCOD(476) =   50000021
      BLTNAM(476) =  'SHOEMAKER-LEVY 9-A'

      BLTCOD(477) =   50000022
      BLTNAM(477) =  'SHOEMAKER-LEVY 9-Q1'

      BLTCOD(478) =   50000023
      BLTNAM(478) =  'SHOEMAKER-LEVY 9-P2'

      BLTCOD(479) =   1000001
      BLTNAM(479) =  'AREND'

      BLTCOD(480) =   1000002
      BLTNAM(480) =  'AREND-RIGAUX'

      BLTCOD(481) =   1000003
      BLTNAM(481) =  'ASHBROOK-JACKSON'

      BLTCOD(482) =   1000004
      BLTNAM(482) =  'BOETHIN'

      BLTCOD(483) =   1000005
      BLTNAM(483) =  'BORRELLY'

      BLTCOD(484) =   1000006
      BLTNAM(484) =  'BOWELL-SKIFF'

      BLTCOD(485) =   1000007
      BLTNAM(485) =  'BRADFIELD'

      BLTCOD(486) =   1000008
      BLTNAM(486) =  'BROOKS 2'

      BLTCOD(487) =   1000009
      BLTNAM(487) =  'BRORSEN-METCALF'

      BLTCOD(488) =   1000010
      BLTNAM(488) =  'BUS'

      BLTCOD(489) =   1000011
      BLTNAM(489) =  'CHERNYKH'

      BLTCOD(490) =   1000012
      BLTNAM(490) =  '67P/CHURYUMOV-GERASIMENKO (1969 R1)'

      BLTCOD(491) =   1000012
      BLTNAM(491) =  'CHURYUMOV-GERASIMENKO'

      BLTCOD(492) =   1000013
      BLTNAM(492) =  'CIFFREO'

      BLTCOD(493) =   1000014
      BLTNAM(493) =  'CLARK'

      BLTCOD(494) =   1000015
      BLTNAM(494) =  'COMAS SOLA'

      BLTCOD(495) =   1000016
      BLTNAM(495) =  'CROMMELIN'

      BLTCOD(496) =   1000017
      BLTNAM(496) =  'D''ARREST'

      BLTCOD(497) =   1000018
      BLTNAM(497) =  'DANIEL'

      BLTCOD(498) =   1000019
      BLTNAM(498) =  'DE VICO-SWIFT'

      BLTCOD(499) =   1000020
      BLTNAM(499) =  'DENNING-FUJIKAWA'

      BLTCOD(500) =   1000021
      BLTNAM(500) =  'DU TOIT 1'

      BLTCOD(501) =   1000022
      BLTNAM(501) =  'DU TOIT-HARTLEY'

      BLTCOD(502) =   1000023
      BLTNAM(502) =  'DUTOIT-NEUJMIN-DELPORTE'

      BLTCOD(503) =   1000024
      BLTNAM(503) =  'DUBIAGO'

      BLTCOD(504) =   1000025
      BLTNAM(504) =  'ENCKE'

      BLTCOD(505) =   1000026
      BLTNAM(505) =  'FAYE'

      BLTCOD(506) =   1000027
      BLTNAM(506) =  'FINLAY'

      BLTCOD(507) =   1000028
      BLTNAM(507) =  'FORBES'

      BLTCOD(508) =   1000029
      BLTNAM(508) =  'GEHRELS 1'

      BLTCOD(509) =   1000030
      BLTNAM(509) =  'GEHRELS 2'

      BLTCOD(510) =   1000031
      BLTNAM(510) =  'GEHRELS 3'

      BLTCOD(511) =   1000032
      BLTNAM(511) =  'GIACOBINI-ZINNER'

      BLTCOD(512) =   1000033
      BLTNAM(512) =  'GICLAS'

      BLTCOD(513) =   1000034
      BLTNAM(513) =  'GRIGG-SKJELLERUP'

      BLTCOD(514) =   1000035
      BLTNAM(514) =  'GUNN'

      BLTCOD(515) =   1000036
      BLTNAM(515) =  'HALLEY'

      BLTCOD(516) =   1000037
      BLTNAM(516) =  'HANEDA-CAMPOS'

      BLTCOD(517) =   1000038
      BLTNAM(517) =  'HARRINGTON'

      BLTCOD(518) =   1000039
      BLTNAM(518) =  'HARRINGTON-ABELL'

      BLTCOD(519) =   1000040
      BLTNAM(519) =  'HARTLEY 1'

      BLTCOD(520) =   1000041
      BLTNAM(520) =  'HARTLEY 2'

      BLTCOD(521) =   1000042
      BLTNAM(521) =  'HARTLEY-IRAS'

      BLTCOD(522) =   1000043
      BLTNAM(522) =  'HERSCHEL-RIGOLLET'

      BLTCOD(523) =   1000044
      BLTNAM(523) =  'HOLMES'

      BLTCOD(524) =   1000045
      BLTNAM(524) =  'HONDA-MRKOS-PAJDUSAKOVA'

      BLTCOD(525) =   1000046
      BLTNAM(525) =  'HOWELL'

      BLTCOD(526) =   1000047
      BLTNAM(526) =  'IRAS'

      BLTCOD(527) =   1000048
      BLTNAM(527) =  'JACKSON-NEUJMIN'

      BLTCOD(528) =   1000049
      BLTNAM(528) =  'JOHNSON'

      BLTCOD(529) =   1000050
      BLTNAM(529) =  'KEARNS-KWEE'

      BLTCOD(530) =   1000051
      BLTNAM(530) =  'KLEMOLA'

      BLTCOD(531) =   1000052
      BLTNAM(531) =  'KOHOUTEK'

      BLTCOD(532) =   1000053
      BLTNAM(532) =  'KOJIMA'

      BLTCOD(533) =   1000054
      BLTNAM(533) =  'KOPFF'

      BLTCOD(534) =   1000055
      BLTNAM(534) =  'KOWAL 1'

      BLTCOD(535) =   1000056
      BLTNAM(535) =  'KOWAL 2'

      BLTCOD(536) =   1000057
      BLTNAM(536) =  'KOWAL-MRKOS'

      BLTCOD(537) =   1000058
      BLTNAM(537) =  'KOWAL-VAVROVA'

      BLTCOD(538) =   1000059
      BLTNAM(538) =  'LONGMORE'

      BLTCOD(539) =   1000060
      BLTNAM(539) =  'LOVAS 1'

      BLTCOD(540) =   1000061
      BLTNAM(540) =  'MACHHOLZ'

      BLTCOD(541) =   1000062
      BLTNAM(541) =  'MAURY'

      BLTCOD(542) =   1000063
      BLTNAM(542) =  'NEUJMIN 1'

      BLTCOD(543) =   1000064
      BLTNAM(543) =  'NEUJMIN 2'

      BLTCOD(544) =   1000065
      BLTNAM(544) =  'NEUJMIN 3'

      BLTCOD(545) =   1000066
      BLTNAM(545) =  'OLBERS'

      BLTCOD(546) =   1000067
      BLTNAM(546) =  'PETERS-HARTLEY'

      BLTCOD(547) =   1000068
      BLTNAM(547) =  'PONS-BROOKS'

      BLTCOD(548) =   1000069
      BLTNAM(548) =  'PONS-WINNECKE'

      BLTCOD(549) =   1000070
      BLTNAM(549) =  'REINMUTH 1'

      BLTCOD(550) =   1000071
      BLTNAM(550) =  'REINMUTH 2'

      BLTCOD(551) =   1000072
      BLTNAM(551) =  'RUSSELL 1'

      BLTCOD(552) =   1000073
      BLTNAM(552) =  'RUSSELL 2'

      BLTCOD(553) =   1000074
      BLTNAM(553) =  'RUSSELL 3'

      BLTCOD(554) =   1000075
      BLTNAM(554) =  'RUSSELL 4'

      BLTCOD(555) =   1000076
      BLTNAM(555) =  'SANGUIN'

      BLTCOD(556) =   1000077
      BLTNAM(556) =  'SCHAUMASSE'

      BLTCOD(557) =   1000078
      BLTNAM(557) =  'SCHUSTER'

      BLTCOD(558) =   1000079
      BLTNAM(558) =  'SCHWASSMANN-WACHMANN 1'

      BLTCOD(559) =   1000080
      BLTNAM(559) =  'SCHWASSMANN-WACHMANN 2'

      BLTCOD(560) =   1000081
      BLTNAM(560) =  'SCHWASSMANN-WACHMANN 3'

      BLTCOD(561) =   1000082
      BLTNAM(561) =  'SHAJN-SCHALDACH'

      BLTCOD(562) =   1000083
      BLTNAM(562) =  'SHOEMAKER 1'

      BLTCOD(563) =   1000084
      BLTNAM(563) =  'SHOEMAKER 2'

      BLTCOD(564) =   1000085
      BLTNAM(564) =  'SHOEMAKER 3'

      BLTCOD(565) =   1000086
      BLTNAM(565) =  'SINGER-BREWSTER'

      BLTCOD(566) =   1000087
      BLTNAM(566) =  'SLAUGHTER-BURNHAM'

      BLTCOD(567) =   1000088
      BLTNAM(567) =  'SMIRNOVA-CHERNYKH'

      BLTCOD(568) =   1000089
      BLTNAM(568) =  'STEPHAN-OTERMA'

      BLTCOD(569) =   1000090
      BLTNAM(569) =  'SWIFT-GEHRELS'

      BLTCOD(570) =   1000091
      BLTNAM(570) =  'TAKAMIZAWA'

      BLTCOD(571) =   1000092
      BLTNAM(571) =  'TAYLOR'

      BLTCOD(572) =   1000093
      BLTNAM(572) =  'TEMPEL_1'

      BLTCOD(573) =   1000093
      BLTNAM(573) =  'TEMPEL 1'

      BLTCOD(574) =   1000094
      BLTNAM(574) =  'TEMPEL 2'

      BLTCOD(575) =   1000095
      BLTNAM(575) =  'TEMPEL-TUTTLE'

      BLTCOD(576) =   1000096
      BLTNAM(576) =  'TRITTON'

      BLTCOD(577) =   1000097
      BLTNAM(577) =  'TSUCHINSHAN 1'

      BLTCOD(578) =   1000098
      BLTNAM(578) =  'TSUCHINSHAN 2'

      BLTCOD(579) =   1000099
      BLTNAM(579) =  'TUTTLE'

      BLTCOD(580) =   1000100
      BLTNAM(580) =  'TUTTLE-GIACOBINI-KRESAK'

      BLTCOD(581) =   1000101
      BLTNAM(581) =  'VAISALA 1'

      BLTCOD(582) =   1000102
      BLTNAM(582) =  'VAN BIESBROECK'

      BLTCOD(583) =   1000103
      BLTNAM(583) =  'VAN HOUTEN'

      BLTCOD(584) =   1000104
      BLTNAM(584) =  'WEST-KOHOUTEK-IKEMURA'

      BLTCOD(585) =   1000105
      BLTNAM(585) =  'WHIPPLE'

      BLTCOD(586) =   1000106
      BLTNAM(586) =  'WILD 1'

      BLTCOD(587) =   1000107
      BLTNAM(587) =  'WILD 2'

      BLTCOD(588) =   1000108
      BLTNAM(588) =  'WILD 3'

      BLTCOD(589) =   1000109
      BLTNAM(589) =  'WIRTANEN'

      BLTCOD(590) =   1000110
      BLTNAM(590) =  'WOLF'

      BLTCOD(591) =   1000111
      BLTNAM(591) =  'WOLF-HARRINGTON'

      BLTCOD(592) =   1000112
      BLTNAM(592) =  'LOVAS 2'

      BLTCOD(593) =   1000113
      BLTNAM(593) =  'URATA-NIIJIMA'

      BLTCOD(594) =   1000114
      BLTNAM(594) =  'WISEMAN-SKIFF'

      BLTCOD(595) =   1000115
      BLTNAM(595) =  'HELIN'

      BLTCOD(596) =   1000116
      BLTNAM(596) =  'MUELLER'

      BLTCOD(597) =   1000117
      BLTNAM(597) =  'SHOEMAKER-HOLT 1'

      BLTCOD(598) =   1000118
      BLTNAM(598) =  'HELIN-ROMAN-CROCKETT'

      BLTCOD(599) =   1000119
      BLTNAM(599) =  'HARTLEY 3'

      BLTCOD(600) =   1000120
      BLTNAM(600) =  'PARKER-HARTLEY'

      BLTCOD(601) =   1000121
      BLTNAM(601) =  'HELIN-ROMAN-ALU 1'

      BLTCOD(602) =   1000122
      BLTNAM(602) =  'WILD 4'

      BLTCOD(603) =   1000123
      BLTNAM(603) =  'MUELLER 2'

      BLTCOD(604) =   1000124
      BLTNAM(604) =  'MUELLER 3'

      BLTCOD(605) =   1000125
      BLTNAM(605) =  'SHOEMAKER-LEVY 1'

      BLTCOD(606) =   1000126
      BLTNAM(606) =  'SHOEMAKER-LEVY 2'

      BLTCOD(607) =   1000127
      BLTNAM(607) =  'HOLT-OLMSTEAD'

      BLTCOD(608) =   1000128
      BLTNAM(608) =  'METCALF-BREWINGTON'

      BLTCOD(609) =   1000129
      BLTNAM(609) =  'LEVY'

      BLTCOD(610) =   1000130
      BLTNAM(610) =  'SHOEMAKER-LEVY 9'

      BLTCOD(611) =   1000131
      BLTNAM(611) =  'HYAKUTAKE'

      BLTCOD(612) =   1000132
      BLTNAM(612) =  'HALE-BOPP'

      BLTCOD(613) =   1003228
      BLTNAM(613) =  'C/2013 A1'

      BLTCOD(614) =   1003228
      BLTNAM(614) =  'SIDING SPRING'

      BLTCOD(615) =   2000001
      BLTNAM(615) =  'CERES'

      BLTCOD(616) =   2000002
      BLTNAM(616) =  'PALLAS'

      BLTCOD(617) =   2000004
      BLTNAM(617) =  'VESTA'

      BLTCOD(618) =   2000016
      BLTNAM(618) =  'PSYCHE'

      BLTCOD(619) =   2000021
      BLTNAM(619) =  'LUTETIA'

      BLTCOD(620) =   2000052
      BLTNAM(620) =  '52_EUROPA'

      BLTCOD(621) =   2000052
      BLTNAM(621) =  '52 EUROPA'

      BLTCOD(622) =   2000216
      BLTNAM(622) =  'KLEOPATRA'

      BLTCOD(623) =   2000253
      BLTNAM(623) =  'MATHILDE'

      BLTCOD(624) =   2000433
      BLTNAM(624) =  'EROS'

      BLTCOD(625) =   2000511
      BLTNAM(625) =  'DAVIDA'

      BLTCOD(626) =   2002867
      BLTNAM(626) =  'STEINS'

      BLTCOD(627) =   2004015
      BLTNAM(627) =  'WILSON-HARRINGTON'

      BLTCOD(628) =   2004179
      BLTNAM(628) =  'TOUTATIS'

      BLTCOD(629) =   2009969
      BLTNAM(629) =  '1992KD'

      BLTCOD(630) =   2009969
      BLTNAM(630) =  'BRAILLE'

      BLTCOD(631) =   2025143
      BLTNAM(631) =  'ITOKAWA'

      BLTCOD(632) =   2101955
      BLTNAM(632) =  'BENNU'

      BLTCOD(633) =   2162173
      BLTNAM(633) =  'RYUGU'

      BLTCOD(634) =   2431010
      BLTNAM(634) =  'IDA'

      BLTCOD(635) =   2431011
      BLTNAM(635) =  'DACTYL'

      BLTCOD(636) =   2486958
      BLTNAM(636) =  'ARROKOTH'

      BLTCOD(637) =   9511010
      BLTNAM(637) =  'GASPRA'

      BLTCOD(638) =   20000617
      BLTNAM(638) =  'PATROCLUS_BARYCENTER'

      BLTCOD(639) =   20000617
      BLTNAM(639) =  'PATROCLUS BARYCENTER'

      BLTCOD(640) =   20003548
      BLTNAM(640) =  'EURYBATES_BARYCENTER'

      BLTCOD(641) =   20003548
      BLTNAM(641) =  'EURYBATES BARYCENTER'

      BLTCOD(642) =   20011351
      BLTNAM(642) =  'LEUCUS'

      BLTCOD(643) =   20015094
      BLTNAM(643) =  'POLYMELE'

      BLTCOD(644) =   20021900
      BLTNAM(644) =  'ORUS'

      BLTCOD(645) =   20052246
      BLTNAM(645) =  'DONALDJOHANSON'

      BLTCOD(646) =   20065803
      BLTNAM(646) =  'DIDYMOS_BARYCENTER'

      BLTCOD(647) =   20065803
      BLTNAM(647) =  'DIDYMOS BARYCENTER'

      BLTCOD(648) =   120000617
      BLTNAM(648) =  'MENOETIUS'

      BLTCOD(649) =   120003548
      BLTNAM(649) =  'QUETA'

      BLTCOD(650) =   120065803
      BLTNAM(650) =  'DIMORPHOS'

      BLTCOD(651) =   920000617
      BLTNAM(651) =  'PATROCLUS'

      BLTCOD(652) =   920003548
      BLTNAM(652) =  'EURYBATES'

      BLTCOD(653) =   920065803
      BLTNAM(653) =  'DIDYMOS'

      BLTCOD(654) =   398989
      BLTNAM(654) =  'NOTO'

      BLTCOD(655) =   398990
      BLTNAM(655) =  'NEW NORCIA'

      BLTCOD(656) =   399001
      BLTNAM(656) =  'GOLDSTONE'

      BLTCOD(657) =   399002
      BLTNAM(657) =  'CANBERRA'

      BLTCOD(658) =   399003
      BLTNAM(658) =  'MADRID'

      BLTCOD(659) =   399004
      BLTNAM(659) =  'USUDA'

      BLTCOD(660) =   399005
      BLTNAM(660) =  'DSS-05'

      BLTCOD(661) =   399005
      BLTNAM(661) =  'PARKES'

      BLTCOD(662) =   399012
      BLTNAM(662) =  'DSS-12'

      BLTCOD(663) =   399013
      BLTNAM(663) =  'DSS-13'

      BLTCOD(664) =   399014
      BLTNAM(664) =  'DSS-14'

      BLTCOD(665) =   399015
      BLTNAM(665) =  'DSS-15'

      BLTCOD(666) =   399016
      BLTNAM(666) =  'DSS-16'

      BLTCOD(667) =   399017
      BLTNAM(667) =  'DSS-17'

      BLTCOD(668) =   399023
      BLTNAM(668) =  'DSS-23'

      BLTCOD(669) =   399024
      BLTNAM(669) =  'DSS-24'

      BLTCOD(670) =   399025
      BLTNAM(670) =  'DSS-25'

      BLTCOD(671) =   399026
      BLTNAM(671) =  'DSS-26'

      BLTCOD(672) =   399027
      BLTNAM(672) =  'DSS-27'

      BLTCOD(673) =   399028
      BLTNAM(673) =  'DSS-28'

      BLTCOD(674) =   399033
      BLTNAM(674) =  'DSS-33'

      BLTCOD(675) =   399034
      BLTNAM(675) =  'DSS-34'

      BLTCOD(676) =   399035
      BLTNAM(676) =  'DSS-35'

      BLTCOD(677) =   399036
      BLTNAM(677) =  'DSS-36'

      BLTCOD(678) =   399042
      BLTNAM(678) =  'DSS-42'

      BLTCOD(679) =   399043
      BLTNAM(679) =  'DSS-43'

      BLTCOD(680) =   399045
      BLTNAM(680) =  'DSS-45'

      BLTCOD(681) =   399046
      BLTNAM(681) =  'DSS-46'

      BLTCOD(682) =   399049
      BLTNAM(682) =  'DSS-49'

      BLTCOD(683) =   399053
      BLTNAM(683) =  'DSS-53'

      BLTCOD(684) =   399054
      BLTNAM(684) =  'DSS-54'

      BLTCOD(685) =   399055
      BLTNAM(685) =  'DSS-55'

      BLTCOD(686) =   399056
      BLTNAM(686) =  'DSS-56'

      BLTCOD(687) =   399061
      BLTNAM(687) =  'DSS-61'

      BLTCOD(688) =   399063
      BLTNAM(688) =  'DSS-63'

      BLTCOD(689) =   399064
      BLTNAM(689) =  'DSS-64'

      BLTCOD(690) =   399065
      BLTNAM(690) =  'DSS-65'

      BLTCOD(691) =   399066
      BLTNAM(691) =  'DSS-66'

      BLTCOD(692) =   399069
      BLTNAM(692) =  'DSS-69'



      RETURN
      END

