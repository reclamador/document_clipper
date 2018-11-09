#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals
from unittest import TestCase
from mock import Mock, patch
import os

from document_clipper.pdf import DocumentClipperPdfReader, DocumentClipperPdfWriter
from PIL import Image

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))

PATH_TO_PDF_FILE = os.path.join(CURRENT_DIR, 'sample-files/sample.pdf')
PATH_TO_JPG_FILE = os.path.join(CURRENT_DIR, 'sample-files/sample.jpg')
PATH_TO_PNG_FILE = os.path.join(CURRENT_DIR, 'sample-files/sample.png')
PATH_TO_NEW_PDF_FILE = os.path.join(CURRENT_DIR, 'new_pdf.pdf')
PATH_TO_NEW_JPG_FILE = os.path.join(CURRENT_DIR, 'new_image.jpg')
PATH_TO_PDF_FILE_WITH_IMAGES = os.path.join(CURRENT_DIR, 'sample-files/dni_samples.pdf')
PATH_TO_PDF_FILE_WITH_IMAGES_NO_JPG = os.path.join(CURRENT_DIR, 'sample-files/pdf_with_images_not_jpg.pdf')
PATH_TO_HORIZONTAL_JPG_FILE = os.path.join(CURRENT_DIR, 'sample-files/horizontal-image-border.jpg')


