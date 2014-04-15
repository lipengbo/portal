#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Filename:aes.py
# Date:二  4月 15 16:51:25 CST 2014
# Author:Pengbo Li
# E-mail:lipengbo10054444@gmail.com
import base64
from etc.config import aes_key
from Crypto.Cipher import AES


class mycrypt():

    def __init__(self, key=aes_key):
        self.key = key
        self.mode = AES.MODE_ECB

    def encrypt(self, text):
        cryptor = AES.new(self.key, self.mode)
        length = 16
        count = text.count('')
        if count < length:
            add = (length - count) + 1
            text = text + (' ' * add)
        elif count > length:
            add = (length - (count % length)) + 1
            text = text + (' ' * add)
        encry_str = cryptor.encrypt(text)
        return base64.b16encode(encry_str)

    def decrypt(self, text):
        decode_base64_str = base64.b16decode(text)
        cryptor = AES.new(self.key, self.mode)
        return cryptor.decrypt(decode_base64_str).strip()


if __name__ == '__main__':
    my1 = mycrypt()
    haha = my1.encrypt('192')
    print haha
    print my1.decrypt(haha)
    print len(my1.decrypt(haha))
