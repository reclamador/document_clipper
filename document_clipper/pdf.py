# -*- coding: utf-8 -*-
import re
import logging
import imghdr
from scraperwiki import pdftoxml
from bs4 import BeautifulSoup
from PyPDF2 import PdfFileWriter, PdfFileReader
from pilkit.processors import ResizeToFit
from PIL import Image
from tempfile import NamedTemporaryFile


PAGE_TAG_NAME = u'page'
BOLD_TAG_NAME = u'b'
TEXT_TAG_NAME = u'text'


class DocumentClipperError(Exception):
    pass


class DocumentClipperPdfReader:
    def __init__(self, pdf_file):
        self.pdf_file = pdf_file
        self._pdf_to_xml = None

    def _read_file(self):
        """
        :return: the contents of the PDF file loaded into the instance
        """
        self.pdf_file.seek(0)
        return self.pdf_file.read()

    def _str_list_to_int_list(self, str_list):
        """
        Converts a list of numbers in string formatinto a list of float items.
        :param str_list: the list of string numbers to be converted
        :return: the list of input string numbers converted into float objects
        """
        return (float(param) for param in str_list)

    def pdf_to_xml(self):
        """
        Returns a structure representing the XML contents of the input PDF file.
        @return: a structure representing the PDF contents as XML nodes, suitable for programmatic manipulation.
        """
        pdf_file_contents = self._read_file()
        pdf_contents_to_xml = pdftoxml(pdf_file_contents)
        self._pdf_to_xml = BeautifulSoup(pdf_contents_to_xml, 'xml')
        return self._pdf_to_xml

    def get_pages(self):
        """Returns a list of `page` nodes representing the pages of the loaded PDF file, in XML format."""
        return self._pdf_to_xml.findAll(PAGE_TAG_NAME)

    def find_text_with_content(self, pages, text_to_find, start_page=0):
        """
        Given a list of 'page' nodes, performs a search of 'text_to_find' on the 'text' nodes of the
        'page' nodes. If no text is found, returns an empty list.
        @param pages: a list of XML nodes (from a BeautifulSoup structure) with 'page' name
        @param text_to_find: the text to lookup in the 'pages' list in Unicode format
        @param start_page: optionally specify the starting position from which the 'pages' list should be iterated over.
        (default=0)
        @return: a list of dictionary items, where each item contains the page index (key 'page_idx') and the XML node
        of type 'text' that contain the searched text (key 'content'). Empty list if none was found.
        """
        looked_up_pages = pages[slice(start_page, None)]  # From some start position to last item (inclusive)
        content = None
        found_nodes = []
        for page_idx, page in enumerate(looked_up_pages):
            content = page.find(text=re.compile(text_to_find))
            if content:
                while content.name != TEXT_TAG_NAME:
                    content = content.parent
                found_nodes.append({'page_idx': page_idx, 'content': content})

        return found_nodes

    def get_text_coordinates(self, text_node):
        """
        Given an XML node of type 'text', fetch the dimensions and location attributes of the node, according to its
        position in the PDF file.

        @param text_node: the XML node with name 'text' that should contain attributes of the text dimensions
        and location coordinates
        @return: a list with the location coordinates (left, top) and the dimensions (width, height) of the text
        associated to the input 'text' node.
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
        """
        Returns the maximum width and height associated to an XML 'page' node.
        :param page_tag_node: page node from which the attributes will be extracted
        :return: a list containing the page's width and height, in that order.
        """
        max_page_width = page_tag_node.attrs.get('width', '0')
        max_page_height = page_tag_node.attrs.get('height', '0')
        params = [max_page_width, max_page_height]

        return self._str_list_to_int_list(params)


class DocumentClipperPdfWriter:

    MAX_SIZE_WITH_MARGINS = (2400, 3400)
    MAX_SIZE_IN_PIXELS = (2480, 3508)
    MARGIN_LEFT = 40
    MARGIN_TOP = 54


    def __init__(self, max_size_in_pixels=MAX_SIZE_IN_PIXELS, max_size_with_margins=MAX_SIZE_WITH_MARGINS,
                 margin_left=MARGIN_LEFT, margin_top=MARGIN_TOP):
        self.max_size_with_margins = max_size_with_margins
        self.max_size_in_pixels = max_size_in_pixels
        self.margin_left = margin_left
        self.margin_top = margin_top

    def image_to_pdf(self, img, pdf_path=None, **kwargs):
        """
        Convert image to pdf.
        :param img: image file opened by PIL
        :param pdf_path: path to save pdf
        :param kwargs: any parameter accepted by Image.save i.e. quality
        :return:
        """
        processor = ResizeToFit(self.MAX_SIZE_WITH_MARGINS[0], self.MAX_SIZE_WITH_MARGINS[1])
        img = processor.process(img)
        # Create a white canvas and paste the image
        tmp_image = Image.new("RGB", self.max_size_in_pixels, "white")
        tmp_image.paste(img, (self.margin_left, self.margin_top,
                        self.margin_left + img.size[0], self.margin_top + img.size[1]))
        # Save the image as .pdf file
        if not pdf_path:
            f = NamedTemporaryFile(delete=False)
            pdf_path = f.name
        tmp_image.save(pdf_path, "PDF", resolution=100.0, **kwargs)
        return pdf_path

    def merge_pdfs(self, final_pdf_path, pdf_files_paths, blank_page=True):
        """
        Merge pdf files in only one PDF
        :param final_pdf_path: file path to save pdf
        :param pdf_files_paths: PDF file paths to merge
        :param blank_page: True if want a blank page between pdf
        :return:
        """

        """ Merge all pdf of a folder in one single file '.pdf'. """

        output = PdfFileWriter()

        for num_doc, pdf_file in enumerate(pdf_files_paths):
            if pdf_file == final_pdf_path:
                continue

            if not pdf_file:
                continue

            logging.info(u"Parse '%s'" % pdf_file)

            try:
                document = PdfFileReader(open(pdf_file, 'rb'), strict=False)
                num_pages = document.getNumPages()
            except Exception as exc:
                logging.exception("Error merging pdf %s: %s" % (pdf_file, str(exc)))
                raise DocumentClipperError

            for num_page in range(num_pages):
                output.addPage(document.getPage(num_page))

            if blank_page:
                output.addBlankPage()

        logging.info(u"Start writing '%s'" % final_pdf_path)
        output_stream = file(final_pdf_path, "wb")
        output.write(output_stream)
        output_stream.close()

    def merge(self, final_pdf_path, files_paths, blank_page=False):
        """
        Merge files (images and pdfs) in to one PDF
        :param final_pdf_path: file path to save pdf
        :param files_paths: file paths to merge
        :param blank_page: True if want a blank page between pdf
        :return:
        """
        real_file_paths = []
        for file_path in files_paths:
            if imghdr.what(file_path):
                img = Image.open(file_path)
                path = self.image_to_pdf(img)
                real_file_paths.append(path)
            else:
                real_file_paths.append(file_path)
        self.merge_pdfs(final_pdf_path, real_file_paths, blank_page)
