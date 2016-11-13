import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))
from base import Base, fix
import re
from unittest import skip

class SrcUri(Base):

    metadata_regex = re.compile('[\+|-]\s*\S*file://([^ \t\n\r\f\v;\'\"]+)(?!.*=.*)')
    src_regex      = re.compile('[\+|-]\s*SRC_URI = [\"|\'](\S+\.\w*)')
    checksum_regex = re.compile('\S*\s*(SRC_URI\[\S*\] = [\"|\']\S*[\"|\'])')

    def setUp(self):
        if self.unidiff_parse_error:
            self.skip([('Parse error', self.unidiff_parse_error)])

    @skip("Currently blocked by YOCTO #9874")
    @fix("Amend the patch containing the software patch file removal")
    def test_src_uri_left_files(self):
        # get the removed files indicated on diff data
        removed_diff_files = set()
        for removed_file in SrcUri.patchset.removed_files:
            removed_diff_files.add(os.path.basename(removed_file.path))

        # get the removed files indicated on the bitbake metadata
        removed_metadata_files = set()
        for patch in SrcUri.patchset:
            payload = patch.__str__()
            for line in payload.splitlines():
                if self.patchmetadata_regex.match(line):
                    continue
                match = self.metadata_regex.search(line)
                if match:
                    fn = os.path.basename(match.group(1))
                    if line.startswith('-'):
                        removed_metadata_files.add(fn)
                    if line.startswith('+'):
                        if fn in removed_metadata_files:
                            removed_metadata_files.remove(fn)

        # every member of metadata must be a member of diff set, otherwise
        # there are files removed from SRC_URI (contained in metadata set)
        # but not from tree (contained in the diff set)
        notremoved = removed_metadata_files - removed_diff_files
        if notremoved:
            self.fail([('Files not removed from tree', '\n'.join(notremoved))])

    @skip("Currently blocked by YOCTO #10059")
    @fix("SRC_SRI so checksums must change")
    def test_src_uri_checksums_not_changed(self):
        checksums_new = set()
        checksums_old = set()
        checksums_exist = 0
        src_exists = 0
        srcuri_new = 0
        srcuri_old = 0
        for patch in SrcUri.patchset:
            payload = patch.__str__()
            for line in payload.splitlines():
                if self.patchmetadata_regex.match(line):
                    continue
                src_uri_match  = self.src_regex.search(line)
                checksum_match = self.checksum_regex.search(line)
                if src_uri_match:
                    if line.startswith('-'):
                        srcuri_old = src_uri_match.group(1)
                        src_exists = 1
                    if line.startswith('+'):
                        srcuri_new = src_uri_match.group(1)
                if checksum_match:
                    checksum = checksum_match.group(1)
                    if line.startswith('+'):
                        checksums_new.add(checksum)
                    else:
                        checksums_old.add(checksum)
                    checksums_exist = 0
                    if len(checksums_new) == len(checksums_old):
                        checksums_exist = 1
        if src_exists and srcuri_new:
            if srcuri_old != srcuri_new:
                if not checksums_exist:
                    self.fail()
                elif checksums_old.intersection(checksums_new):
                    self.fail()
