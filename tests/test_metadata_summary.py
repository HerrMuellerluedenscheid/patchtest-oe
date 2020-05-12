# Checks related to the patch's summary metadata variable
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

# SPDX-License-Identifier: GPL-2.0-or-later

import base
from patchtestdata import PatchTestInput as pti

class Summary(base.Metadata):
    metadata = 'SUMMARY'

    def setUp(self):
        # these tests just make sense on patches that can be merged
        if not pti.repo.canbemerged:
            self.skip('Patch cannot be merged')

    def test_summary_presence(self):
        if not self.added:
            self.skip('No added recipes, skipping test')

        for pn in self.added:
            # we are not interested in images
            if 'core-image' in pn:
                continue
            rd = self.tinfoil.parse_recipe(pn)
            summary = rd.getVar(self.metadata)

            # "${PN} version ${PN}-${PR}" is the default, so fail if default
            if summary.startswith('%s version' % pn):
                self.fail('%s is missing in newly added recipe' % self.metadata,
                          'Specify the variable %s in %s' % (self.metadata, pn))
