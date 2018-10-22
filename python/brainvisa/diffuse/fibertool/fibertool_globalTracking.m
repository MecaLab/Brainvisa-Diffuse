function errStr = fibertool_globalTracking(directory,threshold,density)

    errStr = '';
    
    disp('loading data...')

    data = load([directory,'/MITK_hardi_data.mat']);
    mrStruct = data.mrStruct;

    %% Initialize
    sinterp = load('sinterp128.mat');
    fiberGT_editchemPot1 = '0';
    fiberGT_editconnlike = '0.5';
    fiberGT_editinexbal = '0';
    fiberGT_editstartTemp = '0.1';
    fiberGT_editstopTemp = '0.001';
    fiberGT_editsteps = '50';
    fiberGT_edititnum = '5*10^8';
    fiberGT_editwidth = '???';
    fiberGT_editlength = '???';
    fiberGT_editweight = '???';
    fiberGT_editchemPot2 = '0.2';
    fiberGT_editbfac = '1.0';
    fiberGT_editfiblength = '10;inf';
    p.Tstart = fiberGT_editstartTemp;
    p.Tend = fiberGT_editstopTemp;
    p.numstep = fiberGT_editsteps;
    p.numiterations = fiberGT_edititnum;
    p.p_weight = fiberGT_editweight;
    p.p_len = fiberGT_editlength;
    p.p_wid = fiberGT_editwidth;
    p.c_likli = fiberGT_editconnlike;
    p.b_fac = fiberGT_editbfac;
    p.p_chempot = fiberGT_editchemPot1;
    p.p_chempot_2nd = fiberGT_editchemPot2;
    p.inex_balance = fiberGT_editinexbal;
    p.fibrange = fiberGT_editfiblength;
    
%     global dataStruct;
    dataStruct.sphereInterpolation = sinterp.sinterp128;
    dataStruct.state = single([]);
    dataStruct.currentiteration = 1;
    dataStruct.conratio = [];   
    dataStruct.lengthhistogram = [];
    dataStruct.updownratio = [];
    dataStruct.mask_fname = '';
    dataStruct.edges = [];
    dataStruct.name = [];
    dataStruct.signal_fname = [];
    dataStruct.signal_type = [];
    dataStruct.offset = [];
    dataStruct.ftrname = '';

    %% setHardi
    bTensor = mrStruct.user.bTensor;
    signal = mrStruct.dataAy;
    vox = mrStruct.vox;
    patient = mrStruct.patient;
    dataStruct = preprocessODF(dataStruct, bTensor,signal,patient,vox);
    disp('HARDI data was set manually')

    %% loadMask
    fn = [directory,'/MITK_mask.mat'];
%     threshold = 0;
    dataStruct = loadmask(dataStruct,fn,str2double(threshold));
    disp('ready ...')
    
    %% setFTRname
    [path, fn, ext] = fileparts([directory,'/MITK_tract_data_',density,'.mat']);
    dataStruct.ftrname = strcat(path, '/', fn);
    
    %% suggestSparse or suggestDense
    if strcmp(density,'sparse')
        [hlen,hwid,hwei,hits] = suggest_Callback(dataStruct,[],[],[],[],2);
    elseif strcmp(density,'dense')
        [hlen,hwid,hwei,hits] = suggest_Callback(dataStruct,[],[],[],[],1);
    else
        disp('Missing argument. Please precise if tractography should be computed using "sparse" or "dense" parameters')
    end
    p.p_len = hlen;
    p.p_wid = hwid;
    p.p_weight = hwei;
    p.numiterations = hits;
    
    %% start
    dataStruct = startstop_Callback(dataStruct,[],[],p);


