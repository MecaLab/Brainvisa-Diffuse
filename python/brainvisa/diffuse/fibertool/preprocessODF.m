function datastruct = preprocessODF(datastruct,bTensor,signal,patient,vox)

   disp('computing b0 average');       
   b0indicator = squeeze(squeeze(bTensor(1,1,:)+bTensor(2,2,:)+bTensor(3,3,:)));
   b0indicator = b0indicator/max(b0indicator);
   b0idx = find(b0indicator < 0.101);
   datastruct.b0avg = single(sum(signal(:,:,:,b0idx),4) /length(b0idx));

   disp('preparing signal');
   didx = setdiff(1:size(bTensor,3),b0idx);
   datastruct.signal = single(zeros(length(didx),size(signal,1),size(signal,2),size(signal,3)));
   if isempty(b0idx),
        datastruct.signal = single(signal);
        datastruct.b0avg = single(ones(size(signal,2),size(signal,3),size(signal,4)));
   else
       for k = 1:length(didx),
            datastruct.signal(k,:,:,:) = single((signal(:,:,:,didx(k)) ./(datastruct.b0avg+0.001))); 
       end;
   end;
   datastruct.original_signal = single(signal);
   datastruct.original_bTensor = bTensor;


   datastruct.signal(datastruct.signal>1) = 1;

   disp('correlating with model');          
   frt = FunkRadonTrans(bTensor(:,:,didx),datastruct.sphereInterpolation.bDir,40,0.0002);      
   frt = single(frt);
   sz = size(datastruct.signal);
   sz(1) = size(frt,1);
   datastruct.signal = single(reshape(frt*datastruct.signal(:,:),sz));

   datastruct.offset = [1 0 0 0; 0 1 0 0; 0 0 1 0; 0 0 0 1];
   datastruct.offset(1,1) = vox(1);
   datastruct.offset(2,2) = vox(2);
   datastruct.offset(3,3) = vox(3);        

   datastruct.name = patient;
   datastruct.original_size = size(signal);
