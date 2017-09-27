function [hlen,hwid,hwei,hits] = suggest_Callback(datastruct,eventdata,handles,varargin)  

disp('suggesting parameters');

% hlen = findobj('Tag','fiberGT_editlength');
% hwid = findobj('Tag','fiberGT_editwidth');
% hwei = findobj('Tag','fiberGT_editweight');
% hits = findobj('Tag','fiberGT_edititnum');

if isfield(datastruct,'offset') && isfield(datastruct,'spatialProbabilities'),
    [Hist,Bins] = computeSignalHistogram(datastruct);
    widthSignalDistrib = sqrt((Bins.^2)*Hist/sum(Hist));
    minelsz = min([datastruct.offset(1,1) datastruct.offset(2,2) datastruct.offset(3,3)]);
    if varargin{3} == 2,
        hits = '5*10^7';
        wmul = 1;
    else
        hits = '3*10^8'; 
        wmul = 1/4;
    end;
    hwid = sprintf('%.3f',minelsz*0.5);
    hwei = sprintf('%.3f',widthSignalDistrib*wmul);
    hlen = sprintf('%.3f',minelsz*1.5);    
else
    errordlg('Load a DW-dataset and a mask first.','Parameter suggestion'); 
end;

      
function [h,bins] = computeSignalHistogram(ds)    
    bins = -1:0.001:1;    
    
    ovsamp = max(floor(size(ds.spatialProbabilities)./size(ds.b0avg)));
    spPro = ds.spatialProbabilities;
    if ovsamp > 1,
        spPro = imresize3D_diff(spPro,size(spPro)/ovsamp,'nearest');
    end;
    
    mask = spPro(:) > 0; sigmasked = ds.signal(:,mask);
    h = histc(sigmasked(:),bins);