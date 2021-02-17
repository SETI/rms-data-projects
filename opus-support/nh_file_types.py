################################################################################
# File type assignment procedure for New Horizons
#
# MRS, July 29, 2016
# Revised 9/28/16 to handle MVIC file types as well.
################################################################################

# Define the priority among file types
FILE_TYPE_PRIORITY = {

    # LORRI codes
    '630': 0,  #- LORRI High-res Lossless (CDH 1)/LOR
    '631': 2,  #- LORRI High-res Packetized (CDH 1)/LOR
    '632': 4,  #- LORRI High-res Lossy (CDH 1)/LOR
    '633': 6,  #- LORRI 4x4 Binned Lossless (CDH 1)/LOR
    '634': 8,  #- LORRI 4x4 Binned Packetized (CDH 1)/LOR
    '635': 10, #- LORRI 4x4 Binned Lossy (CDH 1)/LOR
    '636': 1,  #- LORRI High-res Lossless (CDH 2)/LOR
    '637': 3,  #- LORRI High-res Packetized (CDH 2)/LOR
    '638': 5,  #- LORRI High-res Lossy (CDH 2)/LOR
    '639': 7,  #- LORRI 4x4 Binned Lossless (CDH 2)/LOR
    '63A': 9,  #- LORRI 4x4 Binned Packetized (CDH 2)/LOR
    '63B': 11, #- LORRI 4x4 Binned Lossy (CDH 2)/LOR

    # MVIC codes
    '530': 12, #- MVIC Panchromatic TDI Lossless (CDH 1)/MP1,MP2
    '531': 18, #- MVIC Panchromatic TDI Packetized (CDH 1)/MP1,MP2
    '532': 24, #- MVIC Panchromatic TDI Lossy (CDH 1)/MP1,MP2

    '533': 30, #- MVIC Panchromatic TDI 3x3 Binned Lossless (CDH 1)/MP1,MP2
    '534': 32, #- MVIC Panchromatic TDI 3x3 Binned Packetized (CDH 1)/MP1,MP2
    '535': 34, #- MVIC Panchromatic TDI 3x3 Binned Lossy (CDH 1)/MP1,MP2

    '536': 13, #- MVIC Color TDI Lossless (CDH 1)/MC0,MC1,MC2,MC3
    '537': 19, #- MVIC Color TDI Packetized (CDH 1)/MC0,MC1,MC2,MC3
    '538': 25, #- MVIC Color TDI Lossy (CDH 1)/MC0,MC1,MC2,MC3

    '539': 14, #- MVIC Panchromatic Frame Transfer Lossless (CDH 1)/MPF
    '53A': 20, #- MVIC Panchromatic Frame Transfer Packetized (CDH 1)/MPF
    '53B': 26, #- MVIC Panchromatic Frame Transfer Lossy (CDH 1)/MPF

    '53F': 15, #- MVIC Panchromatic TDI Lossless (CDH 2)/MP1,MP2
    '540': 21, #- MVIC Panchromatic TDI Packetized (CDH 2)/MP1,MP2
    '541': 27, #- MVIC Panchromatic TDI Lossy (CDH 2)/MP1,MP2

    '542': 31, #- MVIC Panchromatic TDI 3x3 Binned Lossless (CDH 2)/MP1,MP2
    '543': 33, #- MVIC Panchromatic TDI 3x3 Binned Packetized (CDH 2)/MP1,MP2
    '544': 35, #- MVIC Panchromatic TDI 3x3 Binned Lossy (CDH 2)/MP1,MP2

    '545': 16, #- MVIC Color TDI Lossless (CDH 2)/MC0,MC1,MC2,MC3
    '546': 22, #- MVIC Color TDI Packetized (CDH 2)/MC0,MC1,MC2,MC3
    '547': 28, #- MVIC Color TDI Lossy (CDH 2)/MC0,MC1,MC2,MC3

    '548': 17, #- MVIC Panchromatic Frame Transfer Lossless (CDH 2)/MPF
    '549': 23, #- MVIC Panchromatic Frame Transfer Packetized (CDH 2)/MPF
    '54A': 29, #- MVIC Panchromatic Frame Transfer Lossy (CDH 2)/MPF
}

FILE_TYPE_LOOKUP = (2 * [''] + 2 * ['PACKETIZED_'] + 2 * ['LOSSY_'] +   # LORRI
                    2 * [''] + 2 * ['PACKETIZED_'] + 2 * ['LOSSY_'] +   # LORRI
                    6 * [''] + 6 * ['PACKETIZED_'] + 6 * ['LOSSY_'] +   # MVIC
                    2 * [''] + 2 * ['PACKETIZED_'] + 2 * ['LOSSY_'])    # MVIC

BINNED_TYPE_LOOKUP = 6 * [False] + 6 * [True] + 18 * [False] + 6 * [True]

def nh_file_types(filenames, prefix='RAW', suffix='IMAGE'):
    """Given a list of LORRI or MVIC file names for the same clock count, return
    the associated set of unique file types.
    """

    # If there is just one filename, use the primary type
    primary_type = prefix + '_' + suffix

    if len(filenames) == 1:
        return [primary_type]

    # Sort the filenames by priority
    sortable_priorities = []
    for indx in range(len(filenames)):
        filename = filenames[indx]
        upperfile = filename.upper()
        k = upperfile.index('0X')
        code = upperfile[k:][2:5]
        sortable_priorities.append((FILE_TYPE_PRIORITY[code], indx))

    sortable_priorities.sort()

    # Fill in the top-priority file type
    (priority, indx) = sortable_priorities[0]
    type_of_primary = FILE_TYPE_LOOKUP[priority]
    primary_is_binned = BINNED_TYPE_LOOKUP[priority]
    types_used = [primary_type]
    sortable_types = [(indx, primary_type)]

    # Assign subsequent types based on priority
    for (priority, indx) in sortable_priorities[1:]:
        this_type = FILE_TYPE_LOOKUP[priority] + primary_type

        # If primary is not binned, always identify binned images
        is_binned = BINNED_TYPE_LOOKUP[priority]
        if is_binned and not primary_is_binned:
            this_type = 'BINNED_' + this_type

        # A recurrence of a prior file type is a duplicate
        if this_type in types_used:
            duplicate_type = 'DUPLICATE_' + this_type

            if duplicate_type in types_used:
                raise ValueError('Non-unique file type ' + this_type +
                                 ' for ' + filenames[indx])

            this_type = duplicate_type

        types_used.append(this_type)
        sortable_types.append((indx, this_type))

    # Sort back to the original given order of filenames
    sortable_types.sort()

    return [rec[1] for rec in sortable_types]
