
; CISSCAL Batch mode GUI event handler
; - Ben Knowles, 5/2004

PRO batchgui_event, event
@cisscal_common.pro

; Gain access to the batch GUI's control structure:
widget_control, event.top, get_uvalue=pstruct, /no_copy

; Get ImgObj from uvalue of dummy top-level base:
stash = widget_info(event.top, /child)
widget_control, stash, get_uvalue=dummytlb
widget_control, dummytlb, get_uvalue=ImgObj, /no_copy

case event.id of
    pstruct.cancelid   : BEGIN     ; CANCEL
        widget_control, dummytlb, set_uvalue=ImgObj, /no_copy
        widget_control, event.top, set_uvalue=pstruct, /no_copy
        widget_control, event.top, /destroy
        return
        END
    pstruct.saveid     : BEGIN     ; SAVE OPTIONS
        optionsfile = DIALOG_PICKFILE(FILTER='*batch.sav',$
                                      TITLE='Write Batch Options File', $
                                      PATH=CalibrationBaseDir,FILE='defaultbatch.sav')
        if optionsfile ne '' then begin
            save,BatchParams,filename=optionsfile
            if DebugFlag gt 0 then Cisscal_Log,'Batch options saved to '+optionsfile
        endif
        END
    pstruct.loadid     : BEGIN     ; LOAD OPTIONS
        optionsfile = DIALOG_PICKFILE(FILTER='*batch.sav',$
                                      TITLE='Load Batch Options File', $
                                      PATH=CalibrationBaseDir)
        if file_test(optionsfile) then begin
            restore,optionsfile
            if DebugFlag gt 0 then Cisscal_Log,'Loaded batch options file '+optionsfile

            widget_control, pstruct.indirid, set_value=(*BatchParams).inputdir
            if (*BatchParams).inputtype eq 0 then begin
                widget_control, pstruct.instring, set_value=(*BatchParams).inputregexp
                widget_control, pstruct.inputtype, set_value=0
            endif else begin
                widget_control, pstruct.instring, set_value=(*BatchParams).inputlist
                widget_control, pstruct.inputtype, set_value=1
            endelse
            widget_control, pstruct.outdirid, set_value=(*BatchParams).outputdir
            widget_control, pstruct.outextid, set_value=(*BatchParams).outputext
            widget_control, pstruct.darkdirid, set_value=(*(*BatchParams).dark).dir
            widget_control, pstruct.darklistid, set_value=(*(*BatchParams).dark).list

            if (*(*BatchParams).dark).uselist eq 0 then begin
