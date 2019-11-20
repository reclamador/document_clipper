# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function
import re
import logging
import imghdr
import os
import shutil
from os import path
import tempfile
from bs4 import BeautifulSoup
from PyPDF2 import PdfFileWriter, PdfFileReader
from pilkit.processors import ResizeToFit
from pilkit.utils import save_image
from PIL import Image
from tempfile import NamedTemporaryFile, TemporaryFile
from document_clipper.utils import PDFListImagesCommand, PDFToTextCommand, PDFToImagesCommand, FixPdfCommand, \
    PdfToXMLCommand


PAGE_TAG_NAME = u'page'
BOLD_TAG_NAME = u'b'
TEXT_TAG_NAME = u'text'


class DocumentClipperError(Exception):
    pass


class BaseDocumentClipperPdf(object):

    def compress_img(self, img, quality=70):
        """
        Compress PIL image file to JPEG reducing quality
        :param img: PIL image file
        :param quality:
        :return:
        """
        tmpfile = TemporaryFile()
        return Image.open(save_image(img, tmpfile, 'JPEG', options={'quality': quality}))


class DocumentClipperPdfReader(BaseDocumentClipperPdf):
    def __init__(self, pdf_file, pdf_image_to_text_method=None):
        self.pdf_file = pdf_file
        self._pdf_to_xml = None
        self._pdf_image_to_text_method = pdf_image_to_text_method

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        if self._pdf_to_xml:
            try:
                for image in self._pdf_to_xml.findAll('image'):
                    if image.get('src'):
                        os.remove(image['src'])
            except Exception:
                logging.exception(u"Error cleaning up '%s'" % self.pdf_file.name)

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
        with tempfile.NamedTemporaryFile(suffix='.pdf') as pdffout:
            pdffout.write(pdf_file_contents)
            pdffout.flush()
            pdftoxml_command = PdfToXMLCommand()
            pdf_contents_to_xml = pdftoxml_command.run(pdffout.name)
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
        @return: a x_pdflist of dictionary items, where each item contains the page index (key 'page_idx') and the XML
        node of type 'text' that contain the searched text (key 'content'). Empty list if none was found.
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

    def _convert_to_jpg(self, image_path):
        base = os.path.splitext(image_path)[0]
        new_image_path = base + '.jpg'
        save_image(Image.open(image_path), new_image_path, 'JPEG')
        return new_image_path

    def _pdf_page_to_text(self, page):
        pdftotext_cmd = PDFToTextCommand()
        pdflistimages_cmd = PDFListImagesCommand()
        pdfimages_cmd = PDFToImagesCommand()
        text_out = pdftotext_cmd.run(self.pdf_file.name, page)
        images_out = pdflistimages_cmd.run(self.pdf_file.name, page)
        if pdflistimages_cmd.has_images(images_out):
            images_dir = pdfimages_cmd.run(self.pdf_file.name, page)
            try:
                for f in os.listdir(images_dir):
                    f_path = '/'.join([images_dir, f])
                    if path.isfile(f_path):
                        f_path = self._convert_to_jpg(f_path)
                        text_out += self._pdf_image_to_text_method(f_path)
            except Exception as e:
                shutil.rmtree(images_dir)
                logging.exception("Error extracting text from pdf image")
                raise e
            shutil.rmtree(images_dir)
        return text_out.decode('utf-8')

    def pdf_to_text(self, pdf_image_to_text_method=None):
        """
        Returns the text content of the pdf
        Loops through pages extracting text from images too if necessary
        :return:
        """
        if pdf_image_to_text_method:
            self._pdf_image_to_text_method = pdf_image_to_text_method
        text = ''
        self.pdf_to_xml()
        for index, value in enumerate(self.get_pages()):
            text += self._pdf_page_to_text(index + 1)
        return text


