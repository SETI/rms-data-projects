#!/usr/bin/env python

import sys, os
import numpy as np
import pdsparser
import pyparsing
import traceback
import datetime
import string

################################################################################

# Function to return the sum of elements as an int
def sumover(item):
    try:
        return int(sum(item))
    except TypeError:
        return int(item)

COMMENT3 = ' PDS3 */'
COMMENT4 = ' /* PDS4 */'
MAXLEN = 78

def find_header_rec(header_recs, name, after=0):
    name = name.strip()

    for k,rec in enumerate(header_recs[after:]):
        parts = rec.split(' = ')
        key = parts[0].strip()
        if key == name:
            break

    if key != name:
        raise KeyError('keyword not found:', name)

    if len(parts) < 2:
        return (k + after, parts[0], '')

    return (k + after, parts[0], parts[1])

def find_object_rec(header_recs, name, after=0):
    name = name.strip()

    for k,rec in enumerate(header_recs[after:]):
        parts = rec.split(' = ')
        if parts[0].strip() not in ('OBJECT','GROUP'): continue

        key = parts[1].strip()
        if key == name:
            break

    if key != name:
        raise ValueError('object not found:', name)

    return k

def get_header_values(header_recs, name, after=0):
    (k, _, value) = find_header_rec(header_recs, name, after)

    values = [value]
    while (values[-1].endswith(',')):
        k += 1
        values.append(header_recs[k])

    return values

def hide_header_rec(header_recs, name, after=0):
    if type(name) == int:
        k0 = name
        k1 = name
    else:
      try:
        (k0, name, _) = find_header_rec(header_recs, name, after)
        k1 = k0
        while header_recs[k1].endswith(','):
            k1 += 1
      except KeyError:
         return

    for k in range(k0, k1+1):
        rec = '/* ' + header_recs[k]

        if len(rec) + len(COMMENT3) > MAXLEN:
            rec = rec + COMMENT3
        else:
            rec = rec + ' ' + MAXLEN * '.'
            rec = rec[:MAXLEN - len(COMMENT3)] + COMMENT3

        header_recs[k] = rec

def insert_header_values(header_recs, k, name, values):

    if type(values) == str:
        values = [values]

    rec = name + ' = ' + values[0].rstrip()
    if len(rec) + len(COMMENT4) > MAXLEN:
        rec = rec + COMMENT4
    else:
        rec = rec + (MAXLEN * ' ')
        rec = rec[:MAXLEN - len(COMMENT4)] + COMMENT4

    new_recs = [rec]

    if len(values) > 1:
        blanks = rec[:rec.index('(')] + ' '

    for v in values[1:]:
        rec = blanks + v.strip()
        if len(rec) + len(COMMENT4) > MAXLEN:
            rec = rec + COMMENT4
        else:
            rec = rec + MAXLEN * ' '
            rec = rec[MAXLEN - len(COMMENT4)] + COMMENT4

        new_recs.append(rec)

    header_recs[k:] = new_recs + header_recs[k:]

def update_header_values(header_recs, name, values, after=0):
    (k, name, _) = find_header_rec(header_recs, name, after)
    insert_header_values(header_recs, k, name, values)

    hide_header_rec(header_recs, name, after=k+1)

def append_rec(header_recs, template, header_dict, key, indx=None):
    """Append a record to the header if the key exists in the header_dict."""

    try:
        value = header_dict[key]
    except KeyError:
        return

    if indx is None:
        header_recs.append(template % value)
    else:
        header_recs.append(template % value[indx])

################################################################################

def get_spectral_summing(core):

    for count in (2,4,8,16,32,64):
        if not np.all(core[:,::count,:] == core[:,count-1::count,:]):
            return count//2

    return count

def get_spectral_summing_allow_nulls(core):

    for count in (2,4,8,16,32,64):
        ok = ((core[:,::count,:] == core[:,count-1::count,:]) |
              (core[:,::count,:] == -8192) |
              (core[:,count-1::count,:] == -8192))
        if not np.all(ok):
            return count//2

    return count

################################################################################

