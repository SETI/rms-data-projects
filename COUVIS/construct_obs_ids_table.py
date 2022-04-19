#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#construct_obs_ids_table.py

"""
Created on Thu Dec 16 13:39:19 2021

@author: Mia Mace

Constructs 2 column table of date, observation id from COUVIS_0999_supplemental_index.tab 
To fix bug with previous observation_ids.tab missing obs ids with "_ss" suffix, e.g. fuv2000_209_02_10_40.dat (PDS4) , FUV2000_209_02_10_40.DAT (PDS3) 
This new obs id table is read in by uvis_data_raw_labeler.py during PDS4 UVIS migration

Source: COUVIS_0999_supplemental_index.tab from https://pds-rings.seti.org/holdings/metadata/COUVIS_0xxx/COUVIS_0999/

"""

import pandas as pd

# Create a pandas dataframe of basenames (which contains the date info) and obs ids:
basename_obsid_df = pd.read_csv("./COUVIS_0999_supplemental_index.tab", header=None, usecols=[2,3])

# Name the columns:
basename_obsid_df.columns = ['basename', 'obsid']

# Remove any characters that are not numeric or an underscore (ie remove instrument prepended: EUV, FUV, HDAC, HSP)
dates = basename_obsid_df.basename.str.replace(r'[^0-9_]', '', regex=True) # This works because there is no underscore between inst and date 
basename_obsid_df['date'] = dates

# Save only the date, obs id columns and order by ascending date
basename_obsid_df = basename_obsid_df.sort_values(by=["date"], ascending=True)
basename_obsid_df = basename_obsid_df.drop_duplicates(subset="date") # Otherwise there would be duplication from EUV, FUV, HDAC, HSP
# Save file (as (date, obsid)):
column_order = ['date', 'obsid']
basename_obsid_df[column_order].to_csv("./observation_ids_mjtm_dropduplicates.tab", index=False, header=False)

