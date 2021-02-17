pro mpi_calc_ipt,I0,I60,I120,T1,T2,d,I,Pol,Theta

; To calculate Intensity, Polarization, Theta from measurements in
; three polarizers, and with known transmissions T1 and T2 (Parallel 
; and Perpendicular to the electric vector)
;
; The extra parameter d is if polarizer 0 has extra transmittance of 
; both polarizations such that
;   T1(P0) = T1 + d; T2(P0) = T2 + d.  
;
; On return, I is in the same units as I0, Pol is from 0 to 1, Theta 
; is in degrees

z = I0
s = I60
n = I120
o = T1
w = T2

U1 = (6*(o - w)*(2*d*(n + s) + (o + w)*(n + s - 2*z))*(n + s + z) - $
      4*Sqrt(3)*Sqrt((2*d*(n + s) + (o + w)*(n + s - 2*z))^2*$
      (4*d^2*(n^2 + n*s + s^2) + 6*d*(o + w)*(n^2 + s^2 - (n + s)*z) + $
      3*(o + w)^2*(n^2 + s^2 - s*z + z^2 - n*(s + z)))))/$
      (3*(o - w)*(2*d + 3*(o + w))*(2*d*(n + s) + (o + w)*(n + s - 2*z)))

P1 = (4*Sqrt((2*d*(n + s) + (o + w)*(n + s - 2*z))^2*$
      (4*d^2*(n^2 + n*s + s^2) + 6*d*(o + w)*(n^2 + s^2 - (n + s)*z) + $
      3*(o + w)^2*(n^2 + s^2 - s*z + z^2 - n*(s + z)))))/$
      (Sqrt(3)*(o - w)*(2*d + 3*(o + w))*(2*d*(n + s) + (o + w)*(n + s - 2*z)))

Theta1 = ATAN(-Sqrt((24*d^2*(n^2 + n*s + s^2) + 36*d*(o + w)*$
      (n^2 + s^2 - (n + s)*z) + 18*(o + w)^2*(n^2 + s^2 - s*z + z^2 - $
      n*(s + z)) - 3*Sqrt(3)*Sqrt((2*d*(n + s) + (o + w)*(n + s - 2*z))^2*$
      (4*d^2*(n^2 + n*s + s^2) + 6*d*(o + w)*(n^2 + s^2 - (n + s)*z) + $
      3*(o + w)^2*(n^2 - n*s + s^2 - (n + s)*z + z^2))))/$
      (4*d^2*(n^2 + n*s + s^2) + 6*d*(o + w)*(n^2 + s^2 - (n + s)*z) + $
      3*(o + w)^2*(n^2 - n*s + s^2 - (n + s)*z + z^2))), $
      (Sqrt((8*d^2*(n^2 + n*s + s^2) + 12*d*(o + w)*(n^2 + s^2 - (n + s)*z) + $
      6*(o + w)^2*(n^2 + s^2 - s*z + z^2 - n*(s + z)) - $
      Sqrt(3)*Sqrt((2*d*(n + s) + (o + w)*(n + s - 2*z))^2*$
      (4*d^2*(n^2 + n*s + s^2) + 6*d*(o + w)*(n^2 + s^2 - (n + s)*z) + $
      3*(o + w)^2*(n^2 - n*s + s^2 - (n + s)*z + z^2))))/$
      (4*d^2*(n^2 + n*s + s^2) + 6*d*(o + w)*(n^2 + s^2 - (n + s)*z) + $
      3*(o + w)^2*(n^2 - n*s + s^2 - (n + s)*z + z^2)))*$
      (3*(2*d*(n + s) + (o + w)*(n + s - 2*z))^2 + $
      2*Sqrt(3)*Sqrt((2*d*(n + s) + (o + w)*(n + s - 2*z))^2*$
      (4*d^2*(n^2 + n*s + s^2) + 6*d*(o + w)*(n^2 + s^2 - (n + s)*z) + $
      3*(o + w)^2*(n^2 - n*s + s^2 - (n + s)*z + z^2)))))/$
      ((n - s)*(2*d + 3*(o + w))*(2*d*(n + s) + (o + w)*(n + s - 2*z))))

U3 = (6*(o - w)*(2*d*(n + s) + (o + w)*(n + s - 2*z))*(n + s + z) + $
      4*Sqrt(3)*Sqrt((2*d*(n + s) + (o + w)*(n + s - 2*z))^2*$
      (4*d^2*(n^2 + n*s + s^2) + 6*d*(o + w)*(n^2 + s^2 - (n + s)*z) + $
      3*(o + w)^2*(n^2 + s^2 - s*z + z^2 - n*(s + z)))))/$
      (3*(o - w)*(2*d + 3*(o + w))*(2*d*(n + s) + (o + w)*(n + s - 2*z)))
 
P3 = (-4*Sqrt((2*d*(n + s) + (o + w)*(n + s - 2*z))^2*$
      (4*d^2*(n^2 + n*s + s^2) + 6*d*(o + w)*(n^2 + s^2 - (n + s)*z) + $
      3*(o + w)^2*(n^2 + s^2 - s*z + z^2 - n*(s + z)))))/$
      (Sqrt(3)*(o - w)*(2*d + 3*(o + w))*(2*d*(n + s) + (o + w)*(n + s - 2*z)))
 
