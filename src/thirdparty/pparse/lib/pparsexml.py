


# Job's only purpose is to facilitate kick off of XML import.
class PparseXml:

    def __init__(self, xml):
        self.xml = xml

        # Table for reference matching
        self._result_ref_to_extraction = {}

    def add_result_ref(self, result_ref_id, extraction):
        self._result_ref_to_extraction[result_ref_id] = extraction
    
    def has_extraction(self, result_ref_id) -> bool:
        return result_ref_id in self._result_ref_to_extraction

    def get_extraction(self, result_ref_id):
        return self._result_ref_to_extraction[result_ref_id]

    # pparse xmls use pparse as the root element, but it is wrong to assume <pparse />
    # is the root of the xml we're working with. Instead, we assume its the top of the
    # scope pparse is able to process and reason about.
    @classmethod
    def from_xml(cls, xml_src):

        # TODO: Consider xmlnode.py, xmlentry.py, and shoving this class in _xml.py.
        from thirdparty.pparse._xml import XmlNode
        # Ensure our parameters is an XmlNode
        xml = XmlNode.as_node(xml_src)
        
        # Store an instance of this class with our XmlNode.
        pparse_xml = xml.set_obj_inst(PparseXml(xml))

        if not xml.has_tag('pparse'):
            raise ValueError("root node is not <pparse /> in PparseXml class.")

        # TODO: Verify with schema.
        # TODO: Verify parsers.

        # Kick off parsing by instantiating the root extraction.
        if not xml.extraction.has_attr('type'):
            raise Exception("Extraction must have a type.")
        if xml.extraction['type'] not in globals():
            raise Exception(f"Extraction type {xml.extraction['type']} not in scope.")
        extraction_cls = globals()[xml.extraction['type']]
        xml.extraction.set_obj_inst(extraction_cls.from_xml(xml.extraction, pparse_xml))







        # Parse the results
        for result_xml in xml.results:
            # <result> should only ever have a single <node>
            # Note: <result> exists as a generic referable container for extractions.
            if len(result_xml) != 1 or result_xml.get("node") is None:
                # TODO: What should we do with all cases:
                # TODO: - empty?
                # TODO: - extra?
                continue
            
            node_xml = result_xml.node

            # node type defaults to (pparse) Node
            node_type = node_xml['type'] if node_xml.has_attr('type') else 'Node'
            node_cls = globals()[node_type]

            node = node_cls.from_xml(node_xml, xml_root)
            node_xml.set_obj_inst(node)

            # TODO: At this point, we should know all the extraction result 
            # TODO:   references and can match results (as we parse them) to
            # TODO:   the extraction object.
            result_ref_id = result_xml['id']


