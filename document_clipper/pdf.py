# -*- coding: utf-8 -*-
import re
from scraperwiki import pdftoxml
from bs4 import BeautifulSoup

PAGE_TAG_NAME = u'page'
BOLD_TAG_NAME = u'b'
TEXT_TAG_NAME = u'text'


class DocumentClipperPdf:
    def __init__(self, pdf_file):
        self.pdf_file = pdf_file
        self._pdf_to_xml = None

    def _read_file(self):
        self.pdf_file.seek(0)
        return self.pdf_file.read()

    def _str_list_to_int_list(self, str_list):
        return (float(param) for param in str_list)

    def pdf_to_xml(self):
        """
        Returns the XML counterpart of the input PDF file contents in a structure suitable for programmatic manipulation
        @param pdf_contents: the contents of a PDF file object
        @return: a BeautifulSoup structure representing the PDF contents in XML nodes
        """
        pdf_file_contents = self._read_file()
        pdf_contents_to_xml = pdftoxml(pdf_file_contents)
        self._pdf_to_xml = BeautifulSoup(pdf_contents_to_xml, 'xml')
        return self._pdf_to_xml

    def get_pages(self):
        """Returns a list of `page` nodes of the XML contents of a PDF file."""
        return self._pdf_to_xml.findAll(PAGE_TAG_NAME)

    def find_text_with_content(self, pages, text_to_find, start_page=0):
        """
        Given a list of BeautifulSoup 'page' nodes, performs a search of 'text_to_find' on the 'text' nodes of the
        'page' nodes. If no text is found, returns None
        @param pages: a list of BeautifulSoup nodes with 'page' name
        @param text_to_find: the text to lookup in the 'pages' list in Unicode format
        @param start_page: optionally specify the starting position from which the 'pages' list should be iterated over.
        (default=0)
        @return: the node of type 'text' that contains the searched text, None if no match was found.
        """
        looked_up_pages = pages[slice(start_page, None)]  # From some start position to last item (inclusive)
        content = None

        for page in looked_up_pages:
            content = page.find(text=re.compile(text_to_find))
            if content:
                while content.name != TEXT_TAG_NAME:
                    content = content.parent
                break

        return content

    def get_text_coordinates(self, text_node):
        """
        Given a BeautifulSoup node of type 'text', fetch the dimensions and location of the node in the PDF file.

        @param text_node: the BeautifulSoup node with name 'text' that should contain attributes with the text's
        dimensions and location coordinates
        @return: a list with the location coordinates (left, top) and the dimensions (width, height) of the text
        associated to the input node.
        """
        if text_node.name != TEXT_TAG_NAME:
            raise Exception(u"Input node is not of type 'text'")

        text_node_attrs = text_node.attrs
        x_position = text_node_attrs.get('left', '0')
        y_position = text_node_attrs.get('top', '0')
        width = text_node_attrs.get('width', '0')
        height = text_node_attrs.get('height', '0')

        params = [x_position, y_position, width, height]

        # Return dimensions and coordinates as integers instead of strings
        return self._str_list_to_int_list(params)

    def get_page_max_dimensions(self, page_tag_node):
        max_page_width = page_tag_node.attrs.get('width', '0')
        max_page_height = page_tag_node.attrs.get('height', '0')
        params = [max_page_width, max_page_height]

        return self._str_list_to_int_list(params)
