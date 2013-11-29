#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Filename:ccf-novncproxy.py
# Date:Wed Nov 27 10:49:44 CST 2013
# Author:Pengbo Li
# E-mail:lipengbo10054444@gmail.com

'''
Websocket proxy that is compatible with ccf.
'''

import Cookie
import socket
import websockify


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
        print '----------------------------------'
        token_msg = token.strip().split('_')
        host = token_msg[0]
        port = token_msg[1]

        # Connect to the target
        self.msg("connecting to: %s:%s" % (
                 host, port))
        tsock = self.socket(host, port, connect=True)

        if self.verbose and not self.daemon:
            print(self.traffic_legend)

        # Start proxying
        try:
            self.do_proxy(tsock)
        except:
            if tsock:
                tsock.shutdown(socket.SHUT_RDWR)
                tsock.close()
                self.vmsg("%s:%s: Target closed" % (host, port))
            raise


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
