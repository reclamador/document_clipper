#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function
from unittest import TestCase
import os
import shutil
from bs4 import BeautifulSoup
from mock import patch
from document_clipper.utils import PDFToTextCommand, PDFToImagesCommand, PDFListImagesCommand, FixPdfCommand, \
    PdfToXMLCommand
from document_clipper.exceptions import ShellCommandError
from PIL import Image

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))

PATH_TO_PDF_FILE = os.path.join(CURRENT_DIR, 'sample-files/sample.pdf')
PATH_TO_JPG_FILE = os.path.join(CURRENT_DIR, 'sample-files/sample.jpg')
PATH_TO_NEW_PDF_FILE = os.path.join(CURRENT_DIR, 'new_pdf.pdf')
PATH_TO_PDF_FILE_WITH_IMAGES = os.path.join(CURRENT_DIR, 'sample-files/dni_samples.pdf')
PATH_TO_PDF_FILE_WITH_IMAGES_NO_JPG = os.path.join(CURRENT_DIR, 'sample-files/pdf_with_images_not_jpg.pdf')


class TestShellCommands(TestCase):
    def setUp(self):
        self.pdf_file_with_text = open(PATH_TO_PDF_FILE, 'rb')
        self.img_file = Image.open(PATH_TO_JPG_FILE)
        self.pdf_file_with_images = open(PATH_TO_PDF_FILE_WITH_IMAGES, 'rb')

    def test_pdf_to_text_command_text_found(self):
        pdftotext_cmd = PDFToTextCommand()
        out = pdftotext_cmd.run(PATH_TO_PDF_FILE, 1)
        self.assertIn(b'Sample PDF Document', out)

    def test_pdf_to_text_command_text_found_other_page(self):
        pdftotext_cmd = PDFToTextCommand()
        out = pdftotext_cmd.run(PATH_TO_PDF_FILE, 5)
        self.assertIn(b'Chapter 1', out)

    def test_pdf_to_text_command_no_pdf(self):
        pdftotext_cmd = PDFToTextCommand()
        self.assertRaises(ShellCommandError, pdftotext_cmd.run, PATH_TO_JPG_FILE, 1)

    def test_pdf_images_list_not_found(self):
        pdflistimages_cmd = PDFListImagesCommand()
        out = pdflistimages_cmd.run(PATH_TO_PDF_FILE, 1)
        self.assertNotIn(b'jpg', out)
        self.assertNotIn(b'image', out)

    def test_pdf_images_list_found(self):
        pdflistimages_cmd = PDFListImagesCommand()
        out = pdflistimages_cmd.run(PATH_TO_PDF_FILE_WITH_IMAGES, 1)
        self.assertIn(b'jpeg', out)
        self.assertIn(b'image', out)

    def test_pdf_has_images(self):
        pdflistimages_cmd = PDFListImagesCommand()
        out = pdflistimages_cmd.run(PATH_TO_PDF_FILE_WITH_IMAGES, 1)
        self.assertTrue(pdflistimages_cmd.has_images(out))

    def test_pdf_has_images_no_jpg(self):
        pdflistimages_cmd = PDFListImagesCommand()
        out = pdflistimages_cmd.run(PATH_TO_PDF_FILE_WITH_IMAGES_NO_JPG, 1)
        self.assertTrue(pdflistimages_cmd.has_images(out))

    def test_pdf_images_list_no_pdf(self):
        pdflistimages_cmd = PDFListImagesCommand()
        self.assertRaises(ShellCommandError, pdflistimages_cmd.run, PATH_TO_JPG_FILE, 1)

    def test_pdf_images_not_found(self):
        pdftoimages_cmd = PDFToImagesCommand()
        out = pdftoimages_cmd.run(PATH_TO_PDF_FILE, 1)
        self.assertEqual(0, len(os.listdir(out)))
        shutil.rmtree(out)

    def test_pdf_images_found(self):
        pdftoimages_cmd = PDFToImagesCommand()
        out = pdftoimages_cmd.run(PATH_TO_PDF_FILE_WITH_IMAGES, 1)
        self.assertEqual(4, len(os.listdir(out)))
        shutil.rmtree(out)

    def test_pdf_images_no_pdf(self):
        pdftoimages_cmd = PDFToImagesCommand()
        self.assertRaises(ShellCommandError, pdftoimages_cmd.run, PATH_TO_JPG_FILE, 1)

    def test_pdf_images_no_jpg_found(self):
        pdftoimages_cmd = PDFToImagesCommand()
        out = pdftoimages_cmd.run(PATH_TO_PDF_FILE_WITH_IMAGES_NO_JPG, 1)
        self.assertEqual(1, len(os.listdir(out)))

    @patch('os.remove')
    def test_fix_pdf_command_ok(self, mock_os_remove):
        fix_pdf_command = FixPdfCommand()
        ret_file_path = fix_pdf_command.run(PATH_TO_PDF_FILE)
        self.assertNotEqual(ret_file_path, PATH_TO_PDF_FILE)
        mock_os_remove.assert_called_with(PATH_TO_PDF_FILE)

    @patch('os.remove')
    def test_fix_pdf_command_exception(self, mock_os_remove):
        invalid_file_path = u'/tmp/bla/file.pdf'
        fix_pdf_command = FixPdfCommand()
        ret_file_path = fix_pdf_command.run(invalid_file_path)
        self.assertEqual(ret_file_path, invalid_file_path)
        mock_os_remove.assert_not_called()

    def test_pdf_to_xml(self):
        pdf_to_xml_command = PdfToXMLCommand()

        ret_xml_data = pdf_to_xml_command.run(PATH_TO_PDF_FILE)
        xml_data = BeautifulSoup(ret_xml_data, 'xml')
        self.assertEqual(len(xml_data.findAll('page')), 10)

    @patch('os.remove')
    @patch('document_clipper.utils.subprocess.Popen')
    def test_fix_pdf_command_os_error_exception(self, mock_open, mock_os_remove):
        mocked_exception = OSError('Random os error')
        mocked_exception.errno = None

        fix_pdf_command = FixPdfCommand()
        ret_file_path = fix_pdf_command.run(PATH_TO_PDF_FILE)
        self.assertEqual(ret_file_path, PATH_TO_PDF_FILE)
        mock_os_remove.assert_not_called()

    @patch('os.remove')
    @patch('document_clipper.utils.subprocess.Popen')
    def test_fix_pdf_command_generic_exception(self, mock_popen, mock_os_remove):
        mocked_exception = Exception('blabla')
        mock_popen.side_effect = mocked_exception
        fix_pdf_command = FixPdfCommand()
        ret_file_path = fix_pdf_command.run(PATH_TO_PDF_FILE)
        self.assertEqual(ret_file_path, PATH_TO_PDF_FILE)
        mock_os_remove.assert_not_called()
