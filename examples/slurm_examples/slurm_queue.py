#!/usr/bin/python

from phil import *
import os
import slurm_util
from functools import reduce




#NO_SLURM = 0


if len(argv) != 7:
    print('\nUsage:\n\n%s   <job-tag>   <executable>   <args-file>   <partition>   <number OF NODES to submit>   "submit-log-message"\n\n'\
        %(argv[0]))
    exit(0)

tag = argv[1]
executable = argv[2]
args_file = argv[3]
partition = argv[4]


kill_PD_jobs = True
use_all_under_nodes = False
use_all_idle_nodes = False
exclude_alloc_nodes = False
run_in_exclusive_mode = False ### see if this helps with funny behavior
#run_in_exclusive_mode = True


if argv[5] == 'idle':
    use_all_idle_nodes = True
    exclude_alloc_nodes = True
elif argv[5] == 'under':
    use_all_under_nodes = True
    run_in_exclusive_mode = False
else:
    n_nodes = int(argv[5])
msg = argv[6]

if kill_PD_jobs and ( use_all_idle_nodes or use_all_under_nodes ):
    ## get rid of those silly jobs
    slurm_util.cancel_PD_jobs()

SLEEP = 2

## get a list of the idle nodes on this partition
idle_nodes = slurm_util.get_idle_nodes( partition )
active_nodes = slurm_util.get_active_nodes( partition )

print('found',len(idle_nodes),'idle nodes on partition',partition,'total active_nodes:',len(active_nodes))

#print idle_nodes
#exit(1)


if use_all_idle_nodes:
    n_nodes = len( idle_nodes )
    if n_nodes == 0:
        print('no idle nodes!')
        exit()


underutilized_nodes = []
if use_all_under_nodes:
    free_cores = slurm_util.get_free_cores_for_yhuang_nodes_on_partition( partition )
    print('free_cores:',partition,free_cores)
    #free_cores = slurm_util.get_free_cores_for_partition( partition )
    underutilized_nodes = list(free_cores.keys())[:] ## copy
    n_nodes = len( free_cores )
    if n_nodes == 0:
        print('no underutilized_nodes!',partition)
        exit()
    total_free = reduce( add, list(free_cores.values()) )
    print('running on under-utilized nodes: #nodes: %d ncpus: %d'%( n_nodes, total_free ))


global_exclude_file = '/home/pbradley/exclude_nodes.txt'
global_exclude_nodes = []
data = open( global_exclude_file, 'r' )
for line in data:
    if len(line)>4: global_exclude_nodes.append( line[:-1] )
data.close()

tasks_per_node = slurm_util.get_cores_per_node( partition )


print('Running',n_nodes * tasks_per_node,'tasks!!!!!!!!!!!!!!!')

assert exists( executable ) and exists( args_file )

## write out an info file with the command line args
mkdir( 'slurm_queue_info' )

infofile = 'slurm_queue_info/'+tag+'.info'
if exists( infofile ):
    print('nonunique tag??',infofile,'already exists!')
    exit()

out = open(infofile,'w')
out.write(string.join(argv)+'\n')
out.close()

if exclude_alloc_nodes:
    exclude_file = getcwd()+'/slurm_queue_info/exclude_nodes_'+tag+'.txt'
    nodes_to_be_excluded = slurm_util.get_alloc_nodes( partition ) + global_exclude_nodes
    if nodes_to_be_excluded:
        out = open( exclude_file, 'w' )
        out.write( '\n'.join( nodes_to_be_excluded ) + '\n' )
        out.close()
        assert exists( exclude_file )
        exclude_command = ' --exclude=%s '%exclude_file
    else:
        exclude_command = ''
elif global_exclude_nodes:
    exclude_command = ' --exclude=%s '%global_exclude_file
else:
    exclude_command = ''


assert exists('./input')

mkdir( 'output' )
chdir( 'output' )

total_tasks_submitted = 0

for i in range(n_nodes):
    tasks_for_this_node = tasks_per_node


    id = '%s_%03d'%(tag,i)
    dir = id+"_"+partition
    if exists( dir ):
        print('output dir already exists -- nonunique job name?',dir)
        exit()
    mkdir( dir )
    chdir( dir )


    ## setup for using under-utilized nodes
    if use_all_under_nodes:
        assert n_nodes == len( underutilized_nodes )
        assert not run_in_exclusive_mode
        node = underutilized_nodes[i]
        other_nodes = active_nodes[:]
        assert node in other_nodes
        del other_nodes[ other_nodes.index(node ) ]

        exclude_file = './exclude_nodes.txt' ## must contain / !!!
        out = open( exclude_file, 'w' )
        out.write('\n'.join( other_nodes ) + '\n' )
        out.close()

        exclude_command = ' --nodelist=%s --exclude=%s '%(node,exclude_file )
        tasks_for_this_node = free_cores[ node ]

        if tasks_for_this_node < tasks_per_node -1:
            print('skipping, more than 1 job already running?',node)
            continue

        if tasks_for_this_node == tasks_per_node: tasks_for_this_node = tasks_per_node - 1

        if node in global_exclude_nodes:
            print('skipping node in global_exclude_nodes:',node)
            continue

    cmd = 'ln -s ../../input ./'
    print(cmd)
    system(cmd)

    assert exists('./input')

    if executable[0] == '/':
        exe = executable
    else:
        exe = '../../'+executable

    assert exists( exe )

    if args_file[0] == '/':
        args = args_file
    else:
        args = '../../'+args_file
    assert(exists(args))

    conf = './%s'%tag
    out = open(conf,'w')
    for j in range( tasks_for_this_node ):
        out.write('%d %s -output_tag %s_%d -seed_offset %d @%s\n'\
                      %(j, exe, id, j, total_tasks_submitted + j, args))
    out.close()

    total_tasks_submitted += tasks_for_this_node

    force_desired_node = ''
    if i < len( idle_nodes ):
        #force_desired_node = ' --nodelist=%s '%(idle_nodes[i])
        force_desired_node = ''

    ## PB -- change to -K to prevent jobs from hogging nodes when only a few tasks are still running...
    ##       used to be "-k"
    if run_in_exclusive_mode: exclusive_command = ' --exclusive '
    else: exclusive_command = ' --share '

    cmd = 'nice srun -i none -p %s %s %s -K -o %s_%%t.log -e %s_%%t.err -n %d --multi-prog %s > srun_output 2> srun_error &'\
        %( partition, exclusive_command, exclude_command, id, id, tasks_for_this_node, conf )
    print(cmd)
    system(cmd)

    sleep(SLEEP)

    chdir('../')











#         if NO_SLURM:
#             exe = os.getcwd()+"/../../"+executable
#         else:


#     if NO_SLURM:
#         if len( free_nodes ) == 0: break
#         node = free_nodes[0]
#         del free_nodes[0]

#         for j in range(tasks_per_node):
#             cmd = 'ssh %s "( cd %s; %s -output_tag %s_%d -seed_offset %d @%s > %s_%d.log 2> %s_%d.err & )"'\
#                 %( node, os.getcwd(), exe, id, j, tasks_per_node*i+j, args, id, j, id, j )
#             print cmd
#             system(cmd)

#     else:

