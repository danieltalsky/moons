#!/bin/sh

RUN_DIRECTORY="ScalingTestSim1"
# Chloe does it differently so let's just use something else
SIMULATED_MACHINE="basil"

###############################################################################
### Check if directory exists and if not, create it
if [ ! -d "$RUN_DIRECTORY" ]; then
  echo "$RUN_DIRECTORY does not exist. Copying BlankDir to $RUN_DIRECTORY"
  cp -rp BlankDir $RUN_DIRECTORY
fi

###############################################################################
### Script to repeatedly run moon-planet collision ratio simulations
# Start time
t1=$(date +%s)
machine=$SIMULATED_MACHINE

### Simulation parameters
time=2        # = log(years)
output=-2      # = log(years)
step=0.5      # = days
niter=1       # = number of iterations to run

vers='mercury_TidesGas.for'
user='no'     # use user-defined forces?

nobj=10     # number of ejected fragments
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
    # which generates the files from scratch every time
    uv run python -c 'from merc_module.mercmodule import MercModule; MercModule.MakeBigRand("'$RUN_DIRECTORY'","'$j'",big=["Mercury","Venus","Earth","Mars","Jupiter","Saturn","Uranus","Neptune"],seed=0)'
    # uv run python -c 'from merc_module.mercmodule import MercModule; MercModule.MakeSmall("'$RUN_DIRECTORY'","'$j'",'$nobj',"'$pl'",1.0e12,1.0e2)'
    uv run python -c 'from merc_module.mercmodule import MercModule; MercModule.MakeSmallEjecta("'$RUN_DIRECTORY'","'$j'",'$nobj')'

    # Write param.in file
    ./writeparam.sh $RUN_DIRECTORY $time $output $step $time $user
    # Compile mercury
    gfortran -std=legacy -w -o ${RUN_DIRECTORY}/Out/merc_${RUN_DIRECTORY} Files/$vers
	gfortran -std=legacy -w -o ${RUN_DIRECTORY}/Out/elem Files/elem.for

    #### Run mercury and element inside the specified directory
    cd $RUN_DIRECTORY/Out
    ./merc_$RUN_DIRECTORY
    rm *.aei
    ./elem
    mkdir AeiOutFiles
    \mv *.aei AeiOutFiles
    cd ../..

    ### Write collisions summary, copy good in coords
    # using only the mode previously called "gen"
    uv run python -c 'from merc_module.mercmodule import MercModule; MercModule.CopyInfo("'$RUN_DIRECTORY'","'$j'",True)'

    ### Visualize the trajectories
    uv run python -c 'from merc_module.mercmodule import MercModule; MercModule.PlotAllObjects("'$RUN_DIRECTORY'/Out/AeiOutFiles/")'


done    # j iterations

# Write stop time for this directory:
t2=$(date +%s)
echo ""$RUN_DIRECTORY",  "$machine",  "$time",  "$niter",  "$nobj",  "$user",  "$(echo "$t2 - $t1"|bc ) >> runtime.csv