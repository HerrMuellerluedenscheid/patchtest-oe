# Checks related to the patch's author
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
import re

class Author(base.Base):

    auh_email = '<auh@auh.yoctoproject.org>'

    invalids = [re.compile("^Upgrade Helper.+"),
                re.compile(re.escape(auh_email)),
                re.compile("uh@not\.set"),
                re.compile("\S+@example\.com")]


    def test_author_valid(self):
        for commit in self.commits:
            for invalid in self.invalids:
                if invalid.search(commit.author):
                    self.fail('Invalid author %s' % commit.author, 'Resend the series with a valid patch\'s author', commit)

    def test_non_auh_upgrade(self):
        for commit in self.commits:
            if self.auh_email in commit.payload:
                self.fail('Invalid author %s in commit message' % self.auh_email, 'Resend the series with a valid patch\'s author', commit)
