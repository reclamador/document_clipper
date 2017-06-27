#!/usr/bin/env python
# -*- coding: utf-8 -*-

from unittest import TestCase
import os
from document_clipper.pdf import DocumentClipperPdf

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))

PATH_TO_PDF_FILE = os.path.join(CURRENT_DIR, 'sample-files/sample.pdf')


class TestDocumentClipperPdf(TestCase):
    def setUp(self):
        self.pdf_file = open(PATH_TO_PDF_FILE)
        self.document_clipper_pdf = DocumentClipperPdf(self.pdf_file)

    def tearDown(self):
        self.document_clipper_pdf = None

    def test_pdf_to_xml_ok(self):
        pdf_to_xml = self.document_clipper_pdf.pdf_to_xml()

        self.assertTrue(pdf_to_xml.is_xml)
        self.assertIsNotNone(pdf_to_xml.contents)

    def test_get_pages_ok(self):
        self.document_clipper_pdf.pdf_to_xml()
        pages = self.document_clipper_pdf.get_pages()
        self.assertEqual(len(pages), 10)

    def test_find_text_with_content_ok(self):
        self.document_clipper_pdf.pdf_to_xml()
        pages = self.document_clipper_pdf.get_pages()
        text_node = self.document_clipper_pdf.find_text_with_content(pages=pages,
                                                   text_to_find=u'chapter 3',
                                                   start_page=0)
        self.assertIsNotNone(text_node)

    def test_find_text_with_content_not_ok(self):
        self.document_clipper_pdf.pdf_to_xml()
        pages = self.document_clipper_pdf.get_pages()
        start_page = len(pages) - 1
        text_node = self.document_clipper_pdf.find_text_with_content(pages=pages,
                                                                     text_to_find=u'chapter 3',
                                                                     start_page=start_page)
        self.assertIsNone(text_node)

    def test_get_text_coordinates_ok(self):
        EXPECTED_X_POSITION = 149.0
        EXPECTED_Y_POSITION = 493.0
        EXPECTED_WIDTH = 350.0
        EXPECTED_HEIGHT = 16.0

        self.document_clipper_pdf.pdf_to_xml()
        pages = self.document_clipper_pdf.get_pages()
        text_node = self.document_clipper_pdf.find_text_with_content(pages=pages,
                                                                     text_to_find=u'chapter 3',
                                                                     start_page=0)
        x_position, y_position, width, height = self.document_clipper_pdf.get_text_coordinates(text_node)

        self.assertEqual(x_position, EXPECTED_X_POSITION)
        self.assertEqual(y_position, EXPECTED_Y_POSITION)
        self.assertEqual(width, EXPECTED_WIDTH)
        self.assertEqual(height, EXPECTED_HEIGHT)

    def test_get_page_dimensions_ok(self):
        EXPECTED_MAX_PAGE_WIDTH = 892.0
        EXPECTED_MAX_PAGE_HEIGHT = 1262.0

        self.document_clipper_pdf.pdf_to_xml()
        pages = self.document_clipper_pdf.get_pages()
        first_page = pages[0]

        page_width, page_height = self.document_clipper_pdf.get_page_max_dimensions(first_page)

        self.assertEqual(page_width, EXPECTED_MAX_PAGE_WIDTH)
        self.assertEqual(page_height, EXPECTED_MAX_PAGE_HEIGHT)
