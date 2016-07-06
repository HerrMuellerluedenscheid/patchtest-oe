from unittest import TestCase
from logging import getLogger
from json import dumps
from unidiff import PatchSet, UnidiffParseError
from patchtestdata import PatchTestInput as pti
from mailbox import mbox

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'pyparsing'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'doc'))

from messages import oemessages as msg

logger=getLogger('patchtest')
debug=logger.debug
info=logger.info
warn=logger.warn
error=logger.error

class OEBase(TestCase):

    @classmethod
    def setUpClass(cls):

        cls.mbox = mbox(pti.repo.patch)

        with open(pti.repo.patch) as f:
            try:
                # for the moment, the charset (encoding is hard coded) toUTF-8
                cls.patchset = PatchSet(f, encoding=u'UTF-8')
            except UnidiffParseError as upe:
                # there are some patches that cannot be parsed by unidiff
                # we need to figure out the root reason for this problem
                error('unidiff failed to parse %s' % pti.repo.patch)
                raise upe

        cls.setUpClassLocal()

    @classmethod
    def setUpClassLocal(cls):
        pass
    
    def fail(self, data=[]):
        testid = '.'.join(self.id().split('.')[-2:])
        failvalue = list(msg[testid])
        failvalue.extend(data)
        return super(OEBase, self).fail(dumps(failvalue))
        

