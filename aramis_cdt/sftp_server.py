#-------------------------------------------------------------------------------
#
# Copyright (c) 2012
# IMB, RWTH Aachen University,
# ISM, Brno University of Technology
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in the Spirrid top directory "licence.txt" and may be
# redistributed only under the conditions described in the aforementioned
# license.
#
# Thanks for using Simvisage open source!
#
#-------------------------------------------------------------------------------

import os
import sys
try:
    import paramiko
except ImportError, e:
    print "Install package >>paramiko<<.\n%s" % e

class Server(object):
    """
    Wraps paramiko for super-simple SFTP uploading and downloading.
    """

    def __init__(self, username, password, host, port=22):

        self.transport = paramiko.Transport((host, port))
        privatekeyfile = os.path.expanduser('~/.ssh/id_rsa')
        mykey = paramiko.RSAKey.from_private_key_file(privatekeyfile)
        if password == '':
            self.transport.connect(username=username, pkey=mykey)
        else:
            self.transport.connect(username=username, password=password)
        self.sftp = paramiko.SFTPClient.from_transport(self.transport)

    def upload(self, local, remote):
        self.sftp.put(local, remote, self._printTotals)

    def download(self, remote, local):
        self.sftp.get(remote, local, self._printTotals)

    def close(self):
        """
        Close the connection if it's active
        """

        if self.transport.is_active():
            self.sftp.close()
            self.transport.close()

    def _printTotals(self, transferred, toBeTransferred):
        print "Transferred: {0}\tStill to send: {1}\tProcent: {2}".format(transferred, toBeTransferred, transferred / float(toBeTransferred) * 100)
        # sys.stdout.write("\r" + "Downloading... %3f%%" % percent)
        # sys.stdout.flush()

    # with-statement support
    def __enter__(self):
        return self

    def __exit__(self, type, value, tb):
        self.close()

