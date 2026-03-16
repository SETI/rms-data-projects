#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jun  3 11:56:58 2024

@author: mseritan
"""

import os
from VG_2801_previews_functions import *

def generate_previews(data_directory):
    
    # Walk through sub-directory in the data directory
    for path, dirs, files in os.walk(data_directory):
        
        mirror_path = '/Users/mseritan/previews/VG_28xx/VG_2801/EASYDATA'
        
        # Saturn at 50 km resolution, Uranus & Neptune at 5 km resolution
        if path.endswith('VG_2801/EASYDATA/KM050') or path.endswith('VG_2801/EASYDATA/KM005'):
            for file in files:
                if file.endswith('.TAB'):
                    os.makedirs(mirror_path, exist_ok = True)
                    plot_preview_full(path, file, mirror_path)
                    plot_preview_medium(path, file, mirror_path)
                    plot_preview_small(path, file, mirror_path)
                    plot_preview_thumb(path, file, mirror_path)

if __name__ == "__main__":
    data_directory = '/Users/mseritan/holdings/voyager_occs'
    generate_previews(data_directory)