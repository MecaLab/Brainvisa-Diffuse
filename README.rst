===========
**Diffuse**
===========

------------
Presentation
------------
Diffuse is a Brainvisa toolbox designed to process diffusion weighted MRI (DWI) scans with state-of-the-art algorithms in an
user friendly way. Diffuse is developped  by the MeCA_. research group.
    .. _Meca: https://meca-brain.org/

Diffuse mostly relies on both FSL_.  and Dipy_. algorithms for DWI processing.

.. _FSL: https://fsl.fmrib.ox.ac.uk/fsl/fslwiki/
.. _Dipy: https://nipy.org/dipy

-------------------------------------------
Check your Brainvisa installation encoding
-------------------------------------------

Dipy modules are not compatible with the ``UCS-2 encoding`` used
in some released version of Brainvisa.
To be sure your Brainvisa distribution is compatible with diffuse
test the brainvisa python of your distribution as follow::

>> import sys
>> print sys.maxunicode()

Should be equal to ``1114111`` not 65535



-------------------------------------------
How to get  Diffuse installed in Brainvisa?
-------------------------------------------

1. Click on ``Download ZIP`` on github.

2. Extract the obtained archive with your favorite archive manager
   Here is a example in  a terminal with ``tar`` bash command ::

    tar xvf Brainvisa-Diffuse.zip

3. In the Brainvisa-Diffuse directory, the setup.sh script will handle the copy of Diffuse directories in the correct
   location automatically

4. First change the permissions of setup.sh so that you can execute it ::

   chmod u+rwx setup.

5. Lauch the setup.sh script ::

    ./setup.sh

6. You will be asked by the installation script the location of your Brainvisa install directory
enter it manually.

7. At this stage, the script will manage the installation on its own. If you are getting an error it might be due either
to wrong brainvisa location or insufficient permissions access on the brainvisa directory.

8. Lauch brainvisa and update Diffuse documentation::

 brainvisa --updateDocumentation

if brainvisa is the name of your brainvisa installation (sometimes if might be BrainVISA)
you can check using the bash command which.


Licence
=======

The source code of this work is placed under the CeCILL licence (see `<License.txt>`_).
.. _BrainVISA: http://brainvisa.info/
.. _GSL: http://www.gnu.org/software/gsl/
.. _BrainVISA download page: http://brainvisa.info/web/download.html


   Authors: Brun Lucile  <lucile.brun@univ-amu.fr>.
          : Pron Alexandre <alexandre.pron@univ-amu.fr>.

   Copying and distribution of this file, with or without modification, are permitted in any medium without royalty provided the copyright notice and this notice are preserved. This file is offered as-is, without any warranty.



