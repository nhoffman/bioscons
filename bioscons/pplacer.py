# pplacer and utilities
def pplacer_emitter(target, source, env):
    refpkg, merged = source
    target = os.path.splitext(str(merged))[0] + '.json'
    return target, source

def pplacer_generator(source, target, env, for_signature):
    """
    target = [.place file (derived from query align)]
    source = [refpkg, ref align, query align]

    Will add flags defined by env['pplacer_flags']
    
    Default flags are as follows:
     * -p - calculate posterior probability and Bayes marginal likelihood
    
    See http://matsen.fhcrc.org/pplacer/manual.html
    """

    try:
        flags = env['pplacer_flags']
    except KeyError:
        flags = '-p' # calculate posterior probabilities by default

    refpkg, merged = source
    outdir, _ = split(str(merged))

    # -c Specify the path to the reference package.
        
    action='pplacer %(flags)s --out-dir "%(outdir)s" -c "%(refpkg)s" "%(merged)s"' % locals()
    return action

pplacer = Builder(generator=pplacer_generator, emitter=pplacer_emitter)

