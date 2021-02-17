; CISSCAL Option file reader for GUI and command-line mode
;   Ben Knowles, 5/2006
;   - Update (BDK, 1/28/13): simplified bias/2hz removal options,
;     incorporated into GUI

function cisscal_readoptfile,filename,default=default,nimages=nimages,bias=bias,twohz=twohz,flux=flux,geom=geom,im_threshold=im_threshold,im_pixrange=im_pixrange,spec=spec,mask=mask,suffixes=suffixes,bmode=bmode

nfiles = n_elements(filename)

; start by defining options array with default options:

optsarr = {                                                                 $
             lutc     :   ptr_new({onoff : 1L}),                            $  
             bitw     :   ptr_new({onoff : 1L}),                            $
             bias     :   ptr_new({onoff : 1L,                              $ 
                                   biasstripmean : 0L}),                    $
             twohz    :   ptr_new({onoff : 1L,                              $ 
                                   imagemean : ptr_new({onoff    : 0L,      $
                                                        maskfile  : '',     $
                                                        missingfile : '',   $
                                                        threshold : 0.0,    $
                                                        pixrange  : 9.0})}),$
             dark     :   ptr_new({onoff    : 1L,                           $
                                   darkfile : ''}),                         $
             abpp     :   ptr_new({onoff : 1L,                              $
                                   threshold : 30.0}),                      $
             lin      :   ptr_new({onoff : 1L}),                            $
             flat     :   ptr_new({onoff : 1L}),                            $
             flux     :   ptr_new({onoff : 1L,                              $
                                   ioverf : ptr_new({onoff    : 1L,         $
                                                     specfile : '',         $
                                                     dfs      : -1.0}),     $
                                   gain_onoff : 1L,                         $
                                   expt_onoff : 1L,                         $
                                   opta_onoff : 1L,                         $
                                   tran_onoff : 1L}),                       $
             corr     :   ptr_new({onoff : 1L,                              $
                                   type : 0L}),                             $
             geom     :   ptr_new({onoff : 0L}),                            $
             defval   :   ptr_new({saturated: !values.f_nan,                $
                                   missing:   !values.f_nan})}

if nfiles gt 1 then begin
    optsarr = replicate(optsarr,nfiles)
    suffixes = replicate('',nfiles)
endif else begin
    suffixes = ''
endelse

; Read option file (if /default keyword not set):

if not keyword_set(default) then begin
   for i=0,nfiles-1 do begin
      openr,lun,filename[i],/get_lun
        
      values = strarr(27)
      count = 0
      oneline = ''
      
      while not eof(lun) do begin
         readf, lun, oneline
         
;   Skip blank lines.
         if oneline eq '' then continue
            
;   Parse the line into fields separated by colons.
         split_line = strsplit(oneline, ':', /extract)
         numfields = n_elements(split_line)
            
;   Interested in lines with two or more space-delimited fields.
         if numfields lt 2l then continue
            
         values[count] = strtrim(split_line[1l],2)
            
         count = count + 1
      endwhile
        
      close,lun
      free_lun,lun
   
;   LUT conversion (Y or N)
      if values[0] eq 'Y' then (*(optsarr[i]).lutc).onoff = 1l else $
         (*(optsarr[i]).lutc).onoff = 0l
      
;   bitweight correction (Y or N)
      if values[1] eq 'Y' then (*(optsarr[i]).bitw).onoff = 1l else $
         (*(optsarr[i]).bitw).onoff = 0l
        
;   bias subtraction (Y or N)        
      if values[2] eq 'Y' then begin
         (*(optsarr[i]).bias).onoff = 1l 
      endif else begin
         (*(optsarr[i]).bias).onoff = 0l
         (*(optsarr[i]).twohz).onoff = 0l
      endelse
      
