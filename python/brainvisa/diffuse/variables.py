"""
GLOBALS VARIABLES
"""

#not clean : better create new Exception
FSL_BAD_CONFIG_MSG = ' Neither FSLDIR nor FSL prefix are set! This process will not be launched ! Either FSL is not installed on your system or it is not configured properly.In the second case go open BrainVISA preference menu, go to FSL and set the location of fsl installation directory'
FSL_NO_FSLDIR = 'FSLDIR is not set. It migth be due to package installation or incorrect FSL configuration.In the second case go open BrainVISA preference menu, go to FSL and set the location of fsl installation '