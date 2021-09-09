from __future__ import absolute_import, division, print_function
from datetime import datetime
import errno
import os
import random
import string
import subprocess
import tempfile

from document_clipper import exceptions


class ShellCommand(object):
    """
    Make easier to run external programs.
    Based on textract, thxs :)
    """

    def run(self, args):
        """
        Run command return stdout and stderr as tuple.
        IF not successful raises ShellCommandError
        """
        # run a subprocess and put the stdout and stderr on the pipe object
        try:
            pipe = subprocess.Popen(
                args,
                stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            )
        except OSError as e:
            if e.errno == errno.ENOENT:
                # File not found.
                # This is equivalent to getting exitcode 127 from sh
                raise exceptions.ShellCommandError(
                    ' '.join(args), 127, '', '',
                )
            else:
                raise exceptions.ShellCommandError(' '.join(args), e.errno or -1, '', e.strerror or '')

        # pipe.wait() ends up hanging on large files. using
        # pipe.communicate appears to avoid this issue
        stdout, stderr = pipe.communicate()

        # if pipe is busted, raise an error (unlike Fabric)
        if pipe.returncode != 0:
            raise exceptions.ShellCommandError(
                ' '.join(args), pipe.returncode, stdout, stderr,
            )

        return stdout, stderr

    def temp_dir(self):
        """
        Return
        :return:
        """
        return tempfile.mkdtemp()


class PDFToTextCommand(ShellCommand):
    """
    pdftotext Poppler utils
    """
    def run(self, file_name, page):
        stdout, stderr = super(PDFToTextCommand, self).run(['pdftotext', '-enc', 'UTF-8', '-f', str(page), '-l',
                                                            str(page), file_name, '-'])
        return stdout


class PDFToImagesCommand(ShellCommand):
    """
    pdfimages Poppler utils
    """
    def run(self, file_name, page):
        tmp_dir = self.temp_dir()
        stdout, stderr = super(PDFToImagesCommand, self).run(['pdfimages', '-f', str(page), '-l', str(page), '-j',
                                                              file_name, '%s/%s' % (tmp_dir, str(page))])
        return tmp_dir


class PDFListImagesCommand(ShellCommand):
    """
    pdfimages Poppler utils just check if there are images
    """
    def run(self, file_name, page):
        stdout, stderr = super(PDFListImagesCommand, self).run(['pdfimages', '-f', str(page), '-l', str(page),
                                                                '-list', file_name])
        return stdout

    def has_images(self, out):
        return b'image' in out


class FixPdfCommand(ShellCommand):
    """
    Creates a new PDF file from a possibly-corrupted or bad-formatted PDF file.
    """

    def run(self, input_file_path):
        in_filename = os.path.basename(input_file_path)

        random.seed(datetime.now())
        filename_prefix = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(7))
        path_to_corrected_pdf = u"/tmp/%s_%s" % (filename_prefix, in_filename)

        try:
            super(FixPdfCommand, self).run(['/usr/bin/pdftocairo', '-pdf', '-origpagesizes',
                                            input_file_path, path_to_corrected_pdf])
        except exceptions.ShellCommandError:
            return input_file_path
        except Exception:
            return input_file_path
        else:
            os.remove(input_file_path)
            return path_to_corrected_pdf


class PdfToXMLCommand(ShellCommand):

    def run(self, pdf_file_path):
        with tempfile.NamedTemporaryFile(mode='r', suffix='.xml', encoding='latin-1', errors='replace') as xmlin:
            tmpxml = os.path.splitext(xmlin.name)[0]
            stdout, stderr = super(PdfToXMLCommand, self).run(['pdftohtml', '-xml', '-nodrm', '-zoom', '1.5',
                                                               '-enc', 'Latin1', '-noframes', pdf_file_path, tmpxml])
            xmldata = xmlin.read()
        try:
            return xmldata.decode('utf-8')
        except AttributeError:
            return xmldata