BAND_BIN_RECS = """\tGROUP = BAND_BIN
\t\tBAND_BIN_CENTER = (0.35054,0.35895,0.36629,0.37322,0.37949,0.38790,0.39518,
        0.40252,0.40955,0.41731,0.42436,0.43184,0.43919,0.44652,0.45372,0.46163,
        0.46841,0.47622,0.48629,0.48967,0.49777,0.50628,0.51222,0.51963,0.52766,
        0.53416,0.54156,0.54954,0.55614,0.56353,0.57131,0.57810,0.58548,0.59312,
        0.59938,0.60757,0.61505,0.62207,0.62940,0.63704,0.64408,0.65142,0.65910,
        0.66609,0.67342,0.68102,0.68803,0.69535,0.70288,0.71000,0.71733,0.72484,
        0.73198,0.73930,0.74676,0.75396,0.76128,0.76874,0.77595,0.78328,0.79072,
        0.79793,0.80522,0.81262,0.81989,0.82721,0.83463,0.84190,0.84922,0.85663,
        0.86391,0.87122,0.87863,0.88589,0.89386,0.90032,0.90787,0.91518,0.92254,
        0.92983,0.93713,0.94445,0.95177,0.95907,0.96638,0.97382,0.98100,0.98883,
        0.99588,1.00295,1.01005,1.01695,1.02471,1.03195,1.03865,1.04598,0.88421,
        0.90075,0.91692,0.93308,0.94980,0.96568,0.98226,0.99882,1.01479,1.03132,
        1.04755,1.06541,1.08183,1.09806,1.11396,1.13024,1.14695,1.16370,1.17996,
        1.19622,1.21246,1.22859,1.24492,1.26166,1.27813,1.29482,1.31091,1.32695,
        1.34324,1.35952,1.37695,1.39326,1.40940,1.42557,1.44184,1.45841,1.47514,
        1.49169,1.50794,1.52421,1.54035,1.55674,1.57361,1.59018,1.60228,1.62523,
        1.64160,1.65567,1.67238,1.68901,1.70536,1.72175,1.73802,1.75436,1.77105,
        1.78771,1.80401,1.82004,1.83616,1.85288,1.86933,1.88679,1.90261,1.91916,
        1.93545,1.95191,1.96871,1.98531,2.00167,2.01781,2.03424,2.05091,2.06757,
        2.08400,2.10034,2.11667,2.13337,2.15018,2.16652,2.18288,2.19920,2.21591,
        2.23282,2.24952,2.26622,2.28238,2.29921,2.31612,2.33325,2.35043,2.36765,
        2.38472,2.40156,2.41820,2.43471,2.45097,2.46723,2.48360,2.50002,2.51659,
        2.53292,2.54916,2.56437,2.58176,2.59807,2.61508,2.63000,2.64650,2.66146,
        2.68085,2.69620,2.71205,2.73270,2.74770,2.76305,2.78118,2.79889,2.81606,
        2.83247,2.84954,2.86609,2.88242,2.89878,2.91540,2.93143,2.94726,2.96327,
        2.97720,3.00072,3.01382,3.02970,3.04806,3.06446,3.08036,3.09689,3.11213,
        3.12962,3.14667,3.16304,3.17974,3.19708,3.21364,3.23150,3.24806,3.26561,
        3.28298,3.29946,3.31619,3.33338,3.34981,3.36564,3.38183,3.39872,3.41546,
        3.43178,3.44874,3.46475,3.48137,3.49795,3.51284,3.53015,3.54664,3.56274,
        3.58034,3.59610,3.61387,3.63085,3.64853,3.66522,3.68283,3.69953,3.71743,
        3.73439,3.75103,3.76763,3.78444,3.80083,3.81742,3.83472,3.85141,3.86184,
        3.88167,3.89859,3.91478,3.93069,3.94762,3.96375,3.98015,3.99672,4.01280,
        4.02944,4.04730,4.06295,4.080861,4.09743,4.11450,4.13183,4.14883,4.16644,
        4.18299,4.19839,4.21120,4.22402,4.24220,4.26028,4.27840,4.29650,4.31470,
        4.33280,4.35094,4.36646,4.38295,4.39793,4.41537,4.43172,4.44772,4.46573,
        4.48240,4.499511,4.51591,4.53379,4.55187,4.56797,4.58556,4.60290,4.62010,
        4.63615,4.65416,4.67034,4.68721,4.70290,4.719561,4.73706,4.75351,4.77031,
        4.78673,4.80349,4.81952,4.83577,4.85292,4.869401,4.88553,4.90265,4.91983,
        4.93685,4.95389,4.97178,4.98896,5.00576,5.02240,5.040781,5.05734,5.07402,
        5.09106,5.10680,5.108000)
\t\tBAND_BIN_UNIT = MICROMETER
\t\tBAND_BIN_ORIGINAL_BAND = (1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,
        19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,37,38,39,40,41,42,
        43,44,45,46,47,48,49,50,51,52,53,54,55,56,57,58,59,60,61,62,63,64,65,66,
        67,68,69,70,71,72,73,74,75,76,77,78,79,80,81,82,83,84,85,86,87,88,89,90,
        91,92,93,94,95,96,97,98,99,100,101,102,103,104,105,106,107,108,109,110,
        111,112,113,114,115,116,117,118,119,120,121,122,123,124,125,126,127,128,
        129,130,131,132,133,134,135,136,137,138,139,140,141,142,143,144,145,146,
        147,148,149,150,151,152,153,154,155,156,157,158,159,160,161,162,163,164,
        165,166,167,168,169,170,171,172,173,174,175,176,177,178,179,180,181,182,
        183,184,185,186,187,188,189,190,191,192,193,194,195,196,197,198,199,200,
        201,202,203,204,205,206,207,208,209,210,211,212,213,214,215,216,217,218,
        219,220,221,222,223,224,225,226,227,228,229,230,231,232,233,234,235,236,
        237,238,239,240,241,242,243,244,245,246,247,248,249,250,251,252,253,254,
        255,256,257,258,259,260,261,262,263,264,265,266,267,268,269,270,271,272,
        273,274,275,276,277,278,279,280,281,282,283,284,285,286,287,288,289,290,
        291,292,293,294,295,296,297,298,299,300,301,302,303,304,305,306,307,308,
        309,310,311,312,313,314,315,316,317,318,319,320,321,322,323,324,325,326,
        327,328,329,330,331,332,333,334,335,336,337,338,339,340,341,342,343,344,
        345,346,347,348,349,350,351,352)
\tEND_GROUP = BAND_BIN
END_OBJECT = QUBE
END
""".split('\n')

