#!/usr/bin/env python
################################################################################
# UVIS library
#
# This program looks through COUVIS data volumes from PDS Rings and read 
# each of binary data files into an array.
# For each array, it creates appropertiate images of four different sizes
# for its data type, which may be either "QUBE" or "TIMESERIES".
# The "QUBE" files may be either 2-dimensional (spectral information) or
# 3-dimensional (image), whereas, the "TIMESERIES" files are all dataplots
# respect to time.
#
# Usage:
#   python uvis_previews.py path/COUVIS_xxxx
#
# Operate on a copy of the volume.
# A set of png files will be created for each data file with a label.
#
# Mark Showalter & Deukkwon Yoon, PDS Rings Node, SETI Institute, January 2012
# Simplified main program 7/17/13: MRS
################################################################################

import numpy as np
import os, re, sys, traceback
from PIL import Image
from scipy.misc import imresize
import pylab
import glob
from pdsparser import PdsLabel

# Parameters relevant to a specific size diagram
FULL_DIAGRAM_PARAMS = {
    "SUFFIX": "_full.png",
    "SHAPE": (1024,1024),
    "LINE_WEIGHT": 5,
    "FRAME_WEIGHT": 4,
    "SHADOW_OFFSET": (2,2),
}

MED_DIAGRAM_PARAMS = {
    "SUFFIX": "_med.png",
    "SHAPE": (512,512),
    "LINE_WEIGHT": 3,
    "FRAME_WEIGHT": 2,
    "SHADOW_OFFSET": (1,1),
}

SMALL_DIAGRAM_PARAMS = {
    "SUFFIX": "_small.png",
    "SHAPE": (256,256),
    "LINE_WEIGHT": 2,
    "FRAME_WEIGHT": 2,
    "SHADOW_OFFSET": (1,1),
}

THUMB_DIAGRAM_PARAMS = {
    "SUFFIX": "_thumb.png",
    "SHAPE": (100,100),
    "LINE_WEIGHT": 1,
    "FRAME_WEIGHT": 1,
    "SHADOW_OFFSET": (0,0),
}

# Parameters relevant to all diagrams, regardless of size
GLOBAL_PARAMS = {
    "QUBE3D_MAX_ROWS": 6,             # absolute upper limit on rows per image
    "EUV_MAX_ROWS": 1,
    "EUV_MIN_ROW_SAMPLES": 1024,

    "FUV_MAX_ROWS": 1,
    "FUV_MIN_ROW_SAMPLES": 1024,

    "HSP_MAX_ROWS": 6,
    "HSP_MIN_ROW_SAMPLES": 1024,      # adds a new row if this limit exceeded,
                                      # until MAX_ROWS is reached
    "HDAC_MAX_ROWS": 6,
    "HDAC_MIN_ROW_SAMPLES": 1024,

    "EUV_COLOR": (0,0,255),           # EUV framed in blue
    "EUV_ALPHA": (1.,1.,1.),

    "FUV_COLOR": (0,255,0),           # FUV framed in green
    "FUV_ALPHA": (1.,1.,1.),

    "HSP_COLOR": (255,0,0),           # HSP framed in red
    "HSP_ALPHA": (1.,1.,1.),

    "HDAC_COLOR": (192,192,0),        # HDAC framed in 75% darkened yellow
    "HDAC_ALPHA": (1.,1.,1.),

    "SPECTRUM_COLOR": (0,255,255),    # spectra are plotted in cyan
    "SPECTRUM_ALPHA": (0.5,1.,1.),

    "PROFILE_COLOR": (192,0,255),     # profiles are plotted in violet
    "PROFILE_ALPHA": (1.,0.5,1.),

    "SHADOW_COLOR": (0,0,0),
    "SHADOW_ALPHA": (0.5,0.5,0.5),

    "JPEG_QUALITY": 90,
    "INTERP": ("nearest","bicubic")   # (method for scaling up, down)
}

################################################################################