class TestDocumentClipperPdf(TestCase):
    def setUp(self):
        self.pdf_file = open(PATH_TO_PDF_FILE, 'rb')
        self.img_file = Image.open(PATH_TO_JPG_FILE)
        self.document_clipper_pdf_reader = DocumentClipperPdfReader(self.pdf_file)
        self.document_clipper_pdf_writer = DocumentClipperPdfWriter()

    def tearDown(self):
        self.document_clipper_pdf_reader = None

    def _images_to_text_method_mocked(self):
        method = Mock()
        method.return_value = b'llamada a metodo'
        return method

    def _images_to_text_method_mocked_with_exception(self):
        method = Mock()
        method.side_effect = Exception
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
        new_pdf = open(new_pdf_path, 'rb')
        new_document_clipper_pdf_reader = DocumentClipperPdfReader(new_pdf)
        new_document_clipper_pdf_reader.pdf_to_xml()
        pages = new_document_clipper_pdf_reader.get_pages()
        self.assertEqual(len(pages), 1)
        new_pdf.close()
        os.remove(new_pdf_path)

    def test_compress_image(self):
        self.img_file = Image.open(PATH_TO_PNG_FILE)
        compressed_img = self.document_clipper_pdf_writer.compress_img(self.img_file)
        compressed_img.save(PATH_TO_NEW_JPG_FILE)
        self.assertTrue(os.path.getsize(PATH_TO_PNG_FILE) > os.path.getsize(PATH_TO_NEW_JPG_FILE))
        os.remove(PATH_TO_NEW_JPG_FILE)

    @patch('os.remove')
    def test_horizontal_image_to_vertical_pdf(self, mock_os_remove):
        actions = [
            (self.pdf_file.name, 0),
            (PATH_TO_HORIZONTAL_JPG_FILE, 90)
        ]
        self.document_clipper_pdf_writer.merge(PATH_TO_NEW_PDF_FILE, actions)

        new_pdf = open(PATH_TO_NEW_PDF_FILE, 'rb')
        new_document_clipper_pdf_reader = DocumentClipperPdfReader(new_pdf)
        new_document_clipper_pdf_reader.pdf_to_xml()
        pages = new_document_clipper_pdf_reader.get_pages()

        self.assertEqual(len(pages), 11)
        page_with_image = pages[-1]
        image_width, image_height = new_document_clipper_pdf_reader.get_page_max_dimensions(page_with_image)

        expected_width = 2008.0
        expected_height = 2677.0
        self.assertEqual(image_width, expected_width)
        self.assertEqual(image_height, expected_height)
        mock_os_remove.assert_called()

    @patch('os.remove')
    def test_merge_pdfs_without_rotation(self, mock_os_remove):
        actions = [(self.pdf_file.name, 0), (self.pdf_file.name, 0)]
        self.document_clipper_pdf_writer.merge(PATH_TO_NEW_PDF_FILE, actions)
        new_pdf = open(PATH_TO_NEW_PDF_FILE, 'rb')
        new_document_clipper_pdf_reader = DocumentClipperPdfReader(new_pdf)
        new_document_clipper_pdf_reader.pdf_to_xml()
        pages = new_document_clipper_pdf_reader.get_pages()
        self.assertEqual(len(pages), 20)
        self.assertEqual(len(mock_os_remove.call_args_list), 2)

    @patch('os.remove')
    def test_merge_pdfs_with_pdf_fixing(self, mock_os_remove):
        actions = [(self.pdf_file.name, 0), (self.pdf_file.name, 0)]
        self.document_clipper_pdf_writer.merge(PATH_TO_NEW_PDF_FILE, actions, fix_files=True)
        new_pdf = open(PATH_TO_NEW_PDF_FILE, 'rb')
        new_document_clipper_pdf_reader = DocumentClipperPdfReader(new_pdf)
        new_document_clipper_pdf_reader.pdf_to_xml()
        pages = new_document_clipper_pdf_reader.get_pages()
        self.assertEqual(len(pages), 20)
        mock_os_remove.assert_called()

    @patch('os.remove')
    def test_merge_pdfs_with_rotation(self, mock_os_remove):
        actions = [(self.pdf_file.name, 90), (self.pdf_file.name, 90)]
        self.document_clipper_pdf_writer.merge(PATH_TO_NEW_PDF_FILE, actions)
        new_pdf = open(PATH_TO_NEW_PDF_FILE, 'rb')
        new_document_clipper_pdf_reader = DocumentClipperPdfReader(new_pdf)
        new_document_clipper_pdf_reader.pdf_to_xml()
        pages = new_document_clipper_pdf_reader.get_pages()
        self.assertEqual(len(pages), 20)
        self.assertEqual(len(mock_os_remove.call_args_list), 2)

    @patch('os.remove')
    def test_merge_pdfs_with_blank_page(self, mock_os_remove):
        actions = [(self.pdf_file.name, 0), (self.pdf_file.name, 0)]
        self.document_clipper_pdf_writer.merge(PATH_TO_NEW_PDF_FILE, actions,
                                               append_blank_page=True)
        new_pdf = open(PATH_TO_NEW_PDF_FILE, 'rb')
        new_document_clipper_pdf_reader = DocumentClipperPdfReader(new_pdf)
        new_document_clipper_pdf_reader.pdf_to_xml()
        pages = new_document_clipper_pdf_reader.get_pages()
        self.assertEqual(len(pages), 22)
        self.assertEqual(len(mock_os_remove.call_args_list), 2)

    @patch('os.remove')
    def test_merge_files_without_rotation(self, mock_os_remove):
        actions = [(self.pdf_file.name, 0), (PATH_TO_JPG_FILE, 0)]
        self.document_clipper_pdf_writer.merge(PATH_TO_NEW_PDF_FILE, actions)
        new_pdf = open(PATH_TO_NEW_PDF_FILE, 'rb')
        new_document_clipper_pdf_reader = DocumentClipperPdfReader(new_pdf)
        new_document_clipper_pdf_reader.pdf_to_xml()
        pages = new_document_clipper_pdf_reader.get_pages()
        self.assertEqual(len(pages), 11)
        mock_os_remove.assert_called()

    @patch('os.remove')
    def test_merge_files_with_rotation(self, mock_os_remove):
        actions = [(self.pdf_file.name, 0), (PATH_TO_JPG_FILE, 90)]
        self.document_clipper_pdf_writer.merge(PATH_TO_NEW_PDF_FILE, actions)
        new_pdf = open(PATH_TO_NEW_PDF_FILE, 'rb')
        new_document_clipper_pdf_reader = DocumentClipperPdfReader(new_pdf)
        new_document_clipper_pdf_reader.pdf_to_xml()
        pages = new_document_clipper_pdf_reader.get_pages()
        self.assertEqual(len(pages), 11)
        mock_os_remove.assert_called()

    @patch('os.remove')
    def test_merge_images_with_pdf_fixing(self, mock_os_remove):
        # Setup
        mock_os_remove.side_effect = [None, None, OSError('already deleted'), OSError('already deleted')]
        actions = [(PATH_TO_HORIZONTAL_JPG_FILE, 0), (PATH_TO_JPG_FILE, 90)]
        self.document_clipper_pdf_writer.merge(PATH_TO_NEW_PDF_FILE, actions, fix_files=True)
        new_pdf = open(PATH_TO_NEW_PDF_FILE, 'rb')
        new_document_clipper_pdf_reader = DocumentClipperPdfReader(new_pdf)
        new_document_clipper_pdf_reader.pdf_to_xml()
        pages = new_document_clipper_pdf_reader.get_pages()
        self.assertEqual(len(pages), 2)
        num_os_remove_calls = len(mock_os_remove.call_args_list[0])
        self.assertEqual(num_os_remove_calls, 2)

    @patch('os.remove')
    def test_merge_images_and_pdfs_with_pdf_fixing(self, mock_os_remove):
        # Setup
        mock_os_remove.side_effect = [None, None, OSError('already deleted'), OSError('already deleted')]
        actions = [(self.pdf_file.name, 0), (PATH_TO_JPG_FILE, 90)]
        self.document_clipper_pdf_writer.merge(PATH_TO_NEW_PDF_FILE, actions, fix_files=True)
        new_pdf = open(PATH_TO_NEW_PDF_FILE, 'rb')
        new_document_clipper_pdf_reader = DocumentClipperPdfReader(new_pdf)
        new_document_clipper_pdf_reader.pdf_to_xml()
        pages = new_document_clipper_pdf_reader.get_pages()
        self.assertEqual(len(pages), 11)
        num_os_remove_calls = len(mock_os_remove.call_args_list[0])
        self.assertEqual(num_os_remove_calls, 2)

    @patch('os.remove')
    def test_merge_files_with_blank_page(self, mock_os_remove):
        actions = [(self.pdf_file.name, 0), (PATH_TO_JPG_FILE, 0)]
        self.document_clipper_pdf_writer.merge(PATH_TO_NEW_PDF_FILE, actions,
                                               append_blank_page=True)
        new_pdf = open(PATH_TO_NEW_PDF_FILE, 'rb')
        new_document_clipper_pdf_reader = DocumentClipperPdfReader(new_pdf)
        new_document_clipper_pdf_reader.pdf_to_xml()
        pages = new_document_clipper_pdf_reader.get_pages()
        self.assertEqual(len(pages), 13)
        mock_os_remove.assert_called()

    @patch('os.remove')
    def test_slice(self, mock_os_remove):
        page_actions = [(2, 0), (3, 0)]
        self.document_clipper_pdf_writer.slice(self.pdf_file.name, page_actions, PATH_TO_NEW_PDF_FILE)

        new_pdf = open(PATH_TO_NEW_PDF_FILE, 'rb')
        new_document_clipper_pdf_reader = DocumentClipperPdfReader(new_pdf)
        new_document_clipper_pdf_reader.pdf_to_xml()
        pages = new_document_clipper_pdf_reader.get_pages()
        self.assertEqual(len(pages), 2)
        mock_os_remove.assert_not_called()

    @patch('os.remove')
    def test_slice_out_of_bounds_page_range(self, mock_os_remove):
        page_actions = [(11, 0)]  # Sample PDF file has at most 10 pages

        with self.assertRaisesRegexp(Exception, u'Invalid page numbers range in actions: '
                                                u'page numbers cannot exceed the maximum numbers of '
                                                u'pages of the source PDF document'):
            self.document_clipper_pdf_writer.slice(self.pdf_file.name, page_actions, PATH_TO_NEW_PDF_FILE)
            mock_os_remove.assert_called()

    @patch('os.remove')
    def test_slice_with_pdf_fixing(self, mock_os_remove):
        page_actions = [(2, 0), (3, 0)]
        self.document_clipper_pdf_writer.slice(self.pdf_file.name, page_actions, PATH_TO_NEW_PDF_FILE, fix_file=True)

        new_pdf = open(PATH_TO_NEW_PDF_FILE, 'rb')
        new_document_clipper_pdf_reader = DocumentClipperPdfReader(new_pdf)
        new_document_clipper_pdf_reader.pdf_to_xml()
        pages = new_document_clipper_pdf_reader.get_pages()
        self.assertEqual(len(pages), 2)
        mock_os_remove.assert_called()

    @patch('os.remove')
    def test_slice_with_page_candidate_below_valid_page_range(self, mock_os_remove):
        page_actions = [(0, 0), (3, 0)]

        with self.assertRaisesRegexp(Exception, u'Invalid page numbers range in actions: '
                                                u'page numbers cannot be lower than 1*'):
            self.document_clipper_pdf_writer.slice(self.pdf_file.name, page_actions, PATH_TO_NEW_PDF_FILE)
            mock_os_remove.assert_called()

    @patch('os.remove')
    def test_slice_with_page_candidate_above_valid_page_range(self, mock_os_remove):
        page_actions = [(50, 0), (3, 0)]

        with self.assertRaisesRegexp(Exception, u'Invalid page numbers range in actions: page numbers cannot exceed*'):
            self.document_clipper_pdf_writer.slice(self.pdf_file.name, page_actions, PATH_TO_NEW_PDF_FILE)

            mock_os_remove.assert_not_called()

    @patch('os.remove')
    def test_slice_with_rotation(self, mock_os_remove):
        self.document_clipper_pdf_writer.slice(self.pdf_file.name, [(2, 90), (4, 180)], PATH_TO_NEW_PDF_FILE)

        new_pdf = open(PATH_TO_NEW_PDF_FILE, 'rb')
        new_document_clipper_pdf_reader = DocumentClipperPdfReader(new_pdf)
        new_document_clipper_pdf_reader.pdf_to_xml()
        pages = new_document_clipper_pdf_reader.get_pages()
        self.assertEqual(len(pages), 2)
        mock_os_remove.assert_not_called()

    def test_pdf_to_text_from_pdf_with_only_text(self):
        text = self.document_clipper_pdf_reader.pdf_to_text()
        self.assertIn('Sample PDF Document', text)
        self.assertIn('How to write a document', text)
        self.assertIn('Math', text)
        self.assertIn('Huge', text)

    def test_pdf_to_text_from_pdf_with_images(self):
        self.pdf_file = open(PATH_TO_PDF_FILE_WITH_IMAGES, 'rb')
        self.document_clipper_pdf_reader = DocumentClipperPdfReader(self.pdf_file)
        text = self.document_clipper_pdf_reader.pdf_to_text(self._images_to_text_method_mocked())
        self.assertIn(u'NIF', text)
        self.assertIn(u'Documento de identidad electrónico', text)
        self.assertEqual(4, len(self.document_clipper_pdf_reader._pdf_image_to_text_method.call_args_list))

    def test_pdf_to_text_from_pdf_with_images_no_jpg(self):
        # Only one pbm is extracted, converted to jpg and pdf_to_text
        self.pdf_file = open(PATH_TO_PDF_FILE_WITH_IMAGES_NO_JPG, 'rb')
        self.document_clipper_pdf_reader = DocumentClipperPdfReader(self.pdf_file)
        self.document_clipper_pdf_reader.pdf_to_text(self._images_to_text_method_mocked())
        self.assertEqual(1, len(self.document_clipper_pdf_reader._pdf_image_to_text_method.call_args_list))

    @patch('shutil.rmtree')
    def test_pdf_to_text_from_pdf_with_images_exception_raised(self, mock_rmtree):
        self.pdf_file = open(PATH_TO_PDF_FILE_WITH_IMAGES, 'rb')
        self.document_clipper_pdf_reader = DocumentClipperPdfReader(self.pdf_file)
        self.assertRaises(Exception, self.document_clipper_pdf_reader.pdf_to_text,
                          self._images_to_text_method_mocked_with_exception())
        self.assertEqual(1, len(mock_rmtree.call_args_list))

    @patch('os.remove')
    def test_fix_pdf_ok(self, mock_os_remove):
        ret_file_path = self.document_clipper_pdf_writer.fix_pdf(PATH_TO_PDF_FILE)
        source_file_basename = os.path.basename(PATH_TO_PDF_FILE)
        self.assertNotEqual(ret_file_path, PATH_TO_PDF_FILE)
        self.assertIn(source_file_basename, ret_file_path)
        mock_os_remove.assert_called_with(PATH_TO_PDF_FILE)

    @patch('os.remove')
    def test_fix_pdf_error(self, mock_os_remove):
        invalid_path = u'/invalid/dir/file.pdf'
        ret_file_path = self.document_clipper_pdf_writer.fix_pdf(invalid_path)
        self.assertEqual(ret_file_path, invalid_path)
        mock_os_remove.assert_not_called()

    @patch('os.remove')
    def test_cleaning_up_because_of_pdf_to_xml_tmp_images(self, mock_remove):
        self.pdf_file = open(PATH_TO_PDF_FILE_WITH_IMAGES, 'rb')
        with DocumentClipperPdfReader(self.pdf_file) as document_clipper_pdf_reader:
            pdf_to_xml = document_clipper_pdf_reader.pdf_to_xml()

        self.assertTrue(pdf_to_xml.is_xml)
        self.assertIsNotNone(pdf_to_xml.contents)
        # remove for images from tmp
        self.assertEqual(len(mock_remove.call_args_list), 4)

    @patch('os.remove')
    def test_cleaning_up_because_of_pdf_to_xml_tmp_images_nothing_to_clean(self, mock_remove):
        with DocumentClipperPdfReader(self.pdf_file) as document_clipper_pdf_reader:
            pdf_to_xml = document_clipper_pdf_reader.pdf_to_xml()

        self.assertTrue(pdf_to_xml.is_xml)
        self.assertIsNotNone(pdf_to_xml.contents)
        # remove for images from tmp
        self.assertEqual(len(mock_remove.call_args_list), 0)
