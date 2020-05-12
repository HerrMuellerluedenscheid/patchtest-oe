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

# SPDX-License-Identifier: GPL-2.0-or-later

import base
import parse_upstream_status
import pyparsing
import re
import os

class PatchUpstreamStatus(base.Base):

    upstream_status_regex = re.compile("(?<=\+)Upstream.Status", re.IGNORECASE)

    @classmethod
    def setUpClassLocal(cls):
        cls.newpatches = []
        # get just those relevant patches: new software patches
        for patch in cls.patchset:
            if patch.path.endswith('.patch') and patch.is_added_file:
                cls.newpatches.append(patch)

    def setUp(self):
        if self.unidiff_parse_error:
            self.skip('Python-unidiff parse error')
        self.valid_status    = ', '.join(parse_upstream_status.upstream_status_nonliteral_valid_status)
        self.standard_format = 'Upstream-Status: <Valid status>'

    def test_upstream_status_presence_format(self):
        if not PatchUpstreamStatus.newpatches:
            self.skip("There are no new software patches, no reason to test Upstream-Status presence/format")

        for newpatch in PatchUpstreamStatus.newpatches:
            payload = newpatch.__str__()
            if not self.upstream_status_regex.search(payload):
                self.fail('Added patch file is missing Upstream-Status in the header',
                          'Add Upstream-Status: <Valid status> to the header of %s' % newpatch.path,
                          data=[('Standard format', self.standard_format), ('Valid status', self.valid_status)])
            for line in payload.splitlines():
                if self.patchmetadata_regex.match(line):
                    continue
                if self.upstream_status_regex.search(line):
                        if parse_upstream_status.inappropriate_status_mark.searchString(line):
                            try:
                                parse_upstream_status.upstream_status_inappropriate_info.parseString(line.lstrip('+'))
                            except pyparsing.ParseException as pe:
                                self.fail('Upstream-Status is Inappropriate, but no reason was provided',
                                          'Include a brief reason why %s is inappropriate' % os.path.basename(newpatch.path),
                                          data=[('Current', pe.pstr), ('Standard format', 'Upstream-Status: Inappropriate [reason]')])
                        elif parse_upstream_status.submitted_status_mark.searchString(line):
                            try:
                                parse_upstream_status.upstream_status_submitted_info.parseString(line.lstrip('+'))
                            except pyparsing.ParseException as pe:
                                self.fail('Upstream-Status is Submitted, but it is not mentioned where',
                                          'Include where %s was submitted' % os.path.basename(newpatch.path),
                                          data=[('Current', pe.pstr), ('Standard format', 'Upstream-Status: Submitted [where]')])
                        else:
                            try:
                                parse_upstream_status.upstream_status.parseString(line.lstrip('+'))
                            except pyparsing.ParseException as pe:
                                self.fail('Upstream-Status is in incorrect format',
                                          'Fix Upstream-Status format in %s' % os.path.basename(newpatch.path),
                                          data=[('Current', pe.pstr), ('Standard format', self.standard_format), ('Valid status', self.valid_status)])
