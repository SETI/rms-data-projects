#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jun  4 15:36:08 2024

@author: mseritan
"""

import os
import numpy as np
from numpy import ma
import matplotlib.pyplot as plt
from matplotlib import font_manager

font_path = 'cmunssdc.ttf'
prop = font_manager.FontProperties(fname = font_path)
plt.rcParams['axes.unicode_minus'] = False

stars = {
    'US1': 'δ Sco',
    'US2': 'δ Sco',
    'US3': 'ι Her',
    'UU1': 'σ Sgr',
    'UU2': 'β Per',
    'UN1': 'σ Sgr'}

spacecrafts = {
    'US1': 'Voyager 2',
    'US2': 'Voyager 2',
    'US3': 'Voyager 1',
    'UU1': 'Voyager 2',
    'UU2': 'Voyager 2',
    'UN1': 'Voyager 2'}

spacecrafts_abbrevs = {
    'US1': 'VGR2',
    'US2': 'VGR2',
    'US3': 'VGR1',
    'UU1': 'VGR2',
    'UU2': 'VGR2',
    'UN1': 'VGR2'}

rings = {
    'US1': "Saturn's rings",
    'US2': "Saturn's C Ring",
    'US3': "Saturn's C Ring",
    'UU1': 'Uranus flag',
    'UU2': 'Uranus flag',
    'UN1': "Neptune's rings"}

uranus_rings = {
    'D': "Uranus' δ Ring",
    'E': "Uranus' ε Ring",
    'X': "Uranus' ring plane"}

directions = {
    'US1': ' Egress',
    'US2': ' Ingress',
    'US3': ' Egress',
    'UU1': '',
    'UU2': '',
    'UN1': ' Ingress'}

wavelengths = {
    'US1': '79-162nm',
    'US2': '91-156nm',
    'US3': '91-156nm',
    'UU1': '83-167nm',
    'UU2': '',
    'UN1': '83-167nm'}

instrument = 'UVS'
UVS_color = (197/255, 233/255, 243/255)

#%% Function to plot the full-sized preview

def plot_preview_full(path, file, save_path):

    # Load the file
    filepath = os.path.join(path, file)
    data = np.loadtxt(filepath, dtype = str, delimiter=',')
    
    # Extract the relevant columns from the file
    x_axis = data[:, 0].astype(float)
    x_axis = x_axis / 1000 # convert to thousands of km
    x_axis_name = 'Ring Radius'
    x_axis_units = r'(10$^3$ km)'
    y_axis = data[:, 1].astype(float)
    y_axis_name = 'Mean Signal'
    y_axis_units = '(counts)'
    uncertainty = data[:, 2].astype(float)
    
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
    uncertainty_const = 99.000
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
    panel.ticklabel_format(style = 'plain')
    
    # Add title
    experiment = file[0:3]
    star = stars[experiment]
    spacecraft = spacecrafts[experiment]
    direction = directions[experiment]
    wavelength = wavelengths[experiment]
    ring = rings[experiment]
    if ring == 'Uranus flag':
        ring_char = file[-6]
        ring = uranus_rings[ring_char]
        direction_char = file[-5]
        if direction_char == 'E':
            direction = ' Egress'
        elif direction_char == 'I':
            direction = ' Ingress'
    title_text = star + ' from ' + \
                 spacecraft + ' ' + \
                 instrument + ' ' + \
                 wavelength + '\n' + \
                 ring + direction
    panel.set_title(title_text,
                    fontproperties = prop)
    
    # Create output file name
    if file[0:2] == 'UU':
        file_out = file[0:3] + 'xxx' + file[6:8]
    else:
        file_out = file[0:3] + 'xxx'
    
    # Save file
    full_px = 1500
    file_out = file_out + '_preview_full.png'   
    filepath_out = os.path.join(save_path, file_out)
    plt.savefig(filepath_out, dpi = full_px / figure_side)
    plt.close()
    
#%% Function to plot the medium-sized preview
    
def plot_preview_medium(path, file, save_path):
    
    # Load the file
    filepath = os.path.join(path, file)
    data = np.loadtxt(filepath, dtype = str, delimiter=',')
    
    # Extract the relevant columns from the file
    x_axis = data[:, 0].astype(float)
    x_axis = x_axis / 1000 # convert to thousands of km
    x_axis_name = 'Ring Radius'
    x_axis_units = r'(10$^3$ km)'
    y_axis = data[:, 1].astype(float)
    y_axis_name = 'Mean Signal'
    y_axis_units = '(counts)'
    uncertainty = data[:, 2].astype(float)
    
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
    uncertainty_const = 99.000
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
    panel.ticklabel_format(style = 'plain')

    # Add title
    experiment = file[0:3]
    star = stars[experiment]
    spacecraft = spacecrafts[experiment]
    direction = directions[experiment]
    wavelength = wavelengths[experiment]
    ring = rings[experiment]
    if ring == 'Uranus flag':
        ring_char = file[-6]
        ring = uranus_rings[ring_char]
        direction_char = file[-5]
        if direction_char == 'E':
            direction = ' Egress'
        elif direction_char == 'I':
            direction = ' Ingress'
    title_text = star + ' from ' + \
                 spacecraft + ' ' + \
                 instrument + ' ' + \
                 wavelength + '\n' + \
                 ring + direction
    panel.set_title(title_text,
                    fontproperties = prop)
    
    # Create output file name
    if file[0:2] == 'UU':
        file_out = file[0:3] + 'xxx' + file[6:8]
    else:
        file_out = file[0:3] + 'xxx'
    
    # Save file
    medium_px = 500 
    file_out = file_out + '_preview_med.png'   
    filepath_out = os.path.join(save_path, file_out)
    plt.savefig(filepath_out, dpi = medium_px / figure_side)
    plt.close()
    
#%% Function to plot the small-sized preview
    
def plot_preview_small(path, file, save_path):
    
    # Load the file
    filepath = os.path.join(path, file)
    data = np.loadtxt(filepath, dtype = str, delimiter=',')
    
    # Extract the relevant columns from the file
    x_axis = data[:, 0].astype(float)
    x_axis = x_axis / 1000 # convert to thousands of km
    x_axis_name = 'Ring Radius'
    x_axis_units = r'(10$^3$ km)'
    y_axis = data[:, 1].astype(float)
    y_axis_name = 'Mean Signal'
    y_axis_units = '(counts)'
    uncertainty = data[:, 2].astype(float)
    
    # Create plot
    figure_side = 6.0 # inches
    plt.figure(figsize=(figure_side, figure_side), facecolor = UVS_color)
    panel_side = 5.5 # inches
    rel_panel_side = panel_side / figure_side
    panel = plt.axes([0.07, 0.07, rel_panel_side, rel_panel_side])
    panel.tick_params(bottom = False, labelbottom = False,
                      left = False, labelleft = False,
                      right = False, labelright = False,
                      top = False, labeltop = False)
    panel.set_facecolor(UVS_color)
    
    # Plot line, masking if the mean signal uncertainty is the special constant
    uncertainty_const = 99.000
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
    
    # Add annotation with title information
    experiment = file[0:3]
    star = stars[experiment]
    spacecraft_abbrev = spacecrafts_abbrevs[experiment]
    direction = directions[experiment]
    wavelength = wavelengths[experiment]
    ring = rings[experiment]
    if ring == 'Uranus flag':
        ring_char = file[-6]
        ring = uranus_rings[ring_char]
        direction_char = file[-5]
        if direction_char == 'E':
            direction = ' Egress'
        elif direction_char == 'I':
            direction = ' Ingress'
    annotation_text = star + ' ' + \
                      spacecraft_abbrev + ' ' + \
                      instrument + ' ' + \
                      wavelength + '\n' + \
                      ring + direction
    panel.text(0.5, 0.975, annotation_text,
               horizontalalignment = 'center',
               verticalalignment = 'top',
               transform = panel.transAxes,
               fontsize = 30,
               color = 'black',
               fontproperties = prop)
    
    # Create output file name
    if file[0:2] == 'UU':
        file_out = file[0:3] + 'xxx' + file[6:8]
    else:
        file_out = file[0:3] + 'xxx'
    
    # Save file
    small_px = 250
    file_out = file_out + '_preview_small.png'   
    filepath_out = os.path.join(save_path, file_out)
    plt.savefig(filepath_out, dpi = small_px / figure_side)
    plt.close()
    
#%% Function to plot the thumbnail-sized preview
    
def plot_preview_thumb(path, file, save_path):
    
    # Load the file
    filepath = os.path.join(path, file)
    data = np.loadtxt(filepath, dtype = str, delimiter=',')
    
    # Extract the relevant columns from the file
    x_axis = data[:, 0].astype(float)
    x_axis = x_axis / 1000 # convert to thousands of km
    y_axis = data[:, 1].astype(float)
    uncertainty = data[:, 2].astype(float)
    
    # Create plot
    figure_side = 6.0 # inches
    plt.figure(figsize=(figure_side, figure_side), facecolor = UVS_color)
    panel_side = 6.0 # inches
    rel_panel_side = panel_side / figure_side
    panel = plt.axes([0.0, 0.0, rel_panel_side, rel_panel_side])
    panel.tick_params(bottom = False, labelbottom = False,
                      left = False, labelleft = False,
                      right = False, labelright = False,
                      top = False, labeltop = False)
    panel.axis('off')
    
    # Plot line, masking if the mean signal uncertainty is the special constant
    uncertainty_const = 99.000
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
    experiment = file[0:3]
    star = stars[experiment]
    spacecraft_abbrev = spacecrafts_abbrevs[experiment]
    direction = directions[experiment]
    wavelength = wavelengths[experiment]
    ring = rings[experiment]
    if ring == 'Uranus flag':
        ring_char = file[-6]
        ring = uranus_rings[ring_char]
        direction_char = file[-5]
        if direction_char == 'E':
            direction = ' Egress'
        elif direction_char == 'I':
            direction = ' Ingress'
    annotation_text = star + ' ' + \
                      spacecraft_abbrev + ' ' + \
                      instrument + ' ' + \
                      wavelength + '\n' + \
                      ring + direction
    panel.text(0.5, 0.975, annotation_text,
               horizontalalignment = 'center',
               verticalalignment = 'top',
               transform = panel.transAxes,
               fontsize = 34,
               color = 'black',
               fontproperties = prop)
    
    # Create output file name
    if file[0:2] == 'UU':
        file_out = file[0:3] + 'xxx' + file[6:8]
    else:
        file_out = file[0:3] + 'xxx'
    
    # Save file
    thumb_px = 100 
    file_out = file_out + '_preview_thumb.png'   
    filepath_out = os.path.join(save_path, file_out)
    plt.savefig(filepath_out, dpi = thumb_px / figure_side)
    plt.close()