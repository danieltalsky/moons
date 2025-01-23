#!/bin/sh

###############################################################################
### Set up, run, and process ejecta launched from Earth
### Start time
t1=$(date +%s)

### Simulation parameters
nobj=1000      # number of ejected fragments
time=3         # = simulation length in log(years) 
output=-1      # = data output frequency in log(years)
step=1         # = timestep in days

vers='mercury_TidesGas.for'
user='no'     # use user-defined forces?

RUN_DIRECTORY="ScalingTest_obj"$nobj"_t"$time"_s"$output
machine=$(hostname -s)

###############################################################################
### Check if directory exists and if not, create it
if [ ! -d "$RUN_DIRECTORY" ]; then
  echo "$RUN_DIRECTORY does not exist. Copying BlankDir to $RUN_DIRECTORY"
  cp -rp BlankDir $RUN_DIRECTORY
fi

### Write files.in
./writefiles.sh $RUN_DIRECTORY

### Repeat simulation n times and record summary of collisions
### Range for iterations
if [ $machine = chloe ]; then
    itrange=$(jot $niter 1)    # start at y, go up x-1 steps
else
    itrange=$(seq 1 $niter)    # go from x to y
fi

echo 'Running in '$RUN_DIRECTORY
\rm $RUN_DIRECTORY/Out/*.dmp
\rm $RUN_DIRECTORY/Out/*.out

### Create big.in and small.in object lists, with specific big object positiosn and randomized radial ejecta
uv run python -c 'from merc_module.mercmodule import MercModule; MercModule.MakeBigRand("'$RUN_DIRECTORY'","'$j'",big=["Mercury","Venus","Earth","Mars","Jupiter","Saturn","Uranus","Neptune"],seed=0)'
uv run python -c 'from merc_module.mercmodule import MercModule; MercModule.MakeSmallEjecta("'$RUN_DIRECTORY'","'$j'",'$nobj')'

### Write param.in file
./writeparam.sh $RUN_DIRECTORY $time $output $step $time $user
### Compile mercury and element fortran code
gfortran -std=legacy -w -o ${RUN_DIRECTORY}/Out/merc_${RUN_DIRECTORY} Files/$vers
gfortran -std=legacy -w -o ${RUN_DIRECTORY}/Out/elem Files/elem.for

### Run mercury inside the specified directory
t2=$(date +%s)
cd $RUN_DIRECTORY/Out
./merc_$RUN_DIRECTORY
cd ../..

### Write collisions summary, write Out/element.in with objects that collide somewhere we're tracking
uv run python -c 'from merc_module.mercmodule import MercModule; MercModule.CopyInfo("'$RUN_DIRECTORY'","'$j'",False,True)'

### Run element to get .aei files for planets and identified ejecta
t3=$(date +%s)
cd $RUN_DIRECTORY/Out
rm *.aei
rm -r AeiOutFiles
./elem
mkdir AeiOutFiles
\mv *.aei AeiOutFiles
cd ../..

### Visualize the trajectories 
t4=$(date +%s)
uv run python -c 'from merc_module.mercmodule import MercModule; MercModule.PlotAllObjects("'$RUN_DIRECTORY'/Out/AeiOutFiles/")'

### Track runtimes for this directory:
t5=$(date +%s)
echo ""$RUN_DIRECTORY",  "$machine",  "$user",  "$nobj",  "$time",  "$output",  "$step",  "$(echo "$t2 - $t1"|bc )",  "$(echo "$t3 - $t2"|bc )",  "$(echo "$t4 - $t3"|bc )",  "$(echo "$t5 - $t4"|bc ) >> runtime.csv
# header = directory, machine, user, n_objects, log_sim_time, log_output_step, timestep, prep_time, merc_time, elem_time, plot_time
