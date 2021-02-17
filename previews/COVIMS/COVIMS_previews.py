#!/usr/bin/env python

import numpy as np
import pdsparser
import picmaker
from PIL import Image
import sys, os, os.path

################################################################################
# Routines to read QUB files and extract key information from the label.
################################################################################

# Function to return the sum of elements as an int
def sumover(item):
    try:
        return sum(item)
    except TypeError:
        return int(item)

def FromFile(filename):
    """Returns the extracted cube in (band,line,sample) ordering and also the
    ISIS label."""

    # Read and parse the label
    label = pdsparser.PdsLabel.FromFile(filename)

    # Determine the stride in units of CORE_ITEM_BYTES
    qube = label["QUBE"]
    core_samples = int(qube["CORE_ITEMS"][0])
    core_bands   = int(qube["CORE_ITEMS"][1])
    core_lines   = int(qube["CORE_ITEMS"][2])

    core_bytes   = int(qube["CORE_ITEM_BYTES"])

    suffix_samples = int(qube["SUFFIX_ITEMS"][0])
    suffix_bands   = int(qube["SUFFIX_ITEMS"][1])
    suffix_lines   = int(qube["SUFFIX_ITEMS"][2])

    if suffix_samples > 0:
        sample_suffix_bytes = sumover(qube["SAMPLE_SUFFIX_ITEM_BYTES"])
    else:
        sample_suffix_bytes = 0

    if suffix_bands > 0:
        band_suffix_bytes = sumover(qube["BAND_SUFFIX_ITEM_BYTES"])
    else:
        band_suffix_bytes = 0

    # Suffix samples in units of the core item
    suffix_samples_scaled = sample_suffix_bytes / core_bytes
    suffix_bands_scaled   = band_suffix_bytes / core_bytes

    stride = np.empty((3), "int")
    stride[0] = 1
    stride[1] = core_samples + suffix_samples_scaled
    stride[2] = (stride[1] * core_bands +
                 suffix_bands_scaled * (core_samples + suffix_samples))

    # Determine the dtype for the file core
    core_type = str(qube["CORE_ITEM_TYPE"])

    if "SUN_" in core_type or "MSB_" in core_type:
        core_dtype = ">"
    elif "PC_" in core_type or  "LSB_" in core_type:
        core_dtype = "<"
    else:
        raise TypeError("Unrecognized byte order: " + core_type)

    if  "UNSIGNED" in core_type: core_dtype += "u"
    elif "INTEGER" in core_type: core_dtype += "i"
    elif "REAL"    in core_type: core_dtype += "f"
    else:
        raise TypeError("Unrecognized data type: " + core_type)

    core_dtype += str(core_bytes)

    # Read the file
    buffer = np.fromfile(filename, core_dtype)

    # Select the core items
    record_bytes = int(label["RECORD_BYTES"])
    qube_record  = int(label["^QUBE"])

    offset = record_bytes * (qube_record-1) / core_bytes
    size = stride[2] * core_lines

    buffer = buffer[offset:offset+size]

    # Organize by lines
    buffer = buffer.reshape(core_lines, stride[2])

    # Extract the core as a native 3-D array
    core_dtype = "=" + core_dtype[1:]
    cube = np.empty((core_bands, core_lines, core_samples), core_dtype)

    shape = (core_bands, stride[1])
    size  = shape[0] * shape[1]
    
    for l in range(core_lines):
        slice = buffer[l,0:size]
        slice = slice.reshape(shape)
        slice = slice[:,0:core_samples]

        cube[:,l,:] = slice[:,:]

    # Identify empty regions
    flags = (str(qube["POWER_STATE_FLAG"][0]) != "OFF",
             str(qube["POWER_STATE_FLAG"][1]) != "OFF")

    return (cube, label, flags)

def Wavelengths(label):
    """Returns the array of wavelengths as a numpy array."""

    sequence = label["QUBE"]["BAND_BIN"]["BAND_BIN_CENTER"]
    list = []
    for item in sequence:
        list.append(float(item))
    return np.array(list)

