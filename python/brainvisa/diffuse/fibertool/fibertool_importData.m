function errStr = fibertool_importData(nifti_dir,bvals_path,mask_path,out_dir)

    errStr = '';
    
    disp('importing data')
    disp('please wait...')

    %% import NIFTI
    type = 'series3D';
    %nifti_dir = strcat(indir);
    nifti_list = dir(nifti_dir);
    
    bvals = load(bvals_path);
    b0 = find(bvals<100)-1;
    b0_list = {};
    for i=1:length(b0)
        b0_list = [b0_list, {num2str(b0(i), '%.4d')}];
    end
    step = 0;
    nifti_list_reorganized = nifti_list;
    for i=1:length(nifti_list)
        if nifti_list(i).isdir == 0
            if ismember({nifti_list(i).name(length(nifti_list(i).name)-7:length(nifti_list(i).name)-4)}, b0_list)
                nifti_list_reorganized(3+step).name = nifti_list(i).name;
                step = step+1;
            else
                nifti_list_reorganized(length(b0_list)-step+i).name = nifti_list(i).name;
            end
        end
    end
    
    for i=1:length(nifti_list_reorganized)
        if nifti_list(i).isdir == 0
            nifti_list_reorganized(i).name = strcat(nifti_dir, nifti_list_reorganized(i).name);
        end
    end
    [mrStruct, errStr] = nifti_to_mrstruct(type, {nifti_list_reorganized(3:length(nifti_list_reorganized)).name});
    
    try
        mrstruct_write(mrStruct,strcat(out_dir,'/MITK_raw_data.mat'));
        disp('raw NIFTI data imported')
    catch
        disp(errStr)
    end
    

    %% import mask (unzip .nii)
    [mrStruct, errStr] = nifti_to_mrstruct('volume', mask_path);
%     maskStruct = mrStruct;
%     maskStruct.dataAy = permute(mrStruct.dataAy,[3,2,1]);
    try
        mrstruct_write(mrStruct,strcat(out_dir,'/MITK_mask.mat'));
        disp('MASK structure created')
    catch
        disp(errStr)
    end

    disp('Importation done.')
    
