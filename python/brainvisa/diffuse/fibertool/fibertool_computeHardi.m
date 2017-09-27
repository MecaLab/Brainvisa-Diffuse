function errStr = fibertool_computeHARDI(directory,bval,bvecs_path,Nb0,computeDT)

    if computeDT == '1'
        %% Compute Diffusion Tensor
        dtdStruct.bFactor              = str2double(bval);
        dtdStruct.someValue            = [];
        dtdStruct.deShema              = 'Other';
        dtdStruct.threshold            = 40; 
        dtdStruct.SingleSlice          = 0;
        dtdStruct.MultiSlice          = 1;
        dtdStruct.NumberB0Images       = str2double(Nb0); %[18]
        dtdStruct.status               = sprintf('If is ON, raw DW-data with direction information is saved as a mrstruct.');
        dtdStruct.FileName = fullfile(strcat(directory,'/MITK_raw_data.mat'));
        dtdStruct.diffDirFile = fullfile(bvecs_path);
        dtdStruct.DEscheme = load(dtdStruct.diffDirFile);
        for k = 1:dtdStruct.NumberB0Images,
            dtdStruct.DEscheme(k,:,:)=[0,0,0];
        end
        dtdStruct.diffStatus = [1,0,0];
        slicesavemode = dtdStruct.SingleSlice + dtdStruct.MultiSlice*2;
        [res, errStr] = calculate_dti(dtdStruct.FileName,dtdStruct.threshold,slicesavemode,dtdStruct.DEscheme,dtdStruct.bFactor,dtdStruct.NumberB0Images,dtdStruct.status);  

    elseif computeDT == '0'
        %% Create HARDI structure
        data = load([directory,'/MITK_raw_data.mat']);
        mrStruct = data.mrStruct;
        DWI_set = mrStruct.dataAy(:,:,:,:);
        dataStruct = mrstruct_init('series3D',DWI_set);
        dataStruct.user.FileName = fullfile(strcat(directory,'/MITK_raw_data.mat'));
        dataStruct.vox = mrStruct.vox;
        dataStruct.edges = mrStruct.edges;
        dataStruct.orient = mrStruct.orient;
        dataStruct.patient = mrStruct.patient;
        dataStruct.te = mrStruct.te;
        dataStruct.tr = mrStruct.tr;
        dataStruct.ti = mrStruct.ti;
        dataStruct.user.bfactor = bval;
        dataStruct.user.NumberB0Images = str2double(Nb0);
        dataStruct.user.diffDirFile = fullfile(bvecs_path);
        DE_scheme = load(dataStruct.user.diffDirFile);
        for k = 1:dataStruct.user.NumberB0Images,
            DE_scheme(k,:)=[0,0,0];
        end;
        dataStruct.user.bDir = DE_scheme;
        for k = 1:size(DE_scheme,1),
            dataStruct.user.bTensor(:,:,k) = DE_scheme(k,:)'*DE_scheme(k,:);
        end;
        try
            mrstruct_write(dataStruct,[directory,'/MITK_hardi_data.mat']);
            disp('HARDI structure created')
        catch
            disp(errStr)
        end
    
    else
        disp('Missing argument. Please precise if Diffusion Tensor should be computed (1) or not (0)')
    end
