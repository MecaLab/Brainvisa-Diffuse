#!/bin/bash

####################################################################
# We need 1 argument.
#
ARGS=2
E_BADARGS=65

if [ $#  -lt "$ARGS" ]
then 
   echo "Usage: `basename $0` [ecclog] [list of mats]"
   echo
   echo "[ecclog]     ecclog file"
   echo
   exit $E_BADARGS 
fi

ECCLOG=$1;
#
####################################################################

####################################################################
# Check if the input arguments are correct
#
if [ ! -e $ECCLOG ]; then
   echo "$ECCLOG does not exist!"
   echo "Exiting!"
   exit $E_BADARGS 
fi

#
####################################################################

####################################################################
# Create the mat files from input
#
# Here we read input ecclog file line by line, produce the FSL mat
# file and fill it with respective trasformation. File listing all
# the mat files generates is also created

listfile=$2

if [ -e ${listfile} ]
then
	rm ${listfile}
fi

cat ${ECCLOG} | while read line; do
    #create a file name from processed volumes
    matfile=$(echo ${line} | grep processing | awk '{print $2}');
    if [ "${matfile}" != "" ] ; then
	   matfile=${matfile}.mat;
       #echo "Generating ... ${matfile}";
       echo ${matfile} >> ${listfile};
       # following two reads will deal with unimportant lines
       read line;
       read line;
       # read matrix and store it in the current matfile
       read line;
       echo ${line} > ${matfile};
       read line;
       echo ${line} >> ${matfile};
       read line;
       echo ${line} >> ${matfile};
       read line;
       echo ${line} >> ${matfile};
    fi
 done
#
####################################################################
