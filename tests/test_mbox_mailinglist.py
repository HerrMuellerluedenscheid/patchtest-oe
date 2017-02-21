#!/usr/bin/env python
#
# Check if the series was intended for other project (not OE-Core)
#
# Copyright (C) 2017 Intel Corporation
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

import subprocess
import collections
import base
from patchtestdata import PatchTestInput as pti

class MailingList(base.Base):

    # base paths of main yocto project sub-projects
    paths = {
        'oe-core': ['meta-selftest', 'meta-skeleton', 'meta', 'scripts'],
        'bitbake': ['lib', 'classes', 'conf', 'doc', 'contrib', 'bin'],
        'documentation': ['adt-manual','ref-manual', 'sdk-manual','bsp-guide', 'profile-manual','template','toaster-manual','dev-manual', 'mega-manual','tools','kernel-dev','yocto-project-qs'],
        'poky': ['meta-poky','meta-yocto-bsp'],
        'oe': ['meta-gpe', 'meta-gnome', 'meta-efl', 'meta-networking', 'meta-multimedia','meta-initramfs', 'meta-ruby', 'contrib', 'meta-xfce', 'meta-filesystems', 'meta-perl', 'meta-webserver', 'meta-systemd', 'meta-oe', 'meta-python']
        }

    Project = collections.namedtuple('Project', ['name', 'listemail', 'gitrepo', 'paths'])

    bitbake = Project(name='Bitbake', listemail='bitbake-devel@lists.openembedded.org', gitrepo='http://git.openembedded.org/bitbake/', paths=paths['bitbake'])
    doc     = Project(name='Documentantion', listemail='yocto@yoctoproject.org', gitrepo='http://git.yoctoproject.org/cgit/cgit.cgi/yocto-docs/', paths=paths['documentation'])
    poky    = Project(name='Poky', listemail='poky@yoctoproject.org', gitrepo='http://git.yoctoproject.org/cgit/cgit.cgi/meta-yocto(-bsp)', paths=paths['poky'])
    oe      = Project(name='oe', listemail='openembedded-devel@lists.openembedded.org', gitrepo='http://git.openembedded.org/meta-openembedded/', paths=paths['oe'])


    def test_target_mailing_list(self):
        """In case of merge failure, check for other targeted projects"""
        if pti.repo.ismerged:
            self.skip('Series merged, no reason to check other mailing lists')

        for patch in self.patchset:
            folders = patch.path.split('/')
            base_path = folders[0]
            for project in [self.bitbake, self.doc, self.oe, self.poky]:
                if base_path in  project.paths:
                    self.fail('Series sent to the wrong mailing list', 'Send the series again to the correct mailing list (ML)',
                              data=[('Suggested ML', '%s [%s]' % (project.listemail, project.gitrepo))])


