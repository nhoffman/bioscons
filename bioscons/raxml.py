# raxml
def raxml_emitter(target, source, env):
    """
    source - infile.phy
    targets - RAxML_info.infile, RAxML_result.infile

    Note that RAxML produces other files not emitted as targets.
    """

    outdir, fname = split(str(source[0]))
    label = splitext(fname)[0]

    target = [join(outdir,'RAxML_%s.%s'%(x,label)) for x in ('info','result')]

    return target, source

def raxml_generator(source, target, env, for_signature):
    """
    Implements env.raxml
    Depends on env['RAxML'] or env['RAxML_threaded']
    Number of threads (-T) may be set using env['raxml_threads'], default is 1

    raxmlHPC -m GTRGAMMA -n label -s align.phy

    -m is the model
    -n is the name of the run (will become output filenames)
    -s is the alignment in phylip format

    TODO: will want to have an additional environment variable for
    arbitrary command line flags for raxml.
    """

    try:
        nthreads = int(env['raxml_threads'])
    except (KeyError, ValueError):
        nthreads = 1

    # here we pull from the environment variables to figure out which RAxML to run
    # TODO: decide if we want to provide default values for names of executables

    if nthreads < 2:
        raxml_key = 'RAxML'
        threadflag = ''
    else:
        raxml_key = 'RAxML_threaded'
        threadflag = '-T %s' % nthreads
        
    try:
        raxml = env[raxml_key]
    except KeyError:
        raise KeyError("KeyError: '%s' must be defined in the current environment." % raxml)

    outdir, fname = split(str(source[0]))
    label = splitext(fname)[0]

    removeme = join(outdir, 'RAxML_*.'+label)

    action = (
        'cd %(outdir)s && '
        'rm -f %(removeme)s && '
        '%(raxml)s %(threadflag)s -m GTRGAMMA -n %(label)s -s %(fname)s' % locals()
        )

    return action

raxml = Builder(generator=raxml_generator, emitter=raxml_emitter)

