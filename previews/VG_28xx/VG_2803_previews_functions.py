#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jun  5 13:50:57 2024

@author: mseritan
"""

import os
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import font_manager

font_path = 'cmunssdc.ttf'
prop = font_manager.FontProperties(fname = font_path)
plt.rcParams['axes.unicode_minus'] = False

spacecrafts = {
    'S': 'Voyager 1',
    'U': 'Voyager 2'}
spacecraft_abbrevs = {
    'S': 'VGR1',
    'U': 'VGR2'}
planets = {
    'S': "Saturn's",
    'U': "Uranus'"}
# find these by extracting the index-1 character in the file name

bands = {
    'S': 'S-band',
    'X': 'X-band'}
wavelengths = {
    'S': '13cm',
    'X': '3.6cm'}
# find these by extracting the index-5 character in the file name

rings = {
    'A': 'α Ring',
    'B': 'β Ring',
    'G': 'γ Ring',
    'D': 'δ Ring',
    'E': 'ε Ring',
    'N': 'η Ring',
    '4': 'Ring 4',
    '5': 'Ring 5',
    '6': 'Ring 6',
    '.': 'rings'}
# find these by extracting the index-6 character in the file name

directions = {
    'E': ' Egress',
    'I': ' Ingress',
    'T': ''}
# find this by extracting the index-7 character in the file name

instrument = 'RSS'
RSS_color_S = (251/255, 202/255, 211/255)
RSS_color_X = (245/255, 235/255, 199/255)

#%% Function to plot the full-sized preview

def plot_preview_full(path, file, save_path):
    
    # Load the file
    filepath = os.path.join(path, file)
    data = np.loadtxt(filepath, dtype = str, delimiter=',')
    
    # Extract info from filename
    spacecraft = spacecrafts[file[1]]
    planet = planets[file[1]]
    band = bands[file[5]]
    wavelength = wavelengths[file[5]]
    ring = rings[file[6]]
    direction = directions[file[7]]
    if planet == "Saturn's":
        direction = ''
    
    # Extract the relevant columns from the file
    x_axis = data[:, 0].astype(float)
    x_axis = x_axis / 1000 # convert to thousands of km
    x_axis_name = 'Ring Radius'
    x_axis_units = r'(10$^3$ km)'
    y_axis = data[:, 1].astype(float)
    y_axis_name = 'Median Normal Opacity'
    y_axis_units = ''
    
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
    
    # Plot line
    panel.plot(x_axis, y_axis,
               linewidth = 2.0,
               color = 'black')
    panel.invert_yaxis()
    
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
    title_text = spacecraft + ' ' + \
                 instrument + ' ' + \
                 band + ' ' + \
                 wavelength + '\n' + \
                 planet + ' ' + \
                 ring + direction
    panel.set_title(title_text,
                    fontproperties = prop)
    
    # Create output file name
    if file[0:2] == 'RU':
        file_out = file[0:2] + 'xxx' + file[5:8]
    else:
        file_out = file[0:2] + 'xxx' + file[5]
    
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
    spacecraft = spacecrafts[file[1]]
    planet = planets[file[1]]
    band = bands[file[5]]
    wavelength = wavelengths[file[5]]
    ring = rings[file[6]]
    direction = directions[file[7]]
    
    # Extract the relevant columns from the file
    x_axis = data[:, 0].astype(float)
    x_axis = x_axis / 1000 # convert to thousands of km
    x_axis_name = 'Ring Radius'
    x_axis_units = r'(10$^3$ km)'
    y_axis = data[:, 1].astype(float)
    y_axis_name = 'Median Normal Opacity'
    y_axis_units = ''
    
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
    
    # Plot line
    panel.plot(x_axis, y_axis,
               linewidth = 2.0,
               color = 'black')
    panel.invert_yaxis()
    
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
    title_text = spacecraft + ' ' + \
                 instrument + ' ' + \
                 band + ' ' + \
                 wavelength + '\n' + \
                 planet + ' ' + \
                 ring + direction
    panel.set_title(title_text,
                    fontproperties = prop)
    
    # Create output file name
    if file[0:2] == 'RU':
        file_out = file[0:2] + 'xxx' + file[5:8]
    else:
        file_out = file[0:2] + 'xxx' + file[5]
    
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
    spacecraft_abbrev = spacecraft_abbrevs[file[1]]
    planet = planets[file[1]]
    band = bands[file[5]]
    if band == 'S-band':
        RSS_color = RSS_color_S
    elif band == 'X-band':
        RSS_color = RSS_color_X
    wavelength = wavelengths[file[5]]
    ring = rings[file[6]]
    direction = directions[file[7]]
    
    # Extract the relevant columns from the file
    x_axis = data[:, 0].astype(float)
    x_axis = x_axis / 1000 # convert to thousands of km
    x_axis_name = 'Ring Radius'
    x_axis_units = r'(10$^3$ km)'
    y_axis = data[:, 1].astype(float)
    y_axis_name = 'Median Normal Opacity'
    y_axis_units = ''
    
    # Create plot
    figure_side = 6.0 # inches
    plt.figure(figsize = (figure_side, figure_side), facecolor = RSS_color)
    panel_side = 5.5 # inches
    rel_panel_side = panel_side / figure_side
    panel = plt.axes([0.07, 0.07, rel_panel_side, rel_panel_side])
    panel.tick_params(bottom = False, labelbottom = False,
                      left = False, labelleft = False,
                      right = False, labelright = False,
                      top = False, labeltop = False)
    panel.set_facecolor(RSS_color)
    
    # Plot line
    panel.plot(x_axis, y_axis,
               linewidth = 2.0,
               color = 'black')
    
    # Find max and min of y_axis
    max_val = -1000000
    min_val = 1000000
    for i in range(len(y_axis)):
        y_axis_val = y_axis[i]
        if y_axis_val > max_val:
            max_val = y_axis_val
        if y_axis_val < min_val:
            min_val = y_axis_val
    
    # Set y-axis limits such that annotation can be read at center top
    # y-axis is inverted to match with radio science convention
    H = max_val - min_val
    fraction_above = 0.05 # fraction of total panel height
    fraction_below = 0.22 # fraction of total panel height
    fraction_between = 1.0 - fraction_above - fraction_below
    space_above = fraction_above * (H / fraction_between)
    space_below = fraction_below * (H / fraction_between)
    panel.set_ylim(max_val + space_above, min_val - space_below)
    
    # Set axis labels and their properties
    panel.set_xlabel(x_axis_name + ' ' + x_axis_units,
                     fontsize = 20,
                     fontproperties = prop)
    panel.set_ylabel(y_axis_name + ' ' + y_axis_units,
                     fontsize = 20,
                     fontproperties = prop)
    
    # Add annotation with title information
    title_text = spacecraft_abbrev + ' ' + \
                 instrument + ' ' + \
                 band + ' ' + \
                 wavelength + '\n' + \
                 planet + ' ' + \
                 ring + direction
    panel.text(0.5, 0.975, title_text,
               horizontalalignment = 'center',
               verticalalignment = 'top',
               transform = panel.transAxes,
               fontsize = 32,
               color = 'black',
               fontproperties = prop)
    
    # Create output file name
    if file[0:2] == 'RU':
        file_out = file[0:2] + 'xxx' + file[5:8]
    else:
        file_out = file[0:2] + 'xxx' + file[5]
    
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
    spacecraft_abbrev = spacecraft_abbrevs[file[1]]
    planet = planets[file[1]]
    band = bands[file[5]]
    if band == 'S-band':
        RSS_color = RSS_color_S
    elif band == 'X-band':
        RSS_color = RSS_color_X
    wavelength = wavelengths[file[5]]
    ring = rings[file[6]]
    direction = directions[file[7]]
    
    # Extract the relevant columns from the file
    x_axis = data[:, 0].astype(float)
    x_axis = x_axis / 1000 # convert to thousands of km
    y_axis = data[:, 1].astype(float)
    
    # Create plot
    figure_side = 6.0 # inches
    plt.figure(figsize = (figure_side, figure_side), facecolor = RSS_color)
    panel_side = 6.0 # inches
    rel_panel_side = panel_side / figure_side
    panel = plt.axes([0.0, 0.0, rel_panel_side, rel_panel_side])
    panel.tick_params(bottom = False, labelbottom = False,
                      left = False, labelleft = False,
                      right = False, labelright = False,
                      top = False, labeltop = False)
    panel.axis('off')
    
    # Plot line
    panel.plot(x_axis, y_axis,
               linewidth = 2.0,
               color = 'black')
    
    # Find max and min of y_axis
    max_val = -1000000
    min_val = 1000000
    for i in range(len(y_axis)):
        y_axis_val = y_axis[i]
        if y_axis_val > max_val:
            max_val = y_axis_val
        if y_axis_val < min_val:
            min_val = y_axis_val
    
    # Set y-axis limits such that annotation can be read at center top
    # y-axis is inverted to match with radio science convention
    H = max_val - min_val
    fraction_above = 0.05 # fraction of total panel height
    fraction_below = 0.22 # fraction of total panel height
    fraction_between = 1.0 - fraction_above - fraction_below
    space_above = fraction_above * (H / fraction_between)
    space_below = fraction_below * (H / fraction_between)
    panel.set_ylim(max_val + space_above, min_val - space_below)
    
    # Add annotation with title information
    title_text = spacecraft_abbrev + ' ' + \
                 instrument + ' ' + \
                 band + ' ' + \
                 wavelength + '\n' + \
                 planet + ' ' + \
                 ring + direction
    panel.text(0.5, 0.975, title_text,
               horizontalalignment = 'center',
               verticalalignment = 'top',
               transform = panel.transAxes,
               fontsize = 34,
               color = 'black',
               fontproperties = prop)
    
    # Create output file name
    if file[0:2] == 'RU':
        file_out = file[0:2] + 'xxx' + file[5:8]
    else:
        file_out = file[0:2] + 'xxx' + file[5]
    
    # Save file
    thumb_px = 100 
    file_out = file_out + '_preview_thumb.png'   
    filepath_out = os.path.join(save_path, file_out)
    plt.savefig(filepath_out, dpi = thumb_px / figure_side)
    plt.close()