#!/usr/bin/env python
# -*- coding: utf-8 -*-
import csv
import os

PDF_DIR = '~/Datasets/DAR-txt/'
DATASET = '~/Datasets/parlamento-datas_sessoes/data/datas_sessoes_plenarias.csv'

f = open(os.path.expanduser(DATASET), 'r')
data = csv.reader(f)
first = True
for leg, sess, num, date, date_pub in data:
    if first:
        first = False
        continue
    leg = int(leg)
    if leg < 7:
        # só há PDF a partir da 7 legislatura
        continue
    sess = int(sess)
    if 'S' not in num:
        num = int(num)
        filename = PDF_DIR + "%02d-%d-%03d.txt" % (leg, sess, num)
    else:
        filename = PDF_DIR + "%02d-%d-%s.txt" % (leg, sess, num)
    if not os.path.exists(os.path.expanduser(filename)):
        print filename.split('/')[-1]