def from_label(label_filespec):
    """
    Reads a UVIS label file and returns a tuple containing:
        (array, dict, object_type)

    If object_type is "TIME_SERIES", then the array is 1-D.
    If object_type is "QUBE", the array is 3-D in order (sample, line, band).
    """

    dict = uvis_from_file(label_filespec)

    # See if the object is a TIME_SERIES
    object_type = None
    try:
        object_dict = dict["TIME_SERIES"]
        object_type = "TIME_SERIES"
    except KeyError: pass

    # See if the object is a QUBE
    try:
        object_dict = dict["QUBE"]
        object_type = "QUBE"
    except KeyError: pass

    # See if the object is a SPECTRUM
    try:
        object_dict = dict["SPECTRUM"]
        object_type = "SPECTRUM"
    except KeyError: pass

    # If the object type remains undefined, we have a problem
    if object_type is None:
        raise RuntimeError("unrecognized object type: " + label_filespec)

    # Load the data array assuming 2-byte MSB unsigned integers
    data_filename = dict["^" + object_type].value
    dir = os.path.split(label_filespec)[0]
    data_filespec = os.path.join(dir, data_filename)

    if os.path.isfile(data_filespec) == False:
        label = os.path.split(label_filespec)[1][:-3]
        data_filespec = os.path.join(dir, label + "DAT")

    if os.path.isfile(data_filespec) == False:
        raise IOError("File does not exist: " + data_filespec)  

    array = np.fromfile(data_filespec, sep="", dtype=">u2")
    array = array.astype("int")

    # Interpret the array as a TIME_SERIES
    if object_type == "TIME_SERIES":
        return (time_series_array(array, dict), dict, object_type)
    
    # Interpret the array as a SPECTRUM
    if object_type == "SPECTRUM":
        return (spectrum_array(array, dict), dict, object_type)

    # Otherwise, interpret the array as a QUBE
    return (qube_array(array, dict), dict, object_type)

########################################

def uvis_from_file(filename):
    """
    Specially made to deal with a known syntax issue.
    It reads the file, make corrections, and passes the value.
    """

    # Read file
    lines = PdsLabel.load_file(filename)

    # Deal with corrupt syntax
    for i in range(len(lines)):
        line = lines[i]
        # Missing quotes
        if "CORE_UNIT" in line:
            if '"COUNTS/BIN"' not in line:
                lines[i] = re.sub( "COUNTS/BIN", '"COUNTS/BIN"', line)

        # Invalid comma
        if "ODC_ID" in line:
            lines[i] = re.sub(",", "", line)

    # Get dictionary
    this = PdsLabel.from_string(lines)
    this.filename = filename

    return this

########################################

def qube_array(array, dict):
    """
    Performs approperiate actions to "QUBE" arrays.
    """

    # Get the qube shape
    qube = dict["QUBE"]
    shape = (qube["CORE_ITEMS"][0].value,
             qube["CORE_ITEMS"][1].value,
             qube["CORE_ITEMS"][2].value)

    # Confirm that there are no surprises in the file structure
    assert shape[0] == 1024
    assert shape[1] == 1 or shape[1] == 64
    assert qube["AXES"].value == 3
    assert qube["AXIS_NAME"][0].value == "BAND"
    assert qube["AXIS_NAME"][1].value == "LINE"
    assert qube["AXIS_NAME"][2].value == "SAMPLE"
    assert qube["SUFFIX_ITEMS"][0].value == 0
    assert qube["SUFFIX_ITEMS"][1].value == 0
    assert qube["SUFFIX_ITEMS"][2].value == 0
    assert qube["CORE_ITEM_TYPE"].value == "MSB_UNSIGNED_INTEGER"
    assert qube["CORE_ITEM_BYTES"].value == 2
    assert (qube["CORE_NULL"].value == -1 or
            qube["CORE_NULL"].value == 65535)

    # Update the nulls properly
    array[array == 65535] = -1

    # Reshape the array in (sample, line, band) order and trim nulls
    python_shape = (shape[2], shape[1], shape[0])

    array = array.reshape(python_shape)
    array = trim_bands(array)
    array = trim_samples(array)
    array = trim_lines(array)

    return array

