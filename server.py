#!/usr/bin/python
# -*- coding: utf-8 -*-
__author__ = 'web'

from tornado import httpserver
from tornado import ioloop
from tornado.web import Application
from tornado.options import define, options

import logging


define("port", default=8000, help="run on the given port", type=int)

from handlers import IndexHandler, ListHandler, UpstreamHandler

app = Application(handlers=[
    (r'/', IndexHandler),
    (r'/list', ListHandler),
    (r'/(\w+)', UpstreamHandler)
])

if __name__ == '__main__':
    options.parse_command_line()
    http_server = httpserver.HTTPServer(app)
    http_server.listen(options.port)
    logging.info('Server started at port %d' % 8000)
    ioloop.IOLoop.instance().start()
