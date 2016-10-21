#!/usr/bin/env python

# Checks related to the patch's bugzilla tag
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

import re
from base import Base, fix

class Bugzilla(Base):
    rexp_detect     = re.compile("\[.*YOCTO.*\]", re.IGNORECASE)
    rexp_validation = re.compile("\[\s?YOCTO\s?#\s?(\d+)\s?\]")

    @fix("Provide a bugzilla tag in commit description with format: '[YOCTO #<bugzilla ID>]'")
    def test_bugzilla_entry_format(self):
        for nmessage in xrange(Bugzilla.nmessages):
            commit_message = Bugzilla.commit_messages[nmessage]
            for line in commit_message.splitlines():
                if self.rexp_detect.match(line):
                    if not self.rexp_validation.match(line):
                        self.fail([('Entry', line),
                                   ('Commit shortlog', Bugzilla.shortlogs[nmessage])])