########################################

def time_series_array(array, dict):
    """
    Performs approperiate actions to "TIME_SERIES" arrays.
    """

    # Get the number of rows
    series = dict["TIME_SERIES"]
    rows = series["ROWS"].value

    # Confirm that there are no surprises in the file structure
    assert series["COLUMNS"].value   == 1
    assert series["ROW_BYTES"].value == 2

    column = series["COLUMN"]
    assert column["NAME"].value == "PHOTOMETER_COUNTS"
    assert column["DATA_TYPE"].value == "MSB_UNSIGNED_INTEGER"

    return array

########################################

def spectrum_array(array, dict):
    """
    Performs approperiate actions to "SPECTRUM" arrays.
    """

    # Get the number of rows
    spectrum = dict["SPECTRUM"]
    rows = spectrum["ROWS"].value

    # Confirm that there are no surprises in the file structure
    assert spectrum["COLUMNS"].value   == 1
    assert spectrum["ROW_BYTES"].value == 2

    column = spectrum["COLUMN"]
    assert column["NAME"].value == "SPECTRUM"
    assert column["DATA_TYPE"].value == "MSB_UNSIGNED_INTEGER"

    return array

################################################################################

#Trim null values from the array
def trim_bands(array):

    for b in range(array.shape[-1]):
        if np.all(array[...,0] == -1):
            array = array[...,1:]
        else: break

    for b in range(array.shape[-1]):
        if np.all(array[...,-1] == -1):
            array = array[...,:-1]
        else: break

    return array

def trim_samples(array):

    for b in range(array.shape[0]):
        if np.all(array[0,...] == -1):
            array = array[1:,...]
        else: break

    for b in range(array.shape[0]):
        if np.all(array[-1,...] == -1):
            array = array[:-1, ...]
        else: break

    return array

def trim_lines(array):

    for b in range(array.shape[1]):
        if np.all(array[:,0,:] == -1):
            array = array[:,1:,:]
        else: break

    for b in range(array.shape[1]):
        if np.all(array[:,-1,:] == -1):
            array = array[:,:-1,:]
        else: break

    return array

################################################################################

def to_picture(array, dict, object_type, filename, params):
    """
    Creates a square image of the specified name based on the contents of a
    UVIS data array, a label dictionary, and an object type.
    """

    # Get file name
    product_id = dict["PRODUCT_ID"].value

    # Get instrument name from the file name
    if   product_id.startswith("EUV"):  inst = "EUV"
    elif product_id.startswith("FUV"):  inst = "FUV"
    elif product_id.startswith("HDAC"): inst = "HDAC"
    elif product_id.startswith("HSP"):  inst = "HSP"
    else:
        raise ValueError("unrecognized instrument in PRODUCT_ID: " + product_id)

    if object_type == "QUBE":
        if array.shape[1] == 1:
            array = array.reshape((array.shape[0], array.shape[2]))
            qube2d_to_picture(array, filename, inst, params)
        else:
            qube3d_to_picture(array, filename, inst, params)
    elif object_type == "TIME_SERIES":
        time_series_to_picture(array, filename, inst, params)

    elif object_type == "SPECTRUM":
        spectrum_to_picture(array, filename, inst, params)

########################################

