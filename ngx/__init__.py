#!/usr/bin/python
# -*- coding: utf-8 -*-
__author__ = 'web'

from copy import deepcopy
from grammar_parser import parser


def _parse_server_line(line):
    """ server的配置本文 解析成对象
        :param "server ip:port max_fails=3 fail_timeout=15s;"
        :return ["ip:port", "3", "15s"]
    """
    server = []
    part = line.split()
    if len(part) > 2:
        server.append(part[1])
        for p in part[2:-1]:
            middle = p.split('=')[1]
            server.append(middle)
        # 除去最后一个元素的;
        last = part[-1][:-1].split('=')[1]
        server.append(last)
    else:
        # 格式: server ip:port;
        server.append(part[1][:-1])  # 除去结尾的;
        server.append('1')  # 加入 max_fails 默认值
        server.append('10s')  # 加入fail_timeout 默认值
    return server


class NotFindUpstream(Exception):
    pass

class NotFindServer(NotFindUpstream):
    pass

class UpstreamGroup(object):
    """
    upstreams = {
                    us_name: [ 'lb',
                               [server, max_fails, fail_timeout],
                               [...],...
                             ],
                    us_name2: [....]
                }
    """

    def __init__(self, ngx_home):
        self.ngx_home = ngx_home
        self.ngx_conf = self.ngx_home + '/conf/nginx.conf'
        self.us_group = self.get_upstream_group()

    def get_upstream_conf(self):
        """ 取出关于 upstream 的配置文本 """
        find_upstream = False
        res = []
        with open(self.ngx_conf) as ngx:
            line = ngx.readline()
            while line:
                if line[0] != '#' and 'upstream' in line and '{' in line:
                    find_upstream = True
                    res.append(line)
                elif find_upstream and '}' not in line:
                    res.append(line)
                elif find_upstream and '}' in line:
                    find_upstream = False
                    res.append(line)
                line = ngx.readline()
        return ''.join(res)

    def get_upstream_group(self):
        """返回upstreams对象"""
        # parser = new_parser()
        return parser.parse(self.get_upstream_conf())

    def get_upstream(self, us_name):
        """返回指定 upstream_name 的us对象"""
        us_name = str(us_name)
        try:
            # 对象的副本传递到 Upstream
            us_obj = deepcopy(self.us_group[us_name])
            us = Upstream(us_name, us_obj)
            return us
        except KeyError, e:
            raise NotFindUpstream("Upstream %s is not in conf" % e)

    def update_upstream_group(self, us):
        """更新或添加 upstream 对象"""
        if isinstance(us, Upstream):
            us_obj = [us.lb_algorithm]
            for server in us.servers:
                us_obj.append(server)
            self.get_upstream_group()[us.us_name] = us_obj
            return self.us_group[us.us_name]

    def del_upstream(self, *args):
        """删除一个或多个指定的 us对象,返回删除后的 upstreams 对象"""
        try:
            for us_name in args:
                self.us_group.pop(us_name)
            return self.us_group
        except NotFindUpstream, e:
            return self.us_group

    def dump_upstreams(self):
        """upstreams对象转为文本"""
        res = []
        for us_name, us_stmt in self.us_group.items():
            res.append("upstream %s {\n" % us_name)
            if us_stmt[0] != 'default':
                res.append('    ' + us_stmt[0] + ';\n')
            us_stmt.pop(0)
            for server in us_stmt:
                res.append(server_to_line(server))
            res.append('}\n')
        return ''.join(res)

    def update_ngx_conf(self):
        with open(self.ngx_conf, 'w') as f:
            f.write(self.dump_upstreams())


class Upstream(object):
    def __init__(self, us_name, us_obj):
        # us_obj = ['lb',[server],[server],...]
        self.us_name = us_name
        self.lb_algorithm = None if us_obj[0] == 'default' else us_obj.pop(0)
        self.servers = us_obj

    def add_server(self, ip, port, max_fails=None, fail_timeout=None):
        """ 添加server对象,ip是字符串 参数都是数字"""
        if not max_fails:
            max_fails = "1"
        if not fail_timeout:
            fail_timeout = "10s"
        self.servers.append([
            ip + ':' + port,
            max_fails,
            fail_timeout
        ])

    def del_server(self, ip):
        """ 根据 ip 删除 server 对象 """
        for index, server in enumerate(self.servers):
            if ip in server[0]:
                self.servers.pop(index)
                return self.servers
            else:
                raise NotFindServer("\"%s\" is not in upstream \"%s\"" % (ip, self.us_name))


if __name__ == '__main__':
    pass
    # string = 'server 10.10.10.10:8000 max_fails=11 fail_timeout=310s;'
    # str2 = 'server 10.10.10.10:8000;'
    # print(_parse_server_line(string))
    # print(_parse_server_line(str2))
    # ups = Upstreams('../test')
    # print(ups.get_upstream_conf())
    import json
    #
    # print(json.dumps(
    # ups.get_upstreams(), indent=4
    # ))
    # us_ggpt = ups.get_upstream('ggpt')
    # print(us_ggpt.lb_algorithm)
    # print(json.dumps(
    # us_ggpt.servers, indent=4
    # ))
    # print(json.dumps(
    #     us_ggpt.del_server('10.201.10.224'), indent=4
    # ))

    # print(json.dumps(
    #     us_ggpt.add_server('10.201.10.100', 8080, 10, 15), indent=4
    # ))

    # us_ggpt.add_server('10.201.10.199', 8080, 10, 15)
    # ups.update_upstream(us_ggpt)
    #
    # print(
    #     ups.dump_upstreams()
    # )
    # print(ups.dump_upstreams())
    # print(ups.del_upstream('ggpt', 'pm', 'passport', 'nongxin', 'imapi', 'cas', 'fuck'))
    # print(len(ups.get_upstreams()))
