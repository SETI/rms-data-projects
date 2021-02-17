;;	cassimg__dividebyefficiency.pro
;;	Correct image for filter and CCD efficiency
;;
;;	The calibration results files now include a file
;;	 "effic.db" which is a text database containing
;;	 conversion factors for the two instruments and their
;;	 planned and calibrated filter combinations.
;;
;;	Kevin	July 1999

PRO CassImg::DivideByEfficiency

@cisscal_common.pro	; include COMMON definitions

units = 'UNK'

Filter1 = self.Filter1
Filter2 = self.Filter2

; for polarized filter combinations, use corresponding clear 
; transmission:

if strpos(Filter1+Filter2,'P') ge 0 then begin
   if self.Instrument eq 'ISSNA' then Filter1 = 'CL1'
   if self.Instrument eq 'ISSWA' then Filter2 = 'CL2'
endif 

; read in system transmission (T0*T1*T2*QE)

transfile = CalibrationBaseDir + 'efficiency/systrans/' + $
  strlowcase(self.Instrument + Filter1 + Filter2) + $
  '_systrans.tab'

if file_test(transfile) then begin
    cisscal_readspec, transfile, lambda_t, trans, n_trans
endif else begin
    IF DebugFlag gt 0 THEN BEGIN
        CISSCAL_Log,'  For IBatch = '+strtrim(string(IBatch),2)
        CISSCAL_Log,'    systrans file '+transfile+' not found. Skipping step...'
    ENDIF
    RETURN
endelse

; only apply QE correction if correction factor toggle set:

if (*(*CalOptions).corr).onoff then begin
    if self.Instrument EQ 'ISSNA' then begin
        qecorrfile = CalibrationBaseDir + 'correction/nac_qe_correction.tab'
        cisscal_readspec, qecorrfile, lambda_q, qecorr, n_qecorr
    endif else if self.Instrument EQ 'ISSWA' then begin
        qecorrfile = CalibrationBaseDir + 'correction/wac_qe_correction.tab'
        cisscal_readspec, qecorrfile, lambda_q, qecorr, n_qecorr
    endif
endif else begin
    qecorr = replicate(1.,901)
    lambda_q = findgen(901)+200
endelse


if (*(*(*CalOptions).flux).ioverf).onoff then begin

; I/F mode ON:

   IF DebugFlag gt 0 THEN CISSCAL_Log,'  I/F mode ON: image flux will be normalized'

    ; read in spectral file

    specfile = (*(*(*CalOptions).flux).ioverf).specfile

    if specfile eq '' then begin
        specfile = CalibrationBaseDir + 'efficiency/solarflux.tab'
        ang_to_nm = 10.
        pifact = !pi

        ; get distance from sun (AU):

        dfs_val = (*(*(*CalOptions).flux).ioverf).dfs
        
        if dfs_val le 0 then begin
            if dfs_val eq -1 then body = 'SATURN' else $
              if dfs_val eq -2 then body = 'JUPITER' else $
              body = 'UNKNOWN'

;	Get exposure timestamp, extract year and day, 
;        estimate decimal year of exposure
            ImgTime = self->GetLabel('IMAGE_TIME')

            ; Modifed by MRS
            ; ImgTime is a string array of size 1, so ImgTimeYF was a float
            ; array of size 1. In GDL and in the formal definition of IDL, this
            ; meant that dfs was also a float array of size 1. This had
            ; unfortunate repercussions described below.

            ;ImgTimeY = STRMID(ImgTime,0,4)             ; old
            ImgTimeY = (STRMID(ImgTime,0,4))[0]         ; new
            ;ImgTimeD = STRMID(ImgTime,5,3)             ; old
            ImgTimeD = (STRMID(ImgTime,5,3))[0]         ; new
            ImgTimeYF = ImgTimeY + (ImgTimeD / 365.0)
            
            dfs = SolarDist(body,ImgTimeYF)

            IF DebugFlag gt 0 THEN CISSCAL_Log,'  Solar distance from '+body+' = ',$
              strtrim(string(dfs),2),' AU'

        endif else begin
            dfs = dfs_val
        endelse

        if dfs le 0 then RETURN 
        
        units = 'I/F'

    endif else begin         
        ; for user-specified spectrum, lambda should be in nm,
        ; and flux in photons/cm^2/s/nm(/ster if not integrated
        ; over object)

        ang_to_nm = 1.
        dfs = 1.
        pifact = 1.

        units = 'NORM'

    endelse

    cisscal_readspec, specfile, lambda_f, flux, n_spec

    if n_spec eq 2l then RETURN

    lambda_f = temporary(lambda_f/ang_to_nm)
    flux = temporary(flux*ang_to_nm)

