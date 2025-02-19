################################################################################
# Global metadata unit test functions
################################################################################
import glob
import os

#METADATA = './'
METADATA = os.environ['RMS_METADATA']

#===============================================================================
# get summary filenames  ### LIB
def match(dir, pattern):
    all_files = []
    for root, dirs, files in os.walk(dir):
        all_files += glob.glob(os.path.join(root, pattern))
    return(all_files)

#===============================================================================
# exclude test files  ### LIB
def exclude(files, *patterns):
    result = []
    for i in range(len(files)):
        keep = True
        for pattern in patterns:
            if files[i].find(pattern) != -1:
                keep = False
        if(keep):
            result += [files[i]]
    return(result)

################################################################################
