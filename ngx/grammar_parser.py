#!/usr/bin/python
# -*- coding: utf-8 -*-
__author__ = 'web'

from lex_parser import *
import ply.yacc as yacc

upstream_dict = {}  # upstream 配置解析后的字典对象


def p_upstream_stmt_multi(p):
    """upstream_stmt_multi : upstream_stmt
                           | upstream_stmt_multi upstream_stmt"""
    # 只有一行server
    if len(p) == 2:
        k = p[1][0]
        v = p[1][1]
        upstream_dict[k] = v
    # 多行处理
    else:
        k = p[2][0]
        v = p[2][1]
        upstream_dict[k] = v
    p[0] = upstream_dict


def p_upstream_stmt(p):
    """upstream_stmt : UPSTREAM NAME '{' lb_stmt server_stmt_multi '}'"""
    if not p[4]:
        # 不写负载均衡算法,默认 default
        p[0] = p[2], ['default'] + p[5]
    else:
        p[0] = p[2], [p[4]] + p[5]


def p_lb_stmt(p):
    """lb_stmt : empty
               | LB ';'"""
    if len(p) == 1:
        p[0] = None
    else:
        p[0] = p[1]


def p_server_stmt_multi(p):
    """server_stmt_multi : server_stmt
                         | server_stmt_multi server_stmt"""
    # 只有一行server
    if len(p) == 2:
        p[0] = [p[1]]
    # 多行处理
    else:
        p[0] = p[1] + [p[2]]


def p_server_stmt(p):
    """server_stmt : NAME SERVER MAX_FAILS '=' NUMBER FAIL_TMOUT '=' SEC ';'
                   | NAME SERVER ';'"""
    if p[3] == 'max_fails':
        p[0] = [p[2], p[5], p[8]]
    else:
        # 如果配置中不写 max_fails 和 fail_timeout,自动加入默认值
        p[0] = [p[2], '1', '10s']


def p_empty(p):
    """empty :"""
    pass


def p_error(p):
    print 'parse error, unexpected token:', p.type

# Build the parser
parser = yacc.yacc()

if __name__ == '__main__':
    # 测试数据
    data = """
    upstream imapi {
    ip_hash;
    server   10.201.10.103:8080 max_fails=1 fail_timeout=10s;
    #server   10.201.10.203:8080 max_fails=1 fail_timeout=10s;
    }

    upstream fm {
        server   10.201.10.199:8080;
        server   10.201.10.106:8080 max_fails=18 fail_timeout=108s;

    }

    upstream fuckyou {
    ip_hash;
    server   10.201.10.999:8080 max_fails=1 fail_timeout=10s;
    server   10.201.10.998:8080 max_fails=1 fail_timeout=10s;
    }
    """
    import json

    print(json.dumps(
        parser.parse(data), indent=4
    ))