;   bias subtraction type (BSM or OC or IM)
      bmode = 1
      if values[3] eq 'BSM' then begin
         (*(optsarr[i]).bias).biasstripmean = 1l 
         (*(optsarr[i]).twohz).onoff = 0l
         bmode = 0
      endif else if values[3] eq 'OC' then begin
         (*(optsarr[i]).bias).biasstripmean = 0l 
         (*(optsarr[i]).twohz).onoff = 1l
         (*(*(optsarr[i]).twohz).imagemean).onoff = 0l
         bmode = 1
      endif else if values[3] eq 'IM' then begin
         (*(optsarr[i]).bias).biasstripmean = 1l
         (*(optsarr[i]).twohz).onoff = 1l
         (*(*(optsarr[i]).twohz).imagemean).onoff = 1l
         bmode = 2
      endif
      
;  two hz removal (Y or N)          
;  if values[4] eq 'Y' then (*(optsarr).twohz).onoff = 1l else $
;    (*(optsarr).twohz).onoff = 0l
  
;  two hz removal type  (IM or OC)  
;  if values[5] eq 'OC' then (*(*(optsarr).twohz).imagemean).onoff = 0l else if $
;    values[5] eq 'IM' then (*(*(optsarr).twohz).imagemean).onoff = 1l
        
;      maskfile (auto if not set)     
      if values[4] ne '' then (*(*(optsarr[i]).twohz).imagemean).maskfile = values[4]

;      missingfile (not used)         
        
;      theshold (auto = 0.0)          
      val = float(values[6])
      (*(*(optsarr[i]).twohz).imagemean).threshold = val
        
;      pixrange (default = 9.0)       
      val = float(values[7])
      (*(*(optsarr[i]).twohz).imagemean).pixrange = val
        
;   dark subtraction (Y or N)        
      if values[8] eq 'Y' then (*(optsarr[i]).dark).onoff = 1l else $
         (*(optsarr[i]).dark).onoff = 0l
        
;   dark file (overrides models)   
      if values[9] ne '' then (*(optsarr[i]).dark).darkfile = values[9]
      
;   anti-blooming pixel pair removal 
      if values[10] eq 'Y' then (*(optsarr[i]).abpp).onoff = 1l else $
         (*(optsarr[i]).abpp).onoff = 0l
        
;   abpp threshold (default = 30.0)
      val = float(values[11])
      (*(optsarr[i]).abpp).threshold = val
        
;   linearize (Y or N)
      if values[12] eq 'Y' then (*(optsarr[i]).lin).onoff = 1l else $
         (*(optsarr[i]).lin).onoff = 0l
        
;   flatfield (Y or N)   
      if values[13] eq 'Y' then (*(optsarr[i]).flat).onoff = 1l else $
         (*(optsarr[i]).flat).onoff = 0l
        
;   flux conversion (Y or N)
      if values[14] eq 'Y' then (*(optsarr[i]).flux).onoff = 1l else $
         (*(optsarr[i]).flux).onoff = 0l
        
;   flux conversion type (I or IOF)
      if values[15] eq 'IOF' then (*(*(optsarr[i]).flux).ioverf).onoff = 1l else if $
         values[15] eq 'I' then (*(*(optsarr[i]).flux).ioverf).onoff = 0l
        
;      spectrum file (overrides solar)
      if values[16] ne '' then (*(*(optsarr[i]).flux).ioverf).specfile = values[16]
        
;      distance from sun (J, S, or AU)
      if values[17] eq 'J' then (*(*(optsarr[i]).flux).ioverf).dfs = -2L else if $
         values[17] eq 'S' then (*(*(optsarr[i]).flux).ioverf).dfs = -1L
        
      if stregex(values[17],'[0123456789]',/boolean) then $
         (*(*(optsarr[i]).flux).ioverf).dfs = float(values[17])
        
;      multiply by gain (Y or N)
      if values[18] eq 'Y' then (*(optsarr[i]).flux).gain_onoff = 1L else $
         (*(optsarr[i]).flux).gain_onoff = 0L

;      divide by exposure time (Y or N)
      if values[19] eq 'Y' then (*(optsarr[i]).flux).expt_onoff = 1L else $
         (*(optsarr[i]).flux).expt_onoff = 0L

