#!/bin/bash

if [ $# -eq 0 ]; then
    echo "Usage: $0 <pds4-holdings-dir>"
    exit 1
fi

PDS4_HOLDINGS_DIR=$1

BUNDLE=cassini_uvis_solarocc_beckerjarmak2023

mkdir -p $PDS4_HOLDINGS_DIR/metadata/$BUNDLE
pds4_create_xml_index $PDS4_HOLDINGS_DIR/bundles/$BUNDLE "data/*ingress.xml" "data/*egress.xml" --add-extra-file-info lid,bundle,bundle_lid,filepath --sort-by filepath --fixed-width --simplify-xpaths --limit-xpaths limit_cassini_uvis_solarocc_beckerjarmak2023.txt --dont-number-unique-tags --generate-label ancillary --output-index-file $PDS4_HOLDINGS_DIR/metadata/$BUNDLE/${BUNDLE}_index.csv --rename-headers rename_cassini_uvis_solarocc_beckerjarmak2023.txt
