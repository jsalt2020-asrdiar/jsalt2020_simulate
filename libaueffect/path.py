# -*- coding: utf-8 -*-
import re
import sys
import os

import libaueffect



def _add_postfix(path, postfix):
    if postfix is None:
        return path
    else:
        fn, ext = os.path.splitext(path)
        return '{}{}{}'.format(fn, postfix, ext)



# Caution: Path may contain no white space.
class PathGenerator(object):
    def __init__(self, pathgen_rule):
        self._pathgen_rule = pathgen_rule
        self._pattern = None

        # 'replace' pattern
        match = re.match('\s*replace\(\s*(\S+)\s*,\s*(\S+)\s*\)\s*$', pathgen_rule)
        if match:
            self._pattern='replace'
            self._org = match.group(1).strip().replace('\\', '/')
            self._tgt = match.group(2).strip().replace('\\', '/')

        # 'prefix' pattern
        match = re.match('\s*prefix\(\s*(\S+)\s*\)\s*', pathgen_rule)
        if match:
            self._pattern = 'prefix'
            self._prefix = match.group(1)

        # 'flatten' pattern
        match = re.match('\s*flatten\(\s*(\S+)\s*\)\s*', pathgen_rule)
        if match:
            self._pattern = 'flatten'
            self._prefix = match.group(1)

        # 'overwrite' pattern
        match = re.match('\s*overwrite\s*', pathgen_rule)
        if match:
            self._pattern = 'overwrite'

        if self._pattern is None:
            raise RuntimeError('Invalid path generation expression: {}'.format(pathgen_rule))

        print('PATH GENERATOR INFO')
        print('Pattern to be applied: {}'.format(self._pattern))
        print('Rule expression: {}'.format(pathgen_rule))
        print('', flush=True)



    def __call__(self, src, postfix=None, mkdir=False):
        if os.path.isabs(src):
            _src = os.path.abspath(src)
        else:
            _src = os.path.relpath(src)

        # 'replace' pattern
        if self._pattern == 'replace':
            if not self._org in _src.replace('\\', '/'):
                raise RuntimeError('Source file name "{}" does not contain the replacement target "{}".'.format(_src, self._org))
            path = _add_postfix(_src.replace('\\','/').replace(self._org, self._tgt), postfix)

        # 'prefix' pattern
        if self._pattern == 'prefix':
            path = _add_postfix(os.path.join(self._prefix, _src), postfix)

        # 'flatten' pattern
        if self._pattern == 'flatten':
            path = _add_postfix(os.path.join(self._prefix, os.path.basename(_src)), postfix)

        # 'overwrite' pattern
        if self._pattern == 'overwrite':
            path = _add_postfix(_src, postfix)

        if mkdir:
            os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
        return path
