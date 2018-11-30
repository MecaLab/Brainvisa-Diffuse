#!/usr/bin/bash

echo "Welcome in the Diffuse setup script !"
echo "Please enter the absolute location of your Brainvisa installation"
read -p "Brainvisa installation location :" BV_path
echo Diffuse will be setup up at this location $BV_path
rsync -avz brainvisa/ $BV_path/brainvisa
rsync -avz python/    $BV_path/python
rsync -avz share/     $BV_path/share
echo Diffuse has been succesfully copied into your Brainvisa directory
echo Launch  BrainVISA with the --updateDocumentation option
