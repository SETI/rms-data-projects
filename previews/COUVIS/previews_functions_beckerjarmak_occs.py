#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Dec 23 12:09:53 2024

@author: mseritan
"""

import os
import numpy as np
from numpy import ma
import matplotlib.pyplot as plt
import matplotlib.patheffects as PathEffects
from matplotlib import font_manager
from julian import *

font_path = 'cmunssdc.ttf'
prop = font_manager.FontProperties(fname = font_path)
plt.rcParams['axes.unicode_minus'] = False

#%% Function to create the desired title date string

def make_title_date(year, day):
    
    days_since_2000 = day_from_yd(year, day)
    title_year, title_month, title_day = ymd_from_day(days_since_2000)
    title_year = str(title_year)
    title_month = str(title_month)
    title_day = str(title_day)
    
    # Pad month and day with zeros, if needed
    if len(title_month) == 1:
        title_month = '0' + title_month
    if len(title_day) == 1:
        title_day = '0' + title_day
    
    title_date = title_year + '-' + title_month + '-' + title_day
    
    return title_date

#%% Function to plot the full-sized null preview

def plot_null_preview_full(path, file, save_path):
    
    # Load the file
    filepath = os.path.join(path, file)
    data = np.loadtxt(filepath, dtype = str, delimiter = ',', skiprows = 1)
    
    # Extract info from filename
    filename_info = file.split('_')
    direction = filename_info[7][0]
    year = int(filename_info[2])
    day = int(filename_info[3])
    if direction == 'i':
        direction_text = 'Ingress'
    elif direction == 'e':
        direction_text = 'Egress'
    x_axis_name = 'Ring Plane Radius'
    x_axis_units = r'(10$^3$ km)'
    y_axis_name = 'Signal'
    y_axis_units = '(counts/sec)'
    
    # Create title date string
    title_date = make_title_date(year, day)
    
    # Create figure
    figure_side = 6.0 # inches
    plt.figure(figsize = (figure_side, figure_side))
    panel_side = 4.75 # inches
    rel_panel_side = panel_side / figure_side
    panel = plt.axes([0.13, 0.1, rel_panel_side, rel_panel_side])
    panel.tick_params(bottom = False, labelbottom = False,
                      left = False, labelleft = False,
                      right = False, labelright = False,
                      top = False, labeltop = False)
    
    # Set axis labels and their properties
    panel.set_xlabel(x_axis_name + ' ' + x_axis_units,
                     fontsize = 14,
                     fontproperties = prop)
    panel.set_ylabel(y_axis_name + ' ' + y_axis_units,
                     fontsize = 14,
                     fontproperties = prop)
    
    # Add annotation
    annotation_text = "No valid data"
    panel.text(0.5, 0.5, annotation_text,
                horizontalalignment = 'center',
                verticalalignment = 'center',
                transform = panel.transAxes,
                fontsize = 48,
                color = (69/255, 120/255, 180/255),
                fontproperties = prop)
    
    # Add title
    panel.set_title('Cassini UVIS EUV 57-117nm\n' + \
                    title_date + ' ' + \
                    "Saturn's rings " + direction_text,
                    fontproperties = prop,
                    fontsize = 15)
    
    # Save file
    full_px = 1500
    file_out = file[:-4] + '_preview_full.png'   
    filepath_out = os.path.join(save_path, file_out)
    plt.savefig(filepath_out, dpi = full_px / figure_side)
    plt.close()
    
#%% Function to plot the medium-sized null preview

def plot_null_preview_medium(path, file, save_path):
    
    # Load the file
    filepath = os.path.join(path, file)
    data = np.loadtxt(filepath, dtype = str, delimiter = ',', skiprows = 1)
    
    # Extract info from filename
    filename_info = file.split('_')
    direction = filename_info[7][0]
    year = int(filename_info[2])
    day = int(filename_info[3])
    if direction == 'i':
        direction_text = 'Ingress'
    elif direction == 'e':
        direction_text = 'Egress'
    x_axis_name = 'Ring Plane Radius'
    x_axis_units = r'(10$^3$ km)'
    y_axis_name = 'Signal'
    y_axis_units = '(counts/sec)'
    
    # Create title date string
    title_date = make_title_date(year, day)
    
    # Create figure
    figure_side = 6.0 # inches
    plt.figure(figsize = (figure_side, figure_side))
    panel_side = 4.75 # inches
    rel_panel_side = panel_side / figure_side
    panel = plt.axes([0.13, 0.1, rel_panel_side, rel_panel_side])
    panel.tick_params(bottom = False, labelbottom = False,
                      left = False, labelleft = False,
                      right = False, labelright = False,
                      top = False, labeltop = False)
    
    # Set axis labels and their properties
    panel.set_xlabel(x_axis_name + ' ' + x_axis_units,
                     fontsize = 14,
                     fontproperties = prop)
    panel.set_ylabel(y_axis_name + ' ' + y_axis_units,
                     fontsize = 14,
                     fontproperties = prop)
    
    # Add annotation
    annotation_text = "No valid data"
    panel.text(0.5, 0.5, annotation_text,
                horizontalalignment = 'center',
                verticalalignment = 'center',
                transform = panel.transAxes,
                fontsize = 48,
                color = (69/255, 120/255, 180/255),
                fontproperties = prop)
    
    # Add title
    panel.set_title('Cassini UVIS EUV 57-117nm\n' + \
                    title_date + ' ' + \
                    "Saturn's rings " + direction_text,
                    fontproperties = prop,
                    fontsize = 15)
        
    # Save file
    medium_px = 500 
    file_out = file[:-4] + '_preview_med.png'   
    filepath_out = os.path.join(save_path, file_out)
    plt.savefig(filepath_out, dpi = medium_px / figure_side)
    plt.close()
    
#%% Function to plot the small-sized null preview

def plot_null_preview_small(path, file, save_path):
    
    # Load the file
    filepath = os.path.join(path, file)
    data = np.loadtxt(filepath, dtype = str, delimiter = ',', skiprows = 1)
    
    # Extract info from filename
    filename_info = file.split('_')
    direction = filename_info[7][0]
    year = int(filename_info[2])
    day = int(filename_info[3])
    if direction == 'i':
        direction_text = 'Ingress'
    elif direction == 'e':
        direction_text = 'Egress'
    x_axis_name = 'Ring Plane Radius'
    x_axis_units = r'(10$^3$ km)'
    y_axis_name = 'Signal'
    y_axis_units = '(counts/sec)'
    
    # Create title date string
    title_date = make_title_date(year, day)
    
    # Create plot
    figure_side = 6.0 # inches
    plt.figure(figsize = (figure_side, figure_side))
    panel_side = 5.5 # inches
    rel_panel_side = panel_side / figure_side
    panel = plt.axes([0.07, 0.07, rel_panel_side, rel_panel_side])
    panel.tick_params(bottom = False, labelbottom = False,
                      left = False, labelleft = False,
                      right = False, labelright = False,
                      top = False, labeltop = False)
    
    # Set axis labels and their properties
    panel.set_xlabel(x_axis_name + ' ' + x_axis_units,
                     fontsize = 20,
                     fontproperties = prop)
    panel.set_ylabel(y_axis_name + ' ' + y_axis_units,
                     fontsize = 20,
                     fontproperties = prop)
    
    # Add annotation with title information
    annotation_text = 'CO UVIS EUV 57-117nm\n' + \
                      title_date + ' ' + \
                      "Saturn's rings " + direction_text
    panel.text(0.5, 0.975, annotation_text,
                horizontalalignment = 'center',
                verticalalignment = 'top',
                transform = panel.transAxes,
                fontsize = 24,
                color = (69/255, 120/255, 180/255),
                fontproperties = prop)
    
    # Add annotation
    annotation_text = "No valid data"
    panel.text(0.5, 0.45, annotation_text,
               horizontalalignment = 'center',
               verticalalignment = 'center',
               transform = panel.transAxes,
               fontsize = 56,
               color = 'black',
               fontproperties = prop)
    
    # Save file
    small_px = 250 
    file_out = file[:-4] + '_preview_small.png'   
    filepath_out = os.path.join(save_path, file_out)
    plt.savefig(filepath_out, dpi = small_px / figure_side)
    plt.close()
    
#%% Function to plot the thumbnail-sized null preview

def plot_null_preview_thumb(path, file, save_path):
    
    # Load the file
    filepath = os.path.join(path, file)
    data = np.loadtxt(filepath, dtype = str, delimiter = ',', skiprows = 1)
    
    # Extract info from filename
    filename_info = file.split('_')
    direction = filename_info[7][0]
    year = int(filename_info[2])
    day = int(filename_info[3])
    if direction == 'i':
        direction_text = 'Ingress'
    elif direction == 'e':
        direction_text = 'Egress'
        
    # Create title date string
    title_date = make_title_date(year, day)
        
    # Create plot
    figure_side = 6.0 # inches
    plt.figure(figsize = (figure_side, figure_side))
    panel_side = 6.0 # inches
    rel_panel_side = panel_side / figure_side
    panel = plt.axes([0.0, 0.0, rel_panel_side, rel_panel_side])
    panel.tick_params(bottom = False, labelbottom = False,
                      left = False, labelleft = False,
                      right = False, labelright = False,
                      top = False, labeltop = False)
    panel.axis('off')
    
    # Add annotation with title information
    annotation_text = 'CO UVIS EUV 57-117nm\n' + \
                      title_date + ' ' + \
                      "Saturn's rings " + direction_text
    panel.text(0.5, 0.975, annotation_text,
               horizontalalignment = 'center',
               verticalalignment = 'top',
               transform = panel.transAxes,
               fontsize = 32,
               color = (69/255, 120/255, 180/255),
               fontproperties = prop)
    
    # Add annotation
    annotation_text = "No valid data"
    panel.text(0.5, 0.45, annotation_text,
               horizontalalignment = 'center',
               verticalalignment = 'center',
               transform = panel.transAxes,
               fontsize = 56,
               color = 'black',
               fontproperties = prop)
    
    # Save file
    thumb_px = 100 
    file_out = file[:-4] + '_preview_thumb.png'   
    filepath_out = os.path.join(save_path, file_out)
    plt.savefig(filepath_out, dpi = thumb_px / figure_side)
    plt.close()

#%% Function to plot the full-sized preview

def plot_preview_full(path, file, save_path, min_ring_radius, max_ring_radius):

    # Load the file
    filepath = os.path.join(path, file)
    data = np.loadtxt(filepath, dtype = str, delimiter = ',', skiprows = 1)
    
    # Extract info from filename
    filename_info = file.split('_')
    direction = filename_info[7][0]
    year = int(filename_info[2])
    day = int(filename_info[3])
    if direction == 'i':
        direction_text = 'Ingress'
    elif direction == 'e':
        direction_text = 'Egress'
    x_axis_name = 'Ring Plane Radius'
    x_axis_units = r'(10$^3$ km)'
    y_axis_name = 'Signal'
    y_axis_units = '(counts/sec)'
    
    # Create title date string
    title_date = make_title_date(year, day)
    
    # Extract the relevant columns from the file
    y_axis = data[1:, 14].astype(float)
    x_axis = data[1:, 6].astype(float) / 1000
    # x_axis = np.linspace(min_ring_radius, max_ring_radius, len(y_axis)) / 1000
    note_flags = data[1:, 22].astype(int)
    if direction == 'i':
        y_axis = np.flip(y_axis)
        note_flags = np.flip(note_flags)
    
    # Create mask that covers multiple note flags
    combined_mask = []
    for i in range(len(note_flags)):
        if note_flags[i] >= 32 or \
           note_flags[i] == 8 or \
           note_flags[i] == 10:
            combined_mask.append(1)
        else:
            combined_mask.append(0)
        i += 1
    combined_mask = np.array(combined_mask)
    
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
    
    # Plot line, masking if the y-axis value is flagged
    y_axis_mask = ma.masked_where(combined_mask == 1, y_axis)
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
    panel.set_title('Cassini UVIS EUV 57-117nm\n' + \
                    title_date + ' ' + \
                    "Saturn's rings " + direction_text,
                    fontproperties = prop,
                    fontsize = 15)
    
    # Save file
    full_px = 1500
    file_out = file[:-4] + '_preview_full.png'   
    filepath_out = os.path.join(save_path, file_out)
    plt.savefig(filepath_out, dpi = full_px / figure_side)
    plt.close()
    
#%% Function to plot the medium-sized preview
    
def plot_preview_medium(path, file, save_path, min_ring_radius, max_ring_radius):
    
    # Load the file
    filepath = os.path.join(path, file)
    data = np.loadtxt(filepath, dtype = str, delimiter = ',', skiprows = 1)
    
    # Extract info from filename
    filename_info = file.split('_')
    direction = filename_info[7][0]
    year = int(filename_info[2])
    day = int(filename_info[3])
    if direction == 'i':
        direction_text = 'Ingress'
    elif direction == 'e':
        direction_text = 'Egress'
    x_axis_name = 'Ring Plane Radius'
    x_axis_units = r'(10$^3$ km)'
    y_axis_name = 'Signal'
    y_axis_units = '(counts/sec)'
    
    # Create title date string
    title_date = make_title_date(year, day)
    
    # Extract the relevant columns from the file
    y_axis = data[1:, 14].astype(float)
    x_axis = data[1:, 6].astype(float) / 1000
    # x_axis = np.linspace(min_ring_radius, max_ring_radius, len(y_axis)) / 1000
    note_flags = data[1:, 22].astype(int)
    if direction == 'i':
        y_axis = np.flip(y_axis)
        note_flags = np.flip(note_flags)
    
    # Create mask that covers multiple note flags
    combined_mask = []
    for i in range(len(note_flags)):
        if note_flags[i] >= 32 or \
           note_flags[i] == 8 or \
           note_flags[i] == 10:
            combined_mask.append(1)
        else:
            combined_mask.append(0)
        i += 1
    combined_mask = np.array(combined_mask)
    
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
    
    # Plot line, masking if the y-axis value is flagged
    y_axis_mask = ma.masked_where(combined_mask == 1, y_axis)
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
    panel.set_title('Cassini UVIS EUV 57-117nm\n' + \
                    title_date + ' ' + \
                    "Saturn's rings " + direction_text,
                    fontproperties = prop,
                    fontsize = 15)
    
    # Save file
    medium_px = 500 
    file_out = file[:-4] + '_preview_med.png'   
    filepath_out = os.path.join(save_path, file_out)
    plt.savefig(filepath_out, dpi = medium_px / figure_side)
    plt.close()
    
#%% Function to plot the small-sized preview
    
def plot_preview_small(path, file, save_path, min_ring_radius, max_ring_radius):
    
    # Load the file
    filepath = os.path.join(path, file)
    data = np.loadtxt(filepath, dtype = str, delimiter = ',', skiprows = 1)
    
    # Extract info from filename
    filename_info = file.split('_')
    direction = filename_info[7][0]
    year = int(filename_info[2])
    day = int(filename_info[3])
    if direction == 'i':
        direction_text = 'Ingress'
    elif direction == 'e':
        direction_text = 'Egress'
    x_axis_name = 'Ring Plane Radius'
    x_axis_units = r'(10$^3$ km)'
    y_axis_name = 'Signal'
    y_axis_units = '(counts/sec)'
    
    # Create title date string
    title_date = make_title_date(year, day)
    
    # Extract the relevant columns from the file
    y_axis = data[1:, 14].astype(float)
    x_axis = data[1:, 6].astype(float) / 1000
    # x_axis = np.linspace(min_ring_radius, max_ring_radius, len(y_axis)) / 1000
    note_flags = data[1:, 22].astype(int)
    if direction == 'i':
        y_axis = np.flip(y_axis)
        note_flags = np.flip(note_flags)
        
    # Create mask that covers multiple note flags
    combined_mask = []
    for i in range(len(note_flags)):
        if note_flags[i] >= 32 or \
           note_flags[i] == 8 or \
           note_flags[i] == 10:
            combined_mask.append(1)
        else:
            combined_mask.append(0)
        i += 1
    combined_mask = np.array(combined_mask)
    
    # Create plot
    figure_side = 6.0 # inches
    plt.figure(figsize = (figure_side, figure_side))
    panel_side = 5.5 # inches
    rel_panel_side = panel_side / figure_side
    panel = plt.axes([0.07, 0.07, rel_panel_side, rel_panel_side])
    panel.tick_params(bottom = False, labelbottom = False,
                      left = False, labelleft = False,
                      right = False, labelright = False,
                      top = False, labeltop = False)
    
    # Plot line, masking if the y-axis value is flagged
    y_axis_mask = ma.masked_where(combined_mask == 1, y_axis)
    panel.plot(x_axis, y_axis_mask.T,
               linewidth = 2.0,
               color = 'black')
    
    # Find max and min of array after masking
    max_val = y_axis_mask.max()
    min_val = y_axis_mask.min()
    
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
    annotation_text = 'CO UVIS EUV 57-117nm\n' + \
                      title_date + ' ' + \
                      "Saturn's rings " + direction_text
    panel.text(0.5, 0.975, annotation_text,
                horizontalalignment = 'center',
                verticalalignment = 'top',
                transform = panel.transAxes,
                fontsize = 24,
                color = (69/255, 120/255, 180/255),
                fontproperties = prop)
    
    # Save file
    small_px = 250 
    file_out = file[:-4] + '_preview_small.png'   
    filepath_out = os.path.join(save_path, file_out)
    plt.savefig(filepath_out, dpi = small_px / figure_side)
    plt.close()
    
#%% Function to plot the thumbnail-sized preview
    
def plot_preview_thumb(path, file, save_path, min_ring_radius, max_ring_radius):
    
    # Load the file
    filepath = os.path.join(path, file)
    data = np.loadtxt(filepath, dtype = str, delimiter = ',', skiprows = 1)
    
    # Extract info from filename
    filename_info = file.split('_')
    direction = filename_info[7][0]
    year = int(filename_info[2])
    day = int(filename_info[3])
    if direction == 'i':
        direction_text = 'Ingress'
    elif direction == 'e':
        direction_text = 'Egress'
    
    # Create title date string
    title_date = make_title_date(year, day)
    
    # Extract the relevant columns from the file
    y_axis = data[1:, 14].astype(float)
    x_axis = data[1:, 6].astype(float) / 1000
    # x_axis = np.linspace(min_ring_radius, max_ring_radius, len(y_axis)) / 1000
    note_flags = data[1:, 22].astype(int)
    if direction == 'i':
        y_axis = np.flip(y_axis)
        note_flags = np.flip(note_flags)
        
    # Create mask that covers multiple note flags
    combined_mask = []
    for i in range(len(note_flags)):
        if note_flags[i] >= 32 or \
           note_flags[i] == 8 or \
           note_flags[i] == 10:
            combined_mask.append(1)
        else:
            combined_mask.append(0)
        i += 1
    combined_mask = np.array(combined_mask)
    
    # Create plot
    figure_side = 6.0 # inches
    plt.figure(figsize = (figure_side, figure_side))
    panel_side = 6.0 # inches
    rel_panel_side = panel_side / figure_side
    panel = plt.axes([0.0, 0.0, rel_panel_side, rel_panel_side])
    panel.tick_params(bottom = False, labelbottom = False,
                      left = False, labelleft = False,
                      right = False, labelright = False,
                      top = False, labeltop = False)
    panel.axis('off')
    
    # Plot line, masking if the y-axis value is flagged
    y_axis_mask = ma.masked_where(combined_mask == 1, y_axis)
    panel.plot(x_axis, y_axis_mask.T,
               linewidth = 2.0,
               color = 'black')
    
    # Find max and min of array after masking
    max_val = y_axis_mask.max()
    min_val = y_axis_mask.min()
    
    # Set y-axis limits such that annotation can be read at center top
    H = max_val - min_val
    fraction_above = 0.22 # fraction of total panel height
    fraction_below = 0.05 # fraction of total panel height
    fraction_between = 1.0 - fraction_above - fraction_below
    space_above = fraction_above * (H / fraction_between)
    space_below = fraction_below * (H / fraction_between)
    panel.set_ylim(min_val - space_below, max_val + space_above)
    
    # Add annotation with title information
    annotation_text = 'CO UVIS EUV 57-117nm\n' + \
                      title_date + ' ' + \
                      "Saturn's rings " + direction_text
    panel.text(0.5, 0.975, annotation_text,
                horizontalalignment = 'center',
                verticalalignment = 'top',
                transform = panel.transAxes,
                fontsize = 32,
                color = (69/255, 120/255, 180/255),
                fontproperties = prop)
    
    # Save file
    thumb_px = 100 
    file_out = file[:-4] + '_preview_thumb.png'   
    filepath_out = os.path.join(save_path, file_out)
    plt.savefig(filepath_out, dpi = thumb_px / figure_side)
    plt.close()