import os

class ShellCommandError(Exception):
    """This error is raised when a shell.run returns a non-zero exit code
    (meaning the command failed).
    Based on textract, thxs :)
    """
    def __init__(self, command, exit_code, stdout, stderr):
        self.command = command
        self.exit_code = exit_code
        self.stdout = stdout
        self.stderr = stderr
        self.executable = self.command.split()[0]

    def is_not_installed(self):
        return os.name == 'posix' and self.exit_code == 127

    def not_installed_message(self):
        return (
            "The command `%(command)s` failed because `%(executable)s` is not installed on your system"
        ) % vars(self)

    def failed_message(self):
        return (
            "The command `%(command)s` failed with exit code %(exit_code) stdout %(stdout)s stderr %(stderr)s"
        ) % vars(self)

    def __str__(self):
        if self.is_not_installed():
            return self.not_installed_message()
        else:
            return self.failed_message()