def read_pds3(filename):
    """Returns the extracted data from a PDS3 VIMS file."""

    comments = []

    # Read and parse the ISIS2 header
    reconstructed = False
    try:
        header = pdsparser.PdsLabel.from_file(filename)

    # Scattered files are truncated in the BAND_BIN
    except pyparsing.ParseException as e:
        with open(filename, 'rb') as f:
            header_buffer = f.read(25 * 512)
        header_recs = header_buffer.split('\r\n')

        found = False
        for k,rec in enumerate(header_recs):
            if rec.strip() == 'GROUP = BAND_BIN':
                found = True
                break

        if not found:
            raise

        header_recs = header_recs[:k]
        header_recs += BAND_BIN_RECS
        header = pdsparser.PdsLabel.from_string('\n'.join(header_recs))

        header_buffer = '\r\n'.join(header_recs)
        record_bytes = int(header['RECORD_BYTES'])
        header_records = int(header['LABEL_RECORDS'])
        header_buffer = header_buffer + ((header_records * record_bytes) -
                                         len(header_buffer)) * ' '
        if len(header_buffer) != header_records * record_bytes:
            raise

        reconstructed = True
        comments.append('Truncated header reconstructed')

    record_bytes = int(header['RECORD_BYTES'])
    history_record = int(header['^HISTORY'])
    qube_record = int(header['^QUBE'])
    offset = record_bytes * (qube_record - 1)

    # Read the file
    data_buffer = np.fromfile(filename, 'uint8')[offset:]

    with open(filename, 'rb') as f:
        if reconstructed:
            _ = f.read(record_bytes * (history_record - 1))
        else:
            header_buffer = f.read(record_bytes * (history_record - 1))
        history = f.read(record_bytes * (qube_record - history_record))
        remainder_buffer = f.read()

    header_recs = header_buffer.split('\r\n')

    if 'PDS4' in history or 'PDS4' in header_buffer:
        raise ValueError('File is not a PDS3 qube')

    extra_bytes = len(remainder_buffer) % record_bytes

    # Check for un-printables in history object
    found = False
    for k in range(len(history)):
        if history[k] not in string.printable:
            found = True
            break

    if found:
        unprintables = len(history) - k
        if unprintables:
            comments.append('History ends with %d unprintables' % unprintables)
    else:
        unprintables = 0

    # Move GROUP = UNPACK or GROUP = FIXQUB to history
    k0 = 99999
    try:
        k0 = find_object_rec(header_recs, 'UNPACK')
    except ValueError:
        pass

    k1 = 99999
    try:
        k1 = find_object_rec(header_recs, 'FIXQUB')
    except ValueError:
        pass

    k = min(k0,k1)
    if k < 99999:
        lhist = len(history)
        history = '\r\n' + '\r\n'.join(header_recs[k:]) + history
        history = history[:lhist]
        comments.append('Header GROUP(s) moved to history')
        header_recs = header_recs[:k]

        if header_recs[-1].strip() == '':
            header_recs[-1] = ''
        else:
            header_recs.append('')

        extras = len('xx'.join(header_recs)) % record_bytes
        header_recs[-1] = (record_bytes - extras) * ' '

    # Handle truncated 'END'
    if header_recs[-2] == 'END':
        end_shift = 0
    elif header_recs[-2] == 'END_OBJECT = QUBE':
        end_shift = 5
    elif header_recs[-1] == 'END\r':
        end_shift = 1
    elif header_recs[-1] == 'END':
        end_shift = 2
    elif header_recs[-1] == 'EN':
        end_shift = 3
    elif header_recs[-1] == 'E':
        end_shift = 4
    elif header_recs[-1] == 'END_OBJECT = QUBE\r':
        end_shift = 6
    elif header_recs[-1] == 'END_OBJECT = QUBE':
        end_shift = 7
    elif header_recs[-1] == 'END_OBJECT = QUB':
        end_shift = 8
    elif header_recs[-1] == 'END_OBJECT = QU':
        end_shift = 9
    elif header_recs[-1] == 'END_OBJECT = Q':
        end_shift = 10
    elif header_recs[-2].strip() == 'END':
        end_shift = 0
    elif header_recs[-3].strip() == 'END':
        end_shift = 0
    else:
        raise KeyError('Header END not found: %s' % filename)

    if end_shift != 0:
        comments.append("Header END repaired (was '%s')" %
                        header_recs[-1].replace('\r','\\r'))

        if 'END_OBJECT' in header_recs[-1]:
            header_recs[-1] = 'END_OBJECT = QUBE'
            header_recs.append('END')
        else:
            header_recs[-1] = 'END'

        header_recs.append('')
        extras = len('xx'.join(header_recs)) % record_bytes
        header_recs[-1] = (record_bytes - extras) * ' '

    # Handle corrupted history
    test = history.rstrip()
    if test in ('\nEND', '\r\nEND','D\r\nEND', 'ND\r\nEND', 'END\r\nEND',
                '\nEND\r\nEND', '\r\nEND\r\nEND', 'E\r\nEND\r\nEND',
                'BE\r\nEND\r\nEND', 'UBE\r\nEND\r\nEND',
                'E\r\nEND', 'BE\r\nEND', 'UBE\r\nEND'):
        comments.append("History repaired (was '%s')" %
                        test.replace('\r','\\r').replace('\n','\\n'))
        history = 'END\r\n' + (len(history) - 5) * ' '

    if reconstructed:
        test = history.strip(' ')
        history = test + (len(history) - len(test)) * ' '

    for spaces in range(len(remainder_buffer)):
        if remainder_buffer[spaces] != ' ':
            break

    # Fix for incorrect record length
    if extra_bytes == 0:
        pass
    elif extra_bytes == end_shift and remainder_buffer[0] == ' ':
        comments.append('Data shifted by %d byte(s)' % extra_bytes)
        remainder_buffer = remainder_buffer[extra_bytes:]
        data_buffer = data_buffer[extra_bytes:]
    elif extra_bytes == spaces:
        comments.append('Data shifted by %d byte(s)' % extra_bytes)
        remainder_buffer = remainder_buffer[extra_bytes:]
        data_buffer = data_buffer[extra_bytes:]
    elif spaces == 511 or (reconstructed and spaces):
        extra_bytes = spaces
        comments.append('Data shifted by %d byte(s)' % extra_bytes)
        remainder_buffer = remainder_buffer[extra_bytes:]
        data_buffer = data_buffer[extra_bytes:]
    elif unprintables == 512:
        comments.append('Data shifted by %d byte(s)' % -unprintables)

        # Re-read the file
        offset = record_bytes * (qube_record - 2)
        data_buffer = np.fromfile(filename, 'uint8')[offset:]
        with open(filename, 'rb') as f:
            _ = f.read(record_bytes * (history_record - 1))
            history = f.read(record_bytes * (qube_record - history_record - 1))
            remainder_buffer = f.read()

        history = history + unprintables * ' '

    # Determine the file structure
    qube = header['QUBE']

    core_item_bytes = int(qube['CORE_ITEM_BYTES'])
    core_samples = int(qube['CORE_ITEMS'][0])
    core_bands   = int(qube['CORE_ITEMS'][1])
    core_lines   = int(qube['CORE_ITEMS'][2])

    core_sample_bytes = core_samples * core_item_bytes
    core_band_bytes   = core_bands * core_item_bytes
    core_line_bytes   = core_lines * core_item_bytes

    assert core_item_bytes == 2

    suffix_samples = int(qube['SUFFIX_ITEMS'][0])
    suffix_bands   = int(qube['SUFFIX_ITEMS'][1])
    suffix_lines   = int(qube['SUFFIX_ITEMS'][2])

    suffix_sample_bytes = sumover(qube['SAMPLE_SUFFIX_ITEM_BYTES'])
    assert suffix_sample_bytes == 4

    if suffix_bands:
        suffix_band_bytes = sumover(qube['BAND_SUFFIX_ITEM_BYTES'])
    else:
        suffix_band_bytes = 0

    suffix_item_bytes = suffix_sample_bytes
    suffix_corner_bytes = suffix_samples * suffix_band_bytes

    # Determine the dtype for the file core
    core_type = str(qube['CORE_ITEM_TYPE'])

    if 'SUN_' in core_type or 'MSB_' in core_type:
        core_dtype = '>'
    elif 'PC_' in core_type or  'LSB_' in core_type:
        core_dtype = '<'
    else:
        raise TypeError('Unrecognized byte order: ' + core_type)

    if  'UNSIGNED' in core_type: core_dtype += 'u'
    elif 'INTEGER' in core_type: core_dtype += 'i'
    elif 'REAL'    in core_type: core_dtype += 'f'
    else:
        raise TypeError('Unrecognized data type: ' + core_type)

    core_dtype += str(core_item_bytes)

    # Determine the dtype for the suffixes
    suffix_type = str(qube['SAMPLE_SUFFIX_ITEM_TYPE'])

    if 'SUN_' in core_type or 'MSB_' in suffix_type:
        suffix_dtype = '>'
    elif 'PC_' in core_type or  'LSB_' in suffix_type:
        suffix_dtype = '<'
    else:
        raise TypeError('Unrecognized byte order: ' + suffix_type)

    if  'UNSIGNED' in suffix_type: suffix_dtype += 'u'
    elif 'INTEGER' in suffix_type: suffix_dtype += 'i'
    elif 'REAL'    in suffix_type: suffix_dtype += 'f'
    else:
        raise TypeError('Unrecognized data type: ' + core_type)

    suffix_dtype += str(suffix_item_bytes)

    core_band_stride   = (core_samples * core_item_bytes +
                          suffix_samples * suffix_item_bytes)
    suffix_band_stride = (core_samples + suffix_samples) * suffix_item_bytes
    line_stride        = (core_bands * core_band_stride +
                          suffix_bands * suffix_band_stride)

    core_strides = (line_stride, core_band_stride, core_item_bytes)
    core_shape = (core_lines, core_bands, core_samples)
    core_offset = 0

    splane_strides = (line_stride, core_band_stride, suffix_item_bytes)
    splane_shape = (core_lines, core_bands, suffix_samples)
    splane_offset = core_samples * core_item_bytes

    bplane_strides = (line_stride, suffix_band_stride, suffix_item_bytes)
    bplane_shape = (core_lines, suffix_bands, core_samples)
    bplane_offset = core_bands * core_band_stride

    corner_strides = (line_stride, suffix_band_stride, suffix_item_bytes)
    corner_shape = (core_lines, suffix_bands, suffix_samples)
    corner_offset = (core_bands * core_band_stride +
                     core_samples * suffix_item_bytes)

    padding_offset = core_lines * line_stride

    # Make sure the buffer is the proper length
    if len(data_buffer) >= padding_offset:
        core_buffer = data_buffer[:padding_offset]
        suffix_buffer = data_buffer[:padding_offset]
    elif len(data_buffer) < padding_offset:
        comments.append('QUBE array padded with %d NULL item bytes' %
                        (padding_offset - len(data_buffer)))

        core_buffer = np.empty(padding_offset // core_item_bytes,
                               dtype=core_dtype)
        core_buffer[...] = int(qube['CORE_NULL'])

        items = len(data_buffer) // core_item_bytes
        core_buffer[:items] = np.frombuffer(data_buffer[:items *
                                                         core_buffer.itemsize],
                                            dtype=core_dtype)

        suffix_buffer = np.empty(padding_offset // suffix_item_bytes,
                                 dtype=suffix_dtype)
        suffix_buffer[...] = int(qube['SAMPLE_SUFFIX_NULL'])

        items = len(data_buffer) // suffix_item_bytes
        suffix_buffer[:items] = np.frombuffer(data_buffer[:items *
                                                          suffix_item_bytes],
                                              dtype=suffix_dtype)

    # Extract the core array
    core_buffer = np.frombuffer(core_buffer, dtype=core_dtype,
                                             offset=core_offset)
    core = np.lib.stride_tricks.as_strided(core_buffer, core_shape,
                                           core_strides)

    # Extract the sideplane array
    if splane_offset % suffix_item_bytes == 0:
        splane_buffer = np.frombuffer(suffix_buffer, dtype=suffix_dtype,
                                                     offset=splane_offset)
        splane = np.lib.stride_tricks.as_strided(splane_buffer,
                                                 splane_shape,
                                                 splane_strides)
    else:
        splane_buffer = np.frombuffer(suffix_buffer, dtype='uint8',
                                      offset=splane_offset)
        splane_bytes = np.lib.stride_tricks.as_strided(splane_buffer,
                                            splane_shape + (suffix_item_bytes,),
                                            splane_strides + (1,))
        splane_bytes = splane_bytes.ravel()
        splane_buffer = np.frombuffer(splane_bytes, dtype=suffix_dtype)
        splane = splane_buffer.reshape(splane_shape)

    # Extract the backplane array
    if np.product(bplane_shape) == 0:
          bplane = np.zeros(0, dtype=suffix_dtype).reshape(bplane_shape)
    elif bplane_offset % suffix_item_bytes == 0:
          bplane_buffer = np.frombuffer(suffix_buffer, dtype=suffix_dtype,
                                                       offset=bplane_offset)
          bplane = np.lib.stride_tricks.as_strided(bplane_buffer,
                                                   bplane_shape,
                                                   bplane_strides)
    else:
        bplane_buffer = np.frombuffer(suffix_buffer, dtype='uint8',
                                      offset=bplane_offset)
        bplane_bytes = np.lib.stride_tricks.as_strided(bplane_buffer,
                                            bplane_shape + (suffix_item_bytes,),
                                            bplane_strides + (1,))
        bplane_bytes = bplane_bytes.ravel()
        bplane_buffer = np.frombuffer(bplane_bytes, dtype=suffix_dtype)
        bplane = bplane_buffer.reshape(bplane_shape)

    # Extract the corner array
    if np.product(corner_shape) == 0:
        corner = np.zeros(0, dtype=suffix_dtype).reshape(corner_shape)
    elif corner_offset % suffix_item_bytes == 0:
        corner_buffer = np.frombuffer(suffix_buffer, dtype=suffix_dtype,
                                                     offset=corner_offset)
        corner = np.lib.stride_tricks.as_strided(corner_buffer,
                                                 corner_shape,
                                                 corner_strides)
    else:
        corner_buffer = np.frombuffer(suffix_buffer, dtype='uint8',
                                                     offset=corner_offset)
        corner_bytes = np.lib.stride_tricks.as_strided(corner_buffer,
                                            corner_shape + (suffix_item_bytes,),
                                            corner_strides + (1,))
        corner_bytes = corner_bytes.ravel()
        corner_buffer = np.frombuffer(corner_bytes, dtype=suffix_dtype)
        corner = corner_buffer.reshape(corner_shape)

    # Define the padding
    padding = remainder_buffer[padding_offset:]

    return (header, header_recs, history, core, splane, bplane, corner, padding,
            filename, comments)

