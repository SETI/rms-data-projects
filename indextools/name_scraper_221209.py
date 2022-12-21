#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Nov 28 09:57:04 2022

@author: emiliesimpson
"""
import csv
import os
import re

from lxml import objectify

ns = {"pds":"http://pds.nasa.gov/pds4/pds/v1",
      "cassini": "http://pds.nasa.gov/pds4/mission/cassini/v1"}

fullpaths = []
lids_and_paths = {}
source_lids_all = []

### Enter directory containing bundle.xml (default: current directory)
BUNDLE_MAIN = input("Enter bundle: ")
PATH_MAIN = ("/Users/emiliesimpson/holdingsdisk/pds4-holdings/bundles/"
             + str(BUNDLE_MAIN))

for path, subdirs, files in os.walk(PATH_MAIN + "/"):
    for name in files:
        if name == "bundle.xml":
            bundle_file_path = os.path.join(path, name)
                      
bundle_root = objectify.parse(bundle_file_path, 
                       objectify.makeparser(remove_blank_text=True)).getroot()

bundle_member_entries = bundle_root.findall("pds:Bundle_Member_Entry", 
                                            namespaces=ns)

for bundle_member_entry in bundle_member_entries:
    if bundle_member_entry.reference_type.text == "bundle_has_data_collection":
        lid_source = bundle_member_entry.lid_reference.text

lid_source = lid_source.split(":")
data_collection_term = lid_source[-1]

unwanted_files = ["bundle.xml", "collection_context.xml", 
                  "collection_document.xml", "collection_browse.xml",
                  "collection_xml_schema.xml", "collection_data.xml",
                  "collection_data_raw.xml", ".DS_Store", "uranus_occ_support"]

data_collection_bundles = os.listdir(PATH_MAIN + "/")
for data_bundle in data_collection_bundles:
    fullpath = PATH_MAIN + "/" + data_bundle
    for root, dirs, files in os.walk(fullpath):
        for file in files:
            if data_collection_term in os.path.join(root, file):
                if file.endswith(".xml"):
                    if not file.endswith(("_wavelengths.xml", "_sqw.xml")):
                        fullpaths.append(os.path.join(root, file))   
                            
for fullpath in fullpaths[:50]:
    lid_root = objectify.parse(fullpath, 
                               objectify.makeparser(remove_blank_text=True
                                                    )).getroot()
    lid = lid_root.Identification_Area.logical_identifier
    lids_and_paths.update({str(lid):fullpath})

for data_bundle in data_collection_bundles:
    bundle_path = PATH_MAIN + "/" + data_bundle
    for root, dirs, files in os.walk(bundle_path):
        for file in files:
            if (data_collection_term + "/collection_" + data_collection_term + 
                ".csv" in os.path.join(root, file)):
                if "uranus_occ_support" not in os.path.join(root, file):
                    with open(os.path.join(root, file), "r") as lids:
                        source_lids = lids.readlines()
                        for source_lid in source_lids:
                            source_lids_all.append(source_lid)
                        
source_lids_all = [re.sub("[P, S,]", "", lid) for lid in source_lids_all]
source_lids_all = [re.sub("::\d.\d", "", lid) for lid in source_lids_all]
source_lids_all = [lid.strip() for lid in source_lids_all]

LIDS = list(lids_and_paths.keys())

# =============================================================================
# with open("/Users/emiliesimpson/Desktop/" + str(BUNDLE_MAIN) + 
#           "_general.csv", mode="w") as index_csv:
#     csv_output = csv.writer(index_csv, delimiter=",", quoting=csv.QUOTE_NONE)
#     for lid in LIDS:
#         if lid in source_lids_all:
#             root = objectify.parse(lids_and_paths[lid],
#                    objectify.makeparser(remove_blank_text=True)).getroot()
#             targs = root.Observation_Area.findall("pds:Target_Identification",
#                                                   namespaces=ns)
#             names = [targ.name for targ in targs]
#             length = len(names)
#             csv_output.writerow([lid] + [length] + names)
# =============================================================================