Theta3 = ATAN(-(Sqrt(3)*Sqrt((8*d^2*(n^2 + n*s + s^2) + 12*d*(o + w)*$
      (n^2 + s^2 - (n + s)*z) + 6*(o + w)^2*(n^2 + s^2 - s*z + z^2 - $
      n*(s + z)) + Sqrt(3)*Sqrt((2*d*(n + s) + (o + w)*(n + s - 2*z))^2*$
      (4*d^2*(n^2 + n*s + s^2) + 6*d*(o + w)*(n^2 + s^2 - (n + s)*z) + $
      3*(o + w)^2*(n^2 - n*s + s^2 - (n + s)*z + z^2))))/$
      (4*d^2*(n^2 + n*s + s^2) + 6*d*(o + w)*(n^2 + s^2 - (n + s)*z) + $
      3*(o + w)^2*(n^2 - n*s + s^2 - (n + s)*z + z^2)))), $
      ((3*(2*d*(n + s) + (o + w)*(n + s - 2*z))^2 - $
      2*Sqrt(3)*Sqrt((2*d*(n + s) + (o + w)*(n + s - 2*z))^2*$
      (4*d^2*(n^2 + n*s + s^2) + 6*d*(o + w)*(n^2 + s^2 - (n + s)*z) + $
      3*(o + w)^2*(n^2 - n*s + s^2 - (n + s)*z + z^2))))*$
      Sqrt((8*d^2*(n^2 + n*s + s^2) + 12*d*(o + w)*(n^2 + s^2 - (n + s)*z) + $
      6*(o + w)^2*(n^2 + s^2 - s*z + z^2 - n*(s + z)) + $
      Sqrt(3)*Sqrt((2*d*(n + s) + (o + w)*(n + s - 2*z))^2*$
      (4*d^2*(n^2 + n*s + s^2) + 6*d*(o + w)*(n^2 + s^2 - (n + s)*z) + $
      3*(o + w)^2*(n^2 - n*s + s^2 - (n + s)*z + z^2))))/$
      (4*d^2*(n^2 + n*s + s^2) + 6*d*(o + w)*(n^2 + s^2 - (n + s)*z) + $
      3*(o + w)^2*(n^2 - n*s + s^2 - (n + s)*z + z^2))))/$
      ((n - s)*(2*d + 3*(o + w))*(2*d*(n + s) + (o + w)*(n + s - 2*z))))

I1 = U1 + P1
Pol1 = -p1/I1
theta1 = -theta1*180./!pi       ; Note: May need to change the sign

I3 = U3 + P3
Pol3 = -p3/I3
theta3 = -theta3*180./!pi       ; Note: May need to change the sign

angle = theta1*!Pi/180.
iu = u1
ip = p1
izero1 = iu*(t1 + t2 + 2.*d)/2 + ip*(cos(angle)*cos(angle)*(t1+d) + $
                                     sin(angle)*sin(angle)*(t2+d))
isixty1 = iu*(t1 + t2)/2 + ip*(cos(angle-!Pi/3)*cos(angle-!Pi/3)*(t1) + $
                               sin(angle-!pi/3)*sin(angle-!Pi/3)*(t2))
ionetwenty1 = iu*(t1 + t2)/2 + ip*(cos(angle-2*!Pi/3)*cos(angle-2*!Pi/3)*(t1) + $
                                   sin(angle-2*!pi/3)*sin(angle-2*!pi/3)*(t2))

diff1 = (izero1-i0)^2 + (isixty1-i60)^2 + (ionetwenty1-i120)^2

angle = theta3*!Pi/180.
iu = u3
ip = p3
izero3 = iu*(t1 + t2 + 2.*d)/2 + ip*(cos(angle)*cos(angle)*(t1+d) + $
                                     sin(angle)*sin(angle)*(t2+d))
isixty3 = iu*(t1 + t2)/2 + ip*(cos(angle-!Pi/3)*cos(angle-!Pi/3)*(t1) + $
                               sin(angle-!pi/3)*sin(angle-!Pi/3)*(t2))
ionetwenty3 = iu*(t1 + t2)/2 + ip*(cos(angle-2*!Pi/3)*cos(angle-2*!Pi/3)*(t1) + $
                                   sin(angle-2*!pi/3)*sin(angle-2*!pi/3)*(t2))

diff3 = (izero3-i0)^2 + (isixty3-i60)^2 + (ionetwenty3-i120)^2

good = where(pol3 ge 0)
;good = where(diff3 lt diff1 and pol3 ge 0.)

i = i1
pol = pol1
theta = theta1
if total(good) gt 0 then begin
   i[good] = i3[good]
   pol[good] = pol3[good]
   theta[good] = theta3[good]
endif

if not min(finite(i)) then begin
; try to fix some NANs by replacing by a finite value that can be flagged later
   b = finite(i)
   bad = where(b eq 0)
   i(bad) = 1000.
   if n_elements(i) gt 10000 then begin
      filtered = median(i,7)
      if n_elements(bad)/float(n_elements(i)) lt 0.1 then i(bad) = filtered(bad)
   endif
endif

if not min(finite(pol)) then begin
  ; try to fix some NANs by replacing by a finite value that can be flagged later
   b = finite(pol)
   bad = where(b eq 0)
   pol(bad) = 1000.
   if n_elements(pol) gt 10000 then begin
      filtered = median(pol,7)
      if n_elements(bad)/float(n_elements(pol)) lt 0.1 then pol(bad) = filtered(bad)
   endif
endif

if not min(finite(theta)) then begin
 ; try to fix some NANs by replacing by a finite value that can be flagged later
   b = finite(theta)
   bad = where(b eq 0)
   theta(bad) = 1000.
   if n_elements(theta) gt 10000 then begin
      filtered = median(theta,7)
      if n_elements(bad)/float(n_elements(theta)) lt 0.1 then theta(bad) = filtered(bad)
   endif
endif

end


pro mpi_iterate_pol,I0,I60,I120,TL0,TR0,TL60,TR60,TL120,TR120,I,P,THETA,status
;
; Iteratively solves for I, P, Theta from intensities in polarizers P0, P60, P120

; This code starts from the output of another code that gives a good approximation
;  to I (arbitrary units), P (between 0 and 1), Theta (degrees). It iteratively 
;  improves the estimate and returns the improved I, P, Theta.
;  
;  Note that single elements, not arrays, must be input
;  
;  Input values are I0, I60 and I120, the intensities recorded with the polarizers
;  P0, P60 and P120.  The transmission coefficients are TL0 (T parallel for polarizer 0),
;  TR0 (T perpendicular for polarizer 0) and likewise for polarizers 60 and 120.
;  
;  If any of I0, I60, or I120 I or P are negative, not finite, or not
;  single element arrays, the program returns with no change and
;  status is set to 3.
;
;  If the calculation was successful the status is 0 on return.
;
;  Verion 1.0 by R. West, 7 March, 2014.


off0 = -0.5 ; from lab calibration
off60 = 61.8
off120 = 120.8

