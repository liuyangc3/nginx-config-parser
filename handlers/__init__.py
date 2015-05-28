#!/usr/bin/python
# -*- coding: utf-8 -*-
__author__ = 'web'

import simplejson as json
import os

from tornado import web
from ngx import UpstreamGroup, NotFindUpstream, NotFindServer
import config


def check_ipv4(value):
    parts = value.split('.')
    if len(parts) == 4 and all(x.isdigit() for x in parts):
        numbers = list(int(x) for x in parts)
        return all(0 <= num < 256 for num in numbers)
    return False


class BaseHandler(web.RequestHandler):
    def data_received(self, chunk):
        pass

    def initialize(self):
        self.ngx_home = config.ngx_home
        self.upstream_conf = config.upstream_conf

    def pretty_response(self, data):
        if 'pretty' in self.request.arguments:
            self.write(json.dumps(data, indent=4))
        else:
            self.write(json.dumps(data))


class IndexHandler(BaseHandler):
    def initialize(self):
        self.usgroup = UpstreamGroup(self.upstream_conf)

    def get(self):
        self.pretty_response(self.usgroup.group)


class ListHandler(BaseHandler):
    def initialize(self):
        self.usgroup = UpstreamGroup(self.upstream_conf)

    def get(self):
        self.write("Name:%-25sServers:\n" % '')
        for us_name in self.usgroup.group:
            self.write('%-30s%-25d\n' % (us_name, len(self.usgroup.get_upstream(us_name).servers)))


class UpstreamHandler(BaseHandler):
    def initialize(self):
        self.usgroup = UpstreamGroup(self.upstream_conf)

    def check_us_name(self, us_name):
        try:
            return self.usgroup.get_upstream(us_name)
        except NotFindUpstream, e:
            self.finish(e.message)

    def get(self, us_name):
        us = self.check_us_name(us_name)
        self.pretty_response(us.servers)

    def post(self, us_name):
        """ 增加一个 server 配置
        curl -XPOST 127.0.0.1:8000/us_name -d '["10.201.10.233:3333", "111", "10s"]'
        """
        us = self.check_us_name(us_name)
        if us:
            data = json.loads(self.request.body)
            ip = data[0].split(':')[0]
            if check_ipv4(ip):
                port = data[0].split(':')[1]
                us.add_server(ip, port, data[1], data[2])
                self.usgroup.update_upstream_group(us)
                self.usgroup.update_ngx_conf()
                os.system(self.ngx_home + '/sbin/nginx -s reload')
                self.pretty_response(us.servers)
            else:
                self.write("invalid ip address %s" % ip)
        else:
            return

    def delete(self, us_name):
        """ 删除一个 server 配置
        curl -XPOST 127.0.0.1:8000/us_name -d '10.201.10.233:3333'
        """
        us = self.check_us_name(us_name)
        if us:
            ip = self.request.body
            if check_ipv4(ip):
                try:
                    us.del_server(ip)
                    self.usgroup.update_upstream_group(us)
                    self.usgroup.update_ngx_conf()
                    os.system(self.ngx_home + '/sbin/nginx -s reload')
                    self.pretty_response(us.servers)
                except NotFindServer, e:
                    self.write(e.message)
            else:
                self.write("invalid ip address %s" % ip)
        else:
            return
