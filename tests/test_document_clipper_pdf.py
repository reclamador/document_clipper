#!/usr/bin/env python
# -*- coding: utf-8 -*-

from unittest import TestCase
from mock import Mock
import os
from document_clipper.pdf import DocumentClipperPdfReader, DocumentClipperPdfWriter
from PIL import Image

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))

PATH_TO_PDF_FILE = os.path.join(CURRENT_DIR, 'sample-files/sample.pdf')
PATH_TO_JPG_FILE = os.path.join(CURRENT_DIR, 'sample-files/sample.jpg')
PATH_TO_NEW_PDF_FILE = os.path.join(CURRENT_DIR, 'new_pdf.pdf')
PATH_TO_PDF_FILE_WITH_IMAGES = os.path.join(CURRENT_DIR, 'sample-files/dni_samples.pdf')
PATH_TO_PDF_FILE_WITH_IMAGES_NO_JPG = os.path.join(CURRENT_DIR, 'sample-files/pdf_with_images_not_jpg.pdf')


class TestDocumentClipperPdf(TestCase):
    def setUp(self):
        self.pdf_file = open(PATH_TO_PDF_FILE)
        self.img_file = Image.open(PATH_TO_JPG_FILE)
        self.document_clipper_pdf_reader = DocumentClipperPdfReader(self.pdf_file)
        self.document_clipper_pdf_writer = DocumentClipperPdfWriter()

    def tearDown(self):
        self.document_clipper_pdf_reader = None


    def _images_to_text_method_mocked(self):
        method = Mock()
        method.return_value = 'llamada a metodo'
        return method

    def test_pdf_to_xml_ok(self):
        pdf_to_xml = self.document_clipper_pdf_reader.pdf_to_xml()

        self.assertTrue(pdf_to_xml.is_xml)
        self.assertIsNotNone(pdf_to_xml.contents)

    def test_get_pages_ok(self):
        self.document_clipper_pdf_reader.pdf_to_xml()
        pages = self.document_clipper_pdf_reader.get_pages()
        self.assertEqual(len(pages), 10)

    def test_find_text_with_content_ok(self):
        self.document_clipper_pdf_reader.pdf_to_xml()
        pages = self.document_clipper_pdf_reader.get_pages()
        text_nodes = self.document_clipper_pdf_reader.find_text_with_content(pages=pages,
                                                   text_to_find=u'chapter 3',
                                                   start_page=0)
        text_node_item = text_nodes[0]
        self.assertIsNotNone(text_node_item['content'])
        self.assertEqual(text_node_item['page_idx'], 8)

    def test_find_text_with_content_not_ok(self):
        self.document_clipper_pdf_reader.pdf_to_xml()
        pages = self.document_clipper_pdf_reader.get_pages()
        start_page = len(pages) - 1
        text_nodes = self.document_clipper_pdf_reader.find_text_with_content(pages=pages,
                                                                     text_to_find=u'chapter 3',
                                                                     start_page=start_page)
        self.assertEqual(text_nodes, [])

    def test_get_text_coordinates_ok(self):
        EXPECTED_X_POSITION = 149.0
        EXPECTED_Y_POSITION = 493.0
        EXPECTED_WIDTH = 350.0
        EXPECTED_HEIGHT = 16.0

        self.document_clipper_pdf_reader.pdf_to_xml()
        pages = self.document_clipper_pdf_reader.get_pages()
        text_nodes = self.document_clipper_pdf_reader.find_text_with_content(pages=pages,
                                                                     text_to_find=u'chapter 3',
                                                                     start_page=0)
        text_node = text_nodes[-1]  # Use last text occurrence
        x_position, y_position, width, height = \
            self.document_clipper_pdf_reader.get_text_coordinates(text_node['content'])

        self.assertEqual(x_position, EXPECTED_X_POSITION)
        self.assertEqual(y_position, EXPECTED_Y_POSITION)
        self.assertEqual(width, EXPECTED_WIDTH)
        self.assertEqual(height, EXPECTED_HEIGHT)

    def test_get_text_coordinates_not_ok(self):
        non_text_node = Mock()
        non_text_node.name = 'none'
        with self.assertRaisesRegexp(Exception, u"Input node is not of type 'text'"):
            self.document_clipper_pdf_reader.get_text_coordinates(non_text_node)

    def test_get_page_dimensions_ok(self):
        EXPECTED_MAX_PAGE_WIDTH = 892.0
        EXPECTED_MAX_PAGE_HEIGHT = 1262.0

        self.document_clipper_pdf_reader.pdf_to_xml()
        pages = self.document_clipper_pdf_reader.get_pages()
        first_page = pages[0]

        page_width, page_height = self.document_clipper_pdf_reader.get_page_max_dimensions(first_page)

        self.assertEqual(page_width, EXPECTED_MAX_PAGE_WIDTH)
        self.assertEqual(page_height, EXPECTED_MAX_PAGE_HEIGHT)

    def test_image_to_pdf(self):
        new_pdf_path = self.document_clipper_pdf_writer.image_to_pdf(self.img_file)
        new_pdf = open(new_pdf_path)
        new_document_clipper_pdf_reader = DocumentClipperPdfReader(new_pdf)
        new_document_clipper_pdf_reader.pdf_to_xml()
        pages = new_document_clipper_pdf_reader.get_pages()
        self.assertEqual(len(pages), 1)
        new_pdf.close()
        os.remove(new_pdf_path)

    def test_merge_pdfs_without_rotation(self):
        actions = [(self.pdf_file.name, 0), (self.pdf_file.name, 0)]
        self.document_clipper_pdf_writer.merge(PATH_TO_NEW_PDF_FILE, actions)
        new_pdf = open(PATH_TO_NEW_PDF_FILE)
        new_document_clipper_pdf_reader = DocumentClipperPdfReader(new_pdf)
        new_document_clipper_pdf_reader.pdf_to_xml()
        pages = new_document_clipper_pdf_reader.get_pages()
        self.assertEqual(len(pages), 20)

    def test_merge_pdfs_with_rotation(self):
        actions = [(self.pdf_file.name, 90), (self.pdf_file.name, 90)]
        self.document_clipper_pdf_writer.merge(PATH_TO_NEW_PDF_FILE, actions)
        new_pdf = open(PATH_TO_NEW_PDF_FILE)
        new_document_clipper_pdf_reader = DocumentClipperPdfReader(new_pdf)
        new_document_clipper_pdf_reader.pdf_to_xml()
        pages = new_document_clipper_pdf_reader.get_pages()
        self.assertEqual(len(pages), 20)

    def test_merge_pdfs_with_blank_page(self):
        actions = [(self.pdf_file.name, 0), (self.pdf_file.name, 0)]
        self.document_clipper_pdf_writer.merge(PATH_TO_NEW_PDF_FILE, actions,
                                               append_blank_page=True)
        new_pdf = open(PATH_TO_NEW_PDF_FILE)
        new_document_clipper_pdf_reader = DocumentClipperPdfReader(new_pdf)
        new_document_clipper_pdf_reader.pdf_to_xml()
        pages = new_document_clipper_pdf_reader.get_pages()
        self.assertEqual(len(pages), 22)

    def test_merge_files_without_rotation(self):
        actions = [(self.pdf_file.name, 0), (PATH_TO_JPG_FILE, 0)]
        self.document_clipper_pdf_writer.merge(PATH_TO_NEW_PDF_FILE, actions)
        new_pdf = open(PATH_TO_NEW_PDF_FILE)
        new_document_clipper_pdf_reader = DocumentClipperPdfReader(new_pdf)
        new_document_clipper_pdf_reader.pdf_to_xml()
        pages = new_document_clipper_pdf_reader.get_pages()
        self.assertEqual(len(pages), 11)

    def test_merge_files_with_rotation(self):
        actions = [(self.pdf_file.name, 0), (PATH_TO_JPG_FILE, 90)]
        self.document_clipper_pdf_writer.merge(PATH_TO_NEW_PDF_FILE, actions)
        new_pdf = open(PATH_TO_NEW_PDF_FILE)
        new_document_clipper_pdf_reader = DocumentClipperPdfReader(new_pdf)
        new_document_clipper_pdf_reader.pdf_to_xml()
        pages = new_document_clipper_pdf_reader.get_pages()
        self.assertEqual(len(pages), 11)

    def test_merge_files_with_blank_page(self):
        actions = [(self.pdf_file.name, 0), (PATH_TO_JPG_FILE, 0)]
        self.document_clipper_pdf_writer.merge(PATH_TO_NEW_PDF_FILE, actions,
                                               append_blank_page=True)
        new_pdf = open(PATH_TO_NEW_PDF_FILE)
        new_document_clipper_pdf_reader = DocumentClipperPdfReader(new_pdf)
        new_document_clipper_pdf_reader.pdf_to_xml()
        pages = new_document_clipper_pdf_reader.get_pages()
        self.assertEqual(len(pages), 13)

    def test_slice(self):
        page_actions = [(2, 0), (3, 0)]
        self.document_clipper_pdf_writer.slice(self.pdf_file.name, page_actions, PATH_TO_NEW_PDF_FILE)

        new_pdf = open(PATH_TO_NEW_PDF_FILE)
        new_document_clipper_pdf_reader = DocumentClipperPdfReader(new_pdf)
        new_document_clipper_pdf_reader.pdf_to_xml()
        pages = new_document_clipper_pdf_reader.get_pages()
        self.assertEqual(len(pages), 2)

    def test_slice_with_page_candidate_below_valid_page_range(self):
        page_actions = [(0, 0), (3, 0)]

        with self.assertRaisesRegexp(Exception, u'Invalid page numbers range in actions: '
                                                u'page numbers cannot be lower than 1*'):
            self.document_clipper_pdf_writer.slice(self.pdf_file.name, page_actions, PATH_TO_NEW_PDF_FILE)

    def test_slice_with_page_candidate_above_valid_page_range(self):
        page_actions = [(50, 0), (3, 0)]

        with self.assertRaisesRegexp(Exception, u'Invalid page numbers range in actions: page numbers cannot exceed*'):
            self.document_clipper_pdf_writer.slice(self.pdf_file.name, page_actions, PATH_TO_NEW_PDF_FILE)

    def test_slice_with_rotation(self):
        self.document_clipper_pdf_writer.slice(self.pdf_file.name, [(2, 90), (4, 180)], PATH_TO_NEW_PDF_FILE)

        new_pdf = open(PATH_TO_NEW_PDF_FILE)
        new_document_clipper_pdf_reader = DocumentClipperPdfReader(new_pdf)
        new_document_clipper_pdf_reader.pdf_to_xml()
        pages = new_document_clipper_pdf_reader.get_pages()
        self.assertEqual(len(pages), 2)

    def test_pdf_to_text_from_pdf_with_only_text(self):
        text = self.document_clipper_pdf_reader.pdf_to_text()
        self.assertIn('Sample PDF Document', text)
        self.assertIn('How to write a document', text)
        self.assertIn('Math', text)
        self.assertIn('Huge', text)

    def test_pdf_to_text_from_pdf_with_images(self):
        self.pdf_file = open(PATH_TO_PDF_FILE_WITH_IMAGES)
        self.document_clipper_pdf_reader = DocumentClipperPdfReader(self.pdf_file)
        text = self.document_clipper_pdf_reader.pdf_to_text(self._images_to_text_method_mocked())
        self.assertIn('NIF', text)
        self.assertIn('Documento de identidad electrónico', text)
        self.assertEqual(4, len(self.document_clipper_pdf_reader._pdf_image_to_text_method.call_args_list))

    def test_pdf_to_text_from_pdf_with_images_no_jpg(self):
        # Only one pbm is extracted, converted to jpg and pdf_to_text
        self.pdf_file = open(PATH_TO_PDF_FILE_WITH_IMAGES_NO_JPG)
        self.document_clipper_pdf_reader = DocumentClipperPdfReader(self.pdf_file)
        self.document_clipper_pdf_reader.pdf_to_text(self._images_to_text_method_mocked())
        self.assertEqual(1, len(self.document_clipper_pdf_reader._pdf_image_to_text_method.call_args_list))
