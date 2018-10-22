===========
**Diffuse**
===========

------------
Presentation
------------
Diffuse is a BrainVISA toolbox designed to process diffusion-weighted MRI (DWI) data with state-of-the-art algorithms in a
user-friendly way. Diffuse is currently developed  at the Institut de Neurosciences de la Timone (INT_), Marseille,
France by both MeCA_ and  SCaLP_  research teams.
    .. _INT: http://www.int.univ-amu.fr/
    .. _Meca: https://meca-brain.org/
    .. _SCaLP: http://www.int.univ-amu.fr/spip.php?page=equipe&equipe=SCaLP&lang=en

Diffuse mostly relies on FSL_  and Dipy_ for  DWI processing.
    .. _FSL: https://fsl.fmrib.ox.ac.uk/fsl/fslwiki/
    .. _Dipy: https://nipy.org/dipy


-------------------------------------------
How to install Diffuse ?
-------------------------------------------





-------------------------------------------
Check your BrainVISA installation encoding
-------------------------------------------

Dipy modules are not compatible with the ``UCS-2 encoding`` used
in some released version of BrainVISA.
To check whether your BrainVISA distribution is compatible with Diffuse,
launch Brainvisa and click on Brainvisa then  Start shell. It should launch an Ipython shell where you can type the
following lines::

    >> import sys
    >> print sys.maxunicode
    >> 1114111

Should be equal to ``1114111`` (not 65535).

-------------------------------------------
Prerequisites
-------------------------------------------

* FSL_ must be installed in your operating system.
For informations about FSL_ installation please look at FSL_ installation instructions here:
https://fsl.fmrib.ox.ac.uk/fsl/fslwiki/FslInstallation

Adding FSL path into Brainvisa suite:
Once FSL is installed you should precise to Brainvisa where it is. To do so:
1. Launch Brainvisa
2. Click on preferences and

* Dipy_ python package must be installed in the Brainvisa distribution.
For informations about Dipy_ installation please look at Dipy installation instructions here:
http://nipy.org/dipy/installation.html

* Joblib python package must be installed in the Brainvisa distribution

To check that Brainvisa's python know where Dipy is launch Brainvisa's shell through graphical user interface and type ::
import dipy

If you get an error, it means that you need to tell Brainvisa's python where dipy package is installed.
To do so:
1. Locate where Dipy is installed
2. Add this location to your `PYTHONPATH` environnement variable:
export PYTHONPATH="your_dipy_location":$PYTHONPATH
3. Restart Brainvisa and type the import code in the shell, it should work now.
















-------------------------------------------
Installation
-------------------------------------------

1. Click on ``Download ZIP`` on github.

2. Unpack the archive into any desired location with your favorite archive manager.
   Here is an example using ``tar`` ::

    tar xvf Brainvisa-Diffuse.zip -C <desired_location>

3. Switch to the Brainvisa-Diffuse directory ::

    cd <desired_location>/Brainvisa-Diffuse

4. Change the permissions of setup.sh so that you can execute it ::

    chmod u+rwx setup.sh

5. Run the setup.sh script ::

    ./setup.sh

6. During the installation, you will be asked to enter manually the location of your BrainVISA directory

7. At this stage, the setup.sh script will automatically handle the copy of Diffuse directories in the correct
   location. If any error occurs, please check that you specified the correct BrainVISA location or the access permissions into the BrainVISA directory.

8. Run BrainVISA and update Diffuse documentation::

    brainvisa --updateDocumentation



=======
Licence
=======

The source code of this work is placed under the CeCILL licence (see `<License.txt>`_).
.. _BrainVISA: http://brainvisa.info/
.. _GSL: http://www.gnu.org/software/gsl/
.. _BrainVISA download page: http://brainvisa.info/web/download.html


   Authors:
        Lucile BRUN  <lucile.brun@univ-amu.fr>.
        Alexandre PRON <alexandre.pron@univ-amu.fr>.

   Copying and distribution of this file, with or without modification, are permitted in any medium without royalty provided the copyright notice and this notice are preserved. This file is offered as-is, without any warranty.