def qube3d_to_picture(array, filename, inst, params):
    """
    Converts a 3-D spectral image qube into an RGB image. It wraps long strips
    inside a square boundary and then save the result to an image file.
    """

    (vsize,hsize) = params["SHAPE"]
    gap = params["FRAME_WEIGHT"]
    
    # Reorder the axes (line,sample,band)
    array = array.swapaxes(0,1)

    # Resample into (R,G,B)
    bands = array.shape[2]
    b1 =    bands  / 3
    b2 = (2*bands) / 3

    # Create a copy
    rgb = np.empty(array.shape[:2] + (3,), dtype="float")

    # Split into three arrays and average band values
    rgb[...,2] = np.mean(array[...,   :b1], axis=-1)
    rgb[...,1] = np.mean(array[..., b1:b2], axis=-1)
    rgb[...,0] = np.mean(array[..., b2:  ], axis=-1)

    # Determine the wrapping requirements
    (height, width) = array.shape[:2]

    tiles = width/float(height)
    rows = int(np.sqrt(tiles) + 0.5)
    rows = np.clip(rows, 1, GLOBAL_PARAMS["QUBE3D_MAX_ROWS"])

    width = rows * hsize - 2*gap
    height = (vsize - gap)/rows - gap

    # Convert to unsigned bytes in the proper shape
    rgb *= 256. / max(1.,np.max(rgb))
    rgb = rgb.clip(0,255)
    bytes = resize_image(rgb, (height,width), mode="RGB")

    # Wrap the image
    wrapped = wrap_rgb(bytes, (vsize,hsize), rows,
                               GLOBAL_PARAMS[inst + "_COLOR"])

    # Write the file
    pil = Image.frombytes("RGB", (hsize,vsize), wrapped.tostring())
    pil.save(filename, quality=GLOBAL_PARAMS["JPEG_QUALITY"])

########################################

def qube2d_to_picture(array, filename, inst, params):
    """
    Writes a single spectrogram into an image file. Wavelength increases
    upward and sample number toward the right.
    """

    (vsize,hsize) = params["SHAPE"]
    gap = params["FRAME_WEIGHT"]
    width = hsize - 2*gap
    height = vsize - 2*gap
    
    # Reorder the axes (band,sample) and rescale
    array = array.swapaxes(0,1) * 256. / max(1, np.max(array))

    # Convert to the proper shape
    resized = resize_image(array, (height,width), mode="F")
    resized = resized.clip(0,255.99999999999)

    # Create an RGB array of unsigned bytes
    rgb = np.empty(resized.shape + (3,), dtype="uint8")
    rgb[...] = resized[..., np.newaxis]

    # Overplot the spectrum in red
    spectrum = np.mean(resized, axis=1)
    overplot_rgb_vertical(rgb, spectrum, params, "SPECTRUM")

    # Overplot the profile in yellow
    profile = np.mean(resized, axis=0)
    overplot_rgb(rgb, profile, params, "PROFILE")

    # Wrap the image
    wrapped = wrap_rgb(rgb[::-1], (vsize,hsize), 1,
                               GLOBAL_PARAMS[inst + "_COLOR"])

    # Write the file
    pil = Image.frombytes("RGB", (hsize,vsize), wrapped.tostring())
    pil.save(filename, quality=GLOBAL_PARAMS["JPEG_QUALITY"])

########################################