status = 3

; no change to input if the signal is negative or something wrong with inputs:
if n_elements(I0) + n_elements(I60) + n_elements(I120) + n_elements(I) +$
   n_elements(P) + n_elements(Theta) ne 6 then goto, exit
if min([i,p,i0,i60,i120]) le 0. then goto, exit 
if not finite(i+p+theta+I0+I60+I120) then goto, exit

; Calculate I0, I60, I120 from I, p, theta

Ip = I*p & Iu = I - Ip

loopcount = 0

loop:
loopcount = loopcount + 1
  ; print,'Lopp ',loopcount,' Iu, Ip, theta ',Iu, Ip, theta
  ;I0_test = Iu*(TL0 + TR0)/2 + Ip*(TL0*cos((theta-off0)/!radeg)^2 + $
  ;          TR0*sin((theta-off0)/!radeg)^2)
I0_test = Iu*(TL0 + TR0)/2 + Ip*(TR0 + (TL0-TR0)*cos((theta-off0)/!radeg)^2)
I60_test = Iu*(TL60 + TR60)/2 + Ip*(TL60*cos((theta-off60)/!radeg)^2 + $
                                    TR60*sin((theta-off60)/!radeg)^2)
I120_test = Iu*(TL120 + TR120)/2 + Ip*(TL120*cos((theta-off120)/!radeg)^2 + $
                                       TR120*sin((theta-off120)/!radeg)^2)

Diff = [I0 - I0_test,I60-I60_test,I120-I120_test]
  
  ; derivatives with respect to Iu, Ip and theta
  
d_I0d_iu = (TL0 + TR0)/2
d_I0d_ip = (TL0*cos((theta-off0)/!radeg)^2 + TR0*sin((theta-off0)/!radeg)^2)
d_i0d_theta = Ip*(TR0-TL0)*sin(2*(theta-off0)/!radeg)/!radeg

d_I60d_iu = (TL60 + TR60)/2
d_I60d_ip = (TL60*cos((theta-off60)/!radeg)^2 + TR60*sin((theta-off60)/!radeg)^2)
d_i60d_theta = Ip*(TR60-TL60)*sin(2*(theta-off60)/!radeg)/!radeg
  
d_I120d_iu = (TL120 + TR120)/2
d_I120d_ip = (TL120*cos((theta-off120)/!radeg)^2 + TR120*sin((theta-off120)/!radeg)^2)
d_i120d_theta = Ip*(TR120-TL120)*sin(2*(theta-off120)/!radeg)/!radeg
  
dm = [[d_I0d_iu,d_I0d_ip,d_i0d_theta],[d_I60d_iu,d_I60d_ip,d_i60d_theta],$
      [ d_I120d_iu,d_I120d_ip,d_i120d_theta]]

idm = invert(dm,status,/double)
if status ne 0 then goto, exit  ; exit if singular or a small povot
  
deltas = diff#idm

; check results 

Iu = Iu + float(deltas[0])
Ip = Ip + float(deltas[1])

I = Iu + Ip
P = Ip/I

theta = theta + float(deltas[2])

if loopcount lt 2 then goto, loop 

 ; stop

exit:

end


pro mpi_image_offset,image1,image2,xoff,yoff,silent=silent

;  This program cross-correlates two images to find the offsets in x
;  and y.
;
;  Input:  Image1, Image2: base image and offset image arrays
;
;  Output:  xoff, yoff: the shift in x and y between the two images
;
;  Note: uses convol_fft, which requires IDL 8.1 or later; if using
;  earlier version of IDL, user can swap this out with the convolve.pro
;  function in the IDL astronomy library

  num_params = n_params()

  if num_params lt 4 then begin
     print,' Error in image_offset: too few parameters. Calling sequence:' 
     print,'     image_offset, image1, image2, xoff, yoff'
     xoff = 0 & yoff = 0
     return
  endif

;  Find the steepest gradients in the images (morph_gradient).  Use
;  convolv_fft to produce the cross-correlation.  The location of the
;  maximum of the resulting image gives the offsets.  To get the
;  fractional part of the offsets fit the peak of the convolution with
;  a 2-D Gaussian and solve for the location of the peak to a fraction
;  of a pixel.  Where there are sharp features that correlate well
;  this method is good to about 0.1 pixel or perhaps a little better.
;
  s = size(image1)
  s2 = size(image2)

  if s2(1) ne s(1) or s2(2) ne s(2)  then begin
     print,' Error in image_offset: image dimensions must be identical.'
     print,'     size(image1) = ',s
     print,'     size(image2) = ',s2
     xoff = 0 & yoff = 0
     return
  endif
  
  r = 2
  disc = shift(dist(2*r+1),r,r) le r
  
  temp1 = (image1 - min(image1))*250./(max(image1)-min(image1))
  test1 = morph_gradient(temp1,disc)

  temp2 = (image2 - min(image2))*250./(max(image2)-min(image2))
  test2 = morph_gradient(temp2,disc)

; make the edges 0.0 so that edge effects do not influence the result

  test1(*,0) = 0.
  test1(*,1) = 0.
  test1(0,*) = 0.
  test1(1,*) = 0.
  test1(*,s(2)-1) = 0.
  test1(*,s(2)-2) = 0.
  test1(s(1)-1,*) = 0.
  test1(s(1)-2,*) = 0.

  test2(*,0) = 0.
  test2(*,1) = 0.
  test2(0,*) = 0.
  test2(1,*) = 0.
  test2(*,s(2)-1) = 0.
  test2(*,s(2)-2) = 0.
  test2(s(1)-1,*) = 0.
  test2(s(1)-2,*) = 0.

  corrimage = convol_fft(test1,test2,/correlate)
  corrmax = max(corrimage,m)

  csamp = m mod s(1)
  cline = m/s(2)

