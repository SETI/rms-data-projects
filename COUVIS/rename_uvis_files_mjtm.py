"""
rename_uvis_files_mjtm.py
    Adapted from rename_uvis_files.py

    Renames/copies .DAT and .LBL files and their parent directory trees.
    
    Loops over each of the 60 volumes, and renames/copies each of the data files, according to the following key:
        vv = volume number
        INST = EUV|FUV (neglecting HDAC|HSP for now), 
        yyyy = year
        ddd = day
        hh = hour
        mm = minute
        ss [optional] = seconds
        EXT = filename extension (.DAT|.LBL)
        res = resolution of browse product (full|med|small|thumb)
    
    - 1) Raw data files are renamed/copied   
         from (on external disk shipped to MJTM): /Volumes/COUVIS_0xxx/volumes/COUVIS_00vv/DATA/DYYYY_ddd/INSTyyyy_ddd_hh_mm[_ss].EXT
         [previously (MRS): /Volumes/Migration2/UVIS/holdings/volumes/COUVIS_00vv/DATA/Dyyyy_ddd/INSTyyyy_ddd_hh_mm[_ss].EXT]
         to: /Volumes/COUVIS_0xxx/cassini_uvis_euvfuv_[cruise|saturn]/[data_raw|raw_labels]/yyyy/yyyy_ddd/instyyyy_ddd_hh_mm[_ss].ext
         [previously (MRS): /Volumes/Migration2/UVIS/cassini_uvis_saturn/data_raw_inst/yyyy_ddx/yyyy_ddd_hh_mm_inst.ext]
                 
    - 2) Calibration files are renamed/copied
         from (on external disk shipped to MJTM): /Volumes/COUVIS_0xxx/volumes/COUVIS_00vv/CALIB/VERSION_x/Dyyyy_ddd/INSTyyyy_ddd_hh_mm[_ss]_CAL_x.EXT
         [previously (MRS): /Volumes/Migration2/UVIS/holdings/volumes/COUVIS_00vv/CALIB/VERSION_x/Dyyyy_ddd/INSTyyyy_ddd_hh_mm[_ss]_CAL_x.EXT]
         to: /Volumes/COUVIS_0xxx/cassini_uvis_euvfuv_[cruise|saturn]/[data_calibration|calib_labels]/yyyy/yyyy_ddd/instyyyy_ddd_hh_mm[_ss]_cal_x.ext
         [previously (MRS):/Volumes/Migration2/UVIS/cassini_uvis_saturn/calibration_data_inst/yyyy_ddx/yyyy_ddd_hh_mm_cal_x_inst.dat]
                 
    - 3) Browse files are renamed/copied
         from (on external disk shipped to MJTM): /Volumes/COUVIS_0xxx/previews/COUVIS_00vv/DATA/Dyyyy_ddd/INSTyyyy_ddd_hh_mm[_ss]_res.png
             [previously (MRS): /Volumes/Migration2/UVIS/holdings/previews/COUVIS_00vv/DATA/Dyyyy_ddd/INSTyyyy_ddd_hh_mm[_ss]_res.png]
         to: /Volumes/COUVIS_0xxx/cassini_uvis_euvfuv_[cruise|saturn]/browse_raw/yyyy/yyyy_ddd/inst_yyyy_ddd_hh_mm[_ss]_full.png
         [previously (MRS): /Volumes/Migration2/UVIS/cassini_uvis_saturn/browse_raw_inst/yyyy_ddx/yyyy_ddd_hh_mm[_ss]_inst_full.png']
                 
    - Examples:
      - Raw data:
        /Volumes/COUVIS_0xxx/cassini_uvis_euvfuv_cruise/data_raw/2003/2003_224/euv2003_224_03_54.dat
        /Volumes/COUVIS_0xxx/cassini_uvis_euvfuv_saturn/raw_labels/2004/2004_001/fuv2004_001_05_20.lbl
      - Calibration:
        /Volumes/COUVIS_0xxx/cassini_uvis_euvfuv_saturn/data_calibration/2013/2013_004/euv2013_004_06_02_cal_3.dat
        /Volumes/COUVIS_0xxx/cassini_uvis_euvfuv_cruise/calib_labels/1999/1999_016/fuv1999_016_22_08_cal_3.lbl
      - Preview:
        /Volumes/COUVIS_0xxx/cassini_uvis_euvfuv_cruise/browse_raw/2001/2001_177/euv_2001_177_00_52_full.png
        /Volumes/COUVIS_0xxx/cassini_uvis_euvfuv_saturn/browse_raw/2017/2017_121/fuv_2017_121_22_41_full.png
                    
"""

# Divide the 3 product types (raw data, calibration, browse) into separate cells (delineated by '#%%') to debug/run using Spyder Cell mode

#%% 

# 1) Data

# Clear variables
#from IPython import get_ipython;   
#get_ipython().magic('reset -sf')

