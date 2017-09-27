function datastruct = loadmask(datastruct,fn,threshold,pmap)
        disp('reading');
        if isempty(fn),
            [fn path] = uigetfile({'*.mat;*.nii','Accepted Files (*.mat,*.nii,*.hdr)'},'Load mrStruct/maskStruct');
            if fn == 0,
                return;
            end;
            fn = [path fn];
        end;          
        [fp fndum fext] = fileparts(fn);
        if strcmp(fext(1:4),'.nii') || strcmp(fext(1:4),'.hdr'),          
           mrdum = mrstruct_init;
           mrdum.dataAy = ds.b0avg;
           mrdum.edges = ds.edges;
           mrdum.dim3 = 'size_z';
           h = spm_vol(fn);
           if any(svd(ds.edges(1:3,1:3))*0.6 >  svd(h.mat(1:3,1:3))) %% high resolution mask
               mrdum.edges(1:3,1:3) = mrdum.edges(1:3,1:3)/2;   
               mrdum.dataAy = zeros(size(ds.b0avg)*2);               
           end;
                      
           [mm err] = nifti_to_mrstruct('volume',{fn},mrdum);
           if isempty(err),
                 if isempty(threshold),
                        threshold = chooseThreshold_stackview(ds.b0avg,mm.dataAy);
                        if isempty(threshold)
                           return;
                        end;
                 end; 
                 datastruct = setWMmask(datastruct,mm.dataAy>threshold,sprintf('<loaded> \n\n %s %f',fn,threshold));  
                 addlog(sprintf('WM mask file loaded'));    
                 disp('ready ...');
                 return;
           else
                errordlg('Error during nifti_to_mrstruct','Loading Mask');
                disp('ready ...');
                return;
           end;
            
    
            
        else
            if maskstruct_istype(load(fn),'Ver2')
                mastr = maskstruct_read(fn);        
                if isempty(threshold),
                    [res ok] = listdlg('ListString',mastr.maskNamesCell,'SelectionMode','single','Name','Select a Mask');
                else
                    ok = true;
                    res = threshold;
                end;
                if ok,
                    datastruct = setWMmask(datastruct,mastr.maskCell{res},sprintf('<loaded> \n\n %s %i',fn,res));
                    addlog(sprintf('WM mask file loaded from MaskStruct'));          
                    disp('ready ...');                
                end;
            else            
                [mrstruct fname] = mrstruct_read(fn);
                if isempty(mrstruct),
                    errordlg('Error while reading','Loading Mask');
                    disp('ready ...');
                else
                   if isfield(mrstruct.user,'probInfo'),
                      ok = 1;
                      if not(exist('pmap')),
                          pmap = [];
                      end;                      
                      if isempty(pmap),
                          maptype = probstruct_query(mrstruct,'mapTypes');
                          [res ok] = listdlg('ListString', maptype,'SelectionMode','single','Name','Select a Maptype');
                          pmap = maptype{res};                    
                      end;
                      if ok,
                          wm = probstruct_query(mrstruct,'getMap',pmap);   
                          if isempty(threshold),
                              threshold = chooseThreshold_stackview(ds.b0avg,wm);
                              if isempty(threshold)
                                 return;                          
                              end;                          
                          end; 
                          datastruct = setWMmask(datastruct,wm>threshold,sprintf('<loaded> \n\n %s %f %s',fn,threshold,pmap));
                          addlog(sprintf('WM mask file loaded from ProbMap'));        
                      end;
                      disp('ready ...');
                   else
                       if not(islogical(mrstruct.dataAy)),
                            if isempty(threshold),
                                threshold = chooseThreshold_stackview(ds.b0avg,mrstruct.dataAy(:,:,:,1));
                                if isempty(threshold)
                                   return;                          
                                end;
                            end; 
                       else
                            threshold = 0.5;
                       end;
                       datastruct = setWMmask(datastruct,mrstruct.dataAy>threshold,sprintf('<loaded> \n\n %s %f',fn,threshold));
                       disp(sprintf('WM mask file loaded'));
                   end;
                end;
            end;
        end;

function datastruct = setWMmask(datastruct,mask,fname)
       datastruct.spatialProbabilities = single(mask);         
       datastruct.mask_fname = fname;