# Moons

This is an unholy combination of shell scripts, text files,
python, and compiled Fortran77 code used to calculate some
gravity stuff for Mercury.  I'm sure Rachel could explain it better.

This project aims to modernize and dockerize the original code
and get it running in a container.

To run the `modern_moon_runner.sh` script that calculates starting points,
and then compiles and runs the Fortran code you will need:

- Docker desktop installed

Then, at the project root, simply bring up the docker container:

```bash
docker compose up
```

## Run log

## 100 years, 6000 particles

At 1 CPU and 1GB of memory, ~99% CPU utilization, ~5% memory utilization
8m 15s

At 2 CPU's and 1GB of memory, ~99% CPU utilization, ~5% memory utilization
7m 34s

At 4 CPU's and 16GB of memory, ~99% CPU utilization, ~5% memory utilization
7m 34s