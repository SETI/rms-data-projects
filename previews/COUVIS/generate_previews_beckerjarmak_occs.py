#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Dec 23 12:09:53 2024

@author: mseritan
"""

import os
from previews_functions_beckerjarmak_occs import *

def generate_previews(data_directory):
    
    # Walk through sub-directory in the data directory
    for path, dirs, files in os.walk(data_directory):
        
        # Load file containing ring radius minima and maxima
        ring_radii = np.loadtxt('ring_radius_values.csv', dtype = str, delimiter=',')
        names = ring_radii[:, 0]
            
        for file in files:
            
            # For the one table with only corrupted data, run separate preview
            # generation functions that annotate "No valid data" onto the plot
            if file == 'uvis_euv_2016_269_solar_time_series_ingress.tab':
                
                # I'm not actually sure why these lines run correctly
                # when mirror_path isn't defined yet
                plot_null_preview_full(path, file, mirror_path)
                plot_null_preview_medium(path, file, mirror_path)
                plot_null_preview_small(path, file, mirror_path)
                plot_null_preview_thumb(path, file, mirror_path)
            
            # For all other tables, run the usual preview generation functions
            else:
                # Make previews for the main tables
                if file.endswith('ess.tab'):
                    
                    # Obtain min_ring_radius and max_ring_radius
                    name_index = np.where(names == file[:-4])[0]
                    min_ring_radius = ring_radii[name_index, 1].astype(float)
                    max_ring_radius = ring_radii[name_index, 2].astype(float)
                                    
                    # Run preview generation functions
                    mirror_path = path.replace('bundles',
                                               'previews')
                    os.makedirs(mirror_path, exist_ok = True)
                    plot_preview_full(path, file, mirror_path,
                                      min_ring_radius, max_ring_radius)
                    plot_preview_medium(path, file, mirror_path,
                                        min_ring_radius, max_ring_radius)
                    plot_preview_small(path, file, mirror_path,
                                       min_ring_radius, max_ring_radius)
                    plot_preview_thumb(path, file, mirror_path,
                                       min_ring_radius, max_ring_radius)
                    
                # Make preview for the supplemental table
                if file.endswith('_supplement.tab'):
                    
                    # Obtain min_ring_radius and max_ring_radius
                    name_index = np.where(names == file[:-4])[0]
                    min_ring_radius = ring_radii[name_index, 1].astype(float)
                    max_ring_radius = ring_radii[name_index, 2].astype(float)
                                    
                    # Run preview generation functions
                    mirror_path = path.replace('bundles',
                                               'previews')
                    os.makedirs(mirror_path, exist_ok = True)
                    plot_preview_full(path, file, mirror_path,
                                      min_ring_radius, max_ring_radius)
                    plot_preview_medium(path, file, mirror_path,
                                        min_ring_radius, max_ring_radius)
                    plot_preview_small(path, file, mirror_path,
                                       min_ring_radius, max_ring_radius)
                    plot_preview_thumb(path, file, mirror_path,
                                       min_ring_radius, max_ring_radius)

if __name__ == "__main__":
    data_directory = '/Users/mseritan/holdings_LOCAL/pds4-holdings/bundles/cassini_uvis_solarocc_beckerjarmak2023/data/'
    generate_previews(data_directory)