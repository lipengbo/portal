#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Filename:novnc.py
# Date:一  4月 28 11:30:06 CST 2014
# Author:Pengbo Li
# E-mail:lipengbo10054444@gmail.com
from utils import ccf_novncproxy


if __name__ == '__main__':
    ccf_novncproxy.start_novnc(web='/usr/local/novnc/')