;                if (*(*CalOptions).dark).model eq '2-param' then $
;                  widget_control, pstruct.darkoptsid, set_value=0 else $
;                  if (*(*CalOptions).dark).model eq 'interp' then $
;                  widget_control, pstruct.darkoptsid, set_value=1
                widget_control, pstruct.darkbaseid, sensitive=0
            endif else begin
                widget_control, pstruct.darkoptsid, set_value=2
                widget_control, pstruct.darkbaseid, sensitive=1
            endelse
        endif else begin
            if DebugFlag gt 0 then begin
               Cisscal_Log
               Cisscal_Log,'Batch options file invalid: '+optionsfile
            endif
        endelse
        END
    pstruct.runbatchid : BEGIN     ; RUN BATCH MODE
       ; kill window:
        GuiEnabMenuOpts,0
        widget_control, dummytlb, set_uvalue=ImgObj, /no_copy
        widget_control, event.top, set_uvalue=pstruct, /no_copy
        widget_control, event.top, /destroy

        if DebugFlag gt 0 then begin
           Cisscal_Log
           Cisscal_Log,'Begin batch processing...'
        endif
        
        if strlowcase(!version.os_family) eq 'windows' then $     ; make work in windows
          slash = '\' else slash = '/'

        inputdir = (*BatchParams).inputdir
        if strmid(inputdir, strlen(inputdir)-1, 1) ne slash then $
          inputdir = inputdir + slash
       
        outputdir = (*BatchParams).outputdir
        if strmid(outputdir, strlen(outputdir)-1, 1) ne slash then $
          outputdir = outputdir + slash
        
        if (*BatchParams).inputtype eq 0 then begin   ; if using filter
            
                                ; make filelist array:
            filelist = file_search(inputdir+(*BatchParams).inputregexp,$
                                   count=nfiles,/test_regular)
            
            if nfiles eq 0 then begin ; file list appears to be invalid
                if DebugFlag gt 0 then Cisscal_Log,$
                  '  ERROR: Cannot run batch; no image files found at requested location.'
                return
            endif
    
        endif else begin                              ; if using input list
            inputlist = (*BatchParams).inputlist
           ; if no directory specified, assume list in input directory
            if strpos(inputlist,slash,/reverse_search) eq -1 then $
              inputlist = inputdir + inputlist

            if file_test(inputlist,/read) then begin
                
                cisscal_readlist, inputlist, filelist, nfiles, /noheader
                filelist = strtrim(inputdir + filelist,2)

            endif else begin
                if DebugFlag gt 0 then Cisscal_Log,$
                  '  ERROR: Cannot run batch; no valid file list specified.'
                return
            endelse
        endelse
     
       ; if reading dark files from list, read list into names array:
        if (*(*BatchParams).dark).uselist then begin
            
            darklistfile = (*(*BatchParams).dark).list
            darkdir = (*(*BatchParams).dark).dir
            if strmid(darkdir, strlen(darkdir)-1, 1) ne slash then $
              darkdir = darkdir + slash
            if strpos(darklistfile,slash) eq -1 then $ ;full path not given
              darklistfile = darkdir + darklistfile ; assume file is in darkdir
            
            if file_test(darklistfile,/read) then begin
                cisscal_readlist, darklistfile, darklist, ndfiles, /noheader
                if ndfiles eq nfiles then begin
                    darklist = darkdir + strtrim(darklist,2)
                    if ptr_valid((*(*BatchParams).dark).names) then $
                      ptr_free,(*(*BatchParams).dark).names
                    (*(*BatchParams).dark).names = ptr_new(darklist) 
                endif else begin
                    if DebugFlag gt 0 then Cisscal_Log,$
                      '  ERROR: Cannot run batch; dark list file is invalid.'
                    return
                endelse
            endif else begin
                if DebugFlag gt 0 then Cisscal_Log,$
                  '  ERROR: Cannot run batch; dark list file not found.'
                return
            endelse
        endif    

        WIDGET_CONTROL, /HOURGLASS ; time-intensive...
        for IBatch = 0l, nfiles-1l do begin         
           if DebugFlag gt 0 then begin
              Cisscal_Log
              Cisscal_Log,'****************************************************'          
              Cisscal_Log,'  Now processing image '+ filelist[IBatch]
              Cisscal_Log,'   Image #'+strtrim(IBatch+1,2)+' of '+$
                          strtrim(nfiles,2)
              Cisscal_Log,'****************************************************'          
           endif
           NewImgObj = GuiOpenFile(ImgObj,filename=filelist[IBatch])
           if OBJ_VALID(NewImgObj) then begin
              GuiEnabMenuOpts,1
              NewImgObj->RadiomCalib, /DEBUG
              
;              This seems to be causing problems, so try something else...
;                justfile = strmid(filelist[IBatch],strlen(inputdir))
                
              slashpos = strpos(filelist[IBatch],slash,/reverse_search)
              dotpos = strpos(filelist[IBatch],'.',/reverse_search)
              justfile = strmid(filelist[IBatch],slashpos+1,dotpos-(slashpos+1))
              
              GuiSaveFile, NewImgObj, filename=outputdir + justfile + $
                           (*BatchParams).outputext
           endif else begin
              GuiEnabMenuOpts,0
           endelse
        endfor
        IBatch = -1             ; get out of batch mode
 
        return
        END
    pstruct.indirid   : BEGIN
        widget_control, pstruct.indirid, get_value=temp
        widget_control, pstruct.indirid, set_value=strtrim(temp,2)
        (*BatchParams).inputdir = strtrim(temp,2)
        END
    pstruct.inputtype : BEGIN
        widget_control, pstruct.inputtype, get_value=temp
        (*BatchParams).inputtype = temp
        if (*BatchParams).inputtype eq 0 then $
          widget_control, pstruct.instring, set_value=(*BatchParams).inputregexp else $
          widget_control, pstruct.instring, set_value=(*BatchParams).inputlist
        END
    pstruct.instring   : BEGIN
        widget_control, pstruct.instring, get_value=temp
        widget_control, pstruct.instring, set_value=strtrim(temp,2)
        if (*BatchParams).inputtype eq 0 then $
          (*BatchParams).inputregexp = strtrim(temp,2) else $
          (*BatchParams).inputlist = strtrim(temp,2)
        END
    pstruct.indirbut  : BEGIN
        indir = dialog_pickfile(/directory,path=(*BatchParams).inputdir)
        if file_test(indir,/dir) then begin 
            (*BatchParams).inputdir = indir
            widget_control, pstruct.indirid, set_value=indir
        endif
        END
    pstruct.outdirid  : BEGIN
        widget_control, pstruct.outdirid, get_value=temp
        widget_control, pstruct.outdirid, set_value=strtrim(temp,2)
        (*BatchParams).outputdir = strtrim(temp,2)
        END
    pstruct.outextid  : BEGIN
        widget_control, pstruct.outextid, get_value=temp
        widget_control, pstruct.outextid, set_value=strtrim(temp,2)
        (*BatchParams).outputext = strtrim(temp,2)
        END
    pstruct.outdirbut  : BEGIN
        outdir = dialog_pickfile(/directory,path=(*BatchParams).outputdir)
        if file_test(outdir,/dir) then begin
            (*BatchParams).outputdir = outdir
            widget_control, pstruct.outdirid, set_value=outdir
        endif
        END
    pstruct.darkoptsid : BEGIN
        widget_control, pstruct.darkoptsid, get_value=temp
        if temp eq 0 then begin 
            (*(*CalOptions).dark).darkfile = ''