def Bands(wavelengths, wmin, wmax, minbands=0, channel=None):
    """Returns a tuple containing the minimum and maximum bands capturing the
    specified range of wavelengths."""

    if   channel == "VIS":
        wavelengths = wavelengths[:96]
        offset = 0
    elif channel == "IR":
        wavelengths = wavelengths[96:]
        offset = 96
    else:
        offset = 0

    select = np.where((wavelengths >= wmin) & (wavelengths <= wmax))
    if select[0].size < 1:
        select = np.where(wavelengths >= wmin)
        bmin = select[0][0]
        bmax = bmin + 1
    else:
        bmin = select[0][0]
        bmax = select[0][-1] + 1

    if bmin + offset < 96 and bmax + offset > 96:
        raise ValueError("Band range crosses VIS/IR boundary")

    needed = minbands - (bmax - bmin)
    if needed > 0:
        bmin = max(bmin - needed/2, 0)
        bmax = min(bmin + minbands, wavelengths.size)
        bmin = bmax - minbands

    return (bmin + offset, bmax + offset)

################################################################################
# Routines to process slices of the cube.
################################################################################

def PrepCube(cube):

    # Convert to float and clip
    cube = cube.astype("float")

    # Find empty rows
    lines = np.any(np.any(cube, axis=2), axis=0)
    assert(np.all(lines))

    l0 = np.where(lines)[0][0]
    l1 = np.where(lines)[0][-1] + 1

    # Find empty columns
    samples = np.any(np.any(cube, axis=1), axis=0)
    assert(np.all(samples))

    s0 = np.where(samples)[0][0]
    s1 = np.where(samples)[0][-1] + 1

    return cube[:,l0:l1,s0:s1]

def LineCorr(image, offset=1):
    """Returns the correlation between nearby pixels in the same column."""

    top    = image[:-offset,:]
    bottom = image[ offset:,:]
    return np.sum(top * bottom) / np.sqrt(np.sum(top * top) *
                                          np.sum(bottom * bottom))

def SampleCorr(image, offset=1):
    """Returns the correlation between nearby pixels in the same row."""

    left  = image[:,:-offset]
    right = image[:, offset:]
    return np.sum(left * right) / np.sqrt(np.sum(left * left) *
                                          np.sum(right * right))

def BestAxis(cube, max_offset=3):
    """Identifies the best axis for averaging. It is the one with the fewest
    pixels or, in a square, the one with the higher correlation."""

    cube = cube.astype("float")     # Algorithm fails for ints due to overflow.

    if cube.shape[1] > cube.shape[2]: return 2
    if cube.shape[2] > cube.shape[1]: return 1

    lcorr = 0
    scorr = 0
    for offset in range(1,max_offset+1):
        lcorr += LineCorr(  cube, offset)
        scorr += SampleCorr(cube, offset)

    if lcorr > scorr: return 1
    else:             return 2

def MeanOverBands(cube, tuple):
    """Returns the mean within a specified tuple defining starting and ending
    bands defined by a tuple."""

    if type(tuple[0]) == type(tuple):
        slice = None
        for t in tuple:
            if slice is None:
                slice = cube[t[0]:t[1]]
            else:
                slice = np.vstack((slice, cube[t[0]:t[1]]))
    else:
        slice = cube[tuple[0]:tuple[1]]

    shape = slice.shape

    # Find the mean excluding the darkest 25% and brightest 25% of pixels.
    sorted = np.sort(slice, axis=0)
    blo =      shape[0]/4
    bhi = (3 * shape[0])/4
    image = np.mean(sorted[blo:bhi], axis=0)

    return image

################################################################################
# Routines to construct a variety of color images from the raw VIMS cubes
################################################################################

def BandsToRGB(cube, rbands, gbands, bbands, percents=(1.,99.)):
    """Returns the RGB picture array for the VIS channel."""

    # Create and populate the target buffer
    rgb = np.empty((cube.shape[1], cube.shape[2], 3))
    rgb[:,:,0] = MeanOverBands(cube, rbands)   # red
    rgb[:,:,1] = MeanOverBands(cube, gbands)   # green
    rgb[:,:,2] = MeanOverBands(cube, bbands)   # blue

    # Normalize all three channels together
    sorted = np.sort(rgb.flatten())
    minrgb = sorted[int(percents[0]/100. * sorted.size)]
    maxrgb = sorted[int(percents[1]/100. * sorted.size)]

    minrgb = max(minrgb, 0.)
    rgb -= minrgb
    if maxrgb != minrgb:            # Don't divide by zero
        rgb /= (maxrgb - minrgb)

    # Return the array
    return rgb.clip(0.,1.)

