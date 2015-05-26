#!/usr/bin/python
# -*- coding: utf-8 -*-
__author__ = 'web'

import ply.lex as lex

# List of token names
tokens = (
    'NAME',
    'NUMBER',
    'UPSTREAM',
    'LB',  # upstream load balance
    'SERVER',  # upstream server
    'MAX_FAILS',  # max_fails
    'FAIL_TMOUT',  # fail_timeout
    'SEC',  # fail_timeout seconds
    'INCLUDE',  # nginx include command
    'COMMENT'
)

# Regular expression rules for  tokens
t_SERVER = r'\d+\.\d+\.\d+\.\d+\:\d+'
t_NUMBER = r'\d+'
t_ignore_COMMENT = r'\#.*'
t_ignore = ' \t'  # A string containing ignored characters (spaces and tabs)


def t_UPSTREAM(t):
    r'upstream'
    return t


def t_LB(t):
    r'(url_hash)|(ip_hash)'
    return t


def t_MAX_FAILS(t):
    r'max_fails'
    return t


def t_FAIL_TMOUT(t):
    r'fail_timeout'
    return t


def t_SEC(t):
    r'\d+s'
    return t


def t_INCLUDE(t):
    r'include .*'
    t.value = t.value.split()[1]
    return t


def t_NAME(t):
    r'[a-z_-]+'
    return t


literals = ['{', '}', ';', '=', '/']


# Define a rule so we can track line numbers
def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)


def t_error(t):
    print "Illegal character '%s'" % t.value[0]
    t.lexer.skip(1)

# Build the lexer
lexer = lex.lex()