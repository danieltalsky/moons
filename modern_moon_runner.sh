#!/bin/sh

RUN_DIRECTORY="BDir2"
# Chloe does it differently so let's just use something else
SIMULATED_MACHINE="basil"

###############################################################################
### Script to repeatedly run moon-planet collision ratio simulations
# Start time
t1=$(date +%s)
machine=$SIMULATED_MACHINE

### Simulation parameters
time=2        # = log(years)
output=1      # = log(years)
step=0.5      # = days
niter=1       # = number of iterations to run

vers='mercury_TidesGas.for'
user='no'     # use user-defined forces?

nobj=6000     # number of ejected fragments
pl='J'        # planet to aim for

### Write files.in
./writefiles.sh $RUN_DIRECTORY

### Repeat simulation n times and record summary of collisions
### Range for iterations
if [ $machine = chloe ]; then
    itrange=$(jot $niter 1)    # start at y, go up x-1 steps
else
    itrange=$(seq 1 $niter)    # go from x to y
fi

### Do iterations
for j in $itrange; do
    echo 'Iteration #' $j ' in '$RUN_DIRECTORY
    \rm $RUN_DIRECTORY/Out/*.dmp
    \rm $RUN_DIRECTORY/Out/*.out

    #### Randomize moon phases and rock positions
    # using only the mode previously called "gen"
    uv run python -c 'from merc_module.mercmodule import MercModule; MercModule.MakeBigRand("'$RUN_DIRECTORY'","'$j'")'
    uv run python -c 'from merc_module.mercmodule import MercModule; MercModule.MakeSmall("'$RUN_DIRECTORY'","'$j'",'$nobj',"'$pl'",1.0e12,1.0e2)'

    # Write param.in file
    # ./writeparam.sh $RUN_DIRECTORY $time $output $step $time $user
    # Compile mercury
    gfortran -std=legacy -w -o ${RUN_DIRECTORY}/Out/merc_${RUN_DIRECTORY} Files/$vers
    # Compile with profiling flags
    # gfortran -std=legacy -w -pg -o ${RUN_DIRECTORY}/Out/merc_${RUN_DIRECTORY} Files/$vers
    # Compile with OpenMP support
    # gfortran -w -o ${RUN_DIRECTORY}/Out/merc_${RUN_DIRECTORY} Files/$vers

    #### Run mercury
    cd $RUN_DIRECTORY/Out; ./merc_$RUN_DIRECTORY; cd ../..

    # example of a run with gprof
    # cd $RUN_DIRECTORY/Out; gprof merc_$RUN_DIRECTORY > test_output.txt; cd ../..
#
#    ### Write collisions summary, copy good in coords
#    # using gen only
#    uv run python -c 'from merc_module.mercmodule import MercModule; MercModule.CopyInfo("'$RUN_DIRECTORY'","'$j'",True)'

done    # j iterations

# Write stop time for this directory:
t2=$(date +%s)
echo ""$RUN_DIRECTORY"    "$machine"    "$niter"    "$nobj"    "$user"    "$(echo "$t2 - $t1"|bc ) >> runtime.txt