def ExpandRGB(rgb, percents=(1.,99.)):
    """Returns the RGB picture array with each channel scaled independently."""

    # Check the self-correlation of each band.
    # Use min() to avoid instrumental artifacts along one axis
    corr = np.array([min(LineCorr(rgb[:,:,0]), SampleCorr(rgb[:,:,0])),
                     min(LineCorr(rgb[:,:,1]), SampleCorr(rgb[:,:,1])),
                     min(LineCorr(rgb[:,:,2]), SampleCorr(rgb[:,:,2]))])
    corr /= np.max(corr)

    # Scale each channel but scale by the self-correlation. This suppresses
    # noisy channels
    for band in range(3):
        sorted = np.sort(rgb[:,:,band].flatten())
        bandmin = sorted[int(percents[0]/100. * sorted.size)]
        bandmax = sorted[int(percents[1]/100. * sorted.size)]

        bandmin = max(bandmin, 0.)
        rgb[:,:,band] -= bandmin
        if bandmax != bandmin:      # Don't divide by zero
            rgb[:,:,band] /= (bandmax - bandmin)
        rgb[:,:,band] = rgb[:,:,band].clip(0,1) * corr[band]**2

    return rgb.clip(0,1)

def VIS_rgb_default(cube, waves):
    """Default VIS image."""

    bbands = Bands(waves, 0.375, 0.475, channel="VIS")
    gbands = Bands(waves, 0.475, 0.575, channel="VIS")
    rbands = Bands(waves, 0.575, 0.700, channel="VIS")

    rgb = BandsToRGB(cube, rbands, gbands, bbands)
    return rgb

def VIS_rgb_slopes(cube, waves):
    """A VIS image in which bluer regions have a steeper slope below 0.55
    and redder regions have a steeper slope 0.55 to 0.89 microns (including)
    the methane absorption band."""

    array35 = MeanOverBands(cube, Bands(waves, 0.35, 0.35, minbands=12,
                                                           channel="VIS"))
    array55 = MeanOverBands(cube, Bands(waves, 0.55, 0.55, minbands=12,
                                                           channel="VIS"))
    array89 = MeanOverBands(cube, Bands(waves, 0.89, 0.89, minbands=8,
                                                           channel="VIS"))

    list = RelativeImages([array55, array35, array89])
    if list is None: return np.zeros((cube.shape[0], cube.shape[1], 3))

    rgb = np.dstack((list[1], list[0], list[2]))
    return rgb

def IR_rgb_default(cube, waves):
    """Default IR image."""

    bbands = Bands(waves, 1.70, 1.90, channel="IR") # Bright H20, dark CH4
    gbands = Bands(waves, 2.90, 3.10, channel="IR") # Bright CH4, dark H20
    rbands = Bands(waves, 4.88, 5.13, channel="IR") # Thermal & Titan

    rgb = BandsToRGB(cube, rbands, gbands, bbands)
    rgb = ExpandRGB(rgb)
    return rgb

def IR_rgb_waterice(cube, waves):
    """An IR image in which bluer regions have a steeper slope from 1.1 to 2.2
    microns, and redder regions have a deeper ice band at 2 microns."""

    cont11 = MeanOverBands(cube, Bands(waves, 0.90, 1.30, channel="IR"))
    high18 = MeanOverBands(cube, Bands(waves, 1.75, 1.85, channel="IR"))
    high22 = MeanOverBands(cube, Bands(waves, 2.20, 2.30, channel="IR"))
    band20 = MeanOverBands(cube, Bands(waves, 1.99, 2.05, channel="IR"))

    depth = 2. * band20 / np.maximum(high18 + high22, 0.001) * cont11

    list = RelativeImages([cont11, high22, depth])
    if list is None: return np.zeros((cube.shape[0], cube.shape[1], 3))

    rgb = np.dstack((list[2], list[1], list[0]))
    return rgb

