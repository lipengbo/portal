#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Filename:setup.py
# Date:一  4月 28 10:39:01 CST 2014
# Author:Pengbo Li
# E-mail:lipengbo10054444@gmail.com
import os
import sys
sys.path.insert(0, '../')
import subprocess
import exceptions


def start_process(args, **kw):
    try:
        print args
        p = subprocess.Popen(args,
                             stdin=subprocess.PIPE,
                             stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE, **kw)
        out, err = p.communicate()
        return (p.returncode, out, err)
    except exceptions.OSError as ex:
        print ex
        return (-1, None, None)


NOVNCHOME = os.path.abspath(os.path.curdir)
novnc_init_file = os.path.join(NOVNCHOME, 'etc/init/ccf-novnc.conf')
ln_novnc_init_file = os.path.abspath('/etc/init/ccf-novnc.conf')
ln_novnc_cmd = ['ln', '-s', novnc_init_file, ln_novnc_init_file]

new_novnc_home = os.path.abspath('/usr/local/novnc')
ln_novnc_dir_cmd = ['ln', '-s', NOVNCHOME, new_novnc_home]

print sys.argv
if len(sys.argv) == 2:
    if sys.argv[1] == 'install':
        start_process(ln_novnc_cmd)
        print 'novnc.conf success'
        start_process(ln_novnc_dir_cmd)
        print 'novnc dir success'
    elif sys.argv[1] == 'uninstall':
        print ln_novnc_init_file
        if os.path.exists(ln_novnc_init_file):
            os.remove(ln_novnc_init_file)
        print new_novnc_home
        if os.path.exists(new_novnc_home):
            os.remove(new_novnc_home)
    else:
        print 'unknown option, install|uninstall'
        sys.exit(1)
    init_cmd = ['initctl', 'reload-configuration']
    start_process(init_cmd)
else:
    print 'usage: python setup.py install|uninstall'
