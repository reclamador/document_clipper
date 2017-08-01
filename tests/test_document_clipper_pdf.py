#!/usr/bin/env python
# -*- coding: utf-8 -*-

from unittest import TestCase
from mock import mock
import os
from document_clipper.pdf import DocumentClipperPdfReader, DocumentClipperPdfWriter
from PIL import Image

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))

PATH_TO_PDF_FILE = os.path.join(CURRENT_DIR, 'sample-files/sample.pdf')
PATH_TO_JPG_FILE = os.path.join(CURRENT_DIR, 'sample-files/sample.jpg')
PATH_TO_NEW_PDF_FILE = os.path.join(CURRENT_DIR, 'new_pdf.pdf')


class TestDocumentClipperPdf(TestCase):
    def setUp(self):
        self.pdf_file = open(PATH_TO_PDF_FILE)
        self.img_file = Image.open(PATH_TO_JPG_FILE)
        self.document_clipper_pdf_reader = DocumentClipperPdfReader(self.pdf_file)
        self.document_clipper_pdf_writer = DocumentClipperPdfWriter()

    def tearDown(self):
        self.document_clipper_pdf_reader = None

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
        non_text_node = mock.Mock()
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

    def test_merge_pdfs(self):
        self.document_clipper_pdf_writer.merge(PATH_TO_NEW_PDF_FILE, [self.pdf_file.name, self.pdf_file.name])
        new_pdf = open(PATH_TO_NEW_PDF_FILE)
        new_document_clipper_pdf_reader = DocumentClipperPdfReader(new_pdf)
        new_document_clipper_pdf_reader.pdf_to_xml()
        pages = new_document_clipper_pdf_reader.get_pages()
        self.assertEqual(len(pages), 20)

    def test_merge_pdfs_with_blank_page(self):
        self.document_clipper_pdf_writer.merge(PATH_TO_NEW_PDF_FILE, [self.pdf_file.name, self.pdf_file.name],
                                               blank_page=True)
        new_pdf = open(PATH_TO_NEW_PDF_FILE)
        new_document_clipper_pdf_reader = DocumentClipperPdfReader(new_pdf)
        new_document_clipper_pdf_reader.pdf_to_xml()
        pages = new_document_clipper_pdf_reader.get_pages()
        self.assertEqual(len(pages), 22)

    def test_merge_files(self):
        self.document_clipper_pdf_writer.merge(PATH_TO_NEW_PDF_FILE, [self.pdf_file.name, PATH_TO_JPG_FILE])
        new_pdf = open(PATH_TO_NEW_PDF_FILE)
        new_document_clipper_pdf_reader = DocumentClipperPdfReader(new_pdf)
        new_document_clipper_pdf_reader.pdf_to_xml()
        pages = new_document_clipper_pdf_reader.get_pages()
        self.assertEqual(len(pages), 11)

    def test_merge_files_with_blank_page(self):
        self.document_clipper_pdf_writer.merge(PATH_TO_NEW_PDF_FILE, [self.pdf_file.name, PATH_TO_JPG_FILE],
                                               blank_page=True)
        new_pdf = open(PATH_TO_NEW_PDF_FILE)
        new_document_clipper_pdf_reader = DocumentClipperPdfReader(new_pdf)
        new_document_clipper_pdf_reader.pdf_to_xml()
        pages = new_document_clipper_pdf_reader.get_pages()
        self.assertEqual(len(pages), 13)
