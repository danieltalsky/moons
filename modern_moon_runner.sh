#!/bin/sh

RUN_DIRECTORY="BDir2"

###############################################################################
### Script to repeatedly run moon-planet collision ratio simulations
# Start time
t1=$(date +%s)
machine=$SIMULATED_MACHINE

### Simulation parameters
time=1        # = log(years)
output=1      # = log(years)
step=0.5      # = days
niter=1       # = number of iterations to run

user='no'     # use user-defined forces?

nobj=100     # number of ejected fragments
pl='J'        # planet to aim for

### Write files.in
# ./writefiles.sh $RUN_DIRECTORY

echo 'Running in '$RUN_DIRECTORY
\rm $RUN_DIRECTORY/Out/*.dmp 2> /dev/null
\rm $RUN_DIRECTORY/Out/*.out 2> /dev/null

#### Randomize moon phases and rock positions
# using only the mode previously called "gen"
# which generates the files from scratch every time


#uv run python -c 'from merc_module.mercmodule import MercModule; MercModule.MakeBigRand("'$RUN_DIRECTORY'","'$j'")'
#uv run python -c 'from merc_module.mercmodule import MercModule; MercModule.MakeSmall("'$RUN_DIRECTORY'","'$j'",'$nobj',"'$pl'",1.0e12,1.0e2)'



# Write param.in file


#./writeparam.sh $RUN_DIRECTORY $time $output $step $time $user



# Compile modules
cd Fortran03SourceFiles
# gfortran -c mercury_constants.f03
# gfortran -c swift_constants.f03
gfortran -c mercury_TidesGas.f03
gfortran mercury_TidesGas.o
cd ..

#### Run mercury
# cd $RUN_DIRECTORY/Out; ./merc_MercuryTides90; cd ../..

### Write collisions summary, copy good in coords
# using only the mode previously called "gen"
# uv run python -c 'from merc_module.mercmodule import MercModule; MercModule.CopyInfo("'$RUN_DIRECTORY'","'$j'",True)'

# Write stop time for this directory:
t2=$(date +%s)
# echo ""$RUN_DIRECTORY"    "$machine"    "$niter"    "$nobj"    "$user"    "$(echo "$t2 - $t1"|bc ) >> runtime.txt