################################################################################

def read_pds4(filename):
    """Returns the extracted data from a PDS4 VIMS file."""

    # Read and parse the ISIS2 header
    header = pdsparser.PdsLabel.from_file(filename).as_dict()

    record_bytes = header['RECORD_BYTES']
    file_records = header['FILE_RECORDS']
    history_record = header['^HISTORY'][0]
    qube_record   = header['^QUBE'][0]
    splane_record = header['^SIDEPLANE'][0]

    padding_record = header.get('^PADDING', (file_records+1,'RECORD'))[0]
    bplane_record = header.get('^BACKPLANE', (padding_record,'RECORD'))[0]
    corner_record = header.get('^CORNER', (bplane_record,'RECORD'))[0]

    # Read the file
    with open(filename, 'rb') as f:
        header_buffer  = f.read(record_bytes * (history_record - 1))
        history        = f.read(record_bytes * (qube_record - history_record))
        core_buffer    = f.read(record_bytes * (splane_record - qube_record))
        splane_buffer  = f.read(record_bytes * (bplane_record - splane_record))
        bplane_buffer  = f.read(record_bytes * (corner_record - bplane_record))
        corner_buffer  = f.read(record_bytes * (padding_record - corner_record))
        padding_buffer = f.read(record_bytes * (file_records + 1 - padding_record))

    header_recs = header_buffer.split('\r\n')

    # Determine the file structure
    qube = header['QUBE']
    core_item_bytes = int(qube['CORE_ITEM_BYTES'])
    core_samples = int(qube['CORE_ITEMS'][0])
    core_bands   = int(qube['CORE_ITEMS'][1])
    core_lines   = int(qube['CORE_ITEMS'][2])

    assert core_item_bytes == 2

    suffix_samples = 1
    suffix_lines   = core_lines

    try:
        suffix_bands = int(header['BACKPLANE']['CORE_ITEMS'][2])
    except KeyError:
        suffix_bands = 0

    suffix_item_bytes = int(header['SIDEPLANE']['CORE_ITEM_BYTES'])
    suffix_corner_bytes = suffix_samples * suffix_item_bytes

    # Determine the dtype for the file core
    core_type = str(qube['CORE_ITEM_TYPE'])

    if 'SUN_' in core_type or 'MSB_' in core_type:
        core_dtype = '>'
    elif 'PC_' in core_type or  'LSB_' in core_type:
        core_dtype = '<'
    else:
        raise TypeError('Unrecognized byte order: ' + core_type)

    if  'UNSIGNED' in core_type: core_dtype += 'u'
    elif 'INTEGER' in core_type: core_dtype += 'i'
    elif 'REAL'    in core_type: core_dtype += 'f'
    else:
        raise TypeError('Unrecognized data type: ' + core_type)

    core_dtype += str(core_item_bytes)

    # Determine the dtype for the suffixes
    suffix_type = str(header['SIDEPLANE']['CORE_ITEM_TYPE'])

    if 'SUN_' in core_type or 'MSB_' in suffix_type:
        suffix_dtype = '>'
    elif 'PC_' in core_type or  'LSB_' in suffix_type:
        suffix_dtype = '<'
    else:
        raise TypeError('Unrecognized byte order: ' + suffix_type)

    if  'UNSIGNED' in suffix_type: suffix_dtype += 'u'
    elif 'INTEGER' in suffix_type: suffix_dtype += 'i'
    elif 'REAL'    in suffix_type: suffix_dtype += 'f'
    else:
        raise TypeError('Unrecognized data type: ' + core_type)

    suffix_dtype += str(suffix_item_bytes)

    # Create the arrays
    core_bytes = core_lines * core_bands * core_samples * core_item_bytes
    core = np.frombuffer(core_buffer[:core_bytes], dtype=core_dtype)
    core = core.reshape((core_lines, core_bands, core_samples))

    splane_bytes = core_lines * core_bands * suffix_item_bytes
    splane = np.frombuffer(splane_buffer[:splane_bytes], dtype=suffix_dtype)
    splane = splane.reshape((core_lines, core_bands, suffix_samples))

    bplane_bytes = core_lines * suffix_bands * core_samples * suffix_item_bytes
    bplane = np.frombuffer(bplane_buffer[:bplane_bytes], dtype=suffix_dtype)
    bplane = bplane.reshape((suffix_bands, core_lines, core_samples))
    bplane = bplane.swapaxes(0,1)

    corner_bytes = core_lines * suffix_bands * suffix_samples * suffix_item_bytes
    corner = np.frombuffer(corner_buffer[:corner_bytes], dtype=suffix_dtype)
    corner = corner.reshape((suffix_bands, core_lines, suffix_samples))
    corner = corner.swapaxes(0,1)

    if padding_buffer:
        padding_bytes = int(header['PADDING']['CORE_ITEMS'])
        padding = padding_buffer[:padding_bytes]
    else:
        padding = ''

    return (header, header_recs, history, core, splane, bplane, corner, padding)

