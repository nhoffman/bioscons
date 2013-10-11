#!/bin/sh

case $SLURM_NODEID in
    0) echo "I am running on "
        hostname ;;
    1) hostname
        echo "is where I am running" ;;
esac

env | grep -s SLURM || echo "Not using slurm"

if [ ! -z $SLURM_JOBID ]; then
  scontrol show job $SLURM_JOBID
fi
