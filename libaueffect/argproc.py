# -*- coding: utf-8 -*-
import os
import imp
import distutils.util
from pydoc import locate



def load_class(full_class_string):
    """
    Taken from https://gist.github.com/tsileo/4354068
    """

    class_data = full_class_string.split(".")

    module_str = class_data[0]
    class_str = class_data[-1]
    submodules_list = []


    if len(class_data) > 2:
        submodules_list = class_data[1:-1]

    f, filename, description = imp.find_module(module_str)
    module = imp.load_module(module_str, f, filename, description)


    # Find each submodule
    for smod in submodules_list:
        path = os.path.dirname(filename) if os.path.isfile(filename) else filename

        f, filename, description = imp.find_module(smod, [path])

        # Now we can load the module
        try:
            module = imp.load_module(" ".join(class_data[:-1]), f, filename, description)
        finally:
            if f:
                f.close()
    # Finally, we retrieve the Class
    return getattr(module, class_str)



def opts2kwargs(exprs):
    ret = {}
    for expr in exprs:
        opt = expr.split('=')
        if len(opt) != 2:
            raise RuntimeError('Option parsing error: {}'.format(opt))

        ret[opt[0].strip()] = opt[1].strip()

    return ret
