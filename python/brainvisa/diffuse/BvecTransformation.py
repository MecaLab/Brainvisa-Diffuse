import os
import numpy
from soma.wip.application.api import Application

def bvecRotation(ECpath, bvecs_in, bvecs_out):
    configuration = Application().configuration
    fsldir = configuration.FSL.fsldir
    log = os.path.splitext(os.path.splitext(ECpath)[0])[0]+ '.ecclog'
    if not os.path.isfile(log):
        raise RuntimeError( _t_( 'Log file does not exist!' ))
    if not os.path.isfile(bvecs_in):
        raise RuntimeError( _t_( 'Bvecs file does not exist!' ))
    tmp_file = os.path.dirname(log) + '/tmp.mat'
    flog = open(log, 'r')
    lines = flog.readlines()
    bvecs = numpy.loadtxt(bvecs_in)
    cmd1 = '. ' + fsldir + '/etc/fslconf/fsl.sh'
    newX = []
    newY = []
    newZ = []
    line_count = 0
    file_count = 0
    print lines
    for l in lines:
        if l[:10] == "processing":
            line_count = 0
            mat_file = open(tmp_file, 'w+')
        elif l != '\n' and l != "Final result:\n":
            mat_file.writelines(l)
        if line_count == 7:
            mat_file.close()
            cmd2 = fsldir + '/bin/avscale --allparams ' + mat_file.name
            output = os.popen(cmd1 + ';' + cmd2).readlines()
            rX = float(output[1].split()[0])*bvecs[0,file_count] + float(output[1].split()[1])*bvecs[1,file_count] + float(output[1].split()[2])*bvecs[2,file_count]
            rY = float(output[2].split()[0])*bvecs[0,file_count] + float(output[2].split()[1])*bvecs[1,file_count] + float(output[2].split()[2])*bvecs[2,file_count]
            rZ = float(output[3].split()[0])*bvecs[0,file_count] + float(output[3].split()[1])*bvecs[1,file_count] + float(output[3].split()[2])*bvecs[2,file_count]
            newX.append(rX)
            newY.append(rY)
            newZ.append(rZ)
            file_count += 1
        line_count += 1
    numpy.savetxt(bvecs_out, [newX, newY, newZ])
    flog.close()
    os.remove(tmp_file)
    
    return 0

##def bvecRotation(ECpath, bvecs_file_path, bvecs_rotated_file_path):
##    configuration = Application().configuration
##    fsldir = configuration.FSL.fsldir
##    script_path = os.path.dirname(os.path.abspath(__file__))
##    try:
##        EC_log_path = os.path.splitext(os.path.splitext(ECpath)[0])[0]+ '.ecclog'
##    except:
##        raise RuntimeError( _t_( 'Eddy-current correction log file cannot be found in the database' ))
##    try:
##        mat_file_path = os.path.dirname(EC_log_path) + '/mat.list'
##        os.system(' '.join([script_path + '/ecclog2mat.sh', EC_log_path, mat_file_path]))
##        os.system(' '.join([script_path + '/rotbvecs', bvecs_file_path, bvecs_rotated_file_path, mat_file_path, fsldir]))
##    except:
##        raise RuntimeError( _t_( 'Bash scripts "ecclog2mat.sh" and "rotbvecs" should be in the brainvisa python directory' ))
##    
##    return 0

##if __name__ == "__main__":
##    
##    EC_path = sys.argv[0]
##    bvecs = sys.argv[1]
##    bvecs_out = sys.argv[2]
##    BvecRotate(EC_path, bvecs, bvecs_out)

