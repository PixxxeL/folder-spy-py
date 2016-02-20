# -*- coding: utf-8 -*-
'''
TODO:
1. add parseopts
2. get password from env
3. improve cleaner
'''

import os
from hashlib import md5
import logging
import json
import smtplib
from email.mime.text import MIMEText
import datetime
import sys
import shutil


SNAPSHORT_FILE = ''
ORIGINAL_DIR = ''
TESTED_DIR = ''
SMTP_HOST = 'smtp.mail.ru'
SMTP_PORT = 25 #465-SSL 25 587
SMTP_USER = ''
SMTP_PASS = ''
REPORT_EMAIL = ''
REPORT_SUBJECT = ''
MALEWARE_DIRS = (
    '.X1-unix',
)
#EXCLUDE_DIRS = ()
#EXCLUDE_EXTENSIONS = ()
DATA = {}
IS_CLEAR = False


logging.basicConfig(format='%(message)s', level=logging.INFO)

def email_report(messages):
    msg = datetime.datetime.now().strftime('%d-%m-%Y %H:%M:%S')
    msg = MIMEText(msg + '\n\n' + '\n'.join(messages))
    msg['Subject'] = REPORT_SUBJECT
    msg['From'] = SMTP_USER
    msg['To'] = REPORT_EMAIL
    server = smtplib.SMTP(SMTP_HOST, SMTP_PORT)
    server.starttls()
    server.login(SMTP_USER, SMTP_PASS)
    server.sendmail(SMTP_USER, [REPORT_EMAIL], msg.as_string())
    server.quit()

def compare_with_original():
    DATA = json.load(open(SNAPSHORT_FILE))
    dirs = []
    messages = []
    deleted = []
    for k, v in DATA.items():
        if v is None:
            dirs.append(k)
            deleted.append(k)
    for k in deleted:
        del DATA[k]
    for root, folders, files in os.walk(TESTED_DIR):
        cur_dir = os.path.split(root)[-1]
        if IS_CLEAR and cur_dir in MALEWARE_DIRS:
            shutil.rmtree(root)
            msg = 'Maleware directory: %s' % root
            messages.append(msg)
            logging.warning(msg)
            continue
        if root != TESTED_DIR and root not in dirs:
            msg = 'Suspicious directory: %s' % root
            messages.append(msg)
            logging.warning(msg)
            continue
        for f in files:
            fp = os.path.join(root, f)
            val = md5(open(fp).read()).hexdigest()
            if not DATA.has_key(fp):
                msg = 'Suspicious file: %s' % fp
                messages.append(msg)
                logging.warning(msg)
                continue
            if DATA[fp] != val:
                msg = 'Corrupted file: %s' % fp
                messages.append(msg)
                logging.warning(msg)
    if len(messages):
        email_report(messages)
    logging.info('Test finished!')

def make_snapshort():
    for root, folders, files in os.walk(ORIGINAL_DIR):
        logging.debug(root)
        if root != ORIGINAL_DIR:
            DATA[root] = None
        for f in files:
            fp = os.path.join(root, f)
            logging.debug('  %s' % fp)
            DATA[fp] = md5(open(fp).read()).hexdigest()
    json.dump(DATA, open(SNAPSHORT_FILE, 'wb'))
    logging.info('Snapshort is created!')

def main():
    if 'clear' in sys.argv:
        IS_CLEAR = True
    if 'create' in sys.argv:
        make_snapshort()
    if 'test' in sys.argv:
        compare_with_original()
    else:
        print 'Usage: python watcher.py [create] [test] [clear]'

if __name__ == '__main__':
    main()
