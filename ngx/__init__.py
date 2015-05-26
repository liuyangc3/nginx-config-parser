#!/usr/bin/python
# -*- coding: utf-8 -*-
__author__ = 'web'

from grammar_parser import parser

def _parse_server_line(line):
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
        # server ip:port;   除去;
        server.append(part[1][:-1])

    return tuple(server)


class Upstreams(object):
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
        return res

    def get_upstream(self):
        conf = ''.join(self.get_upstream_conf())
        return parser.parse(conf)

    def add_upstreams(self, string):
        # add lb
        # add server
        pass

    def del_upstarams(self, us_name):
        pass


class Upstream(Upstreams):

    def __call__(self, us_name):
        return

    def add_server(self, string):
        # "server ip:port max=1 timeout=1s;"
        server = _parse_server_line(string)
        self.up.append(server)
        return self.up

    def del_server(self,):
        pass

if __name__ == '__main__':
    ups = Upstreams('../test')
    #print(''.join(ups.get_upstream_conf()))
    import json
    print(json.dumps(
        ups.get_upstream(), indent=4
    ))
    print(len(ups.get_upstream()))