################################################################################

def write_pds4(filename, header, header_recs,
               history, core, splane, bplane, corner, padding,
               infile, comments, verbose=False):

    qube = header['QUBE']
    core_item_bytes = int(qube['CORE_ITEM_BYTES'])
    core_samples = int(qube['CORE_ITEMS'][0])
    core_bands   = int(qube['CORE_ITEMS'][1])
    core_lines   = int(qube['CORE_ITEMS'][2])

    suffix_samples = int(qube['SUFFIX_ITEMS'][0])
    suffix_bands   = int(qube['SUFFIX_ITEMS'][1])
    suffix_lines   = int(qube['SUFFIX_ITEMS'][2])
    assert suffix_samples == 1

    sample_suffix_item_bytes = sumover(qube['SAMPLE_SUFFIX_ITEM_BYTES'])

    if suffix_bands:
        band_suffix_item_bytes = sumover(qube['BAND_SUFFIX_ITEM_BYTES'])
    else:
        band_suffix_item_bytes = 0

    new_recs = list(header_recs)

    (k, _, _) = find_header_rec(new_recs, '^QUBE')
    insert_header_values(new_recs, k+1, '^SIDEPLANE', '    ....')

    if suffix_bands:
        insert_header_values(new_recs, k+2, '^BACKPLANE', '    ....')
        insert_header_values(new_recs, k+3, '^CORNER', '       ....')

        if len(padding):
            insert_header_values(new_recs, k+4, '^PADDING', '      ....')

    elif len(padding):
        insert_header_values(new_recs, k+2, '^PADDING', '      ....')

    update_header_values(new_recs, 'FILE_RECORDS', '         ....')
    update_header_values(new_recs, 'LABEL_RECORDS', '         ....')
    update_header_values(new_recs, '^HISTORY', '         ....')
    update_header_values(new_recs, '^QUBE', '         ....')

    update_header_values(new_recs, 'SUFFIX_ITEMS', '(0,0,0)')

    hide_header_rec(new_recs, 0)
    hide_header_rec(new_recs, 'SUFFIX_BYTES')
    hide_header_rec(new_recs, 'SAMPLE_SUFFIX_NAME')
    hide_header_rec(new_recs, 'SAMPLE_SUFFIX_UNIT')
    hide_header_rec(new_recs, 'SAMPLE_SUFFIX_ITEM_BYTES')
    hide_header_rec(new_recs, 'SAMPLE_SUFFIX_ITEM_TYPE')
    hide_header_rec(new_recs, 'SAMPLE_SUFFIX_BASE')
    hide_header_rec(new_recs, 'SAMPLE_SUFFIX_MULTIPLIER')
    hide_header_rec(new_recs, 'SAMPLE_SUFFIX_VALID_MINIMUM')
    hide_header_rec(new_recs, 'SAMPLE_SUFFIX_NULL')
    hide_header_rec(new_recs, 'SAMPLE_SUFFIX_LOW_REPR_SAT')
    hide_header_rec(new_recs, 'SAMPLE_SUFFIX_LOW_INSTR_SAT')
    hide_header_rec(new_recs, 'SAMPLE_SUFFIX_HIGH_REPR_SAT')
    hide_header_rec(new_recs, 'SAMPLE_SUFFIX_HIGH_INSTR_SAT')

    hide_header_rec(new_recs, 'BAND_SUFFIX_NAME')
    hide_header_rec(new_recs, 'BAND_SUFFIX_UNIT')
    hide_header_rec(new_recs, 'BAND_SUFFIX_ITEM_TYPE')
    hide_header_rec(new_recs, 'BAND_SUFFIX_ITEM_BYTES')
    hide_header_rec(new_recs, 'BAND_SUFFIX_BASE')
    hide_header_rec(new_recs, 'BAND_SUFFIX_MULTIPLIER')
    hide_header_rec(new_recs, 'BAND_SUFFIX_VALID_MINIMUM')
    hide_header_rec(new_recs, 'BAND_SUFFIX_NULL')
    hide_header_rec(new_recs, 'BAND_SUFFIX_LOW_REPR_SAT')
    hide_header_rec(new_recs, 'BAND_SUFFIX_LOW_INSTR_SAT')
    hide_header_rec(new_recs, 'BAND_SUFFIX_HIGH_INSTR_SAT')
    hide_header_rec(new_recs, 'BAND_SUFFIX_HIGH_REPR_SAT')

    (k, _, _) = find_header_rec(new_recs, 'END')
    tail_recs = new_recs[k:]
    new_recs = new_recs[:k]

    qube = header['QUBE']

    new_recs += [
        '',
        '/* Array of values at the end of each SAMPLE axis */',
        '',
        'OBJECT = SIDEPLANE',
        '   AXES = 2',
        '   AXIS_NAME = (%s,%s)'             % (qube['AXIS_NAME'][1], qube['AXIS_NAME'][2]),
        '   CORE_ITEMS = (%s,%s)'            % (core_bands, core_lines),
        '   CORE_ITEM_BYTES = %s'            % sample_suffix_item_bytes,
        '   CORE_ITEM_TYPE = %s'             % qube['SAMPLE_SUFFIX_ITEM_TYPE'],
    ]

    append_rec(new_recs, '   CORE_BASE = %s'                 , qube, 'SAMPLE_SUFFIX_BASE')
    append_rec(new_recs, '   CORE_MULTIPLIER = %s'           , qube, 'SAMPLE_SUFFIX_MULTIPLIER')
    append_rec(new_recs, '   CORE_VALID_MINIMUM = %s'        , qube, 'SAMPLE_SUFFIX_VALID_MINIMUM')
    append_rec(new_recs, '   CORE_NULL = %s'                 , qube, 'SAMPLE_SUFFIX_NULL')
    append_rec(new_recs, '   CORE_LOW_REPR_SATURATION = %s'  , qube, 'SAMPLE_SUFFIX_LOW_REPR_SAT')
    append_rec(new_recs, '   CORE_LOW_INSTR_SATURATION = %s' , qube, 'SAMPLE_SUFFIX_LOW_INSTR_SAT')
    append_rec(new_recs, '   CORE_HIGH_REPR_SATURATION = %s' , qube, 'SAMPLE_SUFFIX_HIGH_REPR_SAT')
    append_rec(new_recs, '   CORE_HIGH_INSTR_SATURATION = %s', qube, 'SAMPLE_SUFFIX_HIGH_INSTR_SAT')
    append_rec(new_recs, '   CORE_NAME = %s'                 , qube, 'SAMPLE_SUFFIX_NAME')
    append_rec(new_recs, '   CORE_UNIT = %s'                 , qube, 'SAMPLE_SUFFIX_UNIT')

    new_recs += [
        'END_OBJECT = SIDEPLANE',
    ]

    if suffix_bands:
      new_recs += [
        '',
        '/* Array of values at the end of each BAND axis */',
        '',
        'OBJECT = BACKPLANE',
        '   AXES = 3',
        '   AXIS_NAME = (%s,%s,BACKPLANE)'   % (qube['AXIS_NAME'][0], qube['AXIS_NAME'][2]),
        '   CORE_ITEMS = (%s,%s,%s)'         % (core_samples, core_lines, suffix_bands),
        '   CORE_ITEM_BYTES = 4',
        '   CORE_ITEM_TYPE = %s'             % qube['BAND_SUFFIX_ITEM_TYPE'][0],
        '   CORE_NAME = BACKPLANE_VALUE  /* See BACKPLANE_NAME below */',
        '   CORE_UNIT = DIMENSIONLESS    /* See BACKPLANE_UNIT below */',
      ]

      append_rec(new_recs, '   CORE_BASE = %s'                 , qube, 'BAND_SUFFIX_BASE'          , 0)
      append_rec(new_recs, '   CORE_MULTIPLIER = %s'           , qube, 'BAND_SUFFIX_MULTIPLIER'    , 0)
      append_rec(new_recs, '   CORE_VALID_MINIMUM = %s'        , qube, 'BAND_SUFFIX_VALID_MINIMUM' , 0)
      append_rec(new_recs, '   CORE_NULL = %s'                 , qube, 'BAND_SUFFIX_NULL'          , 0)
      append_rec(new_recs, '   CORE_LOW_REPR_SATURATION = %s'  , qube, 'BAND_SUFFIX_LOW_REPR_SAT'  , 0)
      append_rec(new_recs, '   CORE_LOW_INSTR_SATURATION = %s' , qube, 'BAND_SUFFIX_LOW_INSTR_SAT' , 0)
      append_rec(new_recs, '   CORE_HIGH_REPR_SATURATION = %s' , qube, 'BAND_SUFFIX_HIGH_REPR_SAT' , 0)
      append_rec(new_recs, '   CORE_HIGH_INSTR_SATURATION = %s', qube, 'BAND_SUFFIX_HIGH_INSTR_SAT', 0)

      new_recs += [
          '   BACKPLANE_NAME = (%s,' % qube['BAND_SUFFIX_NAME'][0]
      ]

      for k in range(1,len(qube['BAND_SUFFIX_NAME'])-1):
        new_recs += [
          '                     %s,' % qube['BAND_SUFFIX_NAME'][k],
        ]

      new_recs += [
          '                     %s)' % qube['BAND_SUFFIX_NAME'][-1],
          '   BACKPLANE_UNIT = (%s,' % qube['BAND_SUFFIX_UNIT'][0],
      ]

      for k in range(1,len(qube['BAND_SUFFIX_UNIT'])-1):
        new_recs += [
          '                     %s,' % qube['BAND_SUFFIX_UNIT'][k],
        ]

      new_recs += [
          '                     %s)' % qube['BAND_SUFFIX_UNIT'][-1],
          'END_OBJECT = BACKPLANE',
          '',
          '/* Array of values in the corner between sideplane and backplane */',
          '',
          'OBJECT = CORNER',
          '    AXES = 2',
          '    AXIS_NAME = (%s,BACKPLANE)' % qube['AXIS_NAME'][2],
          '    CORE_ITEMS = (%s,%s)'       % (qube['CORE_ITEMS'][2], suffix_bands),
          '    CORE_ITEM_BYTES = %s'       % band_suffix_item_bytes,
          '    CORE_ITEM_TYPE = %s'        % qube['BAND_SUFFIX_ITEM_TYPE'][0],
          '    CORE_BASE = 0.',
          '    CORE_MULTIPLIER = 1.',
          '    CORE_NAME = CORNER_ITEMS',
          '    CORE_UNIT = DIMENSIONLESS',
          'END_OBJECT = CORNER',
      ]

    if len(padding):
      new_recs += [
        '',
        '/* Bytes to pad out last record in the original PDS3 file */',
        '',
        'OBJECT = PADDING',
        '   AXES = 1',
        '   AXIS_NAME = SAMPLE',
        '   CORE_ITEMS = %s' % len(padding),
        '   CORE_ITEM_BYTES = 1',
        '   CORE_ITEM_TYPE = SUN_INTEGER',
        '   CORE_NAME = PADDING_BYTES',
        '   CORE_UNIT = DIMENSIONLESS',
        'END_OBJECT = PADDING',
      ]

    # Pad the header
    record_bytes = int(header['RECORD_BYTES'])
    new_recs += tail_recs + ['']
    header_bytes = len('xx'.join(new_recs))
    header_nrecs = (header_bytes + record_bytes - 1) // record_bytes
    header_padding = header_nrecs * record_bytes - header_bytes
    new_recs[-1] = header_padding * ' '

    # Update the history
    history_recs = history.split('\r\n')
    try:
        (k, _, _) = find_header_rec(history_recs, 'END')
        if k != len(history_recs) - 2 or history[-1].strip() != '':
            comments.append('Malformed history; END misplaced')
        end_k = k
        end_recs = history_recs[k:]
    except KeyError:
        if history.strip() != '':
            comments.append('Malformed history; END missing')
        end_k = len(history_recs) - 1
        end_recs = ['END /* PDS4 */','']

    date_str = datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%S')
    infile = os.path.abspath(infile)
    try:
        short_filename = 'COVIMS_00' + infile.split('COVIMS_00')[1]
    except IndexError:
        short_filename = filename

    basename = os.path.basename(infile)
    parts = basename.split('_')
    outfile = parts[0][1:6] + 'xxxxx/' + parts[0][1:]
    if len(parts) == 2:
        outfile = outfile + '.qub'
    else:
        outfile = outfile + '_' + parts[2][:-4] + '.qub'

    new_group = [
        '',
        'GROUP = VIMS2PDS4',
        '   VERSION = 1.0',
        '   VIMS2PDS4_DATE = ' + date_str,
        '   SOFTWARE_DESC = "Move sideplane and backplane for PDS4 compliance;',
        '                    apply necessary repairs"',
        '   INPUT_FILE = "%s"' % short_filename,
        '   OUTPUT_FILE = "%s"' % outfile,
    ]

    for k,comment in enumerate(comments):
        new_group.append('   COMMENT_%d = "%s"' % (k+1, comment))

    new_group.append('END_GROUP = VIMS2PDS4')

    lhist = len(history)
    history_recs = history_recs[:end_k] + new_group + end_recs
    history = '\r\n'.join(history_recs)
    history = history[:lhist]
    history = history + (lhist - len(history)) * ' '

    # Determine record counts and paddings
    core_bytes = core_lines * core_bands * core_samples * core_item_bytes
    core_nrecs = (core_bytes + record_bytes - 1) // record_bytes
    core_padding = core_nrecs * record_bytes - core_bytes

    splane_bytes = core_lines * core_bands * sample_suffix_item_bytes
    splane_nrecs = (splane_bytes + record_bytes - 1) // record_bytes
    splane_padding = splane_nrecs * record_bytes - splane_bytes

    bplane_bytes = core_lines * suffix_bands * core_samples * sample_suffix_item_bytes
    bplane_nrecs = (bplane_bytes + record_bytes - 1) // record_bytes
    bplane_padding = bplane_nrecs * record_bytes - bplane_bytes

    corner_bytes = core_lines * suffix_bands * suffix_samples * sample_suffix_item_bytes
    corner_nrecs = (corner_bytes + record_bytes - 1) // record_bytes
    corner_padding = corner_nrecs * record_bytes - corner_bytes

    if len(padding):
        padding_padding = (-len(padding)) % record_bytes
        padding_nrecs = (len(padding) + padding_padding) // record_bytes
    else:
        padding_padding = 0
        padding_nrecs = 0

    # Fill record offsets in the header
    (k, _, _) = find_header_rec(new_recs, 'LABEL_RECORDS')
    new_recs[k] = new_recs[k].replace('....', '%4d' % header_nrecs)

    history_rec = header_nrecs + 1
    (k, _, _) = find_header_rec(new_recs, '^HISTORY')
    new_recs[k] = new_recs[k].replace('....', '%4d' % history_rec)

    qube_rec = history_rec + header['^QUBE'] - header['^HISTORY']
    (k, _, _) = find_header_rec(new_recs, '^QUBE')
    new_recs[k] = new_recs[k].replace('....', '%4d' % qube_rec)

    splane_rec = qube_rec + core_nrecs
    (k, _, _) = find_header_rec(new_recs, '^SIDEPLANE')
    new_recs[k] = new_recs[k].replace('....', '%4d' % splane_rec)

    bplane_rec = splane_rec + splane_nrecs
    corner_rec = bplane_rec + bplane_nrecs
    try:
        (k, _, _) = find_header_rec(new_recs, '^BACKPLANE')
        new_recs[k] = new_recs[k].replace('....', '%4d' % bplane_rec)

        (k, _, _) = find_header_rec(new_recs, '^CORNER')
        new_recs[k] = new_recs[k].replace('....', '%4d' % corner_rec)
    except KeyError:
        pass

    if len(padding):
        padding_rec = corner_rec + corner_nrecs
        (k, _, _) = find_header_rec(new_recs, '^PADDING')
        new_recs[k] = new_recs[k].replace('....', '%4d' % padding_rec)
        file_nrecs = padding_rec + padding_nrecs - 1
    else:
        file_nrecs = corner_rec + corner_nrecs - 1

    (k, _, _) = find_header_rec(new_recs, 'FILE_RECORDS')
    new_recs[k] = new_recs[k].replace('....', '%4d' % file_nrecs)

    # Write...
    f = open(filename, 'wb')
    f.write('\r\n'.join(new_recs))
    f.write(history)
    f.write(core.ravel())
    f.write(np.zeros(core_padding, dtype='uint8'))
    f.write(splane.ravel())
    f.write(np.zeros(splane_padding, dtype='uint8'))
    f.write(bplane.swapaxes(0,1).ravel())
    f.write(np.zeros(bplane_padding, dtype='uint8'))
    f.write(corner.swapaxes(0,1).ravel())
    f.write(np.zeros(corner_padding, dtype='uint8'))
    f.write(padding)
    f.write(np.zeros(padding_padding, dtype='uint8'))
    f.close()

    # Report comments
    if verbose and comments:
        print 'COMMENTS for ' + filename
        for comment in comments:
            print '    ' + comment

    return new_recs

