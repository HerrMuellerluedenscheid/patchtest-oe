#!/usr/bin/env python

# Checks related to the patch's CVE lines
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
import os
import re

class CVE(base.Base):

    re_cve_pattern = re.compile("CVE\-\d{4}\-\d+", re.IGNORECASE)
    re_cve_word    = re.compile("\s*\+CVE\s?", re.IGNORECASE)
    re_cve_tag     = re.compile("CVE:(\s+CVE\-\d{4}\-\d+)+", re.IGNORECASE)

    def setUp(self):
        if self.unidiff_parse_error:
            self.skip([('Parse error', self.unidiff_parse_error)])

    def test_cve_presence_in_commit_message(self):
        for commit in CVE.commits:
            if self.re_cve_word.search(commit.payload):
                if not self.re_cve_pattern.search(commit.commit_message):
                    self.fail('Missing or incorrectly formatted CVE tag in commit message',
                              'Include a "CVE-xxxx-xxxx" tag in the commit message',
                              commit)

    def test_cve_tag_format(self):
        # there are cases where an upgrade is done in order
        # to include a cve (or several) and it is mentioned
        # on shortlog but there is no attached patch or patches
        # because CVE is already on the upgrade sw
        if len(CVE.patchset) == 2:
            if self.re_cve_pattern.search(' '.join([commit.shortlog for commit in CVE.commits])):
                recipes = [os.path.basename(p.path).split('_')[0] for p in CVE.patchset]
                if recipes[0] == recipes[1]:
                    self.skipTest('No check is done on recipe upgrades')

        # Skip check on metadata classes
        if len(CVE.patchset) == 1:
            if CVE.patchset[0].path.endswith('.bbclass'):
                self.skipTest('No check is done on classes')

        for commit in CVE.commits:
            if self.re_cve_pattern.search(commit.shortlog):
                if not self.re_cve_tag.search(commit.payload):
                    self.fail('Missing or incorrectly formatted CVE tag in included patch file',
                              'Correct or include the CVE tag on cve patch with format: "CVE: CVE-YYYY-XXXX"',
                              commit)
