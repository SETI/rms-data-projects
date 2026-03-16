#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Apr 16 10:48:01 2024

@author: mseritan
"""

import os
import numpy as np
from numpy import ma
import matplotlib.pyplot as plt
import matplotlib.patheffects as PathEffects
from matplotlib import font_manager

font_path = 'cmunssdc.ttf'
prop = font_manager.FontProperties(fname = font_path)
plt.rcParams['axes.unicode_minus'] = False

ring_names = {
    'alpha': 'α Ring',
    'beta': 'β Ring',
    'gamma': 'γ Ring',
    'delta': 'δ Ring',
    'epsilon': 'ε Ring',
    'eta': 'η Ring',
    'lambda': 'λ Ring',
    'four': 'Ring 4',
    'five': 'Ring 5',
    'six': 'Ring 6',
    'atm': 'Atmos',
    'equator': 'ring plane'}

observatory_names = {
    'kao': 'Kuiper Airborne Observatory',
    'teide': 'Observatorio del Teide',
    'lco': 'Las Campanas Observatory',
    'ctio': 'Cerro Tololo Inter-American Observatory',
    'eso': 'European Southern Observatory',
    'sso': 'Siding Spring Observatory',
    'opmt': 'Observatoire du Pic du Midi et de Toulouse',
    'mso': 'Mount Stromlo Observatory',
    'palomar': 'Palomar Observatory',
    'saao': 'South African Astronomical Observatory',
    'mcdonald': 'McDonald Observatory',
    'irtf': 'Infrared Telescope Facility',
    'maunakea': 'United Kingdom Infrared Telescope',
    'hst': 'Hubble Space Telescope',
    'caha': 'Centro Astronomico Hispano-Aleman',
    'lowell': 'Lowell Observatory'}

observatory_abbrevs = {
    'kao': 'KAO',
    'teide': 'Teide',
    'lco': 'LCO',
    'ctio': 'CTIO',
    'eso': 'ESO',
    'sso': 'SSO',
    'opmt': 'OPMT',
    'mso': 'MSO',
    'palomar': 'Pal',
    'saao': 'SAAO',
    'mcdonald': 'McDon',
    'irtf': 'IRTF',
    'maunakea': 'UKIRT',
    'hst': 'HST',
    'caha': 'CAHA',
    'lowell': 'Lowell'}

#%% Function to plot the full-sized preview

def plot_preview_full(path, file, save_path, atm_flag):

    # Load the file
    filepath = os.path.join(path, file)
    data = np.loadtxt(filepath, dtype = str, delimiter=',')
    
    # Once file is loaded, strip the extra '_1000m'
    if not atm_flag:
        file = file[:-10] + file[-4:]
    
    # Extract info from filename
    filename_info = file.split('_')
    star_id = filename_info[0]
    observatory = filename_info[1]
    aperture = filename_info[2]
    observatory_name = observatory_names[observatory]
    if observatory != 'hst':
        aperture_m = str(float(aperture[:-2]) / 100) + 'm'
    else:
        aperture_m = 'FOS'
    wavelength = filename_info[3]
    if atm_flag:
        ring = 'atm'
    else:
        ring = filename_info[5]
    ring_name = ring_names[ring]
    direction = filename_info[6][:-4].capitalize()
    
    # Extract the relevant columns from the file
    x_axis = data[1:, 0].astype(float)
    if atm_flag:
        x_axis_name = 'Observed Event Time'
        x_axis_units = '(seconds)'
    else:
        x_axis_name = 'Ring Radius'
        x_axis = x_axis / 1000 # convert to thousands of km
        x_axis_units = r'(10$^3$ km)'
    if atm_flag:
        y_axis = data[1:, 2].astype(float)
    else:
        y_axis = data[1:, 4].astype(float)
    y_axis_name = 'Mean Signal'
    y_axis_units = '(counts)'
    if atm_flag:
        uncertainty = -1.0 * np.ones(np.size(y_axis))
        # The atmosphere data tables do not have a column for mean signal
        # uncertainty, so I supply a placeholder uncertainty array of -1's.
    else:
        uncertainty = data[1:, 5].astype(float)
        # The rings data tables do have a column for mean signal uncertainty.
    
    # Create figure
    figure_side = 6.0 # inches
    plt.figure(figsize = (figure_side, figure_side))
    panel_side = 4.75 # inches
    rel_panel_side = panel_side / figure_side
    panel = plt.axes([0.13, 0.1, rel_panel_side, rel_panel_side])
    panel.tick_params(bottom = True, labelbottom = True,
                     left = True, labelleft = True,
                     right = False, labelright = False,
                     top = False, labeltop = False)
    
    # Plot line, masking if the mean signal uncertainty is the special constant
    uncertainty_const = 999999999.999999
    y_axis_mask = ma.masked_where(uncertainty == uncertainty_const, y_axis)
    panel.plot(x_axis, y_axis_mask.T,
               linewidth = 2.0,
               color = 'black')
    
    # Set axis labels and their properties
    panel.set_xlabel(x_axis_name + ' ' + x_axis_units,
                     fontsize = 14,
                     fontproperties = prop)
    panel.set_ylabel(y_axis_name + ' ' + y_axis_units,
                     fontsize = 14,
                     fontproperties = prop)
    for label in panel.get_xticklabels():
        label.set_fontproperties(prop)
    for label in panel.get_yticklabels():
        label.set_fontproperties(prop)
    # panel.ticklabel_format(style = 'plain')
    
    # Add title
    panel.set_title(star_id + ' from ' + \
                    observatory_name + ' ' + \
                    aperture_m + '\n' + \
                    wavelength + ' ' + \
                    ring_name + ' ' + \
                    direction,
                    fontproperties = prop,
                    fontsize = 15)
    
    # Save file
    full_px = 1500
    file_out = file[:-4] + '_preview_full.png'   
    filepath_out = os.path.join(save_path, file_out)
    plt.savefig(filepath_out, dpi = full_px / figure_side)
    plt.close()
    
#%% Function to plot the medium-sized preview
    
def plot_preview_medium(path, file, save_path, atm_flag):
    
    # Load the file
    filepath = os.path.join(path, file)
    data = np.loadtxt(filepath, dtype = str, delimiter=',')
    
    # Once file is loaded, strip the extra '_1000m'
    if not atm_flag:
        file = file[:-10] + file[-4:]
    
    # Extract info from filename
    filename_info = file.split('_')
    star_id = filename_info[0]
    observatory = filename_info[1]
    aperture = filename_info[2]
    observatory_name = observatory_names[observatory]
    if observatory != 'hst':
        aperture_m = str(float(aperture[:-2]) / 100) + 'm'
    else:
        aperture_m = 'FOS'
    wavelength = filename_info[3]
    if atm_flag:
        ring = 'atm'
    else:
        ring = filename_info[5]
    ring_name = ring_names[ring]
    direction = filename_info[6][:-4].capitalize()
    
    # Extract the relevant columns from the file
    x_axis = data[1:, 0].astype(float)
    if atm_flag:
        x_axis_name = 'Observed Event Time'
        x_axis_units = '(seconds)'
    else:
        x_axis_name = 'Ring Radius'
        x_axis = x_axis / 1000 # convert to thousands of km
        x_axis_units = r'(10$^3$ km)'
    if atm_flag:
        y_axis = data[1:, 2].astype(float)
    else:
        y_axis = data[1:, 4].astype(float)
    y_axis_name = 'Mean Signal'
    y_axis_units = '(counts)'
    if atm_flag:
        uncertainty = -1.0 * np.ones(np.size(y_axis))
        # The atmosphere data tables do not have a column for mean signal
        # uncertainty, so I supply a placeholder uncertainty array of -1's.
    else:
        uncertainty = data[1:, 5].astype(float)
        # The rings data tables do have a column for mean signal uncertainty.
    
    # Create figure
    figure_side = 6.0 # inches
    plt.figure(figsize = (figure_side, figure_side))
    panel_side = 4.75 # inches
    rel_panel_side = panel_side / figure_side
    panel = plt.axes([0.13, 0.1, rel_panel_side, rel_panel_side])
    panel.tick_params(bottom = True, labelbottom = True,
                      left = True, labelleft = True,
                      right = False, labelright = False,
                      top = False, labeltop = False)
    
    # Plot line, masking if the mean signal uncertainty is the special constant
    uncertainty_const = 999999999.999999
    y_axis_mask = ma.masked_where(uncertainty == uncertainty_const, y_axis)
    panel.plot(x_axis, y_axis_mask.T,
               linewidth = 2.0,
               color = 'black')
    
    # Set axis labels and their properties
    panel.set_xlabel(x_axis_name + ' ' + x_axis_units,
                      fontsize = 15,
                      fontproperties = prop)
    panel.set_ylabel(y_axis_name + ' ' + y_axis_units,
                      fontsize = 15,
                      fontproperties = prop)
    for label in panel.get_xticklabels():
        label.set_fontproperties(prop)
    for label in panel.get_yticklabels():
        label.set_fontproperties(prop)
    # panel.ticklabel_format(style = 'plain')
    
    # Add title
    panel.set_title(star_id + ' from ' + \
                    observatory_name + ' ' + \
                    aperture_m + '\n' + \
                    wavelength + ' ' + \
                    ring_name + ' ' + \
                    direction,
                    fontproperties = prop,
                    fontsize = 15)
    
    # Save file
    medium_px = 500 
    file_out = file[:-4] + '_preview_med.png'   
    filepath_out = os.path.join(save_path, file_out)
    plt.savefig(filepath_out, dpi = medium_px / figure_side)
    plt.close()
    
#%% Function to plot the small-sized preview
    
def plot_preview_small(path, file, save_path, atm_flag):
    
    # Load the file
    filepath = os.path.join(path, file)
    data = np.loadtxt(filepath, dtype = str, delimiter=',')
    
    # Once file is loaded, strip the extra '_1000m'
    if not atm_flag:
        file = file[:-10] + file[-4:]
    
    # Extract info from filename
    filename_info = file.split('_')
    star_id = filename_info[0]
    observatory = filename_info[1]
    aperture = filename_info[2]
    observatory_abbrev = observatory_abbrevs[observatory]
    if observatory != 'hst':
        aperture_m = str(float(aperture[:-2]) / 100) + 'm'
    else:
        aperture_m = 'FOS'
    wavelength = filename_info[3]
    if atm_flag:
        ring = 'atm'
    else:
        ring = filename_info[5]
    ring_name = ring_names[ring]
    direction = filename_info[6][:-4].capitalize()
    
    # Extract the relevant columns from the file
    x_axis = data[1:, 0].astype(float)
    if atm_flag:
        x_axis_name = 'Observed Event Time'
        x_axis_units = '(seconds)'
    else:
        x_axis_name = 'Ring Radius'
        x_axis = x_axis / 1000 # convert to thousands of km
        x_axis_units = r'(10$^3$ km)'
    if atm_flag:
        y_axis = data[1:, 2].astype(float)
    else:
        y_axis = data[1:, 4].astype(float)
    y_axis_name = 'Mean Signal'
    y_axis_units = '(counts)'
    if atm_flag:
        uncertainty = -1.0 * np.ones(np.size(y_axis))
        # The atmosphere data tables do not have a column for mean signal
        # uncertainty, so I supply a placeholder uncertainty array of -1's.
    else:
        uncertainty = data[1:, 5].astype(float)
        # The rings data tables do have a column for mean signal uncertainty.
    
    # Create plot
    figure_side = 6.0 # inches
    plt.figure(figsize=(figure_side, figure_side))
    panel_side = 5.5 # inches
    rel_panel_side = panel_side / figure_side
    panel = plt.axes([0.07, 0.07, rel_panel_side, rel_panel_side])
    panel.tick_params(bottom = False, labelbottom = False,
                      left = False, labelleft = False,
                      right = False, labelright = False,
                      top = False, labeltop = False)
    
    # Plot line, masking if the mean signal uncertainty is the special constant
    uncertainty_const = 999999999.999999
    y_axis_mask = ma.masked_where(uncertainty == uncertainty_const, y_axis)
    panel.plot(x_axis, y_axis_mask.T,
               linewidth = 2.0,
               color = 'black')
    
    # Find max and min of array after masking
    max_val = -1000000
    min_val = 1000000
    for i in range(len(y_axis)):
        y_axis_val = y_axis[i]
        uncertainty_val = uncertainty[i]
        if y_axis_val > max_val and uncertainty_val != uncertainty_const:
            max_val = y_axis_val
        if y_axis_val < min_val and uncertainty_val != uncertainty_const:
            min_val = y_axis_val
    
    # Set y-axis limits such that annotation can be read at center top
    H = max_val - min_val
    fraction_above = 0.22 # fraction of total panel height
    fraction_below = 0.05 # fraction of total panel height
    fraction_between = 1.0 - fraction_above - fraction_below
    space_above = fraction_above * (H / fraction_between)
    space_below = fraction_below * (H / fraction_between)
    panel.set_ylim(min_val - space_below, max_val + space_above)
    
    # Set axis labels and their properties
    panel.set_xlabel(x_axis_name + ' ' + x_axis_units,
                      fontsize = 20,
                      fontproperties = prop)
    panel.set_ylabel(y_axis_name + ' ' + y_axis_units,
                      fontsize = 20,
                      fontproperties = prop)
    for label in panel.get_xticklabels():
        label.set_fontproperties(prop)
    for label in panel.get_yticklabels():
        label.set_fontproperties(prop)
    
    # Add annotation with title information
    annotation_text = star_id + ' ' + \
                      observatory_abbrev + ' ' + \
                      aperture_m + '\n' + \
                      wavelength + ' ' + \
                      ring_name + ' ' + \
                      direction
    panel.text(0.5, 0.975, annotation_text,
                horizontalalignment = 'center',
                verticalalignment = 'top',
                transform = panel.transAxes,
                fontsize = 36,
                color = (69/255, 120/255, 180/255),
                fontproperties = prop)
    
    # Save file
    medium_px = 250 
    file_out = file[:-4] + '_preview_small.png'   
    filepath_out = os.path.join(save_path, file_out)
    plt.savefig(filepath_out, dpi = medium_px / figure_side)
    plt.close()
    
#%% Function to plot the thumbnail-sized preview
    
def plot_preview_thumb(path, file, save_path, atm_flag):
    
    # Load the file
    filepath = os.path.join(path, file)
    data = np.loadtxt(filepath, dtype = str, delimiter=',')
    
    # Once file is loaded, strip the extra '_1000m'
    if not atm_flag:
        file = file[:-10] + file[-4:]
    
    # Extract info from filename
    filename_info = file.split('_')
    star_id = filename_info[0]
    observatory = filename_info[1]
    aperture = filename_info[2]
    observatory_abbrev = observatory_abbrevs[observatory]
    if observatory != 'hst':
        aperture_m = str(float(aperture[:-2]) / 100) + 'm'
    else:
        aperture_m = 'FOS'
    wavelength = filename_info[3]
    if atm_flag:
        ring = 'atm'
    else:
        ring = filename_info[5]
    ring_name = ring_names[ring]
    direction = filename_info[6][:-4].capitalize()
    
    # Extract the relevant columns from the file
    x_axis = data[1:, 0].astype(float)
    if atm_flag:
        y_axis = data[1:, 2].astype(float)
    else:
        y_axis = data[1:, 4].astype(float)
    if atm_flag:
        uncertainty = -1.0 * np.ones(np.size(y_axis))
        # The atmosphere data tables do not have a column for mean signal
        # uncertainty, so I supply a placeholder uncertainty array of -1's.
    else:
        uncertainty = data[1:, 5].astype(float)
        # The rings data tables do have a column for mean signal uncertainty.
    
    # Create plot
    figure_side = 6.0 # inches
    plt.figure(figsize=(figure_side, figure_side))
    panel_side = 6.0 # inches
    rel_panel_side = panel_side / figure_side
    panel = plt.axes([0.0, 0.0, rel_panel_side, rel_panel_side])
    panel.tick_params(bottom = False, labelbottom = False,
                      left = False, labelleft = False,
                      right = False, labelright = False,
                      top = False, labeltop = False)
    panel.axis('off')
    
    # Plot line, masking if the mean signal uncertainty is the special constant
    uncertainty_const = 999999999.999999
    y_axis_mask = ma.masked_where(uncertainty == uncertainty_const, y_axis)
    panel.plot(x_axis, y_axis_mask.T,
               linewidth = 2.0,
               color = 'black')
    
    # Find max and min of array after masking
    max_val = -1000000
    min_val = 1000000
    for i in range(len(y_axis)):
        y_axis_val = y_axis[i]
        uncertainty_val = uncertainty[i]
        if y_axis_val > max_val and uncertainty_val != uncertainty_const:
            max_val = y_axis_val
        if y_axis_val < min_val and uncertainty_val != uncertainty_const:
            min_val = y_axis_val
    
    # Set y-axis limits such that annotation can be read at center top
    H = max_val - min_val
    fraction_above = 0.22 # fraction of total panel height
    fraction_below = 0.05 # fraction of total panel height
    fraction_between = 1.0 - fraction_above - fraction_below
    space_above = fraction_above * (H / fraction_between)
    space_below = fraction_below * (H / fraction_between)
    panel.set_ylim(min_val - space_below, max_val + space_above)
    
    # Add annotation with title information
    annotation_text = star_id + ' ' + \
                      observatory_abbrev + ' ' + \
                      aperture_m + '\n' + \
                      wavelength + ' ' + \
                      ring_name + ' ' + \
                      direction
    panel.text(0.5, 0.95, annotation_text,
                horizontalalignment = 'center',
                verticalalignment = 'top',
                transform = panel.transAxes,
                fontsize = 39,
                color = (69/255, 120/255, 180/255),
                fontproperties = prop)
    
    # Save file
    thumb_px = 100 
    file_out = file[:-4] + '_preview_thumb.png'   
    filepath_out = os.path.join(save_path, file_out)
    plt.savefig(filepath_out, dpi = thumb_px / figure_side)
    plt.close()