; Next solve for the sub-pixel location of the maximum of the correlation
; image assuming the correlation image can be approximated by a parabolic
; shape in line and sample direction: y = y2 + b*(x-x2) + c*(x-x2)^2.

  y1 = corrimage(csamp-1,cline)
  y2 = corrimage(csamp,cline)
  y3 = corrimage(csamp+1,cline)

  b = 0.5*(y3-y1)
  c = y1 + b - y2
  xdelta = -b/(2.*c)
  eps_samp = ((0.03/80.)*(y2/c)^2) < 0.5

  y1 = corrimage(csamp,cline-1)
  y3 = corrimage(csamp,cline+1)
  
  b = 0.5*(y3-y1)
  c = y1 + b - y2
  ydelta = -b/(2.*c)
  eps_line = ((0.03/80.)*(y2/c)^2) < 0.5

  if abs(xdelta) gt 0.6 then begin
     xdelta = 0.0
     if not keyword_set(silent) then print,' Warning: Poor correlation in x image offset.'
  endif

  xoff = (m mod (s(1))) - s(1)/2 + xdelta
  
  if abs(ydelta) gt 0.6 then begin
     ydelta = 0.01
     if not keyword_set(silent) then print,' Warning: Poor correlation in y image offset.'
  endif

  yoff = (m/s(2) - s(2)/2) + ydelta

; final tweak: brute force computation of residuals
; look for minimum RMS residuals for small residual shifts

  residuals = fltarr(3,3)
  
  temp = median(image2,7)
  temp(0:1,*) = 0.0
  temp(*,0:1) = 0.0
  temp(s(1)-2:s(1)-1,*) = 0.0
  temp(*,s(2)-2:s(2)-1) = 0.0
  threshold = 0.1*max(temp)
  
  z = where(temp gt threshold)
  
  xo = fltarr(3,3) & yo = xo
  
  for j = 0,2 do begin
     
     for k = 0,2 do begin

        yo(j,k) = yoff + eps_line*(j-1)
        xo(j,k) = xoff + eps_samp*(k-1)
        image3 = image_shift(image1, xo(j,k),yo(j,k))
        diff = image3-image2
        diffsq = median(diff*diff,7) ; filters out cosmic rays
        diffsq(z) = 0.0              ; exclude sky background and edge noise
        residuals(j,k) = total(diffsq)
        
     endfor
  endfor
  
  x = min(residuals,n)
  
  j = n/3
  k = n mod 3
  
  xoff = xo(j,k)
  yoff = yo(j,k)

  if not finite(xoff + yoff) then begin
     if not keyword_set(silent) then print,' Image alignment failed!'
     xoff = 0
     yoff = 0
  endif

  return
  
end

function mpi_image_shift,in_image,x_shift,y_shift

; Shifts an image given supplied x and y offsets
;
; Calling sequence:
;    output_image = mpi_image_shift(in_image, x_shift, y_shift)

  s = size(in_image)
  numsamps = s(1)
  numlines = s(2)
  samps = float(make_array(size=s)) & lines = samps
  samps(0:numsamps-1,0) = findgen(numsamps)
  for i = 1,numlines-1 do samps(*,i) = samps(*,0)
  lines(0,*) = findgen(numlines)
  for i = 1,numsamps-1 do lines(i,*) = lines(0,*)  
  
  x = (samps + x_shift) < (numsamps-1) > 0
  y = (lines + y_shift) < (numlines-1) > 0
  
  out_image = interpolate(in_image,x,y)
  
  x = samps + x_shift
  y = lines + y_shift
  
  z = where( x lt 0. or y lt 0. or x ge numsamps or y ge numlines)
  
  if total(z) gt 0. then out_image(z) = 0.0

  return,out_image
end


function make_polar_image,file1,file2,file3,align=align,flip=flip,outfile=outfile,silent=silent

;---------------------
; make_polar_image.pro
;---------------------
;
; This function ingests registered or unregistered, calibrated,
; polarized images from the Cassini ISS cameras. Input images must be
; in VICAR format, and specified in sets of two or three, with filters 
; consisting of either: 
;   1) P0, P60 and P120
;   2) IRP0 and IRP90
;   3) CLR and IRP0
; with matching colors in the opposite filter position. The order of input
; images is irrelevant, only that they constitute a matching set.
;
; The code includes the transmissions parallel and perpendicular to
; the polarizing axis of the polarizer, derived from observations.
; These are functions of wavelength, and different passbands have
; different effective parallel and perpendicular transmissions. 
;
; As of November 2014, the following filter combinations are supported:
;
;   WAC IRP0/CLR or IRP0/IRP90 + MT2, CB2, MT3, CB3
;   (NAC currently uses WAC values for these filters)
;   
;   NAC P0/P60/P120 + UV3, BL2, GRN, MT1, CB1, MT2, CB2
;
; The returned value is a structure defined as follows:
; 
; If input is two file names (files containing either [IRP0, IRP90] or
; [IRP0, CLR]) the function returns intensity I (same units as the
; original, and indicated by the tag name "intensity") and the Stokes
; parameter Q defined with respect to IRP0 (tag name: "Q").
;
; If input is three files (containing P0, P60, P120) the returned
; structure contains intensity, polarization (from 0.0 to 1.0; tag
; name: "polarization"), and theta, the angle of the electric vector
; relative to the camera Y axis (+/- 90 degrees; tag name: "theta").
;
; For more information on the polarization code implementation, see the ISS
; Data User's Guide, the latest version of which can be obtained at:
;
;   http://pds-imaging.jpl.nasa.gov/software/
;
; Keywords:
;
;  Set the /align keyword to co-register the images if they have
;   not already been co-registered.
;  Set the /flip keyword to flip the output arrays about the x
;   (sample) axis
;  Set the /silent keyword to suppress warning and info messages (but 
;   not error messages).
;  Set the outfile keyword equal to the filename of a VICAR-format
;   file containing the calculated intensity. This file will be given
;   the same label as file1 to track calibration history.
;
; Invoking the program:
;
;  result = make_polar_image(file1,file2,[file3],[/align],[/flip],$
;          [outfile=outfile],[silent=silent])
;
;
; Written by Bob West
;
;  version 1.0, May 25, 2001
; 
;  version 2.0, October 31, 2002 - uses filter derived t_parallel and
;       t_perp from polarization_package.
;
;  version 3.0, January, 2006 - still needs an absolute calibration factor
;       for the intensity calculation.
;
;  version 4.0, November 2007, various revisions by Ben Knowles.
;
;  version 5.0, December 7 2007, converted image input to file input,
;       instituted automatic detection of filter, polarizers,
;       Vis/IR, created structure output.
;
;  version 6.0, August 20, 2013, Cleaned up and incorporated into
;       CISSCAL by Ben Knowles.
;
;  version 7.0, March 14, 2014, No longer assumes T_parallel and T_perpendiular
;       are the same for all polarizers; updates T_parallel and T_perpendicular
;       based on POLCAL calibration results for some filters.  New
;       algorithm by R. West.
;
;  version 8.0, April 23, 2014, Improved error handling and cleaned up
;       for CISSCAL 3.7 by Ben Knowles.
;
;  version 9.0, November 20, 2014, Additional small bug fixes by B. Knowles.

