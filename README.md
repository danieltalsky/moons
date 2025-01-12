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

## First experiments: time 3, 6000 particles

At 1 CPU and 1GB of memory, ~99% CPU utilization, ~5% memory utilization
8m 15s

At 2 CPU's and 1GB of memory, ~99% CPU utilization, ~5% memory utilization
7m 34s

At 4 CPU's and 16GB of memory, ~99% CPU utilization, ~5% memory utilization
7m 34s

On an amazon EC2 instance
5m 45s

At 3 CPU's and 8GB of memory, compiled without legacy flag
8m 8s

## Second experiments: time 2, 50 particles

```
RAN on 48 cores, 30 processes, 3 time setting, 30 objects
TOTAL SECONDS: 240
TOTAL FORTRAN SECONDS: 224

RAN on 48 cores, 35 processes, 3 time setting, 30 objects
TOTAL SECONDS: 242
TOTAL FORTRAN SECONDS: 224

RAN on 48 cores, 38 processes, 3 time setting, 30 objects
TOTAL SECONDS: 266
TOTAL FORTRAN SECONDS: 248

RAN on 48 cores, 39 processes, 3 time setting, 30 objects
TOTAL SECONDS: 289
TOTAL FORTRAN SECONDS: 270

RAN on 48 cores, 40 processes, 3 time setting, 30 objects
TOTAL SECONDS: 498
TOTAL FORTRAN SECONDS: 479
```

## Setting up an AWS EC2 instance
- Launch in the console
- Login with `ssh -i 'C:\Users\Daniel Talsky\.ssh\RDSRP.pem' ec2-user@<ip-address>`

```shell

sudo yum update -y
sudo yum install docker git -y
sudo service docker start
sudo usermod -a -G docker ec2-user

sudo curl -L https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m) -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
sudo systemctl enable docker.service
sudo systemctl start docker.service

git clone https://github.com/danieltalsky/Moons.git
cd Moons
git checkout performance-benchmark-settings

sudo docker-compose up -d
```
