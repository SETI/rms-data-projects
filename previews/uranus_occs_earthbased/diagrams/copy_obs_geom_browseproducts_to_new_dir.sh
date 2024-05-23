#!/bin/bash

# Author: Mia J.T. Mace

# Set the parent directory path
parent_dir="/path/to/uranus_occs_earthbased"  # Replace this with the actual path to 'uranus_occs_earthbased' bundleset
# (tar.gz available at https://pds-rings.seti.org/pds4/archives-bundles/uranus_occs_earthbased/)

# Create the diagrams directory if it doesn't exist
mkdir -p "$parent_dir/obs_geom_pdfs"

# Initialise counter variable
copied_ctr=0

# Find all directories starting with 'uranus_occ_u' containing the file '_obs_geom.pdf' in browse/global
find "$parent_dir" -type d -name "uranus_occ_u*" -exec sh -c '
    for dirpath do
        # Look for the PDF file in the global directory of each occultation
        pdf_file=$(find "$dirpath/browse/global" -type f -name "*_obs_geom.pdf" -print -quit)
        if [ -n "$pdf_file" ]; then # If the diagram pdf exists then
            # Copy the file to the obs_geom_pdfs/ directory (at same level as individual uranus occ bundles)
            cp "$pdf_file" "$dirpath/../obs_geom_pdfs/"            
            echo "Copied: $pdf_file to $dirpath/../obs_geom_pdfs/"
	    # Increment the counter variable
            ((copied_ctr++))
        else
            # Print a warning if the PDF file does not exist
            echo "Warning: Diagram does not exist for occultation: $(basename "$dirpath")"
        fi
    done
    echo "Complete. $copied_ctr PDF diagrams copied."
' sh {} +