; initialize cisscal variables:
@cisscal_common.pro
CisscalVers = '3.7'
IBatch = -1
debugflag = 1
Cisscal_Log,/nolog

p = n_params()

if p lt 2 then begin
   print,'Error in call to make_polar_image:'
   print,'     Must specify two files for IR, three for VIS polarizers.'
   print,'     You specified ',p
   return,-1
endif

if file_test(file1) eq 0 then begin
   print,'Error in call to make_polar_image:'
   print,'     File ',file1,' does not exist'
   return,-1
endif

if file_test(file2) eq 0 then begin
   print,'Error in call to make_polar_image:'
   print,'     File ',file2,' does not exist'
   return,-1
endif

ImgObj1 = OBJ_NEW('CassImg')
ImgObj1->ReadVic, file1
data1 = ImgObj1->Image()
label1 = ImgObj1->LabelText()

OutObj = ImgObj1

ImgObj2 = OBJ_NEW('CassImg')
ImgObj2->ReadVic, file2
data2 = ImgObj2->Image()
label2 = ImgObj2->LabelText()

x = strpos(label1,'CISSCAL')
cisscal_version = float(strmid(label1,x+8,3))

t = ''''

cal_factor = 1.0

;
; The calibration of the polarizers has changed significantly up to version 3.7.
;  Users should only use version 3.7 or higher

if cisscal_version lt 3.7 then begin
   if not keyword_set(silent) then print,$
      'Intensity will be inaccurate. Use Cisscal 3.7 or higher for polarization studies'
endif

;--------------------------------------------------------------
; For IR polarizers: NAC IRP0+CLR; WAC IRP0+IRP90; WAC IRP0+CLR
;--------------------------------------------------------------

if p eq 2 then begin   

   tt = strpos(label1,'INSTRUMENT_ID') + 15
   camera = strmid(label1,tt,5)

  ; process IR filters

   larray = [label1,label2]
   
   p0index = strpos(larray,t+'IRP0'+t)
   z = where(p0index gt 0)
   if total(z) lt 0 then begin
    print,'Error in make_polar_image: Neither of the input images is IRP0'
    print,'     (Note: Intensity + IRP90 functionality not yet implemented.)'
    return,-1
   endif

   if camera eq 'ISSNA' then begin
      if not keyword_set(silent) then $
         print, 'WARNING: NAC IRP0 is not yet calibrated.  Using WAC Transmission values!!!'
      filter = strmid(larray(z),p0index(z)+8,3)
   endif else begin
      filter = strmid(larray(z),p0index(z)-5,3)
   endelse 

   if total(z) lt 0 then begin
      if camera eq 'ISSNA' then $
         print, 'Error in make_polar_image: Only 2 of 3 files specified' else $
            print, 'Error in make_polar_image: No image labels contain IRP0'
      return,-1
   endif
   if n_elements(z) gt 1 then begin
      print, 'Error in make_polar_image: More than one file contains IRP0'
      return,-1
   endif

   case z of
      0: begin
         irp0 = data1
         label = label2
      end
      1: begin 
         irp0 = data2
         label = label1
      end
   endcase

   if strpos(label,t+filter+t) lt 0 then begin
      print,'Error in make_polar_image: Filters dont match:'
      print,'     IRP0 is coupled with filter ',filter
      if z eq 0 then print,'     '+file2+' is not' else print,'     '+file1+' is not'
      return,-1
   endif

  ; transmissions for IRP0:
   case filter of
      
      'MT2': begin
;         t_parallel  =       0.83
;         t_perp  =    4.78649e-05
;         cal_factor = 2.21155
;         t0 = 1.0
;         t90 = 1.0
         t10 = 0.932473  &    t20 = 0.0180839
         t190 = 0.922464 &  t290 =  0.00000
      end
      
      'CB2': begin
;         t_parallel  =       0.909305
;         t_perp  =    3.95933e-05
;         cal_factor = 2.2238
;         t0 = 1.0
;         t90 = 0.94
         t10 =      0.980000 &    t20 =     0.0178995
         t190 =      0.90512  &  t290 =      0.0320017
      end
      
      'MT3': begin
;         t_parallel  =       0.946314
;         t_perp  =    6.31029e-05
 ;        cal_factor = 2.11791
         t10 =      0.946794 &    t20 =     0.0416498 ; Place-holder number pending calibration
         t190 =      0.966964  &  t290 =     0.00844336 ; Place-holder number pending calibration
         print, 'WARNING: MT3 polarizers not yet calibrated!!!'
      end
      
      'CB3': begin
;         t_parallel  =       0.956206
;         t_perp  =    0.000398540
;;         cal_factor = 2.13846*0.98
;         cal_factor = 2.09569
         t10 =      0.946794 &    t20 =     0.0416498
         t190 =      0.966964  &  t290 =     0.00844336
      end
      
;      'MT1': begin
;         t_parallel  =       0.800691
;         t_perp  =     0.00135032
;      end
;      'CB1': begin
;         t_parallel  =       0.722038
;         t_perp  =     0.00117157
;      end
;      
;      'IR3': begin
;         t_parallel  =       0.954022
;         t_perp  =    0.000325912
;      end
;      
;      'IR1': begin
;         t_parallel  =       0.909035
;         t_perp  =    6.06756e-05
;      end
      
      else: begin
         print,'Error: Filter '+filter+' not yet supported by make_polar_image.pro'
         return,-1
      end
      
   endcase
      
   if strpos(label,t+'IRP90'+t) gt 0 then begin ;IRP0 and IRP90
      case z of
         0: irp90 = data2
         1: irp90 = data1
      endcase
      p90index = strpos(label,t+'IRP90'+t)
      filter2 = strmid(larray(z),p0index(z)-5,3)
        ;irp0 = irp0/t0
        ;irp90 = irp90/t90
         
        ; align images if necesary:   
      if keyword_set(align) then begin
         s = size(irp0)
         numlines = s(2)
         
         if not keyword_set(silent) then print,'Aligning IR images...'
         
         mpi_image_offset,irp90,irp0,xoff,yoff,silent=silent
         irp90 = mpi_image_shift(irp90,xoff,yoff)

         if not keyword_set(silent) then begin
            print,' IRP90 x offset = ',xoff
            print,' IRP90 y offset = ',yoff
         endif
         
         marginx = abs(xoff)
         marginy = abs(yoff)      
      endif
         
;      intensity = (irp0 + irp90) ; old method assumed polarizers have the same transmission values
;      
      denom = t10*t190 - t20*t290
      
      iu = 2.*(irp90*t10 - irp0*t290)/denom                  ; unpolarized component
      ip = (irp0*(t190 + t290) - irp90*(t10 + t20))/denom    ; linearly polarized component
         
      intensity = iu + ip
         
   endif else begin             ;IRP0 and CLR
      case z of
         0: intensity = data2
         1: intensity = data1
      endcase
      
; align images if necesary:   
      if keyword_set(align) then begin
         s = size(irp0)
         numlines = s(2)
            
         if not keyword_set(silent) then print,'Aligning IR images...'
            
         mpi_image_offset,intensity,irp0,xoff,yoff,silent=silent
         intensity = mpi_image_shift(intensity,xoff,yoff)
            
         if not keyword_set(silent) then begin
            print,' CLR x offset = ',xoff
            print,' CLR y offset = ',yoff
         endif
            
         marginx = abs(xoff)
         marginy = abs(yoff)      
      endif
         
      ip = intensity + 2.*(irp0 - intensity*t10)/(t10 - t20)
         
   endelse

; stokes parameter Q:
;   q = ((irp90 - irp0)/(irp90 + irp0))*((t_parallel + t_perp)/(t_parallel - t_perp))
;   q = (irp90 - irp0)/(irp90 + irp0)
   
   q = make_array(size=size(ip),value=0.0)
   z0 = where(intensity ne 0.0)
   q[z0] = -ip[z0]/intensity[z0] > (-1.0) < 1.0
   
; Return  I,Q from IR polarizers

   s = size(q)
   outstruct = {intensity:fltarr(s[2],s[2]),q:fltarr(s[2],s[2])}
      
   if(keyword_set(flip)) then begin
      outstruct.intensity = rotate(intensity,7)
      outstruct.q = rotate(q,7)
   endif else begin
      outstruct.intensity = intensity
      outstruct.q = q
   endelse
      
endif else begin
      
;------------------------------------------
; For NAC Visible polarizers: P0, P60, P120
;------------------------------------------

   result = file_test(file3)
   if result eq 0 then begin
      print,'Error in call to make_polar_image:'
      print,'     File ',file3,' does not exist'
      return,-1
   endif
      
;   data3 = read_vicar(file3,label3)
 
   ImgObj3 = OBJ_NEW('CassImg')
   ImgObj3->ReadVic, file3
   data3 = ImgObj3->Image()
   label3 = ImgObj3->LabelText()  
   
   larray = [label1,label2,label3]
   
   p0index = strpos(larray,t+'P0'+t)
   z = where(p0index gt 0)
   if total(z) lt 0 then begin
      print, 'Error in make_polar_image: No image labels contain P0'
      return,-1
   endif
   if n_elements(z) gt 1 then begin
      print, 'Error in make_polar_image: More than one file contains P0'
      return,-1
   endif
   
   case z of
      0: ip0 = data1
      1: ip0 = data2
      2: ip0 = data3
   endcase
   
   filter = strmid(larray(z),p0index(z)+6,3)
   
   p60index = strpos(larray,t+'P60'+t)
   z = where(p60index gt 0)
   if total(z) lt 0 then begin
      print, 'Error in make_polar_image: No image labels contain P60'
      return,-1
   endif
   if n_elements(z) gt 1 then begin
      print, 'Error in make_polar_image: More than one file contains P60'
      return,-1
   endif
   
   case z of
      0: ip60 = data1
      1: ip60 = data2
      2: ip60 = data3
   endcase
   
   filter2 = strmid(larray(z),p60index(z)+7,3)
   
   p120index = strpos(larray,t+'P120'+t)
   z = where(p120index gt 0)
   if total(z) lt 0 then begin
      print, 'Error in make_polar_image: No image labels contain P120'
      return,-1
   endif
   if n_elements(z) gt 1 then begin
      print, 'Error in make_polar_image: More than one file contains P120'
      return,-1
   endif
   
   case z of
      0: ip120 = data1
      1: ip120 = data2
      2: ip120 = data3
   endcase
   filter3 = strmid(larray(z),p120index(z)+8,3)
   
   if filter ne filter2 or filter ne filter3 then begin
      print,'Error in make_polar_image. Non-polarized filters don''t match:'
      print, filter1
      print, filter2
      print, filter3
      return,-1
   endif
   
; transmissions for P0, P60, P120
   case filter of
      
;      'CL2': begin
;         t_parallel  =       0.568240
;         t_perp  =      0.0255870
;      end
      
      'GRN': begin
;         t_parallel  =       0.614877
;         t_perp  =     0.00303217
;;                    cal_factor = 3.444 ; West derived
;         cal_factor = 3.43011   ; Salmon derived
         T1 = 0.648 & T2 = 0.037 & delta_t = 0.026
         TL0 =  0.675 & TR0 = 0.063
         TL60 = 0.646 & TR60 =  0.045
         TL120 =  0.633 & TR120 = 0.047
      end
      
      'UV3': begin
 ;        t_perp  =       0.0186761
 ;        t_parallel  =       0.471171
;;                    cal_factor = 5.12245 ; West result
;         cal_factor = 5.13161   ; Salmon result
         T1 = 0.54  & T2 = 0.087 & delta_t = 0.043
         TL0 =  0.582 & TR0 = 0.130
         TL60 =  0.538 & TR60 =  0.095
         TL120 =  0.527 & TR120 = 0.093
      end
      
      'BL2': begin
 ;        t_parallel  =       0.560820
 ;        t_perp  =     0.00518267
         T1 = 0.602 & T2 = 0.046 & delta_t = 0.03
         TL0 =  0.632 & TR0 = 0.076
         TL60 = 0.598 & TR60 =  0.056
         TL120 =  0.584 & TR120 = 0.057
      end
      
      'MT2': begin
 ;        t_parallel  =       0.762722
 ;        t_perp  =      0.0544492
 ;        cal_factor = 2.60783
         T1 = 0.793 & T2 = 0.085 & delta_t = 0.051
;         TL0 = 0.845 & TR0 = 0.136
;         TL60 =  0.824 & TR60 =  0.055
;         TL120 =  0.810 & TR120 = 0.069
         TL0 = 0.817 & TR0 = 0.163
         TL60 = 0.794 & TR60 = 0.085
         TL120 = 0.781 & TR120 = 0.097
      end
      
      'CB2': begin
 ;        t_parallel  =       0.777493
 ;        t_perp  =      0.0874226
 ;        cal_factor = 2.41770
         T1 = 0.815 & T2 = 0.125 & delta_t = 0.052
;         TL0 =  0.866 & TR0 = 0.176
;         TL60 = 0.841 & TR60 =  0.102
;         TL120 = 0.841 & TR120 = 0.095
         TL0 = 0.841 & TR0 = 0.202
         TL60 = 0.814 & TR60 = 0.129
         TL120 = 0.813 & TR120 = 0.123
      end
      
      'MT1': begin
 ;        t_parallel  =       0.640370
 ;        t_perp  =     0.00352720
 ;        cal_factor = 3.13776
         T1 = 0.655 & T2 = 0.018 & delta_t = 0.03
         TL0 =  0.685 & TR0 = 0.049
         TL60 = 0.649 & TR60 =  0.029
         TL120 =  0.637 & TR120 = 0.031
      end
      
      'CB1': begin
 ;        t_parallel  =       0.635892
 ;        t_perp  =     0.00350794
 ;        cal_factor = 3.2588
         T1 = 0.654  & T2 = 0.022 & delta_t = 0.032
         TL0 =  0.685 & TR0 = 0.053
         TL60 = 0.649 & TR60 =  0.030
         TL120 =  0.639 & TR120 = 0.034
      end
      
      else: begin
         print,'Error: Filter '+filter+' not yet supported by make_polar_image.pro'
         return,-1
      end
      
   endcase

   if keyword_set(align) then begin
      s = size(ip0)
      numlines = s(2)
      
      if not keyword_set(silent) then print,'Aligning images...'
      
      mpi_image_offset,ip60,ip0,xoff60,yoff60,silent=silent
      ip60 = mpi_image_shift(ip60,xoff60,yoff60)
      
      if not keyword_set(silent) then begin
         print,' P60 x offset = ',xoff60
         print,' P60 y offset = ',yoff60
      endif      

      mpi_image_offset,ip120,ip0,xoff120,yoff120,silent=silent
      ip120 = mpi_image_shift(ip120,xoff120,yoff120)
      
      if not keyword_set(silent) then begin
         print,' P120 x offset = ',xoff120
         print,' P120 y offset = ',yoff120
      endif

      marginx = max([abs(xoff60),abs(xoff120)])
      marginy = max([abs(yoff60),abs(yoff120)])
   endif

; Calculate Intensity, Polarization, Theta:

; IF NAC (P0, P60, P120):
;   intensity = (2./(3.*(t_parallel + t_perp)))*(ip0 + image_p60 + ip120)

; Calculate an approximate value of the angle of the polarization
; assuming the polarizers are oriented at exactly 0, 60 and 120 degrees

  ; term1 = (ip60 + ip120 - 2.*ip0)

   ;term2 = ip60 - ip120

   ;ip = sqrt((term1/(1.5*(t_parallel-t_perp)))^2 + $
   ;          (term2/(sin(!pi*120./180.)*(t_parallel-t_perp)))^2)
   
   ;term2_good = where(abs(term2) ge 1.e-05)
   ;sign = make_array(size = size(term2), value=1.0)
   
   ;sign[term2_good] = term2[term2_good]/abs(term2[term2_good])
   
   ;theta = 0.5*sign*(180./!pi)*acos(term1/(1.5*ip*(t_perp-t_parallel)))
  
   
; make correction for true polarizer orientations
;
; Here the angle theta should be accurate to 0.015 degree.  Better
; estimates can be made of polarization and intensity

;   theta0 = -0.5                ; from the calibration report
;  theta60 = 61.8
;  theta120 = 120.8

   s = size(ip60)
; the following derived by fitting residuals with program generate_polar_lut.pro
;   temp =  theta + 0.658*(1. + cos(4*(theta-6.26)*!pi/180.)) + 0.04
;   theta = temp
;   z = where(temp gt 90.)
;   if total(z) gt 0 then theta[z] = theta[z] -180.
   
   radians = !pi/180.           ; radians per degree
;   c0 = cos((theta-theta0)*radians)^2
;   c60 = cos((theta-theta60)*radians)^2
;   c120 = cos((theta-theta120)*radians)^2
   
;   s0 = sin((theta-theta0)*radians)^2
;   s60 = sin((theta-theta60)*radians)^2
;   s120 = sin((theta-theta120)*radians)^2
   
;   denom1 = t_parallel*(2.*c0-c60-c120) + t_perp*(2.*s0-s60-s120)
   
;   denom2 = t_parallel*(c60-c120) + t_perp*(s60-s120)
   
;   z1 = where(abs(denom1) ge abs(denom2))
;   z2 = where(abs(denom2) ge abs(denom1))
 
; polarized component
;   if total(z1) gt 0 then ip[z1] = (2.*ip0[z1] - ip60[z1] -ip120[z1])/denom1[z1]
;   if total(z2) gt 0 then ip[z2] = (ip60[z2]-ip120[z2])/denom2[z2]

; unpolarized component
;   iu = (2./(3.*(T_parallel + t_perp)))*((ip0 + ip60 + ip120) -$
;        ip*(t_parallel*(c0 + c60 + c120) + t_perp*(s0 + s60 + s120)))
   
;   intensity = ip +  iu
;   polarization = ip/intensity  ; range is 0.0 to 1.0

   mpi_calc_ipt,Ip0,Ip60,Ip120,T1,T2,delta_t,Intensity,Polarization,Theta
   if min(finite(intensity)) eq 0 or min(finite(polarization)) eq 0 or $ 
      min(finite(theta)) eq 0 then begin
      if not keyword_set(silent) then print,' Warning: Non-finite values in output arrays!'
   endif 

   a = finite(theta)
   theta_bad = where(a ne 1)
   if total(theta_bad) gt 0 then theta[theta_bad] = 0.0
   
; set border region to 0 where there is not sufficient overlap
   if keyword_set(align) then begin
      intensity[0:marginx,*] = 0.
      intensity[s[1]-marginx-1:s[1]-1,*] = 0.
      intensity[*,0:marginy] = 0.
      intensity[*,s[2]-marginy-1:s[2]-1] = 0.
      polarization[0:marginx,*] = 0.
      polarization[s[1]-marginx-1:s[1]-1,*] = 0.
      polarization[*,0:marginy] = 0.
      polarization[*,s[2]-marginy-1:s[2]-1] = 0.
      theta[0:marginx,*] = 0.
      theta[s[1]-marginx-1:s[1]-1,*] = 0.
      theta[*,0:marginy] = 0.
      theta[*,s[2]-marginy-1:s[2]-1] = 0.
   endif
   
   diffi0 = make_array(size=size(ip0)) & diffi60 = diffi0 & diffi120 = diffi0
   iu = intensity*(1.0-polarization)
   ip = intensity-iu
   
   diffi0 = ip0-(iu*(TL0+TR0)/2 + Ip*(TL0*cos((theta+0.5)/!radeg)^2 + $
                                      TR0*sin((theta+0.5)/!radeg)^2))
   diffi60 = ip60-(iu*(TL60+TR60)/2 + Ip*(TL60*cos((theta-61.8)/!radeg)^2 + $
                                          TR60*sin((theta-60.8)/!radeg)^2))
   diffi120 = ip120-(iu*(TL120+TR120)/2 + Ip*(TL120*cos((theta-120.8)/!radeg)^2 + $
                                              TR120*sin((theta-120.8)/!radeg)^2))
   rms_image = (sqrt((diffi0^2 + diffi60^2 + diffi120^2)/3.))
   
   rms = total(rms_image)

   ; improve the result with iteration

   tempi = intensity
   temppol = polarization
   temptheta = theta
   status_image = make_array(S[1],S[2],/byte,value=3)
   
   for k = 0,s[2]-1 do begin
      for j = 0,s[1]-1 do begin
 ;     for k = 256, 256 do begin ; for debugging
 ;     for j = 400,400 do begin
         ti = intensity[j,k]
         tp = polarization[j,k]
         ttheta = theta[j,k]
         status = byte(3)
         mpi_iterate_pol,IP0[j,k],IP60[j,k],IP120[j,k],TL0,TR0,TL60,TR60,TL120,TR120,$
                         ti,tp,ttheta,status
         tempI[j,k] = ti
         tempPol[j,k] = tp
         tempTHETA[j,k] = ttheta
         status_image[j,k] = status
      endfor
   endfor
   
   z = where(status_image eq 0)
   bad = where(status_image ne 0)
   if not keyword_set(silent) then $
      print,'Fraction of image with bad pixels is ',n_elements(bad)/(float(n_elements(intensity)))
   intensity[z] = tempi[z]
   polarization[z] = temppol[z]
   theta[z] = temptheta[z]
   
   diffi0 = make_array(size=size(ip0)) & diffi60 = diffi0 & diffi120 = diffi0
   iu = intensity*(1.0-polarization)
   ip = intensity-iu
   diffi0 = ip0-(iu*(TL0+TR0)/2 + Ip*(TL0*cos((theta+0.5)/!radeg)^2 + $
                                      TR0*sin((theta+0.5)/!radeg)^2))
   diffi60 = ip60-(iu*(TL60+TR60)/2 + Ip*(TL60*cos((theta-61.8)/!radeg)^2 + $
                                          TR60*sin((theta-60.8)/!radeg)^2))
   diffi120 = ip120-(iu*(TL120+TR120)/2 + Ip*(TL120*cos((theta-120.8)/!radeg)^2 + $
                                              TR120*sin((theta-120.8)/!radeg)^2))
   rms_image = (sqrt((diffi0^2 + diffi60^2 + diffi120^2)/3.))

   rms = total(rms_image)
   
; return Intensity, Polarization, Theta as a structure
   
   outstruct = {intensity:fltarr(s[2],s[2]),polarization:fltarr(s[2],s[2]),theta:fltarr(s[2],s[2])}
      
   if(keyword_set(flip)) then begin
      outstruct.intensity = rotate(intensity,7)
      outstruct.polarization = rotate(polarization,7)
      outstruct.theta = rotate(theta,7)
   endif else begin
      outstruct.intensity = intensity
      outstruct.polarization = polarization
      outstruct.theta = theta
   endelse
   
endelse

  
; write to Vicar-formatted file include label from file1. 
if keyword_set(outfile) then begin
   if not keyword_set(silent) then print, 'Writing intensity array in VICAR format to file: ',outfile
   OutObj->writevic,outfile,pol=outstruct.intensity
endif

IF OBJ_VALID(OutObj) THEN OBJ_DESTROY,OutObj
IF OBJ_VALID(ImgObj1) THEN OBJ_DESTROY,ImgObj1
IF OBJ_VALID(ImgObj2) THEN OBJ_DESTROY,ImgObj2
IF OBJ_VALID(ImgObj3) THEN OBJ_DESTROY,ImgObj3

return,outstruct

end
