#!/usr/bin/python
# coding:utf8

import sys
from datetime import datetime

 
def logText(text):
    msgTime = datetime.now().strftime('%Y-%m-%d %H:%M:%S | ')
    try:
        print(msgTime + text)
    except UnicodeEncodeError:
        print(msgTime + text.encode('utf8'))
    sys.stdout.flush()
