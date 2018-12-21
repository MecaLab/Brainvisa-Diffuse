
from brainvisa.processes import *
from soma.wip.application.api import Application
from distutils.spawn import find_executable
from soma import aims
import os
import nibabel

configuration = Application().configuration

def defaultBrainExtraction(data_path, bet_output, f='0.3'):
    """  brain extraction using FSL-bet function, with recursive searching of image center """
    
    data = nibabel.load(data_path).get_data()
    cmd =' '.join([configuration.FSL.fsl_commands_prefix + 'bet ', data_path, bet_output, ' -R -m -f ', f])
    os.system(cmd)

    return 0

def interactiveBrainExtraction(context, data_path, bet_output, f='0.3'):
    """ Iterative and interactive brain extraction using FSL-bet function """

    cmds = ['fsleyes', 'fslview']
    viewers = [find_executable(configuration.FSL.fsl_commands_prefix + cmd) for cmd in cmds]

    img = aims.read(data_path)
    data = img.arraydata()
    [Cx, Cy, Cz] = [data.shape[3] / 2, data.shape[2] / 2, data.shape[1] / 2]
    chge = 0
    while True:
        
        if chge == 1:
            context.write('Info: image center', [Cx, Cy, Cz])
            dial = context.dialog(1, 'Choose center', Signature('Cx', Number(), 'Cy', Number(), 'Cz', Number()), _t_('OK'), _t_('Cancel'))
            dial.setValue('Cx', Cx)
            dial.setValue('Cy', Cy)
            dial.setValue('Cz', Cz)
            r = dial.call()
            if r == 0:
                cx=dial.getValue('Cx')
                cy=dial.getValue('Cy')
                cz=dial.getValue('Cz')
            elif r == 1:
                context.write('Last extraction parameters are definitive')
                break
                
            context.write('Extraction parameters: f = ', f, ' ; center = [', str(cx), ', ', str(cy), ', ', str(cz), ']')
            os.system(' '.join([configuration.FSL.fsl_commands_prefix + 'bet', data_path, bet_output, '-m -f', f, '-c', str(cx), str(cy), str(cz)]))
            
        elif chge == 0:
            context.write('Extraction parameters: f = ', f, ' ; recursive center estimation')
            os.system(' '.join([configuration.FSL.fsl_commands_prefix + 'bet', data_path, bet_output, '-R -m -f', f]))

        val = os.popen(' '.join([configuration.FSL.fsl_commands_prefix + 'fslstats', bet_output, '-r'])).read()
        if viewers[0]:
            os.system(' '.join(['fsleyes', data_path, bet_output]))
        else:
            os.system(' '.join(['fslview', data_path, bet_output, '-l Red-Yellow', '-b 0,' + val.split()[1]]))
    	
        #os.system(' '.join(['/usr/bin/fslview', data_path, bet_output, '-l Red-Yellow', '-b 0,' + val.split()[1]]))
        result = context.ask("<p><b>Is brain extraction ok ? y/n\n <b></p>", "yes", "no")
        
        if result == 1:
            dial = context.dialog(1, 'Extraction parameter', Signature('f = ', Number()), _t_('OK'), _t_('Cancel'))
            dial.setValue('f = ', 0.3)
            r = dial.call()
            if r == 0:
                f=dial.getValue('f = ')
                f=str(f)
            elif r == 1:
                context.write('Last extraction parameters are definitive')
                break
                
            chge = 1-context.ask("Change center coordinates: y/n\n", "yes", "no")
            continue
        
        elif result == 0:
            context.write('Last extraction parameters are definitive')
            break

    return 0
