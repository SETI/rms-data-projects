#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Apr 17 16:19:18 2024

@author: mseritan
"""

import os
from previews_functions_uranus_occs_earthbased import *

def generate_previews(data_directory):
    
    # Walk through sub-directory in the data directory
    for path, dirs, files in os.walk(data_directory):
            
        if path.endswith('/data/global') or path.endswith('data/rings'):
            atm_flag = False
            for file in files:
                if file.endswith('_1000m.tab'):
                    mirror_path = path.replace('holdings', 'previews')
                    os.makedirs(mirror_path, exist_ok = True)
                    plot_preview_full(path, file, mirror_path, atm_flag)
                    plot_preview_medium(path, file, mirror_path, atm_flag)
                    plot_preview_small(path, file, mirror_path, atm_flag)
                    plot_preview_thumb(path, file, mirror_path, atm_flag)
            
        if path.endswith('/data/atmosphere'):
            atm_flag = True
            for file in files:
                if file.endswith('.tab'):
                    mirror_path = path.replace('holdings', 'previews')
                    os.makedirs(mirror_path, exist_ok = True)
                    plot_preview_full(path, file, mirror_path, atm_flag)
                    plot_preview_medium(path, file, mirror_path, atm_flag)
                    plot_preview_small(path, file, mirror_path, atm_flag)
                    plot_preview_thumb(path, file, mirror_path, atm_flag)

if __name__ == "__main__":
    data_directory = '/Users/mseritan/holdings/uranus_occs_earthbased'
    generate_previews(data_directory)