def time_series_to_picture(array, filename, inst, params):
    """
    Writes a time series into an image file. Sample increases toward the
    right. The signal intensity is represented as a grayscale image and is
    over-plotted with points that indicate intensity vs. sample.
    """

    # Rescale the array
    array = array * 256. / float(max(1., np.max(array)))

    # Convert to the proper shape
    (vsize,hsize) = params["SHAPE"]
    gap = params["FRAME_WEIGHT"]

    maxrows = GLOBAL_PARAMS[inst + "_MAX_ROWS"]
    minsamp = GLOBAL_PARAMS[inst + "_MIN_ROW_SAMPLES"]

    rows = max(1, array.size // minsamp)
    rows = min(rows, maxrows)

    height = (hsize - gap)/rows - gap
    width  = rows * vsize - 2*gap

    resized = resize_image(array[np.newaxis,:], (height,width), mode="F")

    # Create an RGB array of unsigned bytes
    rgb = np.empty(resized.shape + (3,), dtype="uint8")
    rgb[...] = resized[..., np.newaxis]

    # Overplot the profile in the selected color
    profile = np.max(resized[0]) - resized[0]
    overplot_rgb(rgb, profile, params, inst)

    # Wrap the image
    wrapped = wrap_rgb(rgb, (vsize,hsize), rows,
                               GLOBAL_PARAMS[inst + "_COLOR"])

    # Write the file
    pil = Image.frombytes("RGB", (hsize,vsize), wrapped.tostring())
    pil.save(filename, quality=GLOBAL_PARAMS["JPEG_QUALITY"])

########################################

def spectrum_to_picture(array, filename, inst, params):
    """
    Writes a spectrum into an image file. Wavelength increases toward the
    right.
    """

    # Rescale the array
    array = array * 256. / float(max(1., np.max(array)))

    # Convert to the proper shape
    (vsize,hsize) = params["SHAPE"]
    gap = params["FRAME_WEIGHT"]

    maxrows = GLOBAL_PARAMS[inst + "_MAX_ROWS"]
    minsamp = GLOBAL_PARAMS[inst + "_MIN_ROW_SAMPLES"]

    rows = max(1, array.size // minsamp)
    rows = min(rows, maxrows)
    
    height = (hsize - gap)/rows - gap
    width  = rows * vsize - 2*gap

    resized = resize_image(array[np.newaxis,:], (height,width), mode="F")

    # Create an RGB array of unsigned bytes
    rgb = np.ones(resized.shape + (3,), dtype="uint8")
    rgb[...] = 128

    # Overplot the profile in the selected color
    profile = np.max(resized[0]) - resized[0]
    overplot_rgb(rgb, profile, params, inst)

    # Wrap the image
    wrapped = wrap_rgb(rgb, (vsize,hsize), rows,
                               GLOBAL_PARAMS[inst + "_COLOR"])

    # Write the file
    pil = Image.frombytes("RGB", (hsize,vsize), wrapped.tostring())
    pil.save(filename, quality=GLOBAL_PARAMS["JPEG_QUALITY"])

########################################

def overplot_rgb(rgb, profile, params, inst, flipped=False):
    """
    Plots a profile as a function of the trailing axis atop an RGB image
    array.
    """

    weight = params["LINE_WEIGHT"]
    (height, width) = rgb.shape[:2]

    profile = np.asfarray(profile) / max(1., np.max(profile))
    profile = (profile * (height - weight)).astype("int")
    profile = profile.clip(0, height - weight - 1)

    offset = params["SHADOW_OFFSET"]
    if flipped: offset = offset[::-1]

    if offset != (0,0):
        overplot_rgb1(rgb, profile, weight, GLOBAL_PARAMS["SHADOW_COLOR"],
                                            GLOBAL_PARAMS["SHADOW_ALPHA"],
                                            offset)

    overplot_rgb1(rgb, profile, weight, GLOBAL_PARAMS[inst + "_COLOR"],
                                        GLOBAL_PARAMS[inst + "_ALPHA"])

def overplot_rgb1(rgb, profile, weight, color, alpha, offset=(0,0)):

    (dj,di) = offset
    (height, width) = rgb.shape[:2]
    halfwt = weight / 2

    color = np.array(color)
    alpha = np.array(alpha)

    for i in range(profile.size):
      for ii in range(max(0, i - halfwt + di), min(width, i + halfwt + 1 + di)):
        j0 = max(0, profile[i] + dj)
        j1 = min(height, profile[i] + weight + 1 + dj)
#       Doesn't work!
#         rgb[j0:j1, ii, :] *= (1. - alpha)
#         rgb[j0:j1, ii, :] += alpha * color

        for j in range(j0,j1):
          for k in range(3):
            old_rgb = rgb[j,ii,k]
            new_rgb = old_rgb * (1. - alpha[k]) + alpha[k] * color[k] + 0.5
            new_rgb = min(max(0, new_rgb), 255)
            rgb[j,ii,k] = new_rgb

def overplot_rgb_vertical(rgb, profile, params, inst):
    """
    Plots a profile as a function of the trailing axis atop an image
    array. Plots the profile vs. the vertical axis instead of the horizontal.
    """

    # Operation occurs in-place inside the rgb array
    overplot_rgb(rgb.swapaxes(0,1), profile, params, inst, flipped=True)

########################################

def wrap_rgb(array, shape, rows, frame_color):
    """
    Returns the value of a wide array wrapped into a set of rows enclosed by
    the given shape.
    """

    # Construct the blank array
    wrapped = np.empty(shape + array.shape[2:], dtype=array.dtype)
    wrapped[...,:] = frame_color

    # Determine the gap between rows
    gap = (shape[0] - rows * array.shape[0]) // (rows+1)
    row_stride = (shape[0] - gap) / rows
    row_height = row_stride - gap
    width = shape[1] - 2*gap

    # Copy the data...
    l0 = gap
    s0 = gap
    for i in range(rows-1):
        wrapped[l0:l0+row_height,gap:-gap,...] = array[:,s0:s0+width,...]
        l0 += row_stride
        s0 += width

    wrapped[l0:l0+row_height,gap:-gap,...] = array[:,-width:,...]

    return wrapped

########################################

def resize_image(array, shape, mode):
    """
    Resizes an array using the PIL library method. Selects among the two
    given interpolation methods depending on whether it is doing enlargement or
    shrinkage. Input interp is a tuple containing (enlargement method, shrinkage
    method).
    """

    (interp_up, interp_down) = GLOBAL_PARAMS["INTERP"]

    if array.shape[0] >= shape[0] and array.shape[1] >= shape[1]:
        return imresize(array, shape, mode=mode, interp=interp_down)

    if array.shape[0] <= shape[0] and array.shape[1] <= shape[1]:
        return imresize(array, shape, mode=mode, interp=interp_up)

    # Note: It's important to down-sample before any up-sampling. These arrays
    # can be extremely large
    if array.shape[0] > shape[0]:
        array = imresize(array, (shape[0], array.shape[1]), mode=mode,
                                                            interp=interp_down)

    if array.shape[1] > shape[1]:
        array = imresize(array, (array.shape[0], shape[1]), mode=mode,
                                                            interp=interp_down)

    if array.shape[0] < shape[0]:
        array = imresize(array, (shape[0], array.shape[1]), mode=mode,
                                                            interp=interp_up)

    if array.shape[1] < shape[1]:
        array = imresize(array, (array.shape[0], shape[1]), mode=mode,
                                                            interp=interp_up)

    return array

################################################################################
# Main program
################################################################################

def process1(label_filespec):
    """Processes a single UVIS data file, creating a set of preview images in
    the same directory."""

    try:
        (array, dict, object_type) = from_label(label_filespec)
        print label_filespec

        label_filespec = os.path.abspath(label_filespec)
        prefix = os.path.splitext(label_filespec)[0]

        for params in (FULL_DIAGRAM_PARAMS, MED_DIAGRAM_PARAMS,
                       SMALL_DIAGRAM_PARAMS, THUMB_DIAGRAM_PARAMS):

            image_filename = prefix + params["SUFFIX"]
            image_filename = image_filename.replace('/volumes/', '/previews/')
            absdir = os.path.split(image_filename)[0]
            if not os.path.exists(absdir):
                os.makedirs(absdir)

            to_picture(array, dict, object_type, image_filename, params)

    except Exception as e:
        print 'ERROR IN ' + label_filespec
        print e
        traceback.print_tb(sys.exc_info()[2])

    return

def is_data_label(filespec):
    test = filespec.upper()

    if 'CALIB/' in filespec: return False

    if not test.endswith('.LBL'): return False

    test = os.path.splitext(test)[0] + '.DAT'
    return os.path.exists(test)

def main():

    for arg in sys.argv[1:]:
        if os.path.isfile(arg):
            if is_data_label(arg):
                process1(arg)

        elif os.path.isdir(arg):
            for (root, dirs, files) in os.walk(os.path.join(arg, 'DATA')):
                for name in files:
                    filespec = os.path.join(root, name)
                    if is_data_label(filespec):
                        process1(filespec)

if __name__ == "__main__": main()

################################################################################