def IR_rgb_methane(cube, waves):
    """An IR image designed to reveal the distribution of methane."""

    peak10 = MeanOverBands(cube, Bands(waves, 1.06, 1.09, minbands=4,
                                                          channel="IR"))
    peak13 = MeanOverBands(cube, Bands(waves, 1.25, 1.30, minbands=4,
                                                          channel="IR"))
    peak20 = MeanOverBands(cube, Bands(waves, 2.00, 2.07, minbands=4,
                                                          channel="IR"))
    peak28 = MeanOverBands(cube, Bands(waves, 2.65, 2.81, minbands=4,
                                                          channel="IR"))

    list = RelativeImages([(peak10 + peak13) / 2., peak20, peak28])
    if list is None: return np.zeros((cube.shape[0], cube.shape[1], 3))

    rgb = np.dstack((list[0], list[1], list[2]))
    return rgb

def IR_rgb_titan1(cube, waves):
    """An IR image designed to reveal the surface of Titan."""

    peak10 = MeanOverBands(cube, Bands(waves, 1.06, 1.09, minbands=4,
                                                          channel="IR"))
    peak13 = MeanOverBands(cube, Bands(waves, 1.25, 1.30, minbands=4,
                                                          channel="IR"))
    peak20 = MeanOverBands(cube, Bands(waves, 2.00, 2.07, minbands=4,
                                                          channel="IR"))
    peak28 = MeanOverBands(cube, Bands(waves, 2.79, 2.81, minbands=4,
                                                          channel="IR"))

    list = RelativeImages([(peak10 + peak13) / 2., peak20, peak28])
    if list is None: return np.zeros((cube.shape[0], cube.shape[1], 3))

    rgb = np.dstack((list[0], list[1], list[2]))
    return rgb

def IR_rgb_titan2(cube, waves):
    """An IR image designed to reveal the clouds of Titan."""

    band11 = Bands(waves, 1.14, 1.25, channel="IR")
    band15 = Bands(waves, 1.42, 1.55, channel="IR")
    band21 = Bands(waves, 2.00, 2.21, channel="IR")
    band40 = Bands(waves, 4.00, 4.83, channel="IR")

    rgb = BandsToRGB(cube, band40, band21, (band11, band15))
    rgb = ExpandRGB(rgb)
    return rgb

def IR_rgb_occult(cube, waves):
    """An IR image designed for stellar occultations."""

    full   = MeanOverBands(cube, Bands(waves, 0.0, 4.8, channel="IR"))
    below  = MeanOverBands(cube, Bands(waves, 0.0, 2.9, channel="IR"))
    high25 = MeanOverBands(cube, Bands(waves, 2.2, 2.5, channel="IR"))
    high35 = MeanOverBands(cube, Bands(waves, 3.4, 3.6, channel="IR"))
    band30 = MeanOverBands(cube, Bands(waves, 2.9, 3.1, channel="IR"))
    above  = MeanOverBands(cube, Bands(waves, 3.3, 4.8, channel="IR"))

    depth = 2. * band30 / np.maximum(high25 + high35, 0.001) * full

    list = RelativeImages([full, below, depth, above])
    if list is None: return np.zeros((cube.shape[0], cube.shape[1], 3))

    rgb = np.dstack((list[1], list[2], list[3]))
    return rgb

def RelativeImages(images, percents=(1,99), extremes=(0.7,1.4), minratio=0.1):
    """Returns a list of images scaled to be neutral relative to the first, and
    with good contrast."""

    # Re-format the images if necessary
    images = np.array(images).astype("float")
    denom  = images[0]
    numers = images[1:]

    # Calculate the image ratios, avoiding Infs and NaNs
    ratios = numers / np.maximum(denom, 0.001)

    # Normalize the ratios to their medians
    select = np.where(denom >= 1.)              # Select the best ratios
    for ratio in ratios:
        median = np.median(ratio[select])       # Median of best ratios
        if median == median: ratio /= median    # Avoid divide-by-NaN

    # Clip extreme ratio values
    ratios = ratios.clip(extremes[0], extremes[1])

    # Determine the usable limits of the denominator
    sorted = np.sort(denom.flatten())
    dmin = sorted[int(sorted.size * (percents[0]/100.))]
    dmax = sorted[min(int(sorted.size * (percents[1]/100.)), sorted.size-1)]

    dmin = max(dmin, 0.)
    dmin = min(dmin, dmax * minratio)           # Don't set too large a value to
                                                # black, at least yet

    # Normalize the denominator to the range 0-1 (making a new copy!)
    denom = denom - dmin

    if dmax == dmin: return None                # No constant arrays!
    denom /= (dmax - dmin)
    denom = denom.clip(0,1)

    # Scale each ratio to the same units as the denominator
    ratios *= denom

    # Make the mean color gray and convert to list
    list = [denom]
    dmean = np.mean(denom)
    for ratio in ratios:
        ratio *= dmean / np.mean(ratio)
        list.append(ratio.clip(0,1))

    return list

