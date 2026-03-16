#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jun  5 13:53:23 2024

@author: mseritan
"""

import os
from VG_2803_previews_functions import *

def generate_previews(data_directory):
    
    # Walk through sub-directory in the data directory
    for path, dirs, files in os.walk(data_directory):
        
        mirror_path_1 = '/Users/mseritan/previews/VG_28xx/VG_2803/S_RINGS/EASYDATA'
        mirror_path_2 = '/Users/mseritan/previews/VG_28xx/VG_2803/U_RINGS/EASYDATA'
                
        if 'VG_2803/S_RINGS/EASYDATA/KM050' in path:
            for file in files:
                if file.startswith('RS4P1') and file.endswith('.TAB'):
                    os.makedirs(mirror_path_1, exist_ok = True)
                    plot_preview_full(path, file, mirror_path_1)
                    plot_preview_medium(path, file, mirror_path_1)
                    plot_preview_small(path, file, mirror_path_1)
                    plot_preview_thumb(path, file, mirror_path_1)
                    
        if 'VG_2803/U_RINGS/EASYDATA/KM00_5' in path:
            for file in files:
                if file.startswith('RU4P2') and file.endswith('.TAB'):
                    os.makedirs(mirror_path_2, exist_ok = True)
                    plot_preview_full(path, file, mirror_path_2)
                    plot_preview_medium(path, file, mirror_path_2)
                    plot_preview_small(path, file, mirror_path_2)
                    plot_preview_thumb(path, file, mirror_path_2)

if __name__ == "__main__":
    data_directory = '/Users/mseritan/holdings/voyager_occs'
    generate_previews(data_directory)