; create new wavelength vector

    minlam=ceil(max([min(lambda_t),min(lambda_f),min(lambda_q)]))
    maxlam=floor(min([max(lambda_t),max(lambda_f),max(lambda_q)]))

    lambda = [lambda_f,lambda_t,lambda_q]
    lambda = lambda[where((lambda ge minlam) and (lambda le maxlam))]
    lambda = lambda[uniq(lambda,sort(lambda))]

    newtrans = interpol(trans,lambda_t,lambda)
    newqecorr = interpol(qecorr,lambda_q,lambda)

    ; Note from MRS
    ; The line below did the wrong thing in GDL because dfs was a float array
    ; of size 1 rather than a scalar. Because array arithmetic is formally
    ; defined to return the array of the smallest size, this made newflux an
    ; array of size 1.

    newflux = interpol(flux,lambda_f,lambda)/(pifact * dfs^2)

    ;int_tabulated.pro uses the newton-cotes method to integrate:

    ; Note from MRS
    ; The line below failed in GDL because newtrans*newqecorr*newflux was an
    ; array of size 1, due to the fact that newflux was an array of size 1.
    ; Function int_tabulated requires that both arguments be arrays of the same
    ; size.

    EffFact = int_tabulated(lambda,newtrans*newqecorr*newflux)
    Effic = int_tabulated(lambda,newtrans*newqecorr)

endif else begin

; I/F mode OFF:

; create new wavelength vector

    minlam=ceil(max([min(lambda_t),min(lambda_q)]))
    maxlam=floor(min([max(lambda_t),max(lambda_q)]))

    lambda = [lambda_t,lambda_q]
    lambda = lambda[where((lambda ge minlam) and (lambda le maxlam))]
    lambda = lambda[uniq(lambda,sort(lambda))]

    newtrans = interpol(trans,lambda_t,lambda)
    newqecorr = interpol(qecorr,lambda_q,lambda)
 
    ;int_tabulated.pro uses the newton-cotes method to integrate:

    EffFact = int_tabulated(lambda,newtrans*newqecorr)
    Effic = EffFact

    if (*(*CalOptions).flux).gain_onoff and (*(*CalOptions).flux).expt_onoff and $
       (*(*CalOptions).flux).opta_onoff then units = 'PHOT/CM^2/S/NM/STER'

endelse

*self.ImageP = *self.ImageP / EffFact
IF DebugFlag eq 2 THEN CISSCAL_Log, '  Pixel flux extrema ', self->DNRange()

;	Update calibration history in image label:
;		(added by Ben Knowles, 4/02)
;               (revamped for CISSCAL 3.7, 5/13)

newhistory='Divided by efficiency factor of '+strtrim(string(Effic),2)

oldhistory = self.Labels->Get('RADIOMETRIC_CORRECTION_TEXT',index=rindex,/quiet)

; if keyword found and is the last one set, we know it was set by
; current CISSCAL process, so append new history:

; Modified by MRS:
; In GDL and in the formal IDL definition, you can only access the attributes of
; a class from a function that operates on that class. This function operates on
; class CassImg, so the attribute .NLabels of class CassLabels is inaccessible.
; Use of the new function CassLabels::Get_NLabels() solves this problem.

;if rindex eq (self.Labels).NLabels-1 then begin                ; old
if rindex eq (self.Labels)->Get_NLabels()-1 then begin          ; new
   junk=self.Labels->Set('RADIOMETRIC_CORRECTION_TEXT',oldhistory + '; ' + newhistory,1)
endif else begin
   junk=self.Labels->Set('RADIOMETRIC_CORRECTION_TEXT',newhistory,1,/new)
endelse

junk=self.Labels->Set('UNITS',units,1,/new)

IF DebugFlag gt 0 then begin
   CISSCAL_Log,' ',newhistory
   if units eq 'NORM' then $
      newflag = ' Flux normalized to user-input spectrum' else $
         newflag = 'Units in '+units
   CISSCAL_Log,' ',newflag
ENDIF

END



