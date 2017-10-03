#!/usr/bin/python

from phil import *
import os
import time
import slurm_util

SMALL_SLEEP = 2
SLEEP = 4
BIG_SLEEP = 10 * 60 ## 10 minutes

n_inner_loop = 1 ## used to be 3, but exclude is working better now?

if len(argv) not in [ 5, 6]:
    print('\nUsage:\n\n%s   <job-tag>   <executable>   <args-file>    "submit-log-message" {nloop}\n\n'%(argv[0]))
    exit(0)

tag = argv[1]
executable = argv[2]
args_file = argv[3]
msg = argv[4]
if len( argv ) == 6:
    nloop = int(argv[5])
else:
    nloop = 1

first_infofile = 'slurm_queue/%s.1.info'%tag
if exists( first_infofile ):
    print('nonunique tagbase?',tag,first_infofile,'already exists!')
    exit()

partitions = [ 'br2norm', 'br3norm', 'br1norm', 'publow', 'csquid1base', 'qgelow', 'upbase', 'emlow', 'edrnlow',
               'csquid0base' ]

counter = 0
for loop in range( nloop ):
    for partition in partitions:
        for inner_loop in range( n_inner_loop+1 ): ## because slurm is stupid !!!
            counter += 1
            mytag = '%s_%d'%(tag,counter)
            infofile = 'slurm_queue_info/'+mytag+'.info'
            while exists( infofile ):
                counter += 1
                mytag = '%s_%d'%(tag,counter)
                infofile = 'slurm_queue_info/'+mytag+'.info'

            if inner_loop == n_inner_loop and False:
                ## under-utilized nodes
                under_partitions = slurm_util.get_partitions_with_underutilized_nodes()
                if partition in under_partitions:
                    cmd = '/home/pbradley/slurm_queue.py %s %s %s %s under "%s"'%( mytag, executable, args_file, partition, msg )
                    print(cmd)
                    system(cmd)

            else:
                cmd = '/home/pbradley/slurm_queue.py %s %s %s %s idle "%s"'%( mytag, executable, args_file, partition, msg )
                print(cmd)
                system(cmd)

            print('sleeping',SMALL_SLEEP,'seconds')
            time.sleep( SMALL_SLEEP )
        print('sleeping',SLEEP,'seconds')
        time.sleep( SLEEP )




    print('sleeping',BIG_SLEEP,'seconds')
    time.sleep( BIG_SLEEP )