import os, sys, shutil 
from pathlib import Path

for v in range(1,61): # loop through the 60 volumes: COUVIS_0001/ ... COUVIS_0060/
    ROOT = '/Volumes/COUVIS_0xxx/volumes/COUVIS_00%02d/DATA' % v ## MM
    # According to the AAREADME.TXT: The files contained in these DYYYY_DDD directories have names      
    # of the form <channel>YYYY_DDD_HH_MM[_SS].[LBL | DAT] where <channel> is one of FUV, EUV, HSP, HDAC
    for root, dirs, files in os.walk(ROOT):
        print(root)
        for file in files:
            # If the file is not a data or label file then proceed to next iteration        
            if not file[-4:] in ('.LBL', '.DAT'): continue 
            # To only migrate EUV and FUV, uncomment the following line
            if not file[:3] in ('EUV', 'FUV'): continue
        
            # Rename raw data filepath as /Volumes/COUVIS_0xxx/cassini_uvis_euvfuv_[cruise|saturn]/[data_raw|raw_labels]/yyyy/yyyy_ddd/instyyyy_ddd_hh_mm[_ss].ext
            parts = file.split('_') 
            # parts[0] = XXXYYYY, where XXX = EUV or FUV, and YYYY is the year
            inst = parts[0][:-4].lower() 
            ext = parts[-1][-4:].lower() 

            # Remove the instrument (channel) and file-extension info
            parts[0] = parts[0][-4:] # Store the year YYYY (exclude instrument)
            parts[-1] = parts[-1][:-4] # Store the time MM / SS (remove file extension)
            # Being explicit with year and day variable names
            yyyy = parts[0][-4:] 
            dd = parts[1] 
        
            if int(yyyy) < 2004: # Before SOI
                DAT_DEST = '/Volumes/COUVIS_0xxx/cassini_uvis_euvfuv_cruise/data_raw/'
                LBL_DEST = '/Volumes/COUVIS_0xxx/cassini_uvis_euvfuv_cruise/raw_labels/'
            else: # After SOI
                DAT_DEST = '/Volumes/COUVIS_0xxx/cassini_uvis_euvfuv_saturn/data_raw/'
                LBL_DEST = '/Volumes/COUVIS_0xxx/cassini_uvis_euvfuv_saturn/raw_labels/'
            
            # Generate new filenames and subdirs
            # Note no underscore between instrument and year, to leave filenames closer 
            # to original as no data has been changed from PDS3 to PDS4)
            newname = inst+'_'.join(parts) + ext 
            newdir = yyyy + '/' + yyyy + '_' + dd 
        
            # Define full filepaths:
            if ext == '.dat':
                fulldir = DAT_DEST + newdir
            else:
                fulldir = LBL_DEST + newdir

            # Either 1) Rename files:
            #if not os.path.exists(fulldir):
                #os.mkdir(fulldir) # If the full filepath does not already exist, then make it
            #print(os.path.join(root,file), fulldir + '/' + newname)
            #os.rename(os.path.join(root,file), fulldir + '/' + newname) # CAREFUL! 
        
            # Or 2) Copy files:
            #if not os.path.exists(fulldir):
                #os.makedirs(fulldir, exist_ok=True) # If exist_ok is true, will not throw any exception if the target directory exists.
            # Pass the source and destination strings to the copy command
            # where src = os.path.join(root,file) , dest = fulldir + '/' + newname
            #shutil.copy2(os.path.join(root,file), fulldir + '/' + newname)

print("Finished re-naming/copying raw data labels")                                                     

#%% 

# 2) Calibration

# Clear variables
##from IPython import get_ipython;   
##get_ipython().magic('reset -sf')

import os, sys, shutil
from pathlib import Path