################################################################################
# Routines to create images of spectra
################################################################################

def Spectra(cube, axis):
    """Returns the spectral array, averaging along the specified axis:
    axis = 1 for line averaging; 2 for sample averaging.
    """

    # Model the spatial variations amongst the pixels. Each intensity is an
    # average over the spectral range. Do VIS and IR separately.

    vis_spatial_model = np.mean(cube[:96], axis=0)
    ir_spatial_model  = np.mean(cube[96:], axis=0)

    # Model the mean spectrum by dividing out the spatial variations.

    relative = cube.copy()
    relative[:96] /= vis_spatial_model
    relative[96:] /= ir_spatial_model

    # Now the spectra should be more uniform along each spatial axis.

    # Find the median relative spectrum along the axis being collapsed.

    spectrum = np.median(relative, axis=axis)

    # Scale the median relative spectrum by the spatial average along the
    # axis being collapsed.

    spectrum[:96] *= np.mean(vis_spatial_model, axis=axis-1)
    spectrum[96:] *= np.mean(ir_spatial_model,  axis=axis-1)

    # Because we have both divided and multiplied by the spatial model, we are
    # back to absolute units. The intermediate step enabled us to obtain a
    # median spectrum that was not biased by the underlying variations in
    # intensity among the spatial pixels being combined.

    # Re-scale to the range 0-1.

    sorted = np.sort(spectrum[:96].flatten())

    specmin = sorted[(sorted.size *   5)/1000]
    specmax = sorted[(sorted.size * 995)/1000]
    spectrum[:96] -= specmin
    if specmax != specmin:
        spectrum[:96] /= (specmax - specmin)

    sorted = np.sort(spectrum[96:].flatten())
    specmin = sorted[(sorted.size *   5)/1000]
    specmax = sorted[(sorted.size * 995)/1000]
    spectrum[96:] -= specmin
    if specmax != specmin:
        spectrum[96:] /= (specmax - specmin)

    spectrum = spectrum.clip(0,1)

    # This makes the variations at long wavelength more visible in the image.
    spectrum[96:] = spectrum[96:]**0.7

    rgb = np.empty((spectrum.shape[0], spectrum.shape[1], 3))
    rgb[:,:,0] = spectrum
    rgb[:,:,1] = spectrum
    rgb[:,:,2] = spectrum

    rgb[147:157,:,1] *= 0.5     # bluish band
    rgb[147:157,:,0] *= 0.5

    rgb[213:237,:,2] *= 0.5     # greenish band
    rgb[213:237,:,0] *= 0.5

    rgb[332:348,:,2] *= 0.5     # reddish band
    rgb[332:348,:,1] *= 0.5

    rgb[ 4:17,:,1] *= 0.5       # bluish band
    rgb[ 4:17,:,0] *= 0.5

    rgb[17:31,:,2] *= 0.5       # greenish band
    rgb[17:31,:,0] *= 0.5

    rgb[31:48,:,2] *= 0.4       # reddish band
    rgb[31:48,:,1] *= 0.4

    if axis == 2:
        rgb = rgb.swapaxes(0,1)
        return (rgb[:,:96], rgb[:,96:])

    else:
        return (rgb[:96], rgb[96:])

################################################################################
# Routines to lay out and write the images
################################################################################

def RGBtoPic(rgb, filename, quality=90, shape=None, expand=None):
    """Writes a single RGB array to a file. Re-shapes if necessary."""

    pil = picmaker.ArrayToPIL(rgb)

    if shape is None and expand is not None:
        shape = (rgb.shape[1]*expand, rgb.shape[0]*expand)

    if shape is not None:
        if shape[0] < rgb.shape[1] or shape[1] < rgb.shape[1]:
            filter = Image.ANTIALIAS
        else:
            filter = Image.NEAREST

        pil = pil.resize(shape, filter)

    picmaker.WritePIL(pil, filename, quality)

