import subprocess
import tempfile
import errno

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
        return 'image' in out
