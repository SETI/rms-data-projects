################################################################################
# TOL_search.py 
#
#
#
#
# Deukkwon Yoon, PDS Rings Node, SETI Institute, Sep-12-2012
################################################################################

import numpy as np
import julian
from operator import itemgetter

TOL_FILE = "/Users/dyoon/Desktop/TOL-as-flown.txt"

########################################

def read_tol_file(file = TOL_FILE):

    # Read file, ignoring header
    tol_lines = open(file).readlines()[1:]

    # Get list of UVIS info
    tol_list = []
    for line in tol_lines: 
        line = line.strip()
        if line != "":
            col = line.split("\t")
            event_name = col[0]
            if (event_name.startswith("UVIS_") and not
               event_name.endswith("_SI")): 
                start_time = utc_to_tai(col[3])
                stop_time  = utc_to_tai(col[6])
                tol_list.append([event_name, start_time, stop_time])

    return tol_list

########################################

def utc_to_tai(utc_string):

    # Convert UTC to TAI using julian module
    (day, sec) = julian.day_sec_from_iso(utc_string)
    tai = julian.tai_from_day(day) + sec

    return tai

########################################

def find_event(tai, tol_list):
    """
    find_event

    Finds a mission that is close to given TAI.

    """

    event_names = map(itemgetter(0), tol_list)
    start_times = map(itemgetter(1), tol_list)
    stop_times  = map(itemgetter(2), tol_list)

    number_of_events = len(event_names)

    assert number_of_events == len(start_times)
    assert number_of_events == len(stop_times)

    # Verify that the list is in ascending order
    for i in range(1, number_of_events):
        assert start_times[i] > start_times[i-1]

    # Validate start and stop times
    for i in range(number_of_events):
        assert start_times[i] < stop_times[i]

    loc = np.searchsorted(start_times, tai)

    if loc == 0:

        # TAI too small
        if tai < start_times[0]:
            event = "UNK"

        else: event_names[0]

    # TAI too large
    elif loc == number_of_events:
        print "Time out of range. Last activity returned"
        event = event_names[loc-1]

    # TAI is in range
    else:
        # Exact match
        if tai == start_times[loc]: event = event_names[loc]

        else:
            # Within a mission duration
            if tai <= stop_times[loc-1]: event = event_names[loc-1]

            # Not within a mission duration, return closest mission
            else:
                diff_right =  start_times[loc]   - tai
                diff_left  = -start_times[loc-1] + tai 
                print "No match.", diff_left, diff_right

                # Prefer left...
#                 if diff_left <= diff_right: event = event_names[loc-1]
#                 else: event = event_names[loc]
                if diff_left < 60:
                    event = event_names[loc-1]
                elif diff_right < 60:
                    event = event_names[loc]
                else:
                    event = "UNK"

    return event

################################################################################
# Main program
################################################################################

if __name__ == "__main__":

    tai = int(raw_input("Enter time in TAI: "))

    tol_list = read_tol_file(TOL_FILE)
    events = find_event(tai, tol_list)
    print events
