#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jun  3 11:59:57 2024

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

planet_names = {
    'S': "Saturn's",
    'U': "Uranus'",
    'N': "Neptune's"}

star_names = {
    'ds': 'δ Sco',
    'ss': 'σ Sgr',
    'bp': 'β Per'}

ring_names = {
    'A': 'α Ring',
    'B': 'β Ring',
    'G': 'γ Ring',
    'D': 'δ Ring',
    'E': 'ε Ring',
    'N': 'η Ring',
    'L': 'λ Ring',
    '4': 'Ring 4',
    '5': 'Ring 5',
    '6': 'Ring 6',
    'X': 'ring plane'}

spacecraft = 'Voyager 2'
spacecraft_abbrev = 'VGR2'
instrument = 'PPS'
wavelength = '248-278nm'
# PPS_color = (203/255, 243/255, 199/255)
PPS_color = (192/255, 247/255, 220/255) # green

#%% Function to plot the full-sized preview

def plot_preview_full(path, file, save_path):

    # Load the file
    filepath = os.path.join(path, file)
    data = np.loadtxt(filepath, dtype = str, delimiter=',')
    
    # Extract info from filename
    planet = file[1]
    planet_text = planet_names[planet]
    if planet == 'S':
        star = 'ds'
        star_text = star_names[star]
        direction_text = 'Egress'
    elif planet == 'U':
        star = file[2]
        if star == '1':
            star_text = star_names['ss']
        elif star == '2':
            star_text = star_names['bp']
        ring = file[6]
        ring_text = ring_names[ring]
        direction = file[7]
        if direction == 'I':
            direction_text = 'Ingress'
        elif direction == 'E':
            direction_text = 'Egress'
    elif planet == 'N':
        star = 'ss'
        star_text = star_names[star]
        direction_text = 'Ingress'
    
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
    if planet == 'S' or planet == 'N':
        title_text = star_text + ' from ' + \
                     spacecraft + ' ' + \
                     instrument + ' ' + \
                     wavelength + '\n' + \
                     planet_text + ' rings ' + \
                     direction_text
    elif planet == 'U':
        title_text = star_text + ' from ' + \
                     spacecraft + ' ' + \
                     instrument + ' ' + \
                     wavelength + '\n' + \
                     planet_text +  ' ' + \
                     ring_text + ' ' + \
                     direction_text
    panel.set_title(title_text,
                    fontproperties = prop)
    
    # Create output file name
    if planet == 'S' or planet == 'N':
        file_out = file[0:3] + 'xxx'
    elif planet == 'U':
        file_out = file[0:3] + 'xxx' + file[6:8]
    
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
    
    # Extract info from filename
    planet = file[1]
    planet_text = planet_names[planet]
    if planet == 'S':
        star = 'ds'
        star_text = star_names[star]
        direction_text = 'Egress'
    elif planet == 'U':
        star = file[2]
        if star == '1':
            star_text = star_names['ss']
        elif star == '2':
            star_text = star_names['bp']
        ring = file[6]
        ring_text = ring_names[ring]
        direction = file[7]
        if direction == 'I':
            direction_text = 'Ingress'
        elif direction == 'E':
            direction_text = 'Egress'
    elif planet == 'N':
        star = 'ss'
        star_text = star_names[star]
        direction_text = 'Ingress'
    
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
    if planet == 'S' or planet == 'N':
        title_text = star_text + ' from ' + \
                     spacecraft + ' ' + \
                     instrument + ' ' + \
                     wavelength + '\n' + \
                     planet_text + ' rings ' + \
                     direction_text
    elif planet == 'U':
        title_text = star_text + ' from ' + \
                     spacecraft + ' ' + \
                     instrument + ' ' + \
                     wavelength + '\n' + \
                     planet_text +  ' ' + \
                     ring_text + ' ' + \
                     direction_text
    panel.set_title(title_text,
                    fontproperties = prop)
    
    # Create output file name
    if planet == 'S' or planet == 'N':
        file_out = file[0:3] + 'xxx'
    elif planet == 'U':
        file_out = file[0:3] + 'xxx' + file[6:8]
    
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
    
    # Extract info from filename
    planet = file[1]
    planet_text = planet_names[planet]
    if planet == 'S':
        star = 'ds'
        star_text = star_names[star]
        direction_text = 'Egress'
    elif planet == 'U':
        star = file[2]
        if star == '1':
            star_text = star_names['ss']
        elif star == '2':
            star_text = star_names['bp']
        ring = file[6]
        ring_text = ring_names[ring]
        direction = file[7]
        if direction == 'I':
            direction_text = 'Ingress'
        elif direction == 'E':
            direction_text = 'Egress'
    elif planet == 'N':
        star = 'ss'
        star_text = star_names[star]
        direction_text = 'Ingress'
    
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
    plt.figure(figsize = (figure_side, figure_side), facecolor = PPS_color)
    panel_side = 5.5 # inches
    rel_panel_side = panel_side / figure_side
    panel = plt.axes([0.07, 0.07, rel_panel_side, rel_panel_side])
    panel.tick_params(bottom = False, labelbottom = False,
                      left = False, labelleft = False,
                      right = False, labelright = False,
                      top = False, labeltop = False)
    panel.set_facecolor(PPS_color)
    
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
    if planet == 'S' or planet == 'N':
        annotation_text = star_text + ' ' + \
                          spacecraft_abbrev + ' ' + \
                          instrument + ' ' + \
                          wavelength + '\n' + \
                          planet_text + ' rings ' + \
                          direction_text
    elif planet == 'U':
        annotation_text = star_text + ' ' + \
                          spacecraft_abbrev + ' ' + \
                          instrument + ' ' + \
                          wavelength + '\n' + \
                          planet_text + ' ' + \
                          ring_text + ' ' + \
                          direction_text
    panel.text(0.5, 0.975, annotation_text,
               horizontalalignment = 'center',
               verticalalignment = 'top',
               transform = panel.transAxes,
               fontsize = 30,
               color = 'black',
               fontproperties = prop)
    
    # Create output file name
    if planet == 'S' or planet == 'N':
        file_out = file[0:3] + 'xxx'
    elif planet == 'U':
        file_out = file[0:3] + 'xxx' + file[6:8]
    
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
    
    # Extract info from filename
    planet = file[1]
    planet_text = planet_names[planet]
    if planet == 'S':
        star = 'ds'
        star_text = star_names[star]
        direction_text = 'Egress'
    elif planet == 'U':
        star = file[2]
        if star == '1':
            star_text = star_names['ss']
        elif star == '2':
            star_text = star_names['bp']
        ring = file[6]
        ring_text = ring_names[ring]
        direction = file[7]
        if direction == 'I':
            direction_text = 'Ingress'
        elif direction == 'E':
            direction_text = 'Egress'
    elif planet == 'N':
        star = 'ss'
        star_text = star_names[star]
        direction_text = 'Ingress'
    
    # Extract the relevant columns from the file
    x_axis = data[:, 0].astype(float)
    x_axis = x_axis / 1000 # convert to thousands of km
    y_axis = data[:, 1].astype(float)
    uncertainty = data[:, 2].astype(float)
    
    # Create plot
    figure_side = 6.0 # inches
    plt.figure(figsize = (figure_side, figure_side), facecolor = PPS_color)
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
    if planet == 'S' or planet == 'N':
        annotation_text = star_text + ' ' + \
                          spacecraft_abbrev + ' ' + \
                          instrument + ' ' + \
                          wavelength + '\n' + \
                          planet_text + ' rings ' + \
                          direction_text
    elif planet == 'U':
        annotation_text = star_text + ' ' + \
                          spacecraft_abbrev + ' ' + \
                          instrument + ' ' + \
                          wavelength + '\n' + \
                          planet_text + ' ' + \
                          ring_text + ' ' + \
                          direction_text
    panel.text(0.5, 0.95, annotation_text,
               horizontalalignment = 'center',
               verticalalignment = 'top',
               transform = panel.transAxes,
               fontsize = 34,
               color = 'black',
               fontproperties = prop)
    
    # Create output file name
    if planet == 'S' or planet == 'N':
        file_out = file[0:3] + 'xxx'
    elif planet == 'U':
        file_out = file[0:3] + 'xxx' + file[6:8]
    
    # Save file
    thumb_px = 100 
    file_out = file_out + '_preview_thumb.png'   
    filepath_out = os.path.join(save_path, file_out)
    plt.savefig(filepath_out, dpi = thumb_px / figure_side)
    plt.close()