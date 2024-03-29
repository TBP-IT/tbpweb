from django.core.management import execute_from_command_line


class DevServer(object):
    DEFAULT_IP = '0.0.0.0'

    # The port number to which an offset is added depending on the user
    PORT = 8000

    # The default port offset, if a user is not found in the OFFSETS below
    DEFAULT_OFFSET = 999

    # The value for this dict is the port and should be a number between 80 and
    # 998. These numbers are added to the PORT value above.
    # To add a new person and port: include their username and port offset in
    # the dict. Please pick the next available number.
    OFFSETS = {
        'wli': 80,
        'flieee': 85,
        'christandiono': 95,
        'wangj': 97,
        'giovanni': 100,
        'arunke': 101,
        'natebailey': 102,
        'ehy': 106,
        'jwesor': 107,
        'srinivasapranav': 108,
        'mattchang': 136,
        'sjdemartini': 144,
        'yeseon': 201,
        'jerrycheng': 222,
        'gtan': 245,
        'kevinhu': 294,
        'tonyduan': 333,
        'jerryjrchen': 334,
        'andrewliu': 335,
        'jkim': 418,
        'stefanpalombo': 666,
        'kevinma': 687,
        'giuliozhou': 746,
        'rahulverma': 747,
        'mitch27': 827,
        'ericdwang': 888,
        'mlalwani': 889,
        # Please do not use port 999 since it is the shared port
    }

    def __init__(self, username=None, localhost=False):
        # pylint: disable=C0103
        self.ip = 'localhost' if localhost else DevServer.DEFAULT_IP
        self.port = self.get_port(username)

    def get_port(self, username, verbose=True):
        """
        Given a username, return the corresponding port number using a
        dictionary lookup. If the lookup fails, returns a shared port. The port
        is also set as the current port for the object instance.
        """
        offset = DevServer.OFFSETS.get(username, DevServer.DEFAULT_OFFSET)
        self.port = DevServer.PORT + offset
        if verbose:
            if offset == DevServer.DEFAULT_OFFSET:
                print('WARNING: Using shared port: %d' % self.port)
            print('Current IP and Port is: %s and %d' % (self.ip, self.port))
        return self.port

    def run_server(self, verbose=True):
        """Runs a dev server based on current settings"""
        if verbose:
            print('Running server...')
        try:
            execute_from_command_line(
                ['manage.py', 'runserver', '%s:%d' % (self.ip, self.port)])
        except KeyboardInterrupt:
            # Catch Ctrl-C and exit cleanly without a stacktrace
            if verbose:
                print('KeyboardInterrupt: Exiting')