class DocumentClipperPdfWriter(BaseDocumentClipperPdf):

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

    def _write_to_pdf(self, output, path):
        logging.info(u"Start writing '%s'" % path)
        output_stream = open(path, "wb")
        output.write(output_stream)
        output_stream.close()

    def _close_files(self, files_to_close):
        for file in files_to_close:
            file.close()

    def fix_pdf(self, in_path):
        """
        Generates a non-corrupted, well-formatted PDF file from an input
        possibly-corrupted PDF file path, placed at a temporary directory.
        :param in_path: the possibly-corrupted PDF file path.
        :return: the corrected PDF file path successful. Otherwise, return the original input PDF file path.
        """
        fix_pdf_command = FixPdfCommand()
        return fix_pdf_command.run(in_path)

    def image_to_pdf(self, img, pdf_path=None, **kwargs):
        """
        Converts an input image file to a PDF file.
        :param img: image file opened with the PIL library.
        :param pdf_path: optional parameter indicating file path of the to-be-generated PDF file.
        A temporary file is created if no value is provided.
        :param kwargs: any parameter accepted by Image.save i.e. quality
        :return:
        """
        processor = ResizeToFit(width=self.max_size_in_pixels[0], height=self.max_size_in_pixels[1])
        img = processor.process(img)
        # Create a white canvas and paste the image
        final_img_width = min(img.size[0], self.max_size_in_pixels[0])
        final_img_height = min(img.size[1], self.max_size_in_pixels[1])
        tmp_image = Image.new("RGB", (final_img_width, final_img_height), "white")
        margin_left = 0
        margin_top = 0
        tmp_image.paste(img, (margin_left, margin_top,
                              final_img_width, final_img_height))
        tmp_image = self.compress_img(tmp_image, quality=70)
        # Save the image as .pdf file
        if not pdf_path:
            f = NamedTemporaryFile(delete=False)
            pdf_path = f.name
        tmp_image.save(pdf_path, "PDF", resolution=100.0, **kwargs)
        return pdf_path

    def merge_pdfs(self, final_pdf_path, actions, append_blank_page=True):
        """
        Generate a single PDF file containing the combined contents of the input PDF files.
        :param final_pdf_path: file path to save the merged PDF file.
        :param actions: list of tuples, each tuple containing a PDF file path and the degrees of the counterclockwise
        rotation to perform on the PDF document.
        :param append_blank_page: optional flag to indicate whether to append a blank page between documents.
        :return: None. Generates a single PDF file with the contents of the input PDF files and
        removes any temporary files.
        """
        output = PdfFileWriter()

        docs_to_close = []

        for num_doc, (pdf_file_path, rotation) in enumerate(actions):
            if pdf_file_path == final_pdf_path:
                continue

            if not pdf_file_path:
                continue

            logging.info(u"Parse '%s'" % pdf_file_path)

            try:
                document_file = open(pdf_file_path, 'rb')
                document = PdfFileReader(document_file, strict=False)
                num_pages = document.getNumPages()
            except Exception as exc:
                logging.exception("Error merging pdf %s: %s" % (pdf_file_path, str(exc)))
                raise DocumentClipperError
            # Rotation must be performed per page, not per document
            for num_page in range(num_pages):
                page = document.getPage(num_page)
                page = page.rotateCounterClockwise(rotation)
                output.addPage(page)

            if append_blank_page:
                output.addBlankPage()

            docs_to_close.append(document_file)

        self._write_to_pdf(output, final_pdf_path)

        self._close_files(docs_to_close)

    def merge(self, final_pdf_path, actions, append_blank_page=False, fix_files=False):
        """
        Merge files (images and pdfs) in to one PDF
        :param final_pdf_path: file path to save pdf
        :param actions: list of tuples, each tuple consisting of a PDF file path, and the amount of clockwise rotation
        to apply to the document.
        :param append_blank_page: append a blank page between documents if True.
        :param fix_files: optional boolean flag that when set, attempts to fix the input PDF files provided
        in the 'actions' parameter.
        :return: None. Creates a PDF file in the specified path and removes the temporary files that were
        created (if any).
        """
        real_actions = []
        tmp_to_delete_paths = []
        for file_path, rotation in actions:
            if imghdr.what(file_path):
                img = Image.open(file_path)
                path = self.image_to_pdf(img)
                action = (path, rotation)
                real_actions.append(action)
                tmp_to_delete_paths.append(path)
            else:
                if fix_files:
                    file_path = self.fix_pdf(file_path)
                action = (file_path, rotation)
                real_actions.append(action)
                tmp_to_delete_paths.append(file_path)

        self.merge_pdfs(final_pdf_path, real_actions, append_blank_page)

        for path_to_delete in tmp_to_delete_paths:
            # Tmp files to be deleted may already have been deleted due to a pdf fixing process (which already
            # deletes the bad-formatted PDF file). Skip the triggered exception, since file could be already deleted.
            try:
                os.remove(path_to_delete)
            except OSError:
                logging.warning("Cannot delete file with file path %s. It seems it was already deleted."
                                % path_to_delete)

    def slice(self, pdf_file_path, page_actions, final_pdf_path, fix_file=False):
        """
        Create new pdf from a slice of pages of a PDF
        :param pdf_file_path: path of the source PDF document, from which a new PDF file will be created.
        :param page_actions: list of tuples, each tuple containing the page number and the clockwise rotation to
        be applied. The page number is non-zero indexed (first is page 1, and so on).
        :param final_pdf_path: a string containing the file path of the generated PDF file.
        :param fix_file: an optional boolean flag that when set, attempts to fix the input PDF file,
        which could be possibly corrupted
        :return: None. Writes the resulting PDF file into the provided path.
        """
        output = PdfFileWriter()
        input_pdf_path = pdf_file_path
        if fix_file:
            input_pdf_path = self.fix_pdf(input_pdf_path)

        with open(input_pdf_path, 'rb') as file_input:
            input_reader = PdfFileReader(file_input, strict=False)

            # Check page actions correspond to valid input PDF pages
            input_num_pages = input_reader.getNumPages()
            actions_page_numbers = list(zip(*page_actions))[0]
            largest_page_num = max(actions_page_numbers)
            lowest_page_num = min(actions_page_numbers)

            # Input page numbers are 1-indexed
            if lowest_page_num < 1:
                raise Exception(u"Invalid page numbers range in actions: page numbers cannot be lower than 1.")

            if largest_page_num > input_num_pages:
                raise Exception(u"Invalid page numbers range in actions: page numbers cannot exceed the maximum "
                                u"numbers of pages of the source PDF document.")

            # Perform actual slicing + rotation
            # Here page numbers must be normalized to be 0-indexed
            for num_page, rotation in page_actions:
                output.addPage(input_reader.getPage(num_page - 1).rotateCounterClockwise(rotation) if rotation
                               else input_reader.getPage(num_page - 1))
            self._write_to_pdf(output, final_pdf_path)