################################################################################

def write_pds3(filename, header, header_recs,
               history, core, splane, bplane, corner, padding):

    isis2_header_recs = header_to_pds3(header_recs)[:-1]
    test = 'xx'.join(isis2_header_recs)
    if len(test) % 512 != 0:
        raise ValueError('Invalid record length in reconstructed PDS3 header')

    lhist = len(history)
    history_recs = history.split('\r\n')
    isis2_history_recs = header_to_pds3(history_recs)
    isis2_history = '\r\n'.join(isis2_history_recs)
    if isis2_history.strip() == '':
        isis2_history = ''
    isis2_history = isis2_history + (lhist - len(isis2_history)) * ' '

    qube = header['QUBE']
    (core_lines, core_bands, core_samples) = core.shape
    suffix_samples = splane.shape[2]
    suffix_bands   = bplane.shape[1]

    f = open(filename, 'wb')

    f.write('\r\n'.join(isis2_header_recs))
    f.write(isis2_history)

    for l in range(core_lines):
      for b in range(core_bands):
        f.write(core[l,b].ravel())
        f.write(splane[l,b].ravel())

      for b in range(suffix_bands):
        f.write(bplane[l,b].ravel())
        f.write(corner[l,b].ravel())

    f.write(padding)
    f.close()

    return isis2_header_recs

