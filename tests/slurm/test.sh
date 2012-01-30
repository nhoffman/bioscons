#!/bin/sh

case $SLURM_NODEID in
    0) echo "I am running on "
        hostname ;;
    1) hostname
        echo "is where I am running" ;;
esac

env | grep SLURM
