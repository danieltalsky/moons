#!/bin/sh

SOURCE_DIR="BDir2"
BASE_DESTINATION_DIR="/opt/moons-child-runs/"
NUMBER_OF_CHILD_PROCESSES=1

###############################################################################
### Script to repeatedly run moon-planet collision ratio simulations
# Start time
t1=$(date +%s)

### Simulation parameters
time=1        # = log(years)
output=1      # = log(years)
step=0.5      # = days

vers='mercury_TidesGas.for'
user='no'     # use user-defined forces?

nobj=500     # number of ejected fragments
pl='J'        # planet to aim for

# Run multiple moon files

### Initialize non-random input files
./writefiles.sh $SOURCE_DIR

# Compile mercury
echo "Compiling the Mercury (w Tides and Gas) executable"
gfortran -w -o ${SOURCE_DIR}/Out/merc_${SOURCE_DIR} Files/$vers

### Do per-directory setup
for j in $(seq 1 $NUMBER_OF_CHILD_PROCESSES); do

    cd /app
    CHILD_INSTANCE_DIR=instance_$j
    CHILD_RUN_DIR="$BASE_DESTINATION_DIR""$CHILD_INSTANCE_DIR"
    echo "Creating child run directory $j named: $CHILD_RUN_DIR"
    mkdir -p $BASE_DESTINATION_DIR
    cp -r ./$SOURCE_DIR $CHILD_RUN_DIR
    \rm $CHILD_RUN_DIR/Out/*.dmp 2>/dev/null
    \rm $CHILD_RUN_DIR/Out/*.out 2>/dev/null

    # #### Randomize moon phases and rock positions
    echo "Prepopulating data for $CHILD_RUN_DIR"
    cd $BASE_DESTINATION_DIR
    export PYTHONPATH=/app/
    uv run python -c 'from merc_module.mercmodule import MercModule; MercModule.MakeBigRand("'$CHILD_INSTANCE_DIR'","'$j'")'
    uv run python -c 'from merc_module.mercmodule import MercModule; MercModule.MakeSmall("'$CHILD_INSTANCE_DIR'","'$j'",'$nobj',"'$pl'",1.0e12,1.0e2)'

    # Write param.in file
    /app/writeparam.sh $CHILD_RUN_DIR $time $output $step $time $user

done    # j iterations

### Do parallel mercury runs
for j in $(seq 1 $NUMBER_OF_CHILD_PROCESSES); do

    CHILD_INSTANCE_DIR=instance_$j
    CHILD_RUN_DIR="$BASE_DESTINATION_DIR""$CHILD_INSTANCE_DIR"

    echo "Kicking off $CHILD_RUN_DIR in the background"
    cd $CHILD_RUN_DIR/Out
    (./merc_$SOURCE_DIR) &
done

echo "All processes starting, waiting for them all to complete." 
wait
echo "All the processes ran..."

### Do parallel post-processing mercury runs
mkdir /app/results
OUTPUT_DIRECTORY=/app/results
OUTPUT_SUBDIRECTORY=$(date +"%Y-%m-%d_%H-%M-%S")
for j in $(seq 1 $NUMBER_OF_CHILD_PROCESSES); do

    CHILD_INSTANCE_DIR=instance_$j
    CHILD_RUN_DIR="$BASE_DESTINATION_DIR""$CHILD_INSTANCE_DIR"

    ### Write collisions summary, copy good in coords
    echo "Writing collisions summary for: $CHILD_RUN_DIR"
    cd $BASE_DESTINATION_DIR
    export PYTHONPATH=/app/
    uv run python -c 'from merc_module.mercmodule import MercModule; MercModule.CopyInfo("'$CHILD_INSTANCE_DIR'","'$j'",True)'

    cp $CHILD_RUN_DIR/Out/info.out $OUTPUT_DIRECTORY/$OUTPUT_SUBDIRECTORY/$CHILD_INSTANCE_DIR-info.out
done

# @TODO: Transfer the files
# They'll be here:
echo "Files all moved to $OUTPUT_DIRECTORY/$OUTPUT_SUBDIRECTORY"
ls $OUTPUT_DIRECTORY/$OUTPUT_SUBDIRECTORY/

# Write stop time for this directory:
t2=$(date +%s)
# echo ""$RUN_DIRECTORY"    "$machine"    "$niter"    "$nobj"    "$user"    "$(echo "$t2 - $t1"|bc ) >> runtime.txt