#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Filename:ccf-novncproxy.py
# Date:Wed Nov 27 10:49:44 CST 2013
# Author:Pengbo Li
# E-mail:lipengbo10054444@gmail.com

'''
Websocket proxy that is compatible with ccf.
'''

import time
import Cookie
import socket
import websockify
from Crypto.Cipher import AES
import base64

aes_key = 'fnic123456789012'

class CCFWebSocketProxy(websockify.WebSocketProxy):

    def __init__(self, *args, **kwargs):
        websockify.WebSocketProxy.__init__(self, *args, **kwargs)

    def new_client(self):
        """
        Called after a new WebSocket connection has been established.
        """
        cookie = Cookie.SimpleCookie()
        cookie.load(self.headers.getheader('cookie'))
        token = cookie['token'].value
        print '----------------------------------'
        print token
        token_msg = self.decrypt(token.strip().split('_')[4]).split('_')
        print token_msg
        print '----------------------------------'
        host = token_msg[0]
        port = token_msg[1]
        tsock = None
        print int(time.time())
        print token_msg[2]
        try:
            if int(time.time()) - int(float(token_msg[2])) > 5:
                raise Exception('login expire')



            # Connect to the target
            self.msg("connecting to: %s:%s" % (
                   host, port))
            tsock = self.socket(host, port, connect=True)

            if self.verbose and not self.daemon:
                print(self.traffic_legend)

            # Start proxying

            self.do_proxy(tsock)
        except:
            if tsock:
                tsock.shutdown(socket.SHUT_RDWR)
                tsock.close()
                self.vmsg("%s:%s: Target closed" % (host, port))
            raise

    def decrypt(self, text):
        decode_base64_str = base64.b16decode(text)
        cryptor = AES.new(aes_key, AES.MODE_ECB)
        return cryptor.decrypt(decode_base64_str).strip()

if __name__ == '__main__':
    # Create and start the NovaWebSockets proxy
    server = CCFWebSocketProxy(listen_host='0.0.0.0',
                               listen_port=6080,
                               daemon=False,
                               web='./',
                               target_host='ignore',
                               target_port='ignore',
                               wrap_mode='exit',
                               wrap_cmd=None)
    server.start_server()