def header_to_pds3(header_recs):
    new_recs = []
    for k,rec in enumerate(header_recs):
        if rec.endswith(' PDS3 */'):
            rec = rec[3:-8]

            if rec.endswith('.'):
                while rec.endswith('.'):
                    rec = rec[:-1]

                if rec.endswith(' '):
                    rec = rec[:-1]

            new_recs.append(rec)

        elif rec.endswith('PDS4 */'):
            pass

        else:
            new_recs.append(rec)

    delete_from_header(new_recs, 'SIDEPLANE')
    delete_from_header(new_recs, 'BACKPLANE')
    delete_from_header(new_recs, 'CORNER')
    delete_from_header(new_recs, 'PADDING')
    delete_from_header(new_recs, 'VIMS2PDS4')

    return new_recs

def delete_from_header(header_recs, group):

    try:
        k0 = header_recs.index('GROUP = ' + group)
        k1 = header_recs.index('END_GROUP = ' + group)
    except ValueError:
      try:
        k0 = header_recs.index('OBJECT = ' + group)
        k1 = header_recs.index('END_OBJECT = ' + group)
      except ValueError:
        return

    if header_recs[k0-2].startswith('/*'):
        k0 -= 3
    else:
        k0 -= 1

    del header_recs[k0:k1+1]