;      divide by optics area/pixel solid angle (Y or N)
      if values[20] eq 'Y' then (*(optsarr[i]).flux).opta_onoff = 1L else $
         (*(optsarr[i]).flux).opta_onoff = 0L

;      divide by system transmission (Y or N)
      if values[21] eq 'Y' then (*(optsarr[i]).flux).tran_onoff = 1L else $
         (*(optsarr[i]).flux).tran_onoff = 0L

;   correction factors (Y or N or J)    
      if values[22] eq 'Y' or values[22] eq 'J' then (*(optsarr[i]).corr).onoff = 1l else if $
         values[22] eq 'N' then (*(optsarr[i]).corr).onoff = 0l
      
      if values[22] eq 'J' then (*(optsarr[i]).corr).type = 1l else (*(optsarr[i]).corr).type = 0l

;   geometric correction (Y or N)    
      if values[23] eq 'Y' then (*(optsarr[i]).geom).onoff = 1l else $
         (*(optsarr[i]).geom).onoff = 0l
      
;   default output filename suffix
      if values[24] ne '' then suffixes[i] = values[24]
  
;   default output saturated pixel value
      if values[25] eq '' then (*(optsarr[i]).defval).saturated = !values.f_infinity else if $ ; no change
         values[25] eq 'NAN' then (*(optsarr[i]).defval).saturated = !values.f_nan else $      ; NAN
            (*(optsarr[i]).defval).saturated = float(values[25])
      
;   default output missing pixel value
      if values[26] eq 'NAN' then (*(optsarr[i]).defval).missing = !values.f_nan else $ ; NAN
         (*(optsarr[i]).defval).missing = float(values[26])
      
   endfor 
endif

for i=0,nfiles-1 do begin
;Keyword calibration options override option file settings and defaults:
    if keyword_set(bias) then begin
        if bias eq 'BSM' then (*(optsarr[i]).bias).biasstripmean = 1l else if $
          bias eq 'OC' then (*(optsarr[i]).bias).biasstripmean = 0l else if $
          bias eq 'OFF' then (*(optsarr[i]).bias).onoff = 0l
    endif

    if keyword_set(twohz) then begin
        if twohz eq 'OC' then (*(*(optsarr[i]).twohz).imagemean).onoff = 0l else if $
          twohz eq 'IM' then (*(*(optsarr[i]).twohz).imagemean).onoff = 1l else if $
          twohz eq 'OFF' then (*(optsarr[i]).twohz).onoff = 0l
    endif

    if keyword_set(im_threshold) then $
         (*(*(optsarr[i]).twohz).imagemean).threshold = im_threshold

    if keyword_set(im_pixrange) then $
         (*(*(optsarr[i]).twohz).imagemean).pixrange = im_pixrange

    if keyword_set(twohz) then begin
        if twohz eq 'OC' then (*(*(optsarr[i]).twohz).imagemean).onoff = 0l else if $
          twohz eq 'IM' then (*(*(optsarr[i]).twohz).imagemean).onoff = 1l else if $
          twohz eq 'OFF' then (*(optsarr[i]).twohz).onoff = 0l
    endif

    if keyword_set(geom) then (*(optsarr[i]).geom).onoff = 1l

    if keyword_set(flux) then begin
        if flux eq 'I' then (*(*(optsarr[i]).flux).ioverf).onoff = 0l else if $
          flux eq 'IOF' then (*(*(optsarr[i]).flux).ioverf).onoff = 1l else if $
          flux eq 'OFF' then (*(optsarr[i]).flux).onoff = 0l
    endif 

    if keyword_set(spec) then begin
        (*(optsarr[i]).flux).onoff = 1l
        (*(*(optsarr[i]).flux).ioverf).onoff = 1l
        (*(*(optsarr[i]).flux).ioverf).specfile = spec        
    endif

    if keyword_set(mask) then begin
        (*(optsarr[i]).twohz).onoff = 1l
        (*(*(optsarr[i]).twohz).imagemean).onoff = 1l
        (*(*(optsarr[i]).twohz).imagemean).maskfile = mask
    endif

endfor

return,optsarr


end
