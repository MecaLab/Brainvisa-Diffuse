=========================
Installation
=========================

-------------
Prerequisites
-------------

Mandatory
=========
* **UBUNTU 16.04**: currently the only operating system supported.  Diffuse was tested using  Ubuntu-16.04.5-64bit_

* **BRAINVISA v4.6.1**: click on  BrainVISA-4.6.1-installer_. Once download is finished, open a terminal and type the following lines. ``<download_location>`` refers to the directory where the installer has been downloaded: ::

    cd <download_location>
    chmod u+rwx brainvisa_installer-4.6.1-linux64-glibc-2.23-online
    ./brainvisa_installer-4.6.1-linux64-glibc-2.23-online

 If BrainVISA-4.6.1-installer_ link does not work go to BrainVISA-download_ page and choose the Online installer for OS Linux 64 bits (glibc 2.23) (built on Ubuntu 16.04).



* **JOBLIB**:
    1.  Install the joblib package into the BrainVISA python distribution. ``<BrainVISA_location>`` refers to the install directory of BrainVISA. ::


        <BrainVISA_location>/bin/python -m pip install joblib==0.13.0


    2.  Test the correct installation of joblib. ::

        <BrainVISA_location>/bin/python

        >>> import joblib


* **FSL**:

  1. `FSL installation instructions <https://fsl.fmrib.ox.ac.uk/fsl/fslwiki/FslInstallation>`_. All tests were made with  ``FSL version 6.0.0`` installed througth the ``fslinstaller.py`` script.

  2. Assuming FSL installation worked, add the following command lines to your ``.bashrc`` file where <FSL_INSTALL_DIR> is the directory where FSL is installed (by default ``/usr/local/fsl``) ::

        FSLDIR=<FSL_INSTALL_DIR>
        . ${FSLDIR}/etc/fslconf/fsl.sh
        PATH=${FSLDIR}/bin:${PATH}
        export FSLDIR PATH


  3. FSL configuration into BrainVISA: Once BrainVISA is launched go to BrainVISA/Preferences/FSL menu.


    .. image:: doc/images/fsl_config.png
        :width: 400
        :alt: Checking FSL preferences

    *  ``fsldir`` field value should be identical to $FSLDIR value.  If not change it to $FSLDIR value
    * ``fsl_commands_prefix`` should a priori be empty (default)




Optional
========

* **DCM2NIIX**: ``dcm2niix`` must be installed to handle diffusion weighted dicom data. ``dcm2niix`` can be installed either from dcm2niix github site or from neurodebian.

    + `neurodebian installation <http://neuro.debian.net/install_pkg.html?p=dcm2niix>`_ (requires administrator priviledges) ::

        wget -O- http://neuro.debian.net/lists/xenial.de-m.libre | sudo tee /etc/apt/sources.list.d/neurodebian.sources.list
        sudo apt-key adv --recv-keys --keyserver hkp://pool.sks-keyservers.net:80 0xA5D32F012649A5A9
        sudo apt-get update
        sudo apt-get install dcm2niix


    + github installation:
        * precompiled version :  https://github.com/rordenlab/dcm2niix/releases
        * from sources : https://github.com/rordenlab/dcm2niix

    Diffuse code involving dcm2niix was developped and tested using the neurodebian version of dcm2niix (1:1.0.20180622-1~nd16.04+1).



* **NIFTYREG**: ``niftyreg`` was in general found to be more accurate than FSL and Dipy when it comes to non-linearly register diffusion to structural space. `General installation instructions <http://cmictig.cs.ucl.ac.uk/wiki/index.php/NiftyReg_install>`_.

     1. How to get niftyreg sources: http://cmictig.cs.ucl.ac.uk/wiki/index.php/NiftyReg_install#Source

     2. How to build and install from sources: http://cmictig.cs.ucl.ac.uk/wiki/index.php/NiftyReg_install#Linux

* **NLSAM**: Diffuse relies on Dipy denoising algorithms (LPCA, NLMS). Non Local Spatial and Angular Matching (NLSAM) dwi denoising algorithm is not yet part of Dipy and has to be installed from the `NLSAM reference site <https://github.com/samuelstjean/nlsam>`_.  Using the ``pip`` of the BrainVISA distribution do: ::

        pip install https://github.com/samuelstjean/nlsam/archive/master.zip --user --process-dependency-links




-------------------
Proper Installation
-------------------

1. Click on ``Download ZIP`` on github.

2. Unpack the archive into any desired location with your favorite archive manager.
   Here is an example in command line using ``tar`` ::

    tar xvf Brainvisa-Diffuse.zip -C <desired_location>

3. Switch to the Brainvisa-Diffuse directory ::

    cd <desired_location>/Brainvisa-Diffuse

4. Change the permissions of setup.sh so that you can execute it ::

    chmod u+rwx setup.sh

5. Run the setup.sh script ::

    ./setup.sh

6. During the installation, you will be asked to enter manually the location of your ``BrainVISA`` directory.

7. At this stage, the setup.sh script will automatically handle the copy of Diffuse directories in the correct
   location. If any error occurs, please check that you specified the correct BrainVISA location or the access permissions into the BrainVISA directory.

8. Run BrainVISA and update Diffuse documentation::

    brainvisa --updateDocumentation

9. Congratulations ! Diffuse is installed and ready to be used !


---------------------------------------
Alternative : installation from sources
---------------------------------------

For users already familiar with the BrainVISA compilation from source machinery, aka ``bv_maker`` , Diffuse can be included in the compilation process by adding the following lines to the ``bv_maker.cfg``
file used::

    [ source <source_directory> ]
      git https://github.com/MecaLab/Brainvisa-Diffuse.git master diffuse

    [ build <build_directory> ]
       + <source_directory>/diffuse




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


