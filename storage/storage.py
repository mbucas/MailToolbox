#!/usr/bin/python
# coding:utf8

# Implement Mailbox access to mailboxes types that are not include in Python
# standard mailbox module

# Standard "Mailbox" object uses a path as a filesystem path to a mail
# container that does not have subfolders (some children implement subfolder
# access methods)

# Other local mailboxes have 2 paths:
# - Path to the mailbox file
# - Mail folder or label inside the mailbox file
# IMAP mailboxes have:
# - Connection properties to connect to IMAP server
# - Mail folder or label inside the mailbox

# In this code, the path in standard "Mailbox" will be used as the path to the
# mailbox file, and will be formatted as an URL for IMAP.
# See http://xml.resource.org/public/rfc/html/rfc2192.html
# Example: imap://user@example.com:port/imap-options

# Mail folder inside the mailbox storage wil be passed as a second argument, and
# will start with "/"

import sys

from dumpmail import *
from fakemail import *

from nomailstorage import *
from imap import *
from maildir import *
from thunderbird import *

if sys.platform == 'win32':
    from lotusnotes import *
    from outlook import *
