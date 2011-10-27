from os import path
import json
from SCons.Script import *
    
def get_varlist(pth):
    """
    Return a list of tuples describing refpkg contents. The output can
    be used to define environment variables, where files within the
    refpkg are identified by keys in the 'files' dictionary (each
    value is a PathVariable object), and 'refpkg' provides the path to
    the reference package itself as an instance of
    PathVariable.PathIsDir. For example::

        from bioscons.refpkg import get_vars 
        vars = Variables()
        vars.AddVariables(*get_vars('/path/to/refpkg'))
        env = Environment(ENV=os.environ, variables=vars)
        path_to_refpkg = env['refpkg']
        path_to_profile = env['refpkg_profile']
    """

    _fullpath = lambda fname: path.abspath(path.join(pth, fname))

    output = [PathVariable('refpkg','refpkg directory', path.abspath(pth),
                           PathVariable.PathIsDir)]
    
    with open(_fullpath('CONTENTS.json'), 'rU') as fobj:
            contents = json.load(fobj)

    output.extend(
        [('refpkg_'+key, key, _fullpath(val), PathVariable) \
             for key, val in contents['files'].items()]
        )

    return output
    
