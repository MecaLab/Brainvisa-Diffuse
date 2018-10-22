===========
**Diffuse**
===========

------------
Presentation
------------
Diffuse is a BrainVISA toolbox designed to process diffusion-weighted MRI (DWI) data with state-of-the-art algorithms in a
user-friendly way. Diffuse is currently developed  at the Institut de Neurosciences de la Timone (INT_), Marseille,
France by both MeCA_ and  SCaLP_  research teams. Diffuse relies on  FSL_   and Dipy_ essentialy for  DWI processing.


    .. _INT: http://www.int.univ-amu.fr/
    .. _Meca: https://meca-brain.org/
    .. _SCaLP: http://www.int.univ-amu.fr/spip.php?page=equipe&equipe=SCaLP&lang=en
    .. _FSL: https://fsl.fmrib.ox.ac.uk/fsl/fslwiki/
    .. _Dipy: https://nipy.org/dipy


-------------------------------------------
How to install Diffuse ?
-------------------------------------------

-------------------------------------------
Prerequisites
-------------------------------------------

* FSL_ must be installed on your operating system. For informations about FSL_ installation please look at FSL_ installation instructions https://fsl.fmrib.ox.ac.uk/fsl/fslwiki/FslInstallation .


* The latest BrainVISA_ distribution must be installed on your operating system. Download the latest BrainVISA distribution available here: https://brainvisa.info/web/download

    BrainVISA distributions under the version 4.6.1 are not immediately compatible with Diffuse. We warmly recommend users having an old  BrainVISA distribution (e.g. 4.5.xx) and wanting to use Diffuse to upgrade to the latest version.

*  Set-up the FSL directory location into BrainVISA. (add image)



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

6. During the installation, you will be asked to enter manually the location of your ``BrainVISA`` directory

7. At this stage, the setup.sh script will automatically handle the copy of Diffuse directories in the correct
   location. If any error occurs, please check that you specified the correct BrainVISA location or the access permissions into the BrainVISA directory.

8. Run BrainVISA and update Diffuse documentation::

    brainvisa --updateDocumentation




-------------------------
Installation from sources
-------------------------

For users already familiar with the BrainVISA compilation from source machinery, aka ``bv_maker`` , Diffuse can be included in the compilation process by adding the following lines to the ``bv_maker.cfg``
file used::

    [ source <source_directory> ]
      git https://github.com/MecaLab/Brainvisa-Diffuse.git master diffuse

    [ build <build_directory> ]
       + <source_directory>/diffuse

=======
Licence
=======

The source code of this work is placed under the CeCILL licence (see `<License.txt>`_).

.. _BrainVISA: http://brainvisa.info/
.. _GSL: http://www.gnu.org/software/gsl/
.. _BrainVISA download page: http://brainvisa.info/web/download.html

 Copying and distribution of this file, with or without modification, are permitted in any medium without royalty provided the copyright notice and this notice are preserved. This file is offered as-is, without any warranty.


Authors:
        * Lucile BRUN  <lucile.brun@univ-amu.fr>.
        * Alexandre PRON <alexandre.pron@univ-amu.fr>.




