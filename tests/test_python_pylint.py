#!/usr/bin/env python

# Checks related to the python code done with pylint
#
# Copyright (C) 2016 Intel Corporation
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.

import base
import re
import patchtestdata
import pylint.epylint as lint

#@unittest.skip('Pending for Yocto #10789]')
class PyLint(base.Base):
    pythonpatches = []

    @classmethod
    def setUpClassLocal(cls):
        # get just those patches touching python files
        for patch in cls.patchset:
            if patch.path.endswith('.py'):
                cls.pythonpatches.append(patch)

    def setUp(self):
        if self.unidiff_parse_error:
            self.skip([('Python-unidiff parse error', self.unidiff_parse_error)])
        if not patchtestdata.PatchTestInput.repo.canbemerged:
            self.skipTest('Patch cannot be merged, no reason to execute the test method')
        if not PyLint.pythonpatches:
            self.skipTest('No python related patches, skipping test')

    def pretest_pylint(self):
        patchtestdata.PatchTestDataStore['pylint_pretest'] = list()
        for pythonpatch in self.pythonpatches:
            if pythonpatch.is_modified_file:
                (pylint_stdout, pylint_stderr) = lint.py_run(pythonpatch.path, return_std=True)
                patchtestdata.PatchTestDataStore['pylint_pretest'].extend(pylint_stdout.readlines())

    def test_pylint(self):
        patchtestdata.PatchTestDataStore['pylint_test'] = list()
        for pythonpatch in self.pythonpatches:
            (pylint_stdout, pylint_stderr) = lint.py_run(pythonpatch.path, return_std=True)
            patchtestdata.PatchTestDataStore['pylint_test'].extend(pylint_stdout.readlines())

        # Removing line numbers of pylint log so system focus just on introduced issues
        pylint_pretest = [re.sub(':\d+:', ':', pyline) for pyline in patchtestdata.PatchTestDataStore['pylint_pretest']]
        pylint_test    = [re.sub(':\d+:', ':', pyline) for pyline in patchtestdata.PatchTestDataStore['pylint_test']]

        while pylint_pretest:
            pretest = pylint_pretest.pop(0)
            try:
                pylint_test.remove(pretest)
            except ValueError as ve:
                base.logger.warn('Line %s not found on pylint_test lines' % pretest)

        if pylint_test:
            self.fail('Pylint found issues on your proposed change',
                      'Check your modified python lines with pylint, specially those lines introduced by your patch',
                      data=[('Output', pylint_test[0].strip()), ('',''.join(pylint_test[1:]))])