################################################################################

BLANKS = 512 * ' '

def translate1(pds3_file, replace=True, validate=False, revalidate=False):

    try:
        pds3_file = os.path.abspath(pds3_file)

        (in_dir, basename) = os.path.split(pds3_file)
        out_dir = in_dir.replace('holdings/volumes', 'pds4')
        out_dir = out_dir.replace('Marks-Migration-HD', 'Migration2')

        if in_dir == out_dir:
            print 'Invalid input directory:', in_dir

        if not os.path.exists(out_dir):
            os.makedirs(out_dir)

        pds4_file = os.path.join(out_dir, basename)

        exists = os.path.exists(pds4_file)
        if replace or not exists:
            stuff = read_pds3(pds3_file)
            _ = write_pds4(pds4_file, *stuff, verbose=True)

        if revalidate or (validate and (replace or not exists)):
            stuff4 = read_pds4(pds4_file)

            test_file = pds4_file[:-4] + '_test.qub'
            _ = write_pds3(test_file, *stuff4)

            with open(pds3_file, 'rb') as f:
                pds3_bytes = f.read()

            with open(test_file, 'rb') as f:
                test_bytes = f.read()

            lpds3 = len(pds3_bytes)
            ltest = len(test_bytes)
            success = True
            if lpds3 > ltest:
                success = False
                print '*** validation failed; file too small: ' + pds4_file[:-4] + '_test.qub'
            elif lpds3 == ltest:
              if pds3_bytes != test_bytes:
                success = False
                print '*** validation failed; mismatch: ' + pds4_file[:-4] + '_test.qub'
            else:
              if (lpds3 % 512 == 0 or
                  ltest - lpds3 > 511 or
                  pds3_bytes != test_bytes[:lpds3] or
                  test_bytes[lpds3:] != BLANKS[:(ltest-lpds3)]):
                success = False
                print '*** validation failed; new file too big: ' + pds4_file[:-4] + '_test.qub'

            if success:
                os.remove(test_file)

    except KeyboardInterrupt:
        sys.exit(1)

    except Exception as e:
        print '*** error for: ', pds3_file
        print e
        (etype, value, tb) = sys.exc_info()
        print ''.join(traceback.format_tb(tb))

def main():

    args = sys.argv[1:]
    if '--validate' in args:
        validate = True
        args.remove('--validate')
    else:
        validate = False

    if '--revalidate' in args:
        revalidate = True
        args.remove('--revalidate')
    else:
        revalidate = False

    if '--replace' in args:
        replace = True
        args.remove('--replace')
    else:
        replace = False

    for arg in args:

        if os.path.isfile(arg):
          if arg.endswith('.QUB') or arg.endswith('.qub'):
            translate1(arg, replace, validate, revalidate)

        elif os.path.isdir(arg):
          prev_root = ''
          for root, dirs, files in os.walk(os.path.join(arg, 'data')):
            for name in files:
              if name.endswith('.QUB') or name.endswith('.qub'):

                if root != prev_root:
                    print root
                    prev_root = root

                filename = os.path.join(root, name)
                translate1(filename, replace, validate, revalidate)

if __name__ == "__main__": main()