;            (*(*CalOptions).dark).model = '2-param'
            (*(*BatchParams).dark).uselist = 0
            widget_control,pstruct.darkbaseid,sensitive=0
 ;       endif else if temp eq 1 then begin
 ;           (*(*CalOptions).dark).darkfile = ''
 ;           (*(*CalOptions).dark).model = 'interp'
 ;           (*(*BatchParams).dark).uselist = 0
 ;           widget_control,pstruct.darkbaseid,sensitive=0
        endif else if temp eq 1 then begin
            (*(*BatchParams).dark).uselist = 1
            widget_control,pstruct.darkbaseid,sensitive=1
            widget_control,pstruct.darkdirid, get_value=darkdirval
            (*(*BatchParams).dark).dir = strtrim(darkdirval,2)
            widget_control,pstruct.darklistid, get_value=darklistval
            (*(*BatchParams).dark).list = strtrim(darklistval,2)
        endif
        END
    pstruct.darkdirid : BEGIN
        widget_control, pstruct.darkdirid, get_value=temp
        widget_control, pstruct.darkdirid, set_value=strtrim(temp,2)
        (*(*BatchParams).dark).dir = strtrim(temp,2)
        END
    pstruct.darklistid : BEGIN
        widget_control, pstruct.darklistid, get_value=temp
        widget_control, pstruct.darklistid, set_value=strtrim(temp,2)
        (*(*BatchParams).dark).list = strtrim(temp,2)
        END
    endcase

widget_control, dummytlb, set_uvalue=ImgObj, /no_copy
widget_control, event.top, set_uvalue=pstruct, /no_copy

END



;;	PRO GuiBatch
;;	 Set batch mode options, launch batch processing

PRO cisscal_batchgui, ImgObj, ev
@cisscal_common.pro

 ; main widget base:
  tlb = widget_base(title='Set Batch Options', /column,$
                  group_leader=ev.top, /floating, mbar=MenuBar)

 ; Create dummy top level base widget to hold direct reference to 
 ; ImgObj; widget ID will be placed into first child widget of
 ; the main top level base:  
  dummytlb = widget_base()

 ;******************
 ; construct widget:
 ;******************

  toplab = widget_label(tlb,value='Press return after each entry.',$
                        /align_center)

 ; set default path if no path has already been specified:
  if (*BatchParams).inputdir eq '' then begin
      ImPathSz = SIZE(ImPath)
      IF ( ImPathSz[ImPathSz[0]+1] NE 7 ) THEN BEGIN ; if not a string
          ImPath = ImageBaseDir
      ENDIF

      (*BatchParams).inputdir = ImageBaseDir
      (*BatchParams).outputdir = ImageBaseDir
  endif

 ; file menu:
  fmenu = WIDGET_BUTTON(MenuBar, VALUE='File', /MENU)
  loadid = WIDGET_BUTTON(fmenu, VALUE='Load batch options file')
  saveid = WIDGET_BUTTON(fmenu, VALUE='Save batch options file')

 ; editable text: 
  indirval = (*BatchParams).inputdir
  indirlab = widget_label(tlb,value='Input Directory:',/align_left)
  indirbase = widget_base(tlb,/row)
  indirid = widget_text(indirbase,value=indirval,/edit,xsize=58)
  indirbut = widget_button(indirbase,value='Browse...')

  inputbase = widget_base(tlb,/row)
  inputlab = widget_label(inputbase,value='Use:',/align_left)
  inputtype = cw_bgroup(inputbase,['Input filter','Input file list'],$
                       /exclusive,/no_release,/row,set_value=(*BatchParams).inputtype)
  inregval = (*BatchParams).inputregexp
  inlistval = (*BatchParams).inputlist
