#!/bin/bash
################################################################################
# Create preview images from PDS4 HST bundle browse collections
#
# Processes standalone MAST browse JPG/PNG files in browse_* directories
# (no PDS3 label pointers). One picmaker invocation per browse collection.
# Collection strip suffixes and WFC3 priority are defined in
# hst_bundle_browse_map.txt (default: browse_wfc3_drz only).
#
# Bundles with no browse_* collections fall back to FITS data collections
# defined in hst_bundle_fits_map.txt (e.g. hst_14930 → data_stis_x2d).
#
# Sample usage:
#   hst_bundle_previews.sh <path>/hst_16167/hst_16167-deliverable ...
#   hst_bundle_previews.sh <path>/hst_16167 ...
################################################################################

HOME=`pwd`

# get the absolute path of the executable
SELF_PATH=$(cd -P -- "$(dirname -- "$0")" && pwd -P) && SELF_PATH=$SELF_PATH/$(basename -- "$0")

# resolve symlinks
while [[ -h $SELF_PATH ]]; do
    DIR=$(dirname -- "$SELF_PATH")
    SYM=$(readlink "$SELF_PATH")
    SELF_PATH=$(cd "$DIR" && cd "$(dirname -- "$SYM")" && pwd)/$(basename -- "$SYM")
done

DIR=$(dirname "$SELF_PATH")
cd $DIR

resolve_path() {
    local path=$1
    if [ -d "$path" ]; then
        echo "$path"
    else
        echo "$HOME/$path"
    fi
}

resolve_deliverable() {
    local path=$(resolve_path "$1")

    if [ -f "$path/bundle.xml" ]; then
        echo "$path"
        return
    fi

    local deliverable
    for deliverable in "$path"/*-deliverable; do
        if [ -f "$deliverable/bundle.xml" ]; then
            echo "$deliverable"
            return
        fi
    done

    echo "hst_bundle_previews.sh: no bundle deliverable found under $path" 1>&2
    return 1
}

preview_outpath() {
    local deliverable=$1
    local outpath=${deliverable/volumes/previews}
    outpath=${outpath/HST_BUNDLES/previews}
    outpath=${outpath/bundles/previews}
    echo "$outpath"
}

BROWSE_MAP="$DIR/hst_bundle_browse_map.txt"
FITS_MAP="$DIR/hst_bundle_fits_map.txt"

browse_map_field() {
    local collection=$1
    local column=$2
    awk -v c="$collection" -v col="$column" '
        $0 !~ /^#/ && $0 !~ /^[[:space:]]*$/ && $1 == c {
            print $col
            exit
        }
    ' "$BROWSE_MAP"
}

browse_collection_policy() {
    local policy
    policy=$(browse_map_field "$1" 3)
    if [ -z "$policy" ]; then
        echo include
    else
        echo "$policy"
    fi
}

browse_strip_suffix() {
    local collection=$1
    local strip
    strip=$(browse_map_field "$collection" 2)
    if [ -z "$strip" ]; then
        echo "_${collection##*_}"
    else
        echo "$strip"
    fi
}

bundle_id_from_deliverable() {
    local deliverable=$1
    local id
    id=$(basename "$deliverable")
    echo "${id%-deliverable}"
}

fits_map_field() {
    local bundle_id=$1
    local column=$2
    awk -v b="$bundle_id" -v col="$column" '
        $0 !~ /^#/ && $0 !~ /^[[:space:]]*$/ && $1 == b {
            print $col
            exit
        }
    ' "$FITS_MAP"
}

fits_fallback_policy() {
    local policy
    policy=$(fits_map_field "$1" 4)
    if [ -z "$policy" ]; then
        echo skip
    else
        echo "$policy"
    fi
}

process_fits_fallback() {
    local deliverable=$1
    local outpath=$2
    local bundle_id
    local data_collection strip policy data_dir

    bundle_id=$(bundle_id_from_deliverable "$deliverable")
    policy=$(fits_fallback_policy "$bundle_id")
    if [ "$policy" != "include" ]; then
        return 1
    fi

    data_collection=$(fits_map_field "$bundle_id" 2)
    strip=$(fits_map_field "$bundle_id" 3)
    data_dir="$deliverable/$data_collection"

    if [ ! -d "$data_dir" ]; then
        echo "hst_bundle_previews.sh: FITS fallback $data_collection missing in $deliverable" 1>&2
        return 1
    fi

    mkdir -p "$outpath/$data_collection"

    picmaker "$data_dir" \
        --directory "$outpath/$data_collection" \
        --recursive --pattern \*.fits \
        --strip "$strip" --verbose=2 --proceed \
        --versions hst_bundle_fits_previews.txt

    if [ "$?" = "2" ]; then
        exit 2
    fi

    return 0
}

for bundlepath in "$@"
do
    deliverable=$(resolve_deliverable "$bundlepath") || exit 1
    outpath=$(preview_outpath "$deliverable")

    found_browse=0
    for browse_dir in "$deliverable"/browse_*; do
        [ -d "$browse_dir" ] || continue
        found_browse=1

        collection=$(basename "$browse_dir")
        policy=$(browse_collection_policy "$collection")
        if [ "$policy" = "skip" ]; then
            continue
        fi

        strip=$(browse_strip_suffix "$collection")
        mkdir -p "$outpath/$collection"

        for ext in jpg png JPG PNG; do
            picmaker "$browse_dir" \
                --directory "$outpath/$collection" \
                --recursive --pattern \*.$ext \
                --strip "$strip" --verbose=2 --proceed \
                --versions hst_bundle_previews.txt

            if [ "$?" = "2" ]; then
                exit 2
            fi
        done
    done

    if [ "$found_browse" = "0" ]; then
        if ! process_fits_fallback "$deliverable" "$outpath"; then
            echo "hst_bundle_previews.sh: no browse_* directories in $deliverable and no FITS fallback for $(bundle_id_from_deliverable "$deliverable")" 1>&2
        fi
    fi

done
