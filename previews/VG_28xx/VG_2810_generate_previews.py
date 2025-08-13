#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jun 25 13:08:08 2024

@author: mseritan
"""

import os
from VG_2810_previews_functions import *

def generate_previews(data_directory):
    
    # Walk through sub-directory in the data directory
    for path, dirs, files in os.walk(data_directory):
        
        mirror_path = '/Users/mseritan/previews/VG_28xx/VG_2810/DATA'
        
        if 'VG_2810/DATA' in path:
            for file in files:
                if file == 'IS1_P0001_V01_KM020.TAB' or file == 'IS2_P0001_V01_KM020.TAB':
                    os.makedirs(mirror_path, exist_ok = True)
                    plot_preview_full(path, file, mirror_path)
                    plot_preview_medium(path, file, mirror_path)
                    plot_preview_small(path, file, mirror_path)
                    plot_preview_thumb(path, file, mirror_path)

if __name__ == "__main__":
    data_directory = '/Users/mseritan/holdings/voyager_occs'
    generate_previews(data_directory)