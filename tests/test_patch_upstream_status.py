#!/usr/bin/env python

# Checks related to the patch's upstream-status lines
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
from parse_upstream_status import upstream_status_literal_valid_status as valid_status
from parse_upstream_status import upstream_status_mark as mark
import pyparsing
import re

class PatchUpstreamStatus(base.Base):

    upstream_status_mark  = str(mark).strip('"')
    upstream_status_regex = re.compile("(?<=\+)%s" % upstream_status_mark)

    @classmethod
    def setUpClassLocal(cls):
        cls.newpatches = []
        # get just those relevant patches: new software patches
        for patch in cls.patchset:
            if patch.path.endswith('.patch') and patch.is_added_file:
                cls.newpatches.append(patch)

    def setUp(self):
        if self.unidiff_parse_error:
            self.skip([('Python-unidiff parse error', self.unidiff_parse_error)])

    def test_upstream_status_presence(self):
        if not PatchUpstreamStatus.newpatches:
            self.skipTest("There are no new software patches, no reason to test %s presence" % self.upstream_status_mark)

        for newpatch in PatchUpstreamStatus.newpatches:
            payload = newpatch.__str__()
            for line in payload.splitlines():
                if self.patchmetadata_regex.match(line):
                    continue
                if self.upstream_status_regex.search(payload):
                    break
            else:
                self.fail('Added patch file is missing Upstream-Status in the header',
                          'Add Upstream-Status: <status> to the header of %s (possible values: %s)' % (newpatch.path, ', '.join(valid_status)))

    def test_upstream_status_format(self):
        for newpatch in PatchUpstreamStatus.newpatches:
            payload = newpatch.__str__()
            if not self.upstream_status_regex.search(payload):
                continue
            for line in payload.splitlines():
                if self.patchmetadata_regex.match(line):
                    continue
                if self.upstream_status_regex.search(line):
                    try:
                        parse_upstream_status.upstream_status.parseString(line.lstrip('+'))
                    except pyparsing.ParseException as pe:
                        self.fail('Upstream-Status is in incorrect format',
                                  'Fix Upstream-Status format in %s so it is one of: %s' % (newpatch.path, ', '.join(valid_status)))