;  inreglab = widget_label(tlb,value='Input Filter:',/align_left)
  if (*BatchParams).inputtype eq 0 then ival = inregval else ival = inlistval
  instring = widget_text(tlb,value=ival,/edit)
  
  outdirval = (*BatchParams).outputdir
  outdirlab = widget_label(tlb,value='Output Directory:',/align_left)
  outdirbase = widget_base(tlb,/row)
  outdirid = widget_text(outdirbase,value=outdirval,/edit,xsize=58)
  outdirbut = widget_button(outdirbase,value='Browse...')

  outextval = (*BatchParams).outputext
  outextlab = widget_label(tlb,value='Output Filename Extension:',/align_left)
  outextid = widget_text(tlb,value=outextval,/edit)

 ; dark subtraction options:

  if (*(*CalOptions).dark).darkfile eq '' then begin
;      if (*(*CalOptions).dark).model eq '2-param' then begin
;          (*(*BatchParams).dark).uselist = 0
;          darkoptsval = 0
;          darkfilesens = 0
;      endif else if (*(*CalOptions).dark).model eq 'interp' then begin
;          (*(*BatchParams).dark).uselist = 0
;          darkoptsval = 1
;          darkfilesens = 0
;      endif else begin
;          (*(*BatchParams).dark).uselist = 1
;          darkoptsval = 2
;          darkfilesens = 1
;      endelse
      (*(*BatchParams).dark).uselist = 0
      darkoptsval = 0
      darkfilesens = 0
  endif else begin
      (*(*BatchParams).dark).uselist = 1
      darkoptsval = 1
      darkfilesens = 1
  endelse

  darkoptslab = widget_label(tlb,value='Dark Subtraction Options:',/align_left)
;  darkoptsid = cw_bgroup(tlb,['2-parameter model','Interpolation model',$
;                       'Choose Dark List'], set_value=darkoptsval, /no_release, $
;                        /exclusive, /column)

  darkoptsid = cw_bgroup(tlb,['Interpolation model',$
                       'Choose Dark List'], set_value=darkoptsval, /no_release, $
                        /exclusive, /column)

  darkbaseid = widget_base(tlb,/column,sensitive=darkfilesens)

  darkdirlab = widget_label(darkbaseid,value='Specify directory containing darks:',$
                            /align_left)
  darkdirval = (*(*BatchParams).dark).dir
  darkdirid = widget_text(darkbaseid, value=darkdirval, /edit)

  darklistlab = widget_label(darkbaseid,value=$
           'Specify dark list (assumed to be in dark dir unless full path is given):',$
           /align_left)
  darklistval = (*(*BatchParams).dark).list
  darklistid = widget_text(darkbaseid, value=darklistval, /edit)

 ; buttons:
  btnbase = widget_base(tlb,/row)

;  saveid = widget_button(btnbase,value = 'Save batch options...')
;  loadid = widget_button(btnbase,value = 'Load batch options...')
  cancelid = widget_button(btnbase,value = 'Cancel')
  runbatchid = widget_button(btnbase,value = 'Run batch')

 ; make structure to hold widget IDs:
  pstruct = {indirid    : indirid,$
             instring   : instring,$
             inputtype  : inputtype,$
             indirbut   : indirbut,$
             outdirid   : outdirid,$
             outextid   : outextid,$
             outdirbut  : outdirbut,$
             darkoptsid : darkoptsid,$
             darkbaseid : darkbaseid,$
             darkdirid  : darkdirid,$
             darklistid : darklistid,$
             cancelid   : cancelid,$
             runbatchid : runbatchid,$
             saveid     : saveid,$
             loadid     : loadid}

  widget_control, tlb, /realize
  widget_control, tlb, set_uvalue=pstruct, /no_copy

  widget_control, dummytlb, set_uvalue=ImgObj, /no_copy

  stash = widget_info(tlb, /child)
  widget_control, stash, set_uvalue=dummytlb

  xmanager, 'batchgui', tlb

; Retrieve the reference to the ImgObj, so that it will be 
; associated again with the incoming argument:
  widget_control, dummytlb, get_uvalue=ImgObj, /no_copy

; Release the dummy top-level base:
  widget_control, dummytlb, /destroy

  widget_control, ev.top, set_uvalue=ImgObj, /no_copy

END















