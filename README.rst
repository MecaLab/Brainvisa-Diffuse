===========
DIFFUSE
===========


Diffuse is a BrainVISA toolbox designed to process diffusion-weighted MRI (DWI) data with state-of-the-art algorithms in a
user-friendly way. Diffuse is currently developed  at the Institut de Neurosciences de la Timone (INT_), Marseille,
France by both MeCA_ and  SCaLP_  research teams. Diffuse mainly relies on  FSL_   and Dipy_ for  DWI processing.


=============
Main Features
=============

* diffusion data  management (DICOM, nifti) within a database and diffusion gradient directions reorientation.
* diffusion data denoising
* movement, susceptibility and eddy current induced distorsions correction
* registration with subject structural space and  maps creation stemming from strucutral data.
* diffusion local modeling (DTI, CSD).
* multiple seeding strategies
* tractograpy: both deterministic and  probabilistic local tractography, particle filtering tractography.


=========================
Installation
=========================

To install Diffuse please refer to the `installation guide <doc/installation.rst>`_


=======
License
=======

The source code of this work is placed under the CeCILL licence (see `<license.txt>`_).



 Copying and distribution of this file, with or without modification, are permitted in any medium without royalty provided the copyright notice and this notice are preserved. This file is offered as-is, without any warranty.

=======
Authors
=======
* Lucile BRUN  <lucile.brun@univ-amu.fr>.
* Alexandre PRON <alexandre.pron@univ-amu.fr>.

    .. _INT: http://www.int.univ-amu.fr/
    .. _Meca: https://meca-brain.org/
    .. _SCaLP: http://www.int.univ-amu.fr/spip.php?page=equipe&equipe=SCaLP&lang=en
    .. _FSL: https://fsl.fmrib.ox.ac.uk/fsl/fslwiki/
    .. _Dipy: https://nipy.org/dipy
    .. _BrainVISA: http://brainvisa.info/
    .. _GSL: http://www.gnu.org/software/gsl/
    .. _Ubuntu-16.04.5-64bit: http://releases.ubuntu.com/16.04/ubuntu-16.04.5-desktop-amd64.iso
    .. _BrainVISA-download: http://brainvisa.info/web/download.html
    .. _BrainVISA-4.6.1-installer: http://brainvisa.info/web/download/go.php?url=http://brainvisa.info/packages/4.6.1/linux64-glibc-2.23/brainvisa-installer/brainvisa_installer-4.6.1-linux64-glibc-2.23-online



