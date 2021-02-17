---------------------
 make_polar_image.pro
---------------------

This function ingests registered or unregistered, calibrated,
polarized images from the Cassini ISS cameras. Input images must be
in VICAR format, and specified in sets of two or three, with filters 
consisting of either: 
   1) P0, P60 and P120
   2) IRP0 and IRP90
   3) CLR and IRP0
with matching colors in the opposite filter position. The order of input
images is irrelevant, only that they constitute a matching set.

The code includes the transmissions parallel and perpendicular to
the polarizing axis of the polarizer, derived from observations.
These are functions of wavelength, and different passbands have
different effective parallel and perpendicular transmissions. 

As of November 2014, the following filter combinations are supported:

  WAC IRP0/CLR or IRP0/IRP90 + MT2, CB2, MT3, CB3
  (NAC currently uses WAC values for these filters)
   
  NAC P0/P60/P120 + UV3, BL2, GRN, MT1, CB1, MT2, CB2

The returned value is a structure defined as follows:
 
If input is two file names (files containing either [IRP0, IRP90] or
[IRP0, CLR]) the function returns intensity I (same units as the
original, and indicated by the tag name "intensity") and the Stokes
parameter Q defined with respect to IRP0 (tag name: "Q").

If input is three files (containing P0, P60, P120) the returned
structure contains intensity, polarization (from 0.0 to 1.0 tag
name: "polarization"), and theta, the angle of the electric vector
relative to the camera Y axis (+/- 90 degrees tag name: "theta").

For more information on the polarization code implementation, see the ISS
Data User's Guide, the latest version of which can be obtained at:

   http://pds-imaging.jpl.nasa.gov/software/

Keywords:

  Set the /align keyword to co-register the images if they have
   not already been co-registered.
  Set the /flip keyword to flip the output arrays about the x
   (sample) axis
  Set the /silent keyword to suppress warning and info messages (but 
   not error messages).
  Set the outfile keyword equal to the filename of a VICAR-format
   file containing the calculated intensity. This file will be given
   the same label as file1 to track calibration history.

Invoking the program:

  result = make_polar_image(file1,file2,[file3],[/align],[/flip],$
          [outfile=outfile],[silent=silent])

Written by Bob West

  version 1.0, May 25, 2001
 
  version 2.0, October 31, 2002 - uses filter derived t_parallel and
       t_perp from polarization_package.

  version 3.0, January, 2006 - still needs an absolute calibration factor
       for the intensity calculation.

  version 4.0, November 2007, various revisions by Ben Knowles.

  version 5.0, December 7 2007, converted image input to file input,
       instituted automatic detection of filter, polarizers,
       Vis/IR, created structure output.

  version 6.0, August 20, 2013, Cleaned up and incorporated into
       CISSCAL by Ben Knowles.

  version 7.0, March 14, 2014, No longer assumes T_parallel and T_perpendiular
       are the same for all polarizers; updates T_parallel and T_perpendicular
       based on POLCAL calibration results for some filters.  New
       algorithm by R. West.

  version 8.0, April 23, 2014, Improved error handling and cleaned up
       for CISSCAL 3.7 by Ben Knowles.

  version 9.0, November 20, 2014, Additional small bug fixes by B. Knowles.
