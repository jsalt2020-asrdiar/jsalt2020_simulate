# -*- coding: utf-8 -*-
from pydoc import locate
import distutils.util



def checked_cast(x, t):
    try:
        cast = locate(t)
        if t == 'bool':
            if isinstance(x, bool):
                return x
            else:
                return cast(distutils.util.strtobool(x))
        else:
            return cast(x)
    except:
        raise ValueError('Cannot cast {} to type {}'.format(x, t))
        

def checked_cast_array(x, t, nelems=None):
    try:
        cast = locate(t)
        if t == 'bool':
            ret = [cast(distutils.util.strtobool(xi)) if isinstance(xi, str) else xi for xi in x]
        else:
            # ret = [float(xi) for xi in x]
            ret = [cast(xi) for xi in x]
    except:
        raise ValueError('Cannot cast {} to list of type {}'.format(x, t))


    if nelems is not None and len(ret) != nelems:
        raise RuntimeError('The number of arguments ({}) does not match the desired number ({})'.format(len(ret), nelems))

    return ret

