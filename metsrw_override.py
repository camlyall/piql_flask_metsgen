from datetime import datetime

import metsrw
from lxml import etree
from metsrw import utils


class METSDocument(metsrw.METSDocument):

    def __init__(self):
        super().__init__()

    def serialize(self, fully_qualified=True):
        """
        Returns this document serialized to an xml Element.
        :return: Element for this document
        """
        now = datetime.utcnow().replace(microsecond=0).isoformat("T")
        files = self.all_files()
        mdsecs = self._collect_mdsec_elements(files)
        root = self._document_root(fully_qualified=fully_qualified)
        root.append(self._mets_header(now=now))
        for section in mdsecs:
            root.append(section.serialize(now=now))
        root.append(self._filesec(files))
        root.append(self._structmap())
        # root.append(self._normative_structmap())      # Edit
        return root


class FSEntry(metsrw.FSEntry):
    def __init__(self,
                 path=None,
                 fileid=None,
                 label=None,
                 use="original",
                 type=u"Item",
                 children=None,
                 file_uuid=None,
                 derived_from=None,
                 checksum=None,
                 checksumtype=None,
                 transform_files=None,
                 mets_div_type=None):
        super().__init__(path, fileid, label, use, type, children, file_uuid, derived_from, checksum, checksumtype,
                         transform_files, mets_div_type)

    def serialize_structmap(self, recurse=True, normative=False):
        """Return the div Element for this file, appropriate for use in a
        structMap.
        If this FSEntry represents a directory, its children will be
        recursively appended to itself. If this FSEntry represents a file, it
        will contain a <fptr> element.
        :param bool recurse: If true, serialize and apppend all children.
            Otherwise, only serialize this element but not any children.
        :param bool normative: If true, we are creating a "Normative Directory
            Structure" logical structmap, in which case we add div elements for
            empty directories and do not add fptr elements for files.
        :return: structMap element for this FSEntry
        """
        if not self.label:
            return None
        # Empty directories are not included in the physical structmap.
        if self.is_empty_dir and not normative:
            return None
        el = etree.Element(utils.lxmlns("mets") + "div", TYPE=self.mets_div_type)
        el.attrib["LABEL"] = self.label
        if (not normative) and self.file_id():
            etree.SubElement(el, utils.lxmlns("mets") + "fptr", FILEID=self.file_id())
        if self.dmdids:
            # el.set("DMDID", " ".join(self.dmdids))    # Edit
            el.set('DMDID', self.dmdids[0])             # Edit
        if self.mets_div_type.lower() == "directory" and self.admids:
            el.set("ADMID", " ".join(self.admids))
        if recurse and self._children:
            for child in self._children:
                child_el = child.serialize_structmap(
                    recurse=recurse, normative=normative
                )
                if child_el is not None:
                    el.append(child_el)
        return el
