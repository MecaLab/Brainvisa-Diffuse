function datastruct = startstop_Callback(datastruct,eventdata,handles,param)  

if ~checkdata(datastruct),
    return;
end;

disp('tracking');
Pstruc = getParams(param);

bfac = Pstruc.b_fac*bFacMultiplier ;

[besselexpansion,meanval_sq] = computeFiberCorrelation(datastruct.sphereInterpolation.bDir,bfac);

if strcmp(datastruct.signal_type,'FOD');
    meanval_sq = 0;
end;

p_wei = Pstruc.p_weight;
params = [p_wei Pstruc.p_wid Pstruc.p_len Pstruc.c_likli Pstruc.p_chempot Pstruc.inex_balance Pstruc.p_chempot_2nd meanval_sq];
%params = [(Pstruc.p_weight*2^(3/2)) Pstruc.p_wid Pstruc.p_len Pstruc.c_likli Pstruc.p_chempot Pstruc.inex_balance Pstruc.p_chempot_2nd meanval_sq];

disp('Tracking started');

info.params = Pstruc;
info.name = datastruct.name;

datastruct = trackit(datastruct,Pstruc.Tstart,Pstruc.Tend,Pstruc.numstep,Pstruc.numiterations,params,besselexpansion,info);
disp('Tracking stopped');

%%
function ret = checkdata(datastruct)

ret = false;
if ~isfield(datastruct,'spatialProbabilities'),
    errordlg('No White Matter Mask loaded','Data consistency');
    return
end;

if ~isfield(datastruct,'signal'),
    errordlg('No HARDI signal loaded','Data consistency');
    return
end;

if ~isfield(datastruct,'sphereInterpolation');
    errordlg('Sphere Interpolator not initialized (missing sinterp128.mat)','Data consistency');
    return
end;

szhardi = size(datastruct.signal);
szmask = size(datastruct.spatialProbabilities);
if ~isequal(mod(szmask,szhardi(2:4)),[0 0 0]),
    errordlg('dimensions of WM mask and HARDI signal not consistent','Data consistency');
    return
end;

% if any(cellfun(@isempty,struct2cell(getParams))),
%     errordlg('Parameters are not set correct','Data consistency');
%     return
% end;    

ret = true;
return;

function p = getParams(param)
%     p = getParamsString;
    fields = fieldnames(param);
    for k = 1:length(fields);
        val = param.(fields{k});
        if ischar(val),
            val = str2num(val);
        end;
        p.(fields{k}) = val;
    end;
    
function m = bFacMultiplier    
m =1;

function datastruct = trackit(datastruct,Tstart,Tend,ni,its,params,besselexpansion,info)

if its > 1,
    ipr = round(its/ni);
else
    ipr = its;
end;

lens = [];
h = createStopButton;
% h = '';
sz = size(datastruct.spatialProbabilities);
alpha = log(Tend/Tstart);
vox = [datastruct.offset(1,1) datastruct.offset(2,2) datastruct.offset(3,3)];


ftrname = datastruct.ftrname;
fiblen = info.params.fibrange;
    
doexit = false;
cnt = 1;
% close all;
disp(datastruct.currentiteration)
for k = datastruct.currentiteration:ni,    
    
      datastruct.currentiteration = k;
    
      tic

      T = Tstart * exp(alpha*(k-1)/ni);
      
      [datastruct.state,stat] = pcRJMCMC(datastruct.state,datastruct.signal,datastruct.spatialProbabilities,double(vox),double([T ipr 0.35 params]),single(besselexpansion),datastruct.sphereInterpolation,h);    
      
      concnt = (sum(datastruct.state(9,:) ~= -1) + sum(datastruct.state(10,:) ~= -1))/2; 
      segcnt = size(datastruct.state,2);
     
      fibidx = BuildFibres(datastruct.state,fiblen);
     
      fprintf('%i/%i) #p %i, #c %i, #f %i, T %.4f, t per %.0e its :%.2f min\n',k,ni,segcnt,concnt,length(fibidx), T,stat.iterations, toc/60);
       
      datastruct.conratio(k) = concnt/segcnt;
      datastruct.updownratio(k) = stat.up/(stat.down+1);
 
      datastruct.lengthhistogram = lenhist(lens);

%       updatePlots(datastruct);
%     
%       drawnow;
   

      if isfield(datastruct,'maxnumits'),
          if cnt >= datastruct.maxnumits,
              datastruct.currentiteration = k+1;
              doexit = true;
          end;
      end;      
      cnt = cnt + 1;
            
      
%      if stopButtonPressed,
%           addlog('interrupted by user');
%           doexit = true;
%       end;
%       
      info = gatherFTRinfo(datastruct,info);
      [ftr,lens] = saveFTR(ftrname,datastruct.state,fibidx,datastruct.offset,info);

      if doexit,
          break;
      end;
      
end;

function info = gatherFTRinfo(datastruct,inf)
info.fiberGT_FTRversion = 'V1.0';
info.params = inf.params;
info.Log = [];
info.edges = datastruct.edges;
info.name = datastruct.name;
info.signal_fname = datastruct.signal_fname;
info.signal_type = datastruct.signal_type; 
info.mask_fname = datastruct.mask_fname;
info.conratio = datastruct.conratio;
info.lengthhistogram = datastruct.lengthhistogram;
info.updownratio = datastruct.updownratio;
info.currentiteration = datastruct.currentiteration;

function h = lenhist(lens)
h = [];      
if ~isempty(lens),
        hi = histc(lens,1:1:max(lens));
        h = log(1+hi);       
end;
