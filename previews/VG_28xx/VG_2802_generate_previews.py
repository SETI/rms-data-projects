#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jun  4 15:35:40 2024

@author: mseritan
"""

import os
from VG_2802_previews_functions import *

def generate_previews(data_directory):
    
    # Walk through sub-directory in the data directory
    for path, dirs, files in os.walk(data_directory):
        
        mirror_path = '/Users/mseritan/previews/VG_28xx/VG_2802/EASYDATA'
        
        if path.endswith('VG_2802/EASYDATA/FILTER05'):
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