def MakeRGBs(qubfile):
    """Returns the list of RGB arrays derived from the cube file."""

    (path, ext) = os.path.splitext(qubfile)
    (cube, label, flags) = FromFile(qubfile)
    cube = PrepCube(cube)

    waves = Wavelengths(label)
    obsid = str(label["QUBE"]["OBSERVATION_ID"])
    imode = str(label["QUBE"]["INSTRUMENT_MODE_ID"])

    # Initialize the list
    images = []

    # Special case: OCCULTATION mode is just one frame
    if imode == "OCCULTATION":
        images.append((IR_rgb_occult(cube,waves), (0.5,0.5,0.5)))
        return images

    # Add the default VIS image if necessary
    if flags[0]:
        images.append((VIS_rgb_default(cube,waves), (1,1,1)))

    # Handle the Titan case
    if "TI_" in obsid:
        if flags[1]:
            images.append((IR_rgb_default(cube,waves), (1,0,0)))
            images.append((IR_rgb_titan1(cube,waves),  (0,1,0)))
            images.append((IR_rgb_titan2(cube,waves),  (1,0.5,0)))

    # Handle the Saturn case
    elif "SA_" in obsid:
        if flags[0]:
            images.append((VIS_rgb_slopes(cube,waves),(0,1,1)))
        if flags[1]:
            images.append((IR_rgb_default(cube,waves),(1,0,0)))
            images.append((IR_rgb_methane(cube,waves),(0,1,0)))

    # Otherwise, assume an icy body
    else:
        if flags[0]:
            images.append((VIS_rgb_slopes(cube,waves),(0,1,1)))
        if flags[1]:
            images.append((IR_rgb_default(cube,waves),(1,0,0)))
            images.append((IR_rgb_waterice(cube,waves),(0,0,1)))

    return images

def OverlayProfile(rgb, profile=None, scale=0.5):
    """Over-writes an occultation profile with the intensity vs. line in each
    channel. Works for RGB arrays of floating point or unsigned bytes, altering
    the array in place. However, the profile must be floating point, scaled
    0. to 1."""

    white = 1.
    if rgb.dtype == np.dtype("int"): white = -1
    if rgb.dtype == np.dtype("uint8"): white = 255

    lines   = rgb.shape[0]
    samples = rgb.shape[1]

    if profile is None:
        profile = rgb
    else:
        shape = profile.shape
        if len(shape) == 3:
            profile = profile.reshape((shape[0]*shape[1], shape[2]))

        shape = profile.shape
        step = shape[0] // lines
        profile = profile[:step*lines].reshape((lines, step, shape[1]))

    svals = (samples * np.mean(profile,axis=1)).astype("int").clip(0,samples-1)
    if type(white) == float:
        rgb *= scale
    else:
        rgb //= 2       # Assumes scale=0.5, which is the default

    for l in range(lines):
      for b in [0,2,1]:
        s = svals[l,b]
        rgb[l,s,b] = white
        for bb in [(b+1)%3, (b+2)%3]:
            if rgb[l,s,bb] != white: rgb[l,s,bb] = 0

    return rgb

def EnlargeRGB(rgb, factors):
    """Expand an RGB image by integer factors along each axis."""

    newrgb = np.empty((rgb.shape[0], factors[0], rgb.shape[1], factors[1], 3))
    oldrgb = rgb.reshape((rgb.shape[0],       1, rgb.shape[1],          1, 3))
    newrgb[:,:,:,:,:] = oldrgb[:,:,:,:,:]

    return newrgb.reshape((factors[0]*rgb.shape[0], factors[1]*rgb.shape[1], 3))

def ReshapeRGB(rgb, shape, filename):
    """Re-shape an RGB image and convert to unsigned bytes."""

    # First expand as need so that PIL has to reduce the size
    factor0 = (shape[0] + (rgb.shape[0] - 1)) / rgb.shape[0]    # Round up
    factor1 = (shape[1] + (rgb.shape[1] - 1)) / rgb.shape[1]

    rgb = EnlargeRGB(rgb, (factor0, factor1))

    RGBtoPic(rgb, filename, quality=100, shape=(shape[1],shape[0]))
    pil = picmaker.ReadPIL(filename)

    array = picmaker.PILtoArray(pil)
    return array

