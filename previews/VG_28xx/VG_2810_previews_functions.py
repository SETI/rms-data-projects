#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jun 25 13:06:54 2024

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
    '1': 'Voyager 1',
    '2': 'Voyager 2'}
spacecraft_abbrevs = {
    '1': 'VGR1',
    '2': 'VGR2'}
illuminations = {
    '1': 'Unlit side',
    '2': 'Lit side'}

planet = "Saturn's rings, "
wavelength = '280-640nm'
instrument = 'ISS'

#%% Function to plot the full-sized preview

def plot_preview_full(path, file, save_path):
    
    # Load the file
    filepath = os.path.join(path, file)
    data = np.loadtxt(filepath, dtype = str, delimiter=',')
    
    # Extract info from filename
    illumination = illuminations[file[2]]
    spacecraft = spacecrafts[file[2]]
    
    # Extract the relevant columns from the file
    x_axis = data[:, 0].astype(float)
    x_axis = x_axis / 1000 # convert to thousands of km
    x_axis_name = 'Ring Radius'
    x_axis_units = r'(10$^3$ km)'
    y_axis = data[:, 1].astype(float)
    y_axis_name = 'I/f'
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
    title_text = spacecraft + ' ' + instrument + ' Reflectance Profile\n' + \
                 planet + illumination
    panel.set_title(title_text,
                    fontproperties = prop)
    
    # Save file
    full_px = 1500
    file_out = file[0:9] + '_preview_full.png'   
    filepath_out = os.path.join(save_path, file_out)
    plt.savefig(filepath_out, dpi = full_px / figure_side)
    plt.close()
    
#%% Function to plot the medium-sized preview
    
def plot_preview_medium(path, file, save_path):
    
    # Load the file
    filepath = os.path.join(path, file)
    data = np.loadtxt(filepath, dtype = str, delimiter=',')
    
    # Extract info from filename
    illumination = illuminations[file[2]]
    spacecraft = spacecrafts[file[2]]
    
    # Extract the relevant columns from the file
    x_axis = data[:, 0].astype(float)
    x_axis = x_axis / 1000 # convert to thousands of km
    x_axis_name = 'Ring Radius'
    x_axis_units = r'(10$^3$ km)'
    y_axis = data[:, 1].astype(float)
    y_axis_name = 'I/f'
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
    title_text = spacecraft + ' ' + instrument + ' Reflectance Profile\n' + \
                 planet + illumination
    panel.set_title(title_text,
                    fontproperties = prop)
    
    # Save file
    medium_px = 500 
    file_out = file[0:9] + '_preview_med.png'   
    filepath_out = os.path.join(save_path, file_out)
    plt.savefig(filepath_out, dpi = medium_px / figure_side)
    plt.close()
    
#%% Function to plot the small-sized preview
    
def plot_preview_small(path, file, save_path):
    
    # Load the file
    filepath = os.path.join(path, file)
    data = np.loadtxt(filepath, dtype = str, delimiter=',')
    
    # Extract info from filename
    illumination = illuminations[file[2]]
    spacecraft_abbrev = spacecraft_abbrevs[file[2]]
    
    # Extract the relevant columns from the file
    x_axis = data[:, 0].astype(float)
    x_axis = x_axis / 1000 # convert to thousands of km
    x_axis_name = 'Ring Radius'
    x_axis_units = r'(10$^3$ km)'
    y_axis = data[:, 1].astype(float)
    y_axis_name = 'I/f'
    y_axis_units = ''
    
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
    title_text = spacecraft_abbrev + ' ' + instrument + ' Reflectance\n' + \
                 planet + illumination
    panel.text(0.5, 0.975, title_text,
               horizontalalignment = 'center',
               verticalalignment = 'top',
               transform = panel.transAxes,
               fontsize = 32,
               color = (69/255, 120/255, 180/255),
               fontproperties = prop)
    
    # Save file
    small_px = 250 
    file_out = file[0:9] + '_preview_small.png'   
    filepath_out = os.path.join(save_path, file_out)
    plt.savefig(filepath_out, dpi = small_px / figure_side)
    plt.close()
    
#%% Function to plot the thumbnail-sized preview
    
def plot_preview_thumb(path, file, save_path):
    
    # Load the file
    filepath = os.path.join(path, file)
    data = np.loadtxt(filepath, dtype = str, delimiter=',')
    
    # Extract info from filename
    illumination = illuminations[file[2]]
    spacecraft_abbrev = spacecraft_abbrevs[file[2]]
    
    # Extract the relevant columns from the file
    x_axis = data[:, 0].astype(float)
    x_axis = x_axis / 1000 # convert to thousands of km
    y_axis = data[:, 1].astype(float)
    
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
    H = max_val - min_val
    fraction_above = 0.22 # fraction of total panel height
    fraction_below = 0.05 # fraction of total panel height
    fraction_between = 1.0 - fraction_above - fraction_below
    space_above = fraction_above * (H / fraction_between)
    space_below = fraction_below * (H / fraction_between)
    panel.set_ylim(min_val - space_below, max_val + space_above)
    
    # Add annotation with title information
    title_text = spacecraft_abbrev + ' ' + instrument + ' Reflectance\n' + \
                 planet + illumination
    panel.text(0.5, 0.975, title_text,
               horizontalalignment = 'center',
               verticalalignment = 'top',
               transform = panel.transAxes,
               fontsize = 34,
               color = (69/255, 120/255, 180/255),
               fontproperties = prop)
    
    # Save file
    thumb_px = 100 
    file_out = file[0:9] + '_preview_thumb.png'   
    filepath_out = os.path.join(save_path, file_out)
    plt.savefig(filepath_out, dpi = thumb_px / figure_side)
    plt.close()