#!/bin/bash

if [ $# -eq 0 ]; then
    echo "Usage: $0 <pds4-holdings-dir>"
    exit 1
fi

PDS4_HOLDINGS_DIR=$1

BUNDLESET=uranus_occs_earthbased
for i in `(cd $PDS4_HOLDINGS_DIR/bundles/$BUNDLESET; ls -d *_u[0-9]*)`
do
    echo Processing $i
    mkdir -p $PDS4_HOLDINGS_DIR/metadata/$BUNDLESET/$i
    pds4_create_xml_index $PDS4_HOLDINGS_DIR/bundles/$BUNDLESET "${i}/data/rings/*_*00m.xml" --add-extra-file-info lid,bundle,bundle_lid,filepath --sort-by filepath --fixed-width --rename-headers rename_rings.txt --generate-label ancillary --output-index-file $PDS4_HOLDINGS_DIR/metadata/$BUNDLESET/${i}/${i}_rings_index.csv
    pds4_create_xml_index $PDS4_HOLDINGS_DIR/bundles/$BUNDLESET "${i}/data/global/*_*00m.xml" --add-extra-file-info lid,bundle,bundle_lid,filepath --sort-by filepath --fixed-width --rename-headers rename_global.txt --generate-label ancillary --output-index-file $PDS4_HOLDINGS_DIR/metadata/$BUNDLESET/${i}/${i}_global_index.csv
    pds4_create_xml_index $PDS4_HOLDINGS_DIR/bundles/$BUNDLESET "${i}/data/atmosphere/*_atmos_*.xml" --add-extra-file-info lid,bundle,bundle_lid,filepath --sort-by filepath --fixed-width --rename-headers rename_atmosphere.txt --generate-label ancillary --output-index-file $PDS4_HOLDINGS_DIR/metadata/$BUNDLESET/${i}/${i}_atmosphere_index.csv
done