def BestTiling(tiles, tileshape, frameshape, weight=1, maxratio=4):
    """Returns the optimal size and tiling of the given tiles inside the
    specified image frame. All shapes must be given in the same order."""

    # Define the shape range for individual tiles
    minshape = np.array(tileshape).astype("float")[:2]
    maxshape = minshape.copy()

    if minshape[0] * maxratio < minshape[1]:
       maxshape[0] = minshape[1] / maxratio   # Round up
    if minshape[1] * maxratio < minshape[0]:
       maxshape[1] = minshape[0] / maxratio

    # Identify the output arrangment
    if tiles == 1:
        tilings = np.array([(1,1)])
    elif tiles == 2:
        tilings = np.array([(1,2),(2,1)])   # In order of decreasing preference
    elif tiles == 3:
        tilings = np.array([(1,3),(3,1)])
    else:
        tilings = np.array([(2,2),(1,4),(4,1)])

    # Determine the maximum scale to preserve proportions
    frames = (frameshape - 2 * tilings * weight) / tilings
    scales = frames / minshape
    scale = np.min(scales, axis=1)

    sizes = np.minimum((np.outer(scale,maxshape) + 0.5).astype("int"), frames)
    areas = sizes[:,0].astype("int") * sizes[:,1].astype("int")
    best = np.argmax(areas)

    outshape = (sizes[best] + 0.5).astype("int")

    return (outshape, tilings[best])

def WritePreview(list, filename, quality=90, shape=(100,100), maxratio=4.):
    """Writes the tiled image. Shape is in PIL (width, height) order."""

    # Given shape is (samples,lines) or (width,height).

    # Define the shape of the output image in numpy order
    frameshape = (shape[1], shape[0])

    # Expand the scale to occupy as much as possible of the box
    (outshape, tiling) = BestTiling(len(list), list[0][0].shape, frameshape)

    # Make a new list of re-scaled, framed images
    frames = []
    for item in list:
        color = item[1]

        rgb = item[0]
        newrgb = ReshapeRGB(rgb, outshape, filename)

        if color == (0.5,0.5,0.5):      # Indicates an occultation. Kludge!
            newrgb = OverlayProfile(newrgb, profile=rgb, scale=0.5)

        framed = np.empty((outshape[0]+2, outshape[1]+2, 3), dtype="uint8")
        framed[:,:,:] = (np.array(color) * 255.999).astype("uint8")
        framed[1:-1,1:-1,:] = newrgb[:,:,:]

        frames.append(framed)

    # Lay out the new tiled image
    if np.all(tiling == 1):
        result = frames[0]
    elif tiling[0] == 1:
        result = np.hstack(frames)
    elif tiling[1] == 1:
        result = np.vstack(frames)
    else:
        result = np.vstack((np.hstack(frames[0:2]), np.hstack(frames[2:4])))

    # Surround with black if necessary
    if result.shape[0] < frameshape[0] or result.shape[1] < frameshape[1]:
        black = np.zeros((frameshape[0], frameshape[1], 3), dtype="uint8")

        l0 = (frameshape[0] - result.shape[0]) / 2
        s0 = (frameshape[1] - result.shape[1]) / 2
        black[l0:l0+result.shape[0], s0:s0+result.shape[1]] = result[:,:]

    # Write it
    pil = picmaker.ArrayToPIL(result, rescale=False)
    picmaker.WritePIL(pil, filename, quality)

################################################################################
# Routines to lay out and write the images
################################################################################

def process1(qubfile):

    (path, ext) = os.path.splitext(qubfile)

    list = MakeRGBs(qubfile)

    outpath = path.replace('volumes', 'previews')
    parent = os.path.split(outpath)[0]
    if not os.path.exists(parent):
        os.makedirs(parent)

    WritePreview(list, outpath + "_thumb.png", shape=(100,100))
    WritePreview(list, outpath + "_small.png", shape=(256,256))
    WritePreview(list, outpath + "_med.png",   shape=(512,512))
    WritePreview(list, outpath + "_full.png",  shape=(512,512))

def main():

    for arg in sys.argv[1:]:
        if os.path.isfile(arg):
            if arg.endswith(".QUB") or arg.endswith(".qub"):
                process1(arg)

        elif os.path.isdir(arg):
            prev_root = ''
            for root, dirs, files in os.walk(os.path.join(arg, 'data')):
                for name in files:
                    if name.endswith(".QUB") or name.endswith(".qub"):

                        if root != prev_root:
                            print root
                            prev_root = root

                        process1(os.path.join(root, name))

if __name__ == "__main__": main()