for v in range(1,61):
    ROOT = '/Volumes/COUVIS_0xxx/volumes/COUVIS_00%02d/CALIB/' % v 
    # Make a list containing the names of the entries in the ROOT path. The list is in arbitrary order so needs to be sorted. 
    ROOTlistdir = os.listdir(ROOT) 
    ROOTlistdir.sort()
    versions = [f for f in ROOTlistdir if f.startswith('VERSION_')] # Create list of strings
    for version in versions:
        for root, dirs, files in os.walk(ROOT + version):
            for file in files:
                # If the file is not a data or label file then proceed to next iteration
                if not file[-4:] in ('.LBL', '.DAT'): continue 
                # To only migrate EUV and FUV, uncomment the following line:
                if not file[:3] in ('EUV', 'FUV'): continue
                # Seek to rename calibration filepath as /Volumes/COUVIS_0xxx/cassini_uvis_euvfuv_[cruise|saturn]/[data_calibration|calib_labels]/yyyy/yyyy_ddd/inst_yyyy_ddd_hh_mm_[_ss]_cal_x.ext
                parts = file.split('_') 
        
                # Remove the instrument (channel) and file-extension info:
                inst = parts[0][:-4].lower() 
                ext = parts[-1][-4:].lower()
                parts[0] = parts[0][-4:] # Store the year YYYY (don't include instrument)
                parts[-1] = parts[-1][:-4] # Store the time MM / SS (remove file extension)
                # Being explicit with year and day variable names
                yyyy = parts[0][-4:]
                dd = parts[1]
        
                if int(yyyy) < 2004: # Before SOI
                    DAT_DEST = '/Volumes/COUVIS_0xxx/cassini_uvis_euvfuv_cruise/data_calibration/'
                    LBL_DEST = '/Volumes/COUVIS_0xxx/cassini_uvis_euvfuv_cruise/calib_labels/'
                else: # After SOI
                    DAT_DEST = '/Volumes/COUVIS_0xxx/cassini_uvis_euvfuv_saturn/data_calibration/'  
                    LBL_DEST = '/Volumes/COUVIS_0xxx/cassini_uvis_euvfuv_saturn/calib_labels/'

                # Generate new filenames and subdirs
                # Note no underscore between instrument and year, to leave filenames closer to original
                # as no data has been changed from PDS3 to PDS4)
                newname = inst+'_'.join(parts) + ext 
                newname = newname.lower() # Lowercase CAL
                newdir = yyyy + '/' + yyyy + '_' + dd 

                if ext == '.dat':
                    fulldir = DAT_DEST + newdir
                else:
                    fulldir = LBL_DEST + newdir

                # Either 1) Rename files:
                #if not os.path.exists(fulldir):
                    #os.mkdir(fulldir) # If the full filepath does not already exist, then make it
                #print (os.path.join(root,file), fulldir + '/' + newname)
                #os.rename(os.path.join(root,file), fulldir + '/' + newname)

                # Or 2) Copy files:
                #if not os.path.exists(fulldir):
                    #os.makedirs(fulldir, exist_ok=True) # If exist_ok is true, will not throw any exception if the target directory exists.
                # Pass the source and destination strings to the copy command
                # where src = os.path.join(root,file) , dest = fulldir + '/' + newname
                #shutil.copy2(os.path.join(root,file), fulldir + '/' + newname) 

print("Finished re-naming/copying calibration files")         
                                            
#%% 

# 3) Preview products

# Clear variables
#from IPython import get_ipython;   
#get_ipython().magic('reset -sf')

import os, sys, shutil
from pathlib import Path

for v in range(1,61):
    ROOT = '/Volumes/COUVIS_0xxx/previews/COUVIS_00%02d/DATA/' % v 
    for root, dirs, files in os.walk(ROOT):
        print(root)
        for file in files:
            # If the file is not full resolution then proceed to next iteration
            if not file.endswith('full.png'): continue 
            # To only migrate EUV and FUV, uncomment the following line:
            if not file[:3] in ('EUV', 'FUV'): continue
    
            # Seek to rename preview filepath as /Volumes/COUVIS_0xxx/cassini_uvis_euvfuv_[cruise|saturn]/browse_raw/yyyy/yyyy_ddd/inst_yyyy_ddd_hh_mm[_ss]_full.png
            parts = file.split('_') 
            inst = parts[0][:-4].lower() 
            ext = parts[-1][-4:].lower()

            parts[0] = parts[0][-4:] # Store the year YYYY (don't include instrument)
            parts[-1] = parts[-1][:-4] # Store the time MM / SS (remove file extension)
            # Being explicit with year and day variable names
            yyyy = parts[0][-4:] 
            dd = parts[1] 
        
            if int(yyyy) < 2004: # Before SOI
                PNG_DEST = '/Volumes/COUVIS_0xxx/cassini_uvis_euvfuv_cruise/browse_raw/'  
            else: # After SOI
                PNG_DEST = '/Volumes/COUVIS_0xxx/cassini_uvis_euvfuv_saturn/browse_raw/'

            newname = inst+'_'.join(parts) + ext 
            # Note no underscore between instrument and year, to leave filenames closer to original
            # as no data has been changed from PDS3 to PDS4)
            newdir = yyyy + '/' + yyyy + '_' + dd 
            fulldir = PNG_DEST + newdir

            # Either 1) Rename files:
            #if not os.path.exists(fulldir):
                #os.mkdir(fulldir) # If the full filepath does not already exist, then make it
            #print(os.path.join(root,file), fulldir + '/' + newname)
            #os.rename(os.path.join(root,file), fulldir + '/' + newname)
            
            # Or 2) Copy files:
            #if not os.path.exists(fulldir):
                #os.makedirs(fulldir, exist_ok=True) # If exist_ok is true, will not throw any exception if the target directory exists.
            # Pass the source and destination strings to the copy command:
            # where src = os.path.join(root,file), dest = fulldir + '/' + newname
            #shutil.copy2(os.path.join(root,file), fulldir + '/' + newname) 

print("Finished re-naming/copying full-res browse products")

