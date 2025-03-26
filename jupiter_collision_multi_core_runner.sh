#!/bin/sh

SOURCE_FILES_DIR="/app/MercurySourceFilesTemplate/"
SETUP_DIR=/app/MercuryFileSetup/
BASE_DESTINATION_DIR="/app/moons-child-runs/"
NUMBER_OF_CHILD_PROCESSES=1
PRECALCULATE_RANDOMNESS_FOR_TESTING=true

full_run_start_timestamp=$(date +%s)

### Simulation parameters
nobj=100      # number of ejected fragments
time=7         # = simulation length in log(years) 
output=-1      # = data output frequency in log(years)
step=1         # = timestep in days

fortran_source='mercury_TidesGas.for'
user='no'     # use user-defined forces?

# Create a fresh setup directory from the file template
rm -rf "$BASE_DESTINATION_DIR" "$SETUP_DIR"
mkdir -p "$BASE_DESTINATION_DIR"
cp -rp "$SOURCE_FILES_DIR" "$SETUP_DIR"

# Do the precalculation stuff that is going to be the same for every iteration
./writefiles.sh $SETUP_DIR
./writeparam.sh $SETUP_DIR $time $output $step $time $user
# - compile fortran
gfortran -std=legacy -w -o ${SETUP_DIR}/Out/mercury Files/$fortran_source
gfortran -std=legacy -w -o ${SETUP_DIR}/Out/elem    Files/elem.for

# IF "precalculate randomness ahead of time"
# run MakeBigRand and Make Small Ejecta in the setup directory
if [ "$PRECALCULATE_RANDOMNESS_FOR_TESTING" = true ]; then
  uv run python -c 'from merc_module.mercmodule import MercModule; MercModule.MakeBigRand("'$SETUP_DIR'","0",big=["Mercury","Venus","Earth","Mars","Jupiter","Saturn","Uranus","Neptune"],seed=0)'
  uv run python -c 'from merc_module.mercmodule import MercModule; MercModule.MakeSmallEjecta("'$SETUP_DIR'","0",'$nobj')'
fi

# @TODO: Rachel, begin your investigation here.
# I have it running up to this point.
exit

# Iterate and create child directories
### Do per-directory setup
for j in $(seq 1 $NUMBER_OF_CHILD_PROCESSES); do
    CHILD_INSTANCE_DIR=instance_$j
    CHILD_RUN_DIR="$BASE_DESTINATION_DIR""$CHILD_INSTANCE_DIR"
    echo "Creating child run directory $j named: $CHILD_RUN_DIR"
    cp -r $SETUP_DIR $CHILD_RUN_DIR
  # IF NOT "precalculate randomness ahead of time"
  # Run precalculations in each child dir: MakeBig and SmakeSmallEjecta
  if [ "$PRECALCULATE_RANDOMNESS_FOR_TESTING" = false ]; then
    uv run python -c 'from merc_module.mercmodule import MercModule; MercModule.MakeBigRand("'$CHILD_RUN_DIR'","'$j'",big=["Mercury","Venus","Earth","Mars","Jupiter","Saturn","Uranus","Neptune"],seed=0)'
    uv run python -c 'from merc_module.mercmodule import MercModule; MercModule.MakeSmallEjecta("'$CHILD_RUN_DIR'","'$j'",'$nobj')'
  fi
done    # j iterations

mercury_run_start_timestamp=$(date +%s)

### Do parallel mercury runs
for j in $(seq 1 $NUMBER_OF_CHILD_PROCESSES); do
    CHILD_INSTANCE_DIR=instance_$j
    CHILD_RUN_DIR="$BASE_DESTINATION_DIR""$CHILD_INSTANCE_DIR"

    echo "Kicking off $CHILD_RUN_DIR in the background"
    cd $CHILD_RUN_DIR/Out
    (./mercury) &
done

echo "All processes starting, waiting for them all to complete." 
wait
echo "All the processes ran..."

mercury_run_end_timestamp=$(date +%s)

# setup results directories
mkdir -p /app/results
OUTPUT_DIRECTORY=/app/results
OUTPUT_SUBDIRECTORY=$(date +"%Y-%m-%d_%H-%M-%S")
collisions_detected=0

# Iterate and do post-processing
for j in $(seq 1 $NUMBER_OF_CHILD_PROCESSES); do

  CHILD_INSTANCE_DIR=instance_$j
  CHILD_RUN_DIR="$BASE_DESTINATION_DIR""$CHILD_INSTANCE_DIR"

  # do collisions summaries 
  uv run python -c 'from merc_module.mercmodule import MercModule; MercModule.CopyInfo("'$CHILD_RUN_DIR'","'$j'",False,True)'

  # Detect in each directory if a collision happened
  # IF a collision happened
  if [ -f "$CHILD_RUN_DIR/Out/collision_detected" ]; then

    collisions_detected=$((collisions_detected+1))

    # run elem: extract object positions from binary
    cd "$CHILD_RUN_DIR/Out"
    ./elem
    mkdir AeiOutFiles
    \mv *.aei AeiOutFiles

    # copy files to results directory
    cp -rp "$CHILD_RUN_DIR" "$OUPUT_DIRECTORY/$OUTPUT_SUBDIRECTORY"
  fi
done

full_run_end_timestamp=$(date +%s)

echo "Run completed"
echo "Run start: $full_run_start_timestamp || Run end: $full_run_end_timestamp"
echo "Mercury start: $mercury_run_start_timestamp || Mercury end: $mercury_run_end_timestamp"
echo "Collisions detected: $collisions_detected"