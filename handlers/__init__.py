#!/usr/bin/python
# -*- coding: utf-8 -*-
__author__ = 'web'

import simplejson as json
import os

from tornado import web
from ngx import UpstreamGroup, NotFindUpstream, NotFindServer

ngx_home = os.path.join(os.path.dirname(__file__), "../test")


def check_ipv4(value):
    parts = value.split('.')
    if len(parts) == 4 and all(x.isdigit() for x in parts):
        numbers = list(int(x) for x in parts)
        return all(0 <= num < 256 for num in numbers)
    return False


class IndexHandler(web.RequestHandler):
    def data_received(self, chunk):
        pass

    def get(self):
        us_group = UpstreamGroup(ngx_home)
        if 'pretty' in self.request.arguments:
            self.write(json.dumps(us_group.us_group, indent=4))
        else:
            self.write(json.dumps(us_group.us_group))


class UpstreamHandler(web.RequestHandler):
    def data_received(self, chunk):
        pass

    def initialize(self):
        self.us_group = UpstreamGroup(ngx_home)

    def check_us_name(self, us_name):
        try:
            return self.us_group.get_upstream(us_name)
        except NotFindUpstream, e:
            self.finish(e.message)

    def pretty_response(self, data):
        if 'pretty' in self.request.arguments:
            self.write(json.dumps(data, indent=4))
        else:
            self.write(json.dumps(data))

    def get(self, us_name):
        us = self.check_us_name(us_name)
        self.pretty_response(us.servers)

    def post(self, us_name):
        us = self.check_us_name(us_name)
        if us:
            data = json.loads(self.request.body)
            ip = data[0].split(':')[0]
            if check_ipv4(ip):
                port = data[0].split(':')[1]
                us.add_server(ip, port, data[1], data[2])
                self.us_group.update_upstream_group(us)
                self.us_group.update_ngx_conf()
                os.system(ngx_home + '/sbin/nginx -s reload')
                self.pretty_response(us.servers)
            else:
                self.write("invalid ip address %s" % ip)
        else:
            return

    def delete(self, us_name):
        us = self.check_us_name(us_name)
        if us:
            ip = self.request.body
            if check_ipv4(ip):
                try:
                    us.del_server(ip)
                    self.us_group.update_upstream_group(us)
                    self.us_group.update_ngx_conf()
                    os.system(ngx_home + '/sbin/nginx -s reload')
                    self.pretty_response(us.servers)
                except NotFindServer, e:
                    self.write(e.message)
            else:
                self.write("invalid ip address %s" % ip)
        else:
            return
