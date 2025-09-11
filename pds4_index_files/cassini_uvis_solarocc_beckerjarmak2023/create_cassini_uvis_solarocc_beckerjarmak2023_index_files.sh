#!/bin/bash

if [ $# -eq 0 ]; then
    echo "Usage: $0 <pds4-holdings-dir>"
    exit 1
fi

PDS4_HOLDINGS_DIR=$1

BUNDLE=cassini_uvis_solarocc_beckerjarmak2023

# mkdir -p $PDS4_HOLDINGS_DIR/metadata/$BUNDLE

pds4_create_xml_index $PDS4_HOLDINGS_DIR/bundles/$BUNDLE/$BUNDLE "data/*ingress.xml" "data/*egress.xml" --add-extra-file-info lid,bundle,bundle_lid,filepath --sort-by filepath --simplify-xpaths --limit-xpaths limit_cassini_uvis_solarocc_beckerjarmak2023.txt --simplify-xpaths --dont-number-unique-tags --rename-headers rename_cassini_uvis_solarocc_beckerjarmak2023.txt --generate-label ancillary --output-index-file ${BUNDLE}_index.csv

# pds4_create_xml_index $PDS4_HOLDINGS_DIR/bundles/$BUNDLE/$BUNDLE "data/*ingress.xml" "data/*egress.xml" --add-extra-file-info lid,bundle,bundle_lid,filepath --sort-by filepath --simplify-xpaths --limit-xpaths limit_cassini_uvis_solarocc_beckerjarmak2023.txt --simplify-xpaths --dont-number-unique-tags --rename-headers rename_cassini_uvis_solarocc_beckerjarmak2023.txt --generate-label ancillary --output-index-file $PDS4_HOLDINGS_DIR/metadata/$BUNDLE/${BUNDLE}_index.csv

# pds4_create_xml_index $PDS4_HOLDINGS_DIR/bundles/$BUNDLE "data/*ingress.xml" "data/*egress.xml" --add-extra-file-info lid,bundle,bundle_lid,filepath --sort-by filepath --fixed-width --limit-xpaths limit_cassini_uvis_solarocc_beckerjarmak2023.txt --dont-number-unique-tags --simplify-xpaths --rename-headers rename_cassini_uvis_solarocc_beckerjarmak2023.txt --generate-label ancillary --output-index-file $PDS4_HOLDINGS_DIR/metadata/$BUNDLE/${BUNDLE}_index.csv

# pds4_create_xml_index $PDS4_HOLDINGS_DIR/bundles/$BUNDLE/$BUNDLE "data/*ingress.xml" "data/*egress.xml" --generate-label ancillary --output-index-file ${BUNDLE}_index.csv --limit-xpaths limit_cassini_uvis_solarocc_beckerjarmak2023.txt --add-extra-file-info lid,bundle,bundle_lid,filepath --sort-by filepath --dont-number-unique-tags --simplify-xpaths --output-headers-file headers.txt --rename-headers rename_cassini_uvis_solarocc_beckerjarmak2023.txt

# pds4_create_xml_index $PDS4_HOLDINGS_DIR/bundles/cassini_uvis_solarocc_beckerjarmak2023 "data/*269_solar_time_series_*gress.xml" --limit-xpaths limit_cassini_uvis_solarocc_beckerjarmak2023_bug2.txt --dont-number-unique-tags --config-file config_cassini_uvis_solarocc_beckerjarmak2023.txt --output-index-file index.csv --output-headers-file headers.txt
