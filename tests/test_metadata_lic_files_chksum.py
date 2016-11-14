#!/usr/bin/env python

# Checks related to the patch's lic_files_chksum metadata variable
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

from base import Base
from unittest import skip
from parse_shortlog import shortlog
import re

@skip("Currently blocked by #10059")
class LicFilesChkSum(Base):

    licensemarks = re.compile('LIC_FILES_CHKSUM|LICENSE|CHECKSUM|CHKSUM', re.IGNORECASE)
    addmark      = re.compile('\s*\+LIC_FILES_CHKSUM\s*\??=')
    removemark   = re.compile('\s*-LIC_FILES_CHKSUM\s*\??=')
    licclosed    = re.compile('\s*\+LICENSE\s*=\s*"CLOSED"')
    newpatchrecipes = []

    @classmethod
    def setUpClassLocal(cls):
        """Gets those patches than introduced new recipe metadata"""
        # get just those relevant patches: new software patches
        for patch in cls.patchset:
            if patch.path.endswith('.bb') or patch.path.endswith('.bbappend'):
                if patch.is_added_file:
                    cls.newpatchrecipes.append(patch)

    def setUp(self):
        if self.unidiff_parse_error:
            self.skip([('Parse error', self.unidiff_parse_error)])

    def test_lic_files_chksum_presence(self):
        for patch in self.newpatchrecipes:
            payload = patch.__str__()
            # Closed licenses does not required LIC_FILES_CHKSUM
            if self.licclosed.search(payload):
                continue
            for line in payload.splitlines():
                if self.patchmetadata_regex.match(line):
                    continue
                if self.addmark.search(line):
                    break
            else:
                self.fail('LIC_FILES_CHKSUM is missing in newly added recipe',
                          'Specify the variable LIC_FILES_CHKSUM in %s' % patch.path)

    def test_lic_files_chksum_modified_not_mentioned(self):
        for i in range(LicFilesChkSum.nmessages):
            payload = LicFilesChkSum.payloads[i]
            if self.addmark.search(payload) and self.removemark.search(payload):
                shortlog     = LicFilesChkSum.shortlogs[i]
                commit_message = LicFilesChkSum.commit_messages[i]
                # now lets search in the commit message (summary and commit_message)
                if (not self.licensemarks.search(shortlog)) and \
                   (not self.licensemarks.search(commit_message)):
                    self.fail('LIC_FILES_CHKSUM changed but there was no explanation as to why in the commit message',
                              'Provide a reason for LIC_FILES_CHKSUM change in commit message',
